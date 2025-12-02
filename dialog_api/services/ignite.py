from datetime import timedelta
from typing import Any

import orjson
from pydantic import BaseModel
from pyignite import AioClient
from pyignite.aio_cache import AioCache
from pyignite.datatypes import ExpiryPolicy
from pyignite.datatypes.prop_codes import PROP_EXPIRY_POLICY, PROP_NAME

from dialog_api.settings import Ignite


class AioIgniteClient:
    def __init__(self, settings: Ignite) -> None:
        self.client = AioClient(username=settings.username, password=settings.password)
        self.max_time_duration = settings.max_time_duration
        self.settings = settings

    def create_settings(self, fields: dict | None = None) -> dict:
        if not fields:
            fields = {}
        return {
            PROP_EXPIRY_POLICY: ExpiryPolicy(
                create=timedelta(seconds=self.max_time_duration),
                update=timedelta(seconds=self.max_time_duration),
                access=timedelta(seconds=self.max_time_duration),
            ),
            **fields,
        }

    async def connect(self, addresses: str) -> None:
        addresses: list[list[str, str]] = [address.split(':') for address in addresses.split(',')]
        addresses: list[tuple[str, int]] = [(address[0], int(address[1])) for address in addresses]
        await self.client._connect(addresses)

    async def shutdown(self) -> None:
        await self.client.close()

    async def get_cache(self, client_settings: dict, name: str) -> AioCache:
        client_settings[PROP_NAME] = f"{self.settings.cache_name}-{name}"
        return await self.client.get_or_create_cache(settings=client_settings)


class BaseCache:
    def __init__(self, cache: AioCache) -> None:
        self.cache = cache

    async def get(self, client_id: str, default: Any) -> str | None:
        data = await self.cache.get(client_id)
        return orjson.loads(data) if data else default

    async def put(self, client_id: str, value: Any) -> None:
        await self.cache.put(key=client_id, value=orjson.dumps(value))


class HistoryCache(BaseCache): ...


class CachesContext(BaseModel):
    client: AioIgniteClient | None = None
    history: HistoryCache | None = None

    async def configure(self, settings: Ignite) -> None:
        self.client = AioIgniteClient(settings)
        await self.client.connect(addresses=settings.addresses)
        self.history = HistoryCache(
            cache=await self.client.get_cache(
                client_settings=self.client.create_settings(), name="HISTORY"
            )
        )
        return self.client, self.history

    class Config:
        arbitrary_types_allowed = True

caches_context = CachesContext()

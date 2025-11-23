import asyncio
from time import time as current_time

from aiohttp import ClientSession, hdrs

from dialog_api.clients.giga import logger
from dialog_api.utils.uuid import generate_uuid


class TokenVerification:
    def __init__(
            self, session: ClientSession, access_key: str, scope: str,
            access_token_url: str, token_lifetime: int = 20 * 60,
    ) -> None:
        """
        Клиент для вызова GigaChat

        :param session: Сессия GigaChat
        :param url: Путь до GigaChat
        :param temperature: Параметр креативности ответов (0.0 - 1.0)
        :param profanity_check: Фильтр нецензурной лексики
        :param scope: Права доступа для токена
        """
        self._session = session
        self._access_token_url = access_token_url
        self._access_token: str | None = None
        self._access_key = access_key
        self._token_expires_at = None
        self._token_lifetime = token_lifetime
        self.scope = scope
        self._alock = asyncio.Lock()

    async def refresh_token(self) -> str:
        async with self._alock:
            headers = {
                hdrs.CONTENT_TYPE: "application/x-www-form-urlencoded",
                hdrs.ACCEPT: "application/json",
                hdrs.AUTHORIZATION: f"Basic {self._access_key}",
                "RqUID": generate_uuid(),
            }
            body = {"scope": self.scope}

            async with self._session.post(self._access_token_url, headers=headers, data=body) as response:
                response.raise_for_status()
                data = await response.json()

            if "access_token" not in data:
                raise ValueError("Access token was not received")

            self._access_token = data["access_token"]
            self._token_expires_at = current_time() + self._token_lifetime
            logger.debug(f"Обновление сессии до времени '{self._token_expires_at}'")
            return self._access_token

    def _is_token_expired(self) -> bool:
        if not self._access_token or not self._token_expires_at:
            return True
        return current_time() >= (self._token_expires_at - 30)


    async def _ensure_valid_token(self) -> str:
        if self._is_token_expired():
            await self.refresh_token()
        return self._access_token

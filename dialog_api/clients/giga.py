import logging

from langchain_community.chat_models import GigaChat

from dialog_api.settings import GigaSettings

logger = logging.getLogger(__name__)


def create_gigachat_client(
        settings: GigaSettings, access_token: str
) -> GigaChat:

    return GigaChat(
        access_token=access_token,
        base_url=settings.url,
        model=settings.model,
        profanity_check=settings.profanity_check,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        timeout=settings.timeout,
        verify_ssl_certs=settings.verify_ssl_certs,
    )

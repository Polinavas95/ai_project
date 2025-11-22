import logging
import ssl

from langchain_community.chat_models import GigaChat

from app.settings import GigaSettings

logger = logging.getLogger(__name__)


def create_gigachat_client(
        settings: GigaSettings, access_token: str
) -> GigaChat:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    return GigaChat(
        access_token=access_token,
        base_url=settings.url,
        model=settings.model,
        profanity_check=settings.profanity_check,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        timeout=settings.timeout,
        ssl_context=ssl_context,
        verify_ssl_certs=settings.verify_ssl_certs,
    )

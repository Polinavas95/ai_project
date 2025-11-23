import pytest
from unittest.mock import Mock, patch
from dialog_api.clients.giga import create_gigachat_client
from dialog_api.settings import GigaSettings
from langchain_community.chat_models import GigaChat


class TestCreateGigaChatClient:

    def test_create_gigachat_client_success(self):
        """Тест успешного создания клиента GigaChat"""
        mock_settings = Mock(spec=GigaSettings)
        mock_settings.url = "https://api.gigachat.test"
        mock_settings.model = "GigaChat-Pro"
        mock_settings.profanity_check = True
        mock_settings.temperature = 0.7
        mock_settings.max_tokens = 1000
        mock_settings.timeout = 30
        mock_settings.verify_ssl_certs = True

        access_token = "test-token-123"
        with patch("dialog_api.clients.giga.GigaChat") as mock_giga_chat:
            mock_giga_chat.return_value = Mock(spec=GigaChat)
            client = create_gigachat_client(mock_settings, access_token)

        mock_giga_chat.assert_called_once_with(
            access_token=access_token,
            base_url=mock_settings.url,
            model=mock_settings.model,
            profanity_check=mock_settings.profanity_check,
            temperature=mock_settings.temperature,
            max_tokens=mock_settings.max_tokens,
            timeout=mock_settings.timeout,
            verify_ssl_certs=mock_settings.verify_ssl_certs,
        )
        assert client is not None

    def test_create_gigachat_client_with_none_settings(self):
        """Тест создания клиента с None настройками"""
        access_token = "test-token-123"
        with pytest.raises(Exception):
            create_gigachat_client(None, access_token)

    def test_create_gigachat_client_with_empty_token(self):
        """Тест создания клиента с пустым токеном"""
        mock_settings = Mock(spec=GigaSettings)
        with pytest.raises(Exception):
            create_gigachat_client(mock_settings, "")

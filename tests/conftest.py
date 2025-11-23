import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from gigachat import GigaChat
from langchain.chains.llm import LLMChain
from langchain_core.prompts import ChatPromptTemplate

from dialog_api.agents.dialog_agent import DialogAgent
from dialog_api.services.rag import RAGService
from dialog_api.utils.token_verification import TokenVerification


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_giga_client():
    mock = Mock(spec=GigaChat)
    mock.ainvoke = AsyncMock()
    mock.invoke = Mock()
    mock.batch = Mock()
    mock.abatch = AsyncMock()
    mock.stream = Mock()
    mock.astream = AsyncMock()
    return mock


@pytest.fixture
def mock_llm_chain():
    mock = Mock(spec=LLMChain)
    mock.ainvoke = AsyncMock()
    mock.llm = Mock()
    return mock


@pytest.fixture
def mock_token_verification():
    mock = Mock(spec=TokenVerification)
    mock._is_token_expired.return_value = False
    mock._ensure_valid_token = AsyncMock(return_value="new-token-123")
    return mock


@pytest.fixture
def mock_rag_service():
    mock = Mock(spec=RAGService)
    mock.get_relevant_context.return_value = "Test context from RAG"
    return mock


@pytest.fixture
def mock_chat_prompt_template():
    mock = Mock(spec=ChatPromptTemplate)
    return mock


@pytest.fixture
def dialog_agent(mock_giga_client, mock_token_verification, mock_rag_service, mock_llm_chain):
    with pytest.MonkeyPatch().context() as m:
        m.setattr('dialog_api.agents.dialog_agent.LLMChain', Mock(return_value=mock_llm_chain))

        agent = DialogAgent(
            giga_client=mock_giga_client,
            token_verification=mock_token_verification,
            rag_service=mock_rag_service,
            message_history_number=5
        )

        agent._mock_llm_chain = mock_llm_chain
        return agent


@pytest.fixture
def sample_dialog_data():
    return {
        "history": ["Привет!", "Как дела?"],
        "study_topic": "Python programming",
        "current_message": "Что такое декоратор?",
        "user_level": "beginner"
    }


@pytest.fixture
def mock_giga_settings():
    mock_settings = Mock()
    mock_settings.url = "https://api.gigachat.test"
    mock_settings.model = "GigaChat-Pro"
    mock_settings.profanity_check = True
    mock_settings.temperature = 0.7
    mock_settings.max_tokens = 1000
    mock_settings.timeout = 30
    mock_settings.verify_ssl_certs = True
    return mock_settings


@pytest.fixture(autouse=True)
def mock_app_settings(monkeypatch, mock_giga_settings):
    try:
        from dialog_api.agents.dialog_agent import app_settings
        mock_settings = Mock()
        mock_settings.giga = mock_giga_settings
        monkeypatch.setattr("dialog_api.agents.dialog_agent.app_settings", mock_settings)
    except ImportError:
        pass

import pytest
from unittest.mock import AsyncMock, patch, Mock

from dialog_api.agents.dialog_agent import DialogAgent


class TestDialogAgent:

    @pytest.mark.asyncio
    async def test_ainvoke_success(self, dialog_agent, mock_rag_service, sample_dialog_data):
        mock_output = Mock()
        mock_output.__getitem__ = Mock(side_effect=lambda
            key: "{\"answer\": \"Python это классный язык программирования\"}" if key == "text" else None)
        mock_output.text = "{\"answer\": \"Python это классный язык программирования\"}"

        dialog_agent._mock_llm_chain.ainvoke = AsyncMock(return_value=mock_output)

        with patch('dialog_api.agents.dialog_agent.parse_json') as mock_parse_json:
            mock_parse_json.return_value = {"answer": "Python это классный язык программирования"}

            answer, updated_history = await dialog_agent.ainvoke(**sample_dialog_data)

        assert answer == "Python это классный язык программирования"
        assert len(updated_history) == 3  # original 2 + 1 new
        mock_rag_service.get_relevant_context.assert_called_once_with(
            query=sample_dialog_data["current_message"],
            topic=sample_dialog_data["study_topic"]
        )
        dialog_agent._mock_llm_chain.ainvoke.assert_called_once()
        mock_parse_json.assert_called_once_with("{\"answer\": \"Python это классный язык программирования\"}")

    @pytest.mark.asyncio
    async def test_ainvoke_with_token_refresh(self, dialog_agent, mock_token_verification, sample_dialog_data, mock_giga_settings):
        mock_token_verification._is_token_expired.return_value = True

        mock_output = Mock()
        mock_output.__getitem__ = Mock(
            side_effect=lambda key: "{\"answer\": \"Test answer\"}" if key == "text" else None)
        mock_output.text = "{\"answer\": \"Test answer\"}"

        dialog_agent._mock_llm_chain.ainvoke = AsyncMock(return_value=mock_output)

        with patch('dialog_api.agents.dialog_agent.create_gigachat_client') as mock_create_client, \
                patch('dialog_api.agents.dialog_agent.parse_json') as mock_parse_json:
            mock_parse_json.return_value = {"answer": "Test answer"}
            mock_new_client = Mock()
            mock_create_client.return_value = mock_new_client

            answer, updated_history = await dialog_agent.ainvoke(**sample_dialog_data)

        mock_token_verification._ensure_valid_token.assert_called_once()
        mock_create_client.assert_called_once_with(
            access_token="new-token-123",
            settings=mock_giga_settings
        )
        assert dialog_agent._mock_llm_chain.llm == mock_new_client
        assert answer == "Test answer"


class TestDialogAgentInitialization:
    def test_dialog_agent_init(self, mock_giga_client, mock_token_verification, mock_rag_service, mock_llm_chain):
        with patch("dialog_api.agents.dialog_agent.LLMChain", return_value=mock_llm_chain):
            agent = DialogAgent(
                giga_client=mock_giga_client,
                token_verification=mock_token_verification,
                rag_service=mock_rag_service,
                message_history_number=10
            )

            assert agent._giga_client == mock_giga_client
            assert agent._token_verification == mock_token_verification
            assert agent._rag_service == mock_rag_service
            assert agent.message_history_number == 10

    def test_dialog_agent_prompt_templates(self, dialog_agent):
        assert dialog_agent.system_message is not None
        assert dialog_agent.human_message is not None
        assert dialog_agent.chat_template is not None
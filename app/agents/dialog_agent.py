import logging
from typing import Any

from langchain.chains.llm import LLMChain
from langchain_community.chat_models import GigaChat
from langchain_core.messages import AIMessage
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from prometheus_async.aio import time

from app.clients.giga import create_gigachat_client
from app.metrics import DIALOG_GIGA_AINVOKE
from app.prompts.dialog import system_prompt, user_prompt
from app.services.rag import RAGService
from app.settings import app_settings
from app.utils.parser import parse_json
from app.utils.token_verification import TokenVerification

logger = logging.getLogger(__name__)


class DialogAgentError(Exception): ...


class DialogAgent:
    system_message = SystemMessagePromptTemplate.from_template(system_prompt)
    human_message = HumanMessagePromptTemplate.from_template(user_prompt)
    chat_template = ChatPromptTemplate.from_messages(messages=[system_message, human_message])

    def __init__(
            self, giga_client: GigaChat, token_verification: TokenVerification,
            rag_service: RAGService, message_history_number: int
    ) -> None:
        self.__llm_chain = LLMChain(llm=giga_client, prompt=self.chat_template)
        self._token_verification = token_verification
        self._giga_client = giga_client
        self._rag_service = rag_service
        self.message_history_number = message_history_number


    @time(DIALOG_GIGA_AINVOKE)
    async def ainvoke(
            self, history: list[str], study_topic: str, current_message: str, user_level: str,
    ) -> tuple[str, list[str]]:
        try:
            if self._token_verification._is_token_expired():
                access_token = await self._token_verification._ensure_valid_token()
                self._giga_client = create_gigachat_client(
                    access_token=access_token,
                    settings=app_settings.giga,
                )
                self.__llm_chain.llm = self._giga_client

            current_history = [self.system_message, self.human_message] + history
            topic_context = self._rag_service.get_relevant_context(
                query=current_message,
                topic=study_topic,
            )

            output = await self.__llm_chain.ainvoke(
                input={
                    "history": current_history[:self.message_history_number],
                    "user_level": user_level,
                    "study_topic": study_topic,
                    "current_message": current_message,
                    "topic_context": topic_context,
                }
            )
            content: dict[Any, Any] = parse_json(output["text"])
            logger.debug(f"DialogAgent output: {content=}")
            history.append(AIMessage(content=str(content)).model_dump(mode="json"))
            return content["answer"], history
        except DialogAgentError as e:
            logging.exception(f"DialogAgent exception: {e}")
            return "Попробуйте задать вопрос позже. Ошибка на стороне сервера"
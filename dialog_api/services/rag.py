import logging

from dialog_api.services.document_loader import DocumentLoader

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, vector_db, documents_number: int, document_loader: DocumentLoader):
        self.vector_db = vector_db
        self.document_loader = document_loader
        self.n_results = documents_number

    def initialize_with_documents(self):
        try:
            documents = self.document_loader.load_documents()
            if documents:
                self.vector_db.add_documents(documents)
            else:
                logger.warning("Нет документов для загрузки")

        except Exception as e:
            logger.error(f"Ошибка инициализации RAG service: {e}")

    def get_relevant_context(self, query: str, topic: str) -> str:
        """
        Метод получения релевантного контекста из документов
        :param query: запрос пользователя
        :param topic: тема обучения
        :return: контекст
        """
        try:
            documents = self.vector_db.search(
                query=query,
                where_filter={"topic": topic},
                n_results=self.n_results,
            )

            if not documents:
                logger.warning(f"Не найдено документов для темы: {topic}, запроса: {query}")
                return ""

            context_parts = []
            for i, doc in enumerate(documents, 1):
                doc_level = doc.get("metadata", {}).get("level", "unknown")
                context_parts.append(f"{i}. [{doc_level}] {doc['content']}")

            return "\n".join(context_parts)

        except Exception as e:
            logger.error(f"Error getting relevant context: {e}")
            return ""

import logging
from typing import Any

from app.services.document_loader import DocumentLoader

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, vector_db, documents_number: int, document_loader: DocumentLoader, n_results: int = 5):
        self.vector_db = vector_db
        self.documents_number = documents_number
        self.document_loader = document_loader
        self.n_results = n_results

    def initialize_with_documents(self):
        try:
            documents = self.document_loader.load_documents()

            if documents:
                self.vector_db.add_documents(documents)
                logger.info(f"RAG service initialized with {len(documents)} documents")
            else:
                logger.warning("No documents found to initialize RAG service")

        except Exception as e:
            logger.error(f"Error initializing RAG service with documents: {e}")

    def get_relevant_context(self, query: str, topic: str) -> str:
        """Получает релевантный контекст из векторной БД"""
        try:
            documents = self.vector_db.search(
                query=query,
                topic=topic,
                n_results=self.n_results,
            )

            if not documents:
                return ""

            context_parts = []
            for i, doc in enumerate(documents, self.documents_number):
                doc_level = doc.get("metadata", {}).get("level", "unknown")
                context_parts.append(f"{i}. [{doc_level}] {doc['content']}")

            return "\n".join(context_parts)

        except Exception as e:
            logger.error(f"Error getting relevant context: {e}")
            return ""


    def get_stats(self) -> dict[str, Any]:
        """Возвращает статистику векторной БД"""
        try:
            return self.vector_db.get_collection_stats()
        except Exception as e:
            logger.error(f"Error getting RAG stats: {e}")
            return {"error": "Unable to get statistics"}

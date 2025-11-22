import logging
import uuid
from typing import Any

from app.schemas import UserLevel
from app.services.document_loader import DocumentLoader

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self, vector_db, documents_number: int, document_loader: DocumentLoader):
        self.vector_db = vector_db
        self.documents_number = documents_number
        self.document_loader = document_loader

    def initialize_with_documents(self):
        try:
            loader = self.document_loader
            documents = loader.load_documents()

            self.vector_db.add_documents(documents)
            logger.info(f"RAG service initialized with {len(documents)} documents")

        except Exception as e:
            logger.error(f"Error initializing RAG service with documents: {e}")

    def get_relevant_context(self, query: str, topic: str, user_level: str = "beginner") -> str:
        try:
            where_filter = {"topic": topic, "level": user_level} if user_level else {"topic": topic}

            documents = self.vector_db.search(query, topic, where_filter=where_filter, n_results=3)

            if not documents:
                return "Релевантная информация не найдена в базе знаний."

            context_parts = ["Релевантная информация из базы знаний:"]
            for i, doc in enumerate(documents, self.documents_number):
                doc_level = doc.get("metadata", {}).get("level", "unknown")
                context_parts.append(f"{i}. [{doc_level}] {doc['content']}")

            return "\n".join(context_parts)

        except Exception as e:
            logger.error(f"Error getting relevant context: {e}")
            return "Ошибка при поиске информации в базе знаний."

    def add_custom_document(self, content: str, topic: str, subtopic: str = "", level: str = UserLevel.beginner.value):
        """Добавляет пользовательский документ в векторную БД"""
        document = {
            "id": f"custom_{uuid.uuid4().hex[:8]}",
            "content": content,
            "metadata": {
                "topic": topic,
                "subtopic": subtopic,
                "level": level,
                "source": "custom"
            }
        }

        self.vector_db.add_documents([document])
        logger.info(f"Added custom document for topic: {topic}")

    def get_stats(self) -> dict[str, Any]:
        try:
            return self.vector_db.get_collection_stats()
        except Exception as e:
            logger.error(f"Error getting RAG stats: {e}")
            return {"error": "Unable to get statistics"}

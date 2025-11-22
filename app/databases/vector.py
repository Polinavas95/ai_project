import logging
from typing import Any
from chromadb.config import Settings
import chromadb
from sentence_transformers import SentenceTransformer

from app.settings import VectorDBSettings

logger = logging.getLogger(__name__)


class VectorDB:
    def __init__(self, vector_db_settings: VectorDBSettings):
        self.vector_db_settings = vector_db_settings
        self.client = chromadb.PersistentClient(
            path=vector_db_settings.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.embedding_model = SentenceTransformer(vector_db_settings.embedding_model)
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        try:
            return self.client.get_collection(self.vector_db_settings.collection_name)
        except Exception:
            return self.client.create_collection(
                name=self.vector_db_settings.collection_name,
                metadata={"description": "Learning materials for educational assistant"}
            )

    def add_documents(self, documents: list[dict[str, Any]]):
        try:
            ids = [doc["id"] for doc in documents]
            texts = [doc["content"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]

            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to vector DB")
        except Exception as e:
            logger.error(f"Error adding documents to vector DB: {e}")

    def search(self, query: str, topic: str, n_results: int = 5) -> list[dict[str, Any]]:
        try:
            where_filter = {"topic": topic}

            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                # where=where_filter,
            )
            logger.debug(f"Raw results: {results}")

            documents = []
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
                    score = 0
                    if results["distances"] and i < len(results["distances"][0]):
                        score = results["distances"][0][i]

                    documents.append({
                        "content": doc,
                        "metadata": metadata,
                        "score": score
                    })

            logger.debug(f"Found {len(documents)} relevant documents for query: {query}")
            return documents

        except Exception as e:
            logger.error(f"Error searching in vector DB: {e}")
            return []

    def get_collection_stats(self) -> dict[str, Any]:
        try:
            count = self.collection.count()
            return {"document_count": count}
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"document_count": 0}

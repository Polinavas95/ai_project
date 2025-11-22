import logging
from typing import Any
from chromadb.config import Settings
import chromadb
from sentence_transformers import SentenceTransformer
from app.settings import VectorDBSettings

logger = logging.getLogger(__name__)


class CustomEmbeddingFunction:
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name, device="cpu")
        logger.info(f"Загружена модель для эмбеддингов: {model_name}")

    def __call__(self, input: list[str]) -> list[list[float]]:
        try:
            embeddings = self.model.encode(input, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Ошибка генерации эмбеддингов: {e}")
            return [[0.0] * 384 for _ in input]


class VectorDB:
    def __init__(self, vector_db_settings: VectorDBSettings):
        self.vector_db_settings = vector_db_settings
        self.embedding_function = CustomEmbeddingFunction(vector_db_settings.embedding_model)
        self.client = chromadb.PersistentClient(
            path=vector_db_settings.persist_directory,
            settings=Settings(anonymized_telemetry=False),
        )

        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        try:
            collection = self.client.get_collection(
                name=self.vector_db_settings.collection_name,
            )
            logger.info(f"Коллекция найдена: {self.vector_db_settings.collection_name}")
            return collection
        except Exception as e:
            logger.warning(f"Коллекция не найдена, создаем новую: {e}")
            collection = self.client.create_collection(
                name=self.vector_db_settings.collection_name,
                embedding_function=self.embedding_function,  # Только для create
                metadata={"description": "Learning materials for educational assistant"}
            )
            logger.info(f"Создана новая коллекция: {self.vector_db_settings.collection_name}")
            return collection

    def add_documents(self, documents: list[dict[str, Any]]):
        try:
            logger.info(f"Добавляем {len(documents)} документов...")

            # Разбиваем на батчи чтобы избежать переполнения памяти
            batch_size = 100
            total_added = 0

            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]

                ids = [doc["id"] for doc in batch]
                texts = [doc["content"] for doc in batch]
                metadatas = [doc["metadata"] for doc in batch]

                logger.debug(f"Добавляем батч {i // batch_size + 1}: {len(batch)} документов")

                self.collection.add(
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                total_added += len(batch)

            logger.info(f"✅ Успешно добавлено {total_added} документов")

            # Проверяем добавление
            count = self.collection.count()
            logger.info(f"Теперь в коллекции: {count} документов")

        except Exception as e:
            logger.error(f"Ошибка добавления документов: {e}")
            raise

    def search(self, query: str, where_filter: dict[str, str], n_results: int = 5) -> list[dict[str, Any]]:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter,
            )

            documents = []
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                        results["documents"][0],
                        results["metadatas"][0],
                        results["distances"][0] if results["distances"] else [999] * len(results["documents"][0])
                )):
                    documents.append({
                        "content": doc,
                        "metadata": metadata,
                        "score": distance
                    })

            logger.debug(f"Найдено {len(documents)} релевантных документов для запроса: {query}")
            return documents

        except Exception as e:
            logger.error(f"Ошибка поиска в векторной БД: {e}")
            return []

    def get_collection_stats(self) -> dict[str, Any]:
        try:
            count = self.collection.count()
            return {"document_count": count}
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {"document_count": 0}

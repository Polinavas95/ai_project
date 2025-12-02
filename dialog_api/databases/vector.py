import logging
import os
from typing import Any
from chromadb.config import Settings
import chromadb
from sentence_transformers import SentenceTransformer
from dialog_api.settings import VectorDBSettings

logger = logging.getLogger(__name__)

os.environ["ORT_DISABLE_ML_OPS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["CHROMA_EMBEDDING_FUNCTION_PROVIDER"] = "sentence_transformers"
os.environ["CHROMA_ANONYMIZED_TELEMETRY"] = "FALSE"


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
        auth_token = vector_db_settings.auth_token

        self.client = chromadb.HttpClient(
            host=vector_db_settings.host,
            port=str(vector_db_settings.port),
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
            headers={"X_CHROMA_TOKEN": auth_token} if auth_token else {},
        )
        logger.info(f"Подключение к ChromaDB серверу: {vector_db_settings.host}:{vector_db_settings.port}")

        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        client_type = self.client.__class__.__name__

        try:
            if client_type == "HttpClient":
                return self.client.get_collection(
                    name=self.vector_db_settings.collection_name,
                    embedding_function=self.embedding_function,
                )
            return self.client.get_collection(name=self.vector_db_settings.collection_name)
        except Exception:
            return self.client.create_collection(
                name=self.vector_db_settings.collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Learning materials for educational assistant"}
            )

    def add_documents(self, documents: list[dict[str, Any]]) -> None:
        """
        Метод добавления документов в вевторную БД
        :param documents: cписок документов
        :return:
        """
        try:
            logger.info(f"Добавляем {len(documents)} документов...")
            batch_size = 50
            total_added = 0

            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]

                ids = [doc["id"] for doc in batch]
                texts = [doc["content"] for doc in batch]
                metadatas = [doc["metadata"] for doc in batch]

                self.collection.add(
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                total_added += len(batch)

            logger.info(f"Успешно добавлено {total_added} документов")

            # Проверяем добавление
            count = self.collection.count()
            logger.info(f"Теперь в коллекции: {count} документов")

        except Exception as e:
            logger.error(f"Ошибка добавления документов: {e}")
            raise

    def search(self, query: str, where_filter: dict[str, str], n_results: int = 5) -> list[dict[str, Any]]:
        """
        Метод семантического поиска учебных материалов по запросу пользователя
        :param query: запрос пользователя
        :param where_filter: фильтрация по метаданным
        :param n_results: количество документов
        :return: n_results наиболее релевантных документов
        """
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

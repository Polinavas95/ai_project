import os
import logging
from typing import Any

from dialog_api.schemas import StudyTopic, UserLevel

logger = logging.getLogger(__name__)


class DocumentLoader:
    def __init__(self, documents_path: str):
        self.documents_path = documents_path

    def load_documents(self) -> list[dict[str, Any]]:
        """Загрузка документов из папки"""
        documents = []

        if not os.path.exists(self.documents_path):
            logger.warning(f"Documents path {self.documents_path} does not exist")
            return documents

        python_docs = self._load_topic_documents(StudyTopic.python.value)
        documents.extend(python_docs)

        js_docs = self._load_topic_documents(StudyTopic.javascript.value)
        documents.extend(js_docs)

        logger.info(f"Loaded {len(documents)} documents")
        return documents

    def _load_topic_documents(self, topic: str) -> list[dict[str, Any]]:
        topic_path = os.path.join(self.documents_path, topic)
        documents = []

        if not os.path.exists(topic_path):
            logger.warning(f"Topic path {topic_path} does not exist")
            return documents

        for filename in os.listdir(topic_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(topic_path, filename)
                documents.extend(self._parse_text_file(file_path, topic, filename))

        return documents

    def _parse_text_file(self, file_path: str, topic: str, filename: str) -> list[dict[str, Any]]:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            sections = content.split("\n\n")
            documents = []

            for i, section in enumerate(sections):
                if section.strip():  # Пропуск пустых секциий
                    doc_id = f"{topic}_{filename[:-4]}_{i + 1}"

                    documents.append({
                        "id": doc_id,
                        "content": section.strip(),
                        "metadata": {
                            "topic": topic,
                            "subtopic": filename[:-4],
                            "level": self._detect_level(section),
                            "source": filename
                        }
                    })

            logger.debug(f"Loaded {len(documents)} sections from {filename}")
            return documents

        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return []

    def _detect_level(self, content: str) -> str:
        content_lower = content.lower()
        professional_keywords = ["decorator", "async", "await", "promise", "class", "inheritance", "prototype"]
        advanced_keywords = ["function", "object", "array", "method", "loop", "conditional"]

        if any(keyword in content_lower for keyword in professional_keywords):
            return UserLevel.professional.value
        elif any(keyword in content_lower for keyword in advanced_keywords):
            return UserLevel.advanced.value
        return UserLevel.beginner.value

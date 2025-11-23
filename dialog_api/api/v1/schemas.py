from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from dialog_api.schemas import QuizAction, StudyTopic


class ClientIDModel(BaseModel):
    client_id: str = Field(example="6f707083-7458-4193-9435-36b539115049")


class HistoryResponse(BaseModel):
    history: dict[str, Any]


class ChatRequest(ClientIDModel):
    message: str
    study_topic: StudyTopic


class ChatResponse(ClientIDModel):
    client_id: UUID
    giga_answer: str


class QuizRequest(ChatRequest):
    action: QuizAction


class QuizResponse(ClientIDModel):
    is_correct: bool | None = None
    score: int | None = None
    feedback: str | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    question: str | None = None
    question_type: str | None = None
    difficulty: str | None = None
    topic: str | None = None
    hint: str | None = None

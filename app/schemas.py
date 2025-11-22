from dataclasses import dataclass
from enum import Enum
from typing import Any

from pydantic import BaseModel


class Role(Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class StudyTopic(Enum):
    python = "python"
    javascript = "javascript"


class UserLevel(Enum):
    beginner = "beginner"
    advanced = "advanced"
    professional = "professional"


class QuizAction(Enum):
    generate_question = "generate_question"
    check_answer = "check_answer"


@dataclass(frozen=True, kw_only=True, slots=True)
class Message:
    role: Role
    content: str


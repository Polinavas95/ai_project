import logging

from fastapi import APIRouter, Request

from app.api.v1.schemas import ChatRequest, ChatResponse, QuizResponse, QuizRequest, ClientIDModel, HistoryResponse
from app.prompts.dialog import TOPIC_CONTEXT
from app.schemas import StudyTopic, UserLevel

app_router = APIRouter(prefix="/api/v1", tags=["v1"])
logger = logging.getLogger(__name__)


@app_router.post("/dialog", response_model=ChatResponse)
async def agent_dialog(request: Request, data: ChatRequest):
    cache = request.app.state.cache
    study_topic = data.study_topic.value
    client_id, message = data.client_id, data.message
    logger.debug(f"[{client_id}] Request with message {message}")
    dialog_agent = request.app.state.dialog_agent
    user_session = await cache.get(client_id=client_id, default={})
    history = user_session.get(study_topic, {}).get("history", [])
    user_level = user_session.get(study_topic, {}).get("user_level", UserLevel.beginner.value)
    topic_context = TOPIC_CONTEXT.get(study_topic, TOPIC_CONTEXT[StudyTopic.python])

    giga_chat_answer, history = await dialog_agent.ainvoke(
        history=history, study_topic=study_topic,
        current_message=message, user_level=user_level,
    )

    user_session.update(
        {
            study_topic: {
                "history": history,
                "user_level": user_level,
                "topic_context": topic_context,
            }
        }
    )
    await cache.put(client_id=client_id, value=user_session)

    return {"giga_answer": giga_chat_answer, "client_id": client_id}


@app_router.post("/quiz", response_model=QuizResponse, response_model_exclude_none=True)
async def agent_dialog(request: Request, data: QuizRequest):
    study_topic = data.study_topic
    cache = request.app.state.cache
    client_id, message = data.client_id, data.message
    logger.debug(f"[{client_id}] Request with message {message}")
    quiz_agent = request.app.state.quiz_agent
    user_session = await cache.get(client_id=client_id, default={})
    history = user_session.get(study_topic, {}).get("history", [])
    user_level = user_session.get(study_topic, {}).get("user_level", UserLevel.beginner.value)
    topic_context = TOPIC_CONTEXT.get(study_topic, TOPIC_CONTEXT[StudyTopic.python])
    giga_chat_answer, history = await quiz_agent.ainvoke(
        history=history, action=data.action, user_level=user_level, study_topic=study_topic,
    )

    user_session.update(
        {
            study_topic: {
                "history": history + [message],
                "user_level": user_level,
                "topic_context": topic_context,
            }
        }
    )
    await cache.put(client_id=client_id, value=user_session)

    return {**giga_chat_answer, "client_id": client_id}


@app_router.get("/history", response_model=HistoryResponse, response_model_exclude_none=True)
async def agent_dialog(request: Request, data: ClientIDModel):
    cache = request.app.state.cache
    history = await cache.get(client_id=data.client_id, default={})
    return {"history": history, "client_id": data.client_id}

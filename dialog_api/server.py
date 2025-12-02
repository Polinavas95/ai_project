import logging
import ssl

import aiohttp
from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics

from dialog_api.agents.dialog_agent import DialogAgent
from dialog_api.agents.quiz_agent import QuizAgent
from dialog_api.api.v1.handlers import app_router
from dialog_api.clients.giga import create_gigachat_client
from dialog_api.databases.vector import VectorDB
from dialog_api.services.document_loader import DocumentLoader
from dialog_api.services.ignite import caches_context
from dialog_api.services.rag import RAGService
from dialog_api.settings import app_settings
from dialog_api.utils.token_verification import TokenVerification

logger = logging.getLogger(__name__)


def make_httpsession(connection_pool_limit: int):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    return aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=connection_pool_limit, ssl=ssl_context))


async def lifespan(app: FastAPI):
    giga_session = make_httpsession(connection_pool_limit=app_settings.giga.limit)
    token_verification = TokenVerification(
        session=giga_session,
        access_key=app_settings.giga.access_key,
        scope=app_settings.giga.scope,
        access_token_url=app_settings.giga.access_token_url,
    )
    access_token = await token_verification.refresh_token()
    document_loader = DocumentLoader(documents_path=app_settings.vector_db.documents_path)
    rag_service = RAGService(
        vector_db=VectorDB(vector_db_settings=app_settings.vector_db),
        documents_number=app_settings.vector_db.documents_number,
        document_loader=document_loader,
    )
    rag_service.initialize_with_documents()
    giga_client = create_gigachat_client(settings=app_settings.giga, access_token=access_token)
    dialog_agent = DialogAgent(
        giga_client=giga_client,
        token_verification=token_verification,
        message_history_number=app_settings.giga.message_history_number,
        rag_service=rag_service,
    )
    quiz_agent = QuizAgent(giga_client=giga_client, token_verification=token_verification, rag_service=rag_service)
    cache_client, cache = await caches_context.configure(settings=app_settings.ignite)
    app.state.dialog_agent = dialog_agent
    app.state.quiz_agent = quiz_agent
    app.state.cache = cache
    logger.info(f"Запуск приложения с уровнем логирования: {app_settings.logger.level}")
    yield
    logger.info("Завершение сессий...")
    await giga_session.close()
    await cache_client.shutdown()
    logger.info("Завершение сессий выполнено")

app = FastAPI(lifespan=lifespan, docs_url="/")

app.include_router(router=app_router)
app.add_middleware(PrometheusMiddleware, app_name=app_settings.app_name, group_paths=True)
app.add_route("/prometheus", handle_metrics)

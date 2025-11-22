import logging
import ssl

import aiohttp
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette_exporter import PrometheusMiddleware, handle_metrics

from app.agents.dialog_agent import DialogAgent
from app.agents.quiz_agent import QuizAgent
from app.api.v1.handlers import app_router
from app.clients.giga import create_gigachat_client
from app.databases.vector import VectorDB
from app.services.document_loader import DocumentLoader
from app.services.ignite import AioIgniteClient
from app.services.rag import RAGService
from app.settings import app_settings
from app.utils.token_verification import TokenVerification

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
    rag_service = RAGService(
        vector_db=VectorDB(vector_db_settings=app_settings.vector_bd),
        documents_number=app_settings.vector_bd.documents_number,
        document_loader=DocumentLoader(documents_path=app_settings.vector_bd.documents_path)
    )
    rag_service.initialize_with_documents()
    giga_client = create_gigachat_client(settings=app_settings.giga, access_token=access_token)
    dialog_agent = DialogAgent(
        giga_client=giga_client,
        token_verification=token_verification,
        message_history_number=app_settings.giga.message_history_number,
        rag_service=rag_service,
    )
    quiz_agent = QuizAgent(giga_client=giga_client, token_verification=token_verification)
    cache = AioIgniteClient(settings=app_settings.ignite)
    await cache.connect(addresses=app_settings.ignite.addresses)
    app.state.dialog_agent = dialog_agent
    app.state.quiz_agent = quiz_agent
    app.state.cache = cache
    app.state.rag_service = rag_service
    logger.info(f"Запуск приложения с уровнем логирования: {app_settings.logger.level}")
    yield
    logger.info("Завершение сессий...")
    await giga_session.close()
    await cache.shutdown()
    logger.info("Завершение сессий выполнено")

app = FastAPI(lifespan=lifespan, docs_url="/")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router=app_router)
app.add_middleware(PrometheusMiddleware, app_name=app_settings.app_name, group_paths=True)
app.add_route("/prometheus", handle_metrics)

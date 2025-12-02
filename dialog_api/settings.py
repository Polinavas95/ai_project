from typing import Annotated

from dotenv import load_dotenv
from pydantic import Field, AfterValidator
from pydantic_settings import BaseSettings as PydanticBaseSettings

from dialog_api.utils.logger_config import logger_settings, setup_logging

load_dotenv()


class BaseSettings(PydanticBaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class GigaSettings(BaseSettings):
    url: Annotated[str, Field(alias="GIGA_URL")] = ""
    access_token_url: Annotated[str, Field(alias="GIGA_ACCESS_TOKEN_URL")] = ""
    model: Annotated[str, Field(alias="GIGA_MODEL")] = "GigaChat-2"
    limit: Annotated[int, Field(alias="GIGA_LIMIT")] = 30
    timeout: Annotated[float, Field(alias="GIGA_TIMEOUT")] = 30.0
    temperature: Annotated[float, Field(alias="GIGA_TEMPERATURE")] = 0.0000001
    max_tokens: Annotated[int, Field(alias="GIGA_MAX_TOKENS")] = 512
    scope: Annotated[str, Field(alias="GIGA_API_SCOPE")] = "GIGACHAT_API_PERS"
    profanity_check: Annotated[bool, Field(alias="GIGA_PROFANITY_CHECK")] = False
    access_key: Annotated[str, Field(alias="GIGA_ACCESS_KEY")] = ""
    verify_ssl_certs: Annotated[bool, Field(alias="GIGA_VERIFY_SSL_CERTS")] = False
    message_history_number: Annotated[int, Field(alias="GIGA_MESSAGE_HISTORY_NUMBER")] = 10


class Ignite(BaseSettings):
    cache_name: Annotated[str, Field(alias="IGNITE_CACHE_NAME")] = "history"
    addresses: Annotated[str, Field(alias="IGNITE_ADDRESSES")] = "0.0.0.0:10800"
    username: Annotated[str, Field(alias="IGNITE_USERNAME")] = ""
    password: Annotated[str, Field(alias="IGNITE_PASSWORD")] = ""
    max_time_duration: Annotated[int, Field(alias="IGNITE_MAX_TIME_DURATION")] = 1 * 60 * 60


class VectorDBSettings(BaseSettings):
    host: Annotated[str, Field(alias="CHROMA_SERVER_HOST")] = ""
    port: Annotated[int, Field(alias="CHROMA_SERVER_HTTP_PORT")] = 8000
    auth_credentials: Annotated[str, Field(alias="CHROMA_AUTH_CREDENTIALS")] = ""
    collection_name: Annotated[str, Field(alias="VECTOR_DB_COLLECTION_NAME")] = "learning_materials"
    embedding_model: Annotated[str, Field(alias="VECTOR_DB_EMBEDDING_MODEL")] = "all-MiniLM-L6-v2"
    documents_number: Annotated[int, Field(alias="VECTOR_DB_DOCUMENTS_NUMBER")] = 4
    documents_path: Annotated[str, Field(alias="VECTOR_DB_DOCUMENTS_PATH")] = ""
    auth_token: Annotated[str, Field(alias="VECTOR_DB_AUTH_TOKEN")] = ""

    @property
    def chroma_client_settings(self) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "headers": {
                "X_CHROMA_TOKEN": self.auth_token
            } if self.auth_token else {}
        }


class LoggingSettings(BaseSettings):
    level: Annotated[str, Field(alias="LOGGING_APP_LOGLEVEL"), AfterValidator(str.upper)] = "INFO"

    @property
    def dictconfig(self) -> dict:
        return logger_settings(self.level)


class Settings(BaseSettings):
    app_name: Annotated[str, Field(alias="APP_NAME")] = "gigachat-agent"
    host: Annotated[str, Field(alias="APP_HOST")] = "0.0.0.0"
    port: Annotated[int, Field(alias="APP_PORT")] = 8082
    giga: GigaSettings = GigaSettings()
    ignite: Ignite = Ignite()
    vector_db: VectorDBSettings = VectorDBSettings()
    logger: LoggingSettings = LoggingSettings()


app_settings = Settings()
setup_logging(app_settings.logger.level)

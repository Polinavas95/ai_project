import os

from app.settings import app_settings


os.environ["ORT_DISABLE_ML_OPS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["CHROMA_EMBEDDING_FUNCTION_PROVIDER"] = "sentence_transformers"


if __name__ == "__main__":
    from granian.constants import Interfaces
    from granian.server import Server

    Server(
        "app.server:app",
        interface=Interfaces.ASGI,
        workers=1,
        address=app_settings.host,
        port=app_settings.port,
        log_dictconfig=app_settings.logger.dictconfig,
    ).serve()

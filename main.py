from app.settings import app_settings


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

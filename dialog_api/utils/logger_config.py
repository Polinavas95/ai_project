import logging.config

def logger_settings(level: str) -> dict:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(funcName)s - %(message)s",
            },
            "error": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - [%(pathname)s:%(lineno)d] - %(funcName)s - %(message)s",
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "detailed",
                "filename": "dialog_api.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "error",
                "filename": "error.log",
                "maxBytes": 10485760,
                "backupCount": 5,
                "level": "ERROR",
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["default", "file", "error_file"],
                "level": level,
                "propagate": False,
            },
            "backend": {
                "handlers": ["default", "file", "error_file"],
                "level": level,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["default", "file", "error_file"],
                "level": level,
                "propagate": False,
            },
            "granian": {
                "handlers": ["default", "file", "error_file"],
                "level": level,
                "propagate": False,
            },
        },
    }

def setup_logging(level: str = "INFO"):
    """Настройка логирования"""
    config = logger_settings(level)
    logging.config.dictConfig(config)

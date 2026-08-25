import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "@timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "service": {"name": "movies-api"},
            "log": {"level": record.levelname, "logger": record.name},
            "message": record.getMessage(),
            "process": {"pid": record.process},
        }
        if record.exc_info:
            payload["error"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "stack_trace": self.formatException(record.exc_info),
            }
        if record.stack_info:
            payload["stack_trace"] = self.formatStack(record.stack_info)

        return json.dumps(payload, ensure_ascii=False)


LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DEFAULT_HANDLERS = [
    "console",
]

if settings.log_file_path:
    Path(settings.log_file_path).parent.mkdir(parents=True, exist_ok=True)
    LOG_DEFAULT_HANDLERS.append("json_file")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {"()": JsonFormatter},
        "verbose": {"format": LOG_FORMAT},
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        **(
            {
                "json_file": {
                    "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
                    "filename": settings.log_file_path,
                    "maxBytes": settings.log_max_bytes,
                    "backupCount": settings.log_backup_count,
                    "encoding": "utf-8",
                    "formatter": "json",
                }
            }
            if settings.log_file_path
            else {}
        ),
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": LOG_DEFAULT_HANDLERS,
            "level": "INFO",
        },
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": [
                "access",
                *(["json_file"] if settings.log_file_path else []),
            ],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "level": "INFO",
        "formatter": "verbose",
        "handlers": LOG_DEFAULT_HANDLERS,
    },
}

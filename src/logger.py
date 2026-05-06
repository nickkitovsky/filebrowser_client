import logging
import logging.config
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


@dataclass(slots=True)
class LoggerConfig:
    format: str = "[%(asctime)s.%(msecs)03d]  %(levelname)-7s - %(message)s"
    console_log_level: LogLevel = "DEBUG"
    file_log_level: LogLevel = "WARNING"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    logfile: Path | None = None

    def __post_init__(self):
        if self.logfile is None:
            self.logfile = Path.cwd() / "logs" / "app.log"
        self.logfile.parent.mkdir(parents=True, exist_ok=True)


def setup_logging(config: LoggerConfig | None = None) -> None:
    if config is None:
        config = LoggerConfig()

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": config.format,
                "datefmt": config.date_format,
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": config.console_log_level,
                "formatter": "default",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": config.file_log_level,
                "formatter": "default",
                "filename": str(config.logfile),
                "maxBytes": 1024 * 1024 * 5,
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": min(
                config.console_log_level,
                config.file_log_level,
            ),
        },
    }

    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


setup_logging()

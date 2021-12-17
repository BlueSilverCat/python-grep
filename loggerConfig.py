import logging
import logging.handlers
import logging.config

import loggerHelper
from virtualTerminalSequences import VirtualTerminalSequences as VTS

logFileName = "log.log"

config = {
    "version": 1,
    "formatters": {
        "normalColor": {
            "class":
                "logging.Formatter",
            "format":
                f"{VTS.FOREGROUND_COLORS['BLACK']}{VTS.BACKGROUND_COLORS['WHITE']}" + "{asctime}" + f"{VTS.RESET}" +
                " - {message}",
            "datefmt":
                "%H:%M:%S",
            "style":
                "{",
        },
        "normal": {
            "class": "logging.Formatter",
            "format": "{asctime} - {message}",
            "datefmt": "%H:%M:%S",
            "style": "{",
        },
        "detail": {
            "class": "logging.Formatter",
            "format": "{asctime}.{msecs:03.0f} - {name:<15} - {levelname:<8} - {message}",
            "datefmt": "%Y-%m-%d-%H:%M:%S",
            "style": "{",
        },
    },
    "filters": {
        "level": {
            "()": "loggerHelper.LevelFilter",  # ()は明示的にインスタンス化する。インスタンス変数で制御しているので必要
            "level": logging.INFO,  # int
        },
        "color": {
            "()": "loggerHelper.ColorFilter",
        },
    },
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
            "level": "DEBUG",  # logging.DEBUG も可能
        },
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "normalColor",
            "filters": ["level"],
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detail",
            "filename": logFileName,
            "maxBytes": 1024 * 1024,
            "backupCount": 2,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "console": {
            "handlers": ["console"],
            "level": logging.INFO,
            "filters": ["color"],
        },
        "__main__": {
            "handlers": ["console", "file"],
            "level": logging.DEBUG,
        },
        "file": {  # 
            "handlers": ["file"],
            "level": logging.DEBUG,
        },
    },
}

logging.config.dictConfig(config)

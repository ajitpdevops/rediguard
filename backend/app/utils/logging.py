"""Logging configuration for Rediguard backend"""

import logging
import logging.config
from typing import Dict, Any


def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration"""
    
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
            },
            "simple": {
                "format": "%(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "detailed",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.FileHandler",
                "level": log_level,
                "formatter": "detailed",
                "filename": "rediguard.log",
                "mode": "a"
            }
        },
        "loggers": {
            "app": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console"]
        }
    }
    
    logging.config.dictConfig(config)

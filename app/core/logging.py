# -*- coding: utf-8 -*-
import logging
import sys
from app.core.config import settings

def setup_logging():
    log_format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    # Silence overly verbose external loggers
    logging.getLogger("weasyprint").setLevel(logging.WARNING)
    logging.getLogger("fontTools").setLevel(logging.WARNING)
    logging.getLogger("pdfminer").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

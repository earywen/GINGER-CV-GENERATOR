# -*- coding: utf-8 -*-
"""
Graphic assets and SVG vectors for Ginger Burgeap 2026 PDF generation.
"""
import base64
from functools import lru_cache
from pathlib import Path

from app.core import settings, get_logger

logger = get_logger(__name__)

GINGER_CURVE_SVG = (
    '<svg viewBox="0 0 4507.26 4493.29" xmlns="http://www.w3.org/2000/svg" '
    'style="position: absolute; bottom: 0; right: 0; width: 33mm; height: 33mm; pointer-events: none;">'
    '<path d="M4436.17 4447.4 4436.17 70.71C2786.59 3317.65 59.48 4447.4 59.48 4447.4L4436.17 4447.4Z" fill="#FFFFFF"/>'
    '<path d="M4436.17 4447.4 1501.68 4447.4C1501.68 4447.4 3402.47 3376.93 4436.17 426.98L4436.17 4447.4Z" fill="#96C63E"/>'
    '</svg>'
)

@lru_cache(maxsize=1)
def get_logo_base64() -> str:
    """Loads and caches the official Ginger Burgeap base64 PNG logo."""
    logo_path = settings.LOGO_PATH
    if logo_path.exists():
        try:
            with open(logo_path, "rb") as lf:
                return base64.b64encode(lf.read()).decode("utf-8")
        except Exception as e:
            logger.warning(f"Could not load logo from {logo_path}: {e}")
    return ""

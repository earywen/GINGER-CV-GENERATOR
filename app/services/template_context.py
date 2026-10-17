# -*- coding: utf-8 -*-
"""
Jinja2 Template Context Builder (Backward Compatibility Façade).
Delegates to the consolidated deep Document Engine in app.services.pdf_engine.
"""
from app.services.pdf_engine import (
    build_template_context,
    get_footer_text,
    GINGER_CURVE_SVG,
    get_logo_base64
)

__all__ = [
    "build_template_context",
    "get_footer_text",
    "GINGER_CURVE_SVG",
    "get_logo_base64"
]

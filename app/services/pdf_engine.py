# -*- coding: utf-8 -*-
"""
WeasyPrint PDF and HTML Rendering Engine.
Handles template compilation, pagination constraint verification,
and predictive font scaling.
"""
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader
import weasyprint

from app.core import settings, get_logger
from app.services.template_context import build_template_context, get_footer_text
from app.services.pdf_assets import GINGER_CURVE_SVG

logger = get_logger(__name__)

# Compile template environment once
_jinja_env = Environment(
    loader=FileSystemLoader(str(settings.TEMPLATE_DIR)),
    autoescape=False
)
_cv_template = _jinja_env.get_template("cv_template.html")

def render_html_template(
    data: Dict[str, Any],
    lang: str = "fr",
    font_scale: Optional[float] = None,
    p1_count: Optional[int] = None
) -> str:
    """
    Renders the unified Jinja2 CV template into an HTML string for preview or PDF printing.
    """
    context = build_template_context(data, lang=lang, font_scale=font_scale, p1_count=p1_count)
    return _cv_template.render(**context)

def generate_pdf_bytes(data: Dict[str, Any], lang: str = "fr") -> bytes:
    """
    Generates PDF bytes using WeasyPrint with predictive font scale optimization.
    """
    is_fr = (lang.lower() == "fr")
    refs = data.get("refs_fr" if is_fr else "refs_en", [])
    total_refs = len(refs)

    target_p1 = total_refs if total_refs <= 10 else 10
    expected_pages = 1 if total_refs <= 10 else 2

    # Predictive candidate scale selection
    if target_p1 >= 10:
        candidate_scales = [0.95, 0.94, 0.93] if is_fr else [0.93, 0.94, 0.92]
    elif target_p1 == 9:
        candidate_scales = [0.97, 0.95]
    else:
        candidate_scales = [1.0, 0.97]

    for scale in candidate_scales:
        html = render_html_template(data, lang=lang, font_scale=scale, p1_count=target_p1)
        doc = weasyprint.HTML(string=html).render()
        if len(doc.pages) == expected_pages:
            return doc.write_pdf()

    # Fallback with p1=9 if 10 caused an unexpected spill
    if target_p1 > 9:
        for scale in [0.96, 0.94]:
            html = render_html_template(data, lang=lang, font_scale=scale, p1_count=9)
            doc = weasyprint.HTML(string=html).render()
            if len(doc.pages) == expected_pages:
                return doc.write_pdf()

    # Final guaranteed fallback
    html = render_html_template(data, lang=lang, font_scale=0.93, p1_count=min(total_refs, 9))
    return weasyprint.HTML(string=html).write_pdf()

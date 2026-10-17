# -*- coding: utf-8 -*-
"""
Deep Document Engine Module for Ginger Burgeap CV Generator.
Encapsulates SVG/PNG assets, template context preparation, typography scaling,
predictive A4 pagination constraints, and non-blocking WeasyPrint compilation.
"""
import io
import base64
import asyncio
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from jinja2 import Environment, FileSystemLoader
import weasyprint

from app.core import settings, get_logger
from app.utils.formatters import compute_initials, sanitize_filename

logger = get_logger(__name__)

# =============================================================================
# ASSETS & LOGOS
# =============================================================================

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

# =============================================================================
# TEMPLATE COMPILATION & CONTEXT
# =============================================================================

_jinja_env = Environment(
    loader=FileSystemLoader(str(settings.TEMPLATE_DIR)),
    autoescape=False
)
_cv_template = _jinja_env.get_template("cv_template.html")

def get_footer_text(agency_str: Optional[str], is_fr: bool) -> str:
    """Returns the standardized official regional directorate footer line."""
    u = (agency_str or "").upper()
    if is_fr:
        if "ILE-DE-FRANCE" in u and "NORD-OUEST" in u:
            return "Ginger Burgeap – Direction Régionale Nord-Ouest & Ile-de-France"
        elif "ILE-DE-FRANCE" in u:
            return "Ginger Burgeap – Direction Régionale Ile-de-France"
        elif "QSE" in u or "QUALIT" in u:
            return "Ginger Burgeap – Direction QSE & Métrologies"
        elif "MÉTIER" in u or "METIER" in u:
            return "Ginger Burgeap – Direction des Métiers"
        else:
            return "Ginger Burgeap – Direction Régionale Nord-Ouest"
    else:
        if "ILE-DE-FRANCE" in u and ("NORD-OUEST" in u or "NORTH-WEST" in u):
            return "Ginger Burgeap – North-West & Ile-de-France Regional Directorate"
        elif "ILE-DE-FRANCE" in u:
            return "Ginger Burgeap – Ile-de-France Regional Directorate"
        elif "QSE" in u or "QUALIT" in u:
            return "Ginger Burgeap – QSE & Metrology Directorate"
        elif "MÉTIER" in u or "METIER" in u or "TECHNICAL EXPERTISE" in u or "EXPERTISE DIRECTORATE" in u:
            return "Ginger Burgeap – Technical Expertise Directorate"
        else:
            return "Ginger Burgeap – North-West Regional Directorate"

def build_template_context(
    data: Dict[str, Any],
    lang: str = "fr",
    font_scale: Optional[float] = None,
    p1_count: Optional[int] = None
) -> Dict[str, Any]:
    """
    Builds the complete dictionary context for Jinja2 template rendering.
    Calculates pagination thresholds, font scales, and bilingual field defaults.
    """
    is_fr = (lang.lower() == "fr")
    name = data.get("name", "Prénom NOM")
    role = data.get("role_fr" if is_fr else "role_en", "Titre du Poste")
    exp = data.get("exp_fr" if is_fr else "exp_en", "Années d'expérience")
    agency = data.get("agency_fr" if is_fr else "agency_en", "GINGER BURGEAP")
    footer_text = get_footer_text(agency, is_fr)
    t_projets_missions = "PROJETS & MISSIONS" if is_fr else "PROJECTS & MISSIONS"

    refs = data.get("refs_fr" if is_fr else "refs_en", [])
    total_refs = len(refs)

    # Maximize Page 1 filling (holds up to 10 references before spilling to Page 2)
    if p1_count is None:
        p1_count = total_refs if total_refs <= 10 else 10

    if font_scale is None:
        if p1_count <= 8:
            font_scale = 1.0
        elif p1_count == 9:
            font_scale = 0.97
        else:
            font_scale = 0.95 if is_fr else 0.93

    photo_b64 = data.get("photo_b64")
    initials = data.get("initials")
    if not initials and not photo_b64:
        initials = compute_initials(name)

    t_diplomes = data.get("t_diplomes_fr", "DIPLÔMES") if is_fr else data.get("t_diplomes_en", "EDUCATION & DEGREES")
    diplomes = data.get("diplomes_fr" if is_fr else "diplomes_en", [])

    t_formations = data.get("t_formations_fr", "FORMATIONS & CERTIFICATIONS") if is_fr else data.get("t_formations_en", "PROFESSIONAL TRAINING & CERTIFICATIONS")
    formations = data.get("formations_fr" if is_fr else "formations_en", [])

    # Backward compatibility: if data only has old "formations" array containing degrees
    if not diplomes and formations:
        diplomes = formations
        formations = []

    t_competences = data.get("t_competences_fr", "COMPÉTENCES CLÉS") if is_fr else data.get("t_competences_en", "CORE COMPETENCIES")
    competences = data.get("competences_fr" if is_fr else "competences_en", [])

    t_exp_pro = "EXPÉRIENCES PROFESSIONNELLES" if is_fr else "PROFESSIONAL EXPERIENCE"
    exp_pros = data.get("exp_pros_fr" if is_fr else "exp_pros_en", [])

    t_lang = "LANGUES & MOBILITÉ" if is_fr else "LANGUAGES & MOBILITY"
    langs = data.get("langs_fr" if is_fr else "langs_en", [])

    t_profil = "PROFIL ET PARCOURS" if is_fr else "PROFILE & BACKGROUND"
    pitch = data.get("pitch_fr" if is_fr else "pitch_en", "")

    t_qualif = "PRINCIPALES QUALIFICATIONS" if is_fr else "CORE QUALIFICATIONS & EXPERTISE"
    qualifs = data.get("qualifs_fr" if is_fr else "qualifs_en", [])

    t_refs = "PRINCIPALES RÉFÉRENCES – MISSIONS RÉCENTES" if is_fr else "KEY PROJECT REFERENCES – RECENT MISSIONS"

    has_p2 = (total_refs > p1_count)
    refs_p1 = refs[:p1_count] if has_p2 else refs
    refs_p2 = refs[p1_count:p1_count + 8] if has_p2 else []

    raw_show_badges = data.get("show_badges")
    show_badges = (raw_show_badges not in (False, "false", "0", 0, "False"))

    return {
        "lang": lang,
        "name": name,
        "role": role,
        "exp": exp,
        "agency": agency,
        "footer_text": footer_text,
        "t_projets_missions": t_projets_missions,
        "photo_b64": photo_b64,
        "initials": initials,
        "logo_b64": get_logo_base64(),
        "ginger_curve_svg": GINGER_CURVE_SVG,
        "t_diplomes": t_diplomes,
        "diplomes": diplomes,
        "t_formations": t_formations,
        "formations": formations,
        "show_badges": show_badges,
        "t_competences": t_competences,
        "competences": competences,
        "t_exp_pro": t_exp_pro,
        "exp_pros": exp_pros,
        "t_lang": t_lang,
        "langs": langs,
        "t_profil": t_profil,
        "pitch": pitch,
        "t_qualif": t_qualif,
        "qualifs": qualifs,
        "t_refs": t_refs,
        "refs_p1": refs_p1,
        "refs_p2": refs_p2,
        "has_p2": has_p2,
        "p1_count": p1_count,
        "font_scale": font_scale,
        "page_1_pagination": "Page 1 / 2" if has_p2 else "",
        "t_refs_p2": "PRINCIPALES RÉFÉRENCES – SUITE DES MISSIONS" if is_fr else "KEY PROJECT REFERENCES – CONTINUED MISSIONS",
        "t_suite_sidebar": "RÉFÉRENCES & EXPERTISE" if is_fr else "REFERENCES & EXPERTISE",
        "desc_suite_sidebar": (
            "Suite des missions et projets d'ingénierie conseil réalisés pour les maîtres d'ouvrage publics et privés."
            if is_fr else
            "Continued project references and environmental engineering missions conducted for public and private stakeholders."
        ),
        "base_font": f"{7.9 * font_scale:.2f}",
        "side_font": f"{6.8 * font_scale:.2f}",
        "body_font": f"{7.1 * font_scale:.2f}",
        "line_height": f"{1.28 * font_scale:.2f}",
        "gap_size": str(int(6 * font_scale))
    }

# =============================================================================
# PUBLIC DEEP RENDERING INTERFACE
# =============================================================================

def render_html(
    data: Dict[str, Any],
    lang: str = "fr",
    font_scale: Optional[float] = None,
    p1_count: Optional[int] = None
) -> str:
    """
    Renders the unified Jinja2 CV template into an HTML string for vector preview or printing.
    """
    context = build_template_context(data, lang=lang, font_scale=font_scale, p1_count=p1_count)
    return _cv_template.render(**context)

def _generate_pdf_bytes_sync(data: Dict[str, Any], lang: str = "fr") -> bytes:
    """
    Synchronously compiles PDF bytes using WeasyPrint with predictive font scale optimization.
    Verifies that the document strictly conforms to 1 or 2 pages.
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
        html = render_html(data, lang=lang, font_scale=scale, p1_count=target_p1)
        doc = weasyprint.HTML(string=html).render()
        if len(doc.pages) == expected_pages:
            return doc.write_pdf()

    # Fallback with p1=9 if 10 caused an unexpected spill
    if target_p1 > 9:
        for scale in [0.96, 0.94]:
            html = render_html(data, lang=lang, font_scale=scale, p1_count=9)
            doc = weasyprint.HTML(string=html).render()
            if len(doc.pages) == expected_pages:
                return doc.write_pdf()

    # Final guaranteed fallback
    html = render_html(data, lang=lang, font_scale=0.93, p1_count=min(total_refs, 9))
    return weasyprint.HTML(string=html).write_pdf()

async def render_pdf(data: Dict[str, Any], lang: str = "fr") -> bytes:
    """
    Non-blocking async interface for WeasyPrint PDF compilation.
    Dispatches CPU-heavy rendering to an internal threadpool.
    """
    return await asyncio.to_thread(_generate_pdf_bytes_sync, data, lang)

async def render_bilingual_bundle(data: Dict[str, Any]) -> Tuple[bytes, str]:
    """
    Generates twin French and English official PDFs in parallel and packages them
    into a standardized ZIP archive.
    Returns (zip_bytes, zip_filename).
    """
    name = data.get("name", "Collaborateur")
    pdf_fr, pdf_en = await asyncio.gather(
        render_pdf(data, "fr"),
        render_pdf(data, "en")
    )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        fn_fr = sanitize_filename(name, lang="FR", ext="pdf")
        fn_en = sanitize_filename(name, lang="EN", ext="pdf")
        zf.writestr(fn_fr, pdf_fr)
        zf.writestr(fn_en, pdf_en)

    zip_buffer.seek(0)
    zip_filename = sanitize_filename(name, lang="BURGEAP_2026", ext="zip")
    return zip_buffer.getvalue(), zip_filename

# Backward compatibility aliases
generate_pdf_bytes = _generate_pdf_bytes_sync
render_html_template = render_html

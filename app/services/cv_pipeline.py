# -*- coding: utf-8 -*-
"""
Unified CV Pipeline Services.
Centralizes photo framing, initials fallback, and cached AI parsing logic
to avoid duplicated paths between synchronous endpoints and background workers.
"""
import copy
from typing import Dict, Any, Optional

from app.core import get_logger
from app.services.image_processor import crop_studio_bust
from app.services.cache_manager import cache_manager
from app.services.ai_parser import parse_cv_with_agy
from app.utils.formatters import compute_initials

logger = get_logger(__name__)

def attach_photo_or_initials(
    cv_data: Dict[str, Any],
    photo_bytes: Optional[bytes] = None,
    photo_b64: Optional[str] = None
) -> Dict[str, Any]:
    """
    Attaches either a cropped studio bust photo or generates corporate initials.
    Guarantees deterministic behavior for both sync routes and async job pipelines.
    """
    if photo_b64 and len(photo_b64.strip()) > 50:
        cv_data["photo_b64"] = photo_b64.strip()
    elif photo_bytes and len(photo_bytes) > 0:
        cv_data["photo_b64"] = crop_studio_bust(photo_bytes)
    else:
        cv_data["photo_b64"] = None
        if not cv_data.get("initials"):
            cv_data["initials"] = compute_initials(cv_data.get("name", ""))
    return cv_data

async def parse_and_cache_cv(
    raw_text: str,
    agency: str,
    cache_mgr=cache_manager
) -> Dict[str, Any]:
    """
    Retrieves parsed CV from content-addressed cache if available,
    otherwise runs AI parser via agy CLI and persists into cache.
    """
    if not raw_text or len(raw_text.strip()) < 20:
        raise ValueError("Impossible d'extraire le texte du CV. Vérifiez le format du fichier.")

    cache_key = cache_mgr.compute_cache_key(raw_text, agency=agency)
    cached_data = cache_mgr.get_cached_parse(cache_key)

    if cached_data:
        logger.info(f"Cache HIT for parse key {cache_key[:12]}...")
        return copy.deepcopy(cached_data)

    structured_data = await parse_cv_with_agy(raw_text, default_agency=agency)
    cache_mgr.save_cached_parse(cache_key, structured_data)
    return structured_data

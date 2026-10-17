# -*- coding: utf-8 -*-
"""
Deep CV Ingestion Pipeline Module.
Encapsulates text extraction, content-addressed disk caching, LLM orchestration,
self-healing translations, and studio bust photo normalization behind a unified interface.
"""
import copy
import time
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable

from app.core import get_logger
from app.services.extractor import extract_text
from app.services.cache_manager import cache_manager
from app.services.ai_parser import parse_cv_with_agy
from app.services.image_processor import crop_studio_bust
from app.utils.formatters import compute_initials

logger = get_logger(__name__)

ProgressCallback = Callable[[int, str, str], Awaitable[None]]

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

async def ingest_cv(
    cv_filename: str,
    cv_bytes: bytes,
    photo_bytes: Optional[bytes] = None,
    photo_b64: Optional[str] = None,
    agency: str = "RÉGION NORD-OUEST",
    on_progress: Optional[ProgressCallback] = None,
    cache_mgr=cache_manager
) -> Dict[str, Any]:
    """
    Deep CV Ingestion Interface.
    Orchestrates the entire CV transformation flow:
    1. Extracts text from raw bytes (PDF, DOCX, PPTX).
    2. Checks the content-addressed cache (skipping LLM if already processed).
    3. Executes AI parsing & bilingual mirror generation (with optional live progress updates).
    4. Caches structured result.
    5. Formats studio bust photo or generates corporate monogram initials.
    """
    if on_progress:
        await on_progress(20, "Extraction du texte du document...", "Lecture des pages et des tableaux du CV source.")

    raw_text = extract_text(cv_filename, cv_bytes)
    if not raw_text or len(raw_text.strip()) < 20:
        raise ValueError("Impossible d'extraire le texte du CV. Vérifiez le format du fichier.")

    # Check persistent content-addressed cache
    cache_key = cache_mgr.compute_cache_key(raw_text, agency=agency)
    cached_data = cache_mgr.get_cached_parse(cache_key)

    if cached_data:
        logger.info(f"Cache HIT for parse key {cache_key[:12]}... (saved agy LLM execution)")
        if on_progress:
            await on_progress(85, "Document reconnu en cache !", "Restitution instantanée sans ré-exécution de l'IA.")
            await asyncio.sleep(0.3)
        structured_data = copy.deepcopy(cached_data)
    else:
        if on_progress:
            await on_progress(40, "Extraction et Structuration IA...", "Identification des missions, compétences et habilitations officielles.")

        if on_progress:
            parse_task = asyncio.create_task(
                parse_cv_with_agy(raw_text, default_agency=agency)
            )
            start_time = time.time()
            while not parse_task.done():
                await asyncio.sleep(0.5)
                elapsed = time.time() - start_time
                current_progress = min(95, int(20 + (elapsed / 45.0) * 75))

                if elapsed < 6:
                    step = "Extraction et Structuration IA..."
                    desc = "Identification des missions, compétences et habilitations officielles."
                elif elapsed < 12:
                    step = "Traduction technique bilingue..."
                    desc = "Génération du profil miroir officiel en anglais."
                else:
                    step = "Formatage des projets de référence..."
                    desc = "Harmonisation des intitulés et mots-clés selon la charte 2026."

                await on_progress(current_progress, step, desc)

            structured_data = await parse_task
        else:
            structured_data = await parse_cv_with_agy(raw_text, default_agency=agency)

        # Persist into disk cache
        cache_mgr.save_cached_parse(cache_key, structured_data)

    if on_progress:
        await on_progress(95, "Traitement de la photo...", "Formatage du studio buste officiel ou calcul des initiales.")

    # Associate photo or corporate initials
    attach_photo_or_initials(structured_data, photo_bytes=photo_bytes, photo_b64=photo_b64)

    if on_progress:
        await on_progress(100, "Terminé avec succès !", f"Profil officiel généré pour {structured_data.get('name', '')}.")

    return structured_data

async def parse_and_cache_cv(
    raw_text: str,
    agency: str,
    cache_mgr=cache_manager
) -> Dict[str, Any]:
    """
    Backward-compatible helper. Delegates to cache and AI parser.
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

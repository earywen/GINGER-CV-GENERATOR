# -*- coding: utf-8 -*-
import uuid
import time
import asyncio
import copy
from typing import Dict, Any, Optional

from app.core import settings, get_logger
from app.services.extractor import extract_text
from app.services.ai_parser import parse_cv_with_agy
from app.services.image_processor import crop_studio_bust
from app.services.cache_manager import cache_manager
from app.utils.formatters import compute_initials

logger = get_logger(__name__)

class JobManager:
    """
    Thread-safe in-memory asynchronous job manager for parsing and background tasks.
    Manages job states, TTL eviction and memory limits.
    """
    def __init__(self, expiration_seconds: int = 1800, max_stored: int = 200):
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._expiration_seconds = expiration_seconds
        self._max_stored = max_stored

    async def create_job(self) -> str:
        job_id = str(uuid.uuid4())
        async with self._lock:
            # Automatic eviction of expired jobs
            now = time.time()
            expired = [
                jid for jid, j in self._jobs.items()
                if now - j.get("created_at", now) > self._expiration_seconds
            ]
            for jid in expired:
                self._jobs.pop(jid, None)

            # Evict oldest if exceeding capacity
            if len(self._jobs) >= self._max_stored:
                oldest = sorted(self._jobs.items(), key=lambda x: x[1].get("created_at", 0))[:20]
                for jid, _ in oldest:
                    self._jobs.pop(jid, None)

            self._jobs[job_id] = {
                "status": "processing",
                "progress": 10,
                "step": "Fichier reçu, démarrage du traitement...",
                "desc": "Initialisation du moteur de conversion.",
                "data": None,
                "error": None,
                "created_at": now
            }
        return job_id

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        async with self._lock:
            job = self._jobs.get(job_id)
            return dict(job) if job else None

    async def update_job(self, job_id: str, **kwargs):
        async with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].update(kwargs)

    async def run_parse_job(
        self,
        job_id: str,
        cv_filename: str,
        cv_bytes: bytes,
        photo_bytes: bytes,
        photo_b64: Optional[str],
        agency: str
    ):
        try:
            await self.update_job(
                job_id,
                step="Extraction du texte du document...",
                desc="Lecture des pages et des tableaux du CV source.",
                progress=20
            )

            raw_text = extract_text(cv_filename, cv_bytes)
            if not raw_text or len(raw_text.strip()) < 20:
                await self.update_job(
                    job_id,
                    status="failed",
                    error="Impossible d'extraire le texte du CV. Vérifiez le format du fichier."
                )
                return

            # Check persistent content-addressed cache
            cache_key = cache_manager.compute_cache_key(raw_text, agency=agency)
            cached_data = cache_manager.get_cached_parse(cache_key)

            if cached_data:
                logger.info(f"Using cached parse result for job {job_id}")
                await self.update_job(
                    job_id,
                    step="Document reconnu en cache !",
                    desc="Restitution instantanée sans ré-exécution de l'IA.",
                    progress=85
                )
                await asyncio.sleep(0.3)
                structured_data = copy.deepcopy(cached_data)
            else:
                await self.update_job(
                    job_id,
                    step="Extraction et Structuration IA...",
                    desc="Identification des missions, compétences et habilitations officielles.",
                    progress=40
                )

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

                    await self.update_job(
                        job_id,
                        progress=current_progress,
                        step=step,
                        desc=desc
                    )

                structured_data = await parse_task
                # Save structured data in cache for future calls
                cache_manager.save_cached_parse(cache_key, structured_data)

            await self.update_job(
                job_id,
                step="Traitement de la photo...",
                progress=95
            )

            # Process photo or generate official initials
            if photo_b64 and len(photo_b64.strip()) > 50:
                structured_data["photo_b64"] = photo_b64.strip()
            elif photo_bytes and len(photo_bytes) > 0:
                structured_data["photo_b64"] = crop_studio_bust(photo_bytes)
            else:
                structured_data["photo_b64"] = None
                if not structured_data.get("initials"):
                    structured_data["initials"] = compute_initials(structured_data.get("name", ""))

            await self.update_job(
                job_id,
                status="completed",
                progress=100,
                step="Terminé avec succès !",
                data=structured_data
            )
            logger.info(f"Parse job {job_id} successfully completed for {structured_data.get('name')}")

        except Exception as e:
            logger.error(f"Error in parse job {job_id}: {e}", exc_info=True)
            await self.update_job(
                job_id,
                status="failed",
                error=str(e)
            )

job_manager = JobManager(
    expiration_seconds=settings.JOB_EXPIRATION_SECONDS,
    max_stored=settings.JOB_MAX_STORED
)

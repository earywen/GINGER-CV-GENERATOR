# -*- coding: utf-8 -*-
import uuid
import time
import asyncio
from typing import Dict, Any, Optional

from app.core import settings, get_logger
from app.services.cv_pipeline import ingest_cv

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
        """
        Executes background CV processing by delegating directly to the deep ingest_cv pipeline.
        Progress updates are seamlessly forwarded to the job state.
        """
        try:
            async def progress_callback(progress: int, step: str, desc: str):
                await self.update_job(
                    job_id,
                    progress=progress,
                    step=step,
                    desc=desc
                )

            structured_data = await ingest_cv(
                cv_filename=cv_filename,
                cv_bytes=cv_bytes,
                photo_bytes=photo_bytes,
                photo_b64=photo_b64,
                agency=agency,
                on_progress=progress_callback
            )

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

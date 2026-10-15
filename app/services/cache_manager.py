# -*- coding: utf-8 -*-
"""
Content-Addressed Parse Cache Manager.
Maintains disk-backed cache for AI parsing using SHA-256 fingerprinting.
"""
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any

from app.core import settings, get_logger
from app.services.disk_store import DiskTTLStore

logger = get_logger(__name__)

class ParseCacheManager:
    """
    Disk-backed persistent content-addressed cache for CV AI parses.
    Prevents redundant calls to the agy LLM when the same CV text
    is re-submitted or when a page reload occurs.
    """
    def __init__(self, cache_dir: Optional[Path] = None, expiration_days: int = 30):
        self.cache_dir = Path(cache_dir or (settings.CACHE_DIR / "parses"))
        self.expiration_seconds = expiration_days * 86400
        self._store = DiskTTLStore(self.cache_dir, self.expiration_seconds)

    def compute_cache_key(self, raw_text: str, agency: str = "") -> str:
        """
        Computes a deterministic SHA-256 fingerprint based on normalized raw text and target agency.
        """
        normalized_text = " ".join((raw_text or "").split()).strip()
        normalized_agency = " ".join((agency or "").split()).strip().upper()
        payload = f"{normalized_agency}:::{normalized_text}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get_cached_parse(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves cached structured CV data if valid and non-expired.
        """
        data = self._store.get(cache_key)
        if data:
            logger.info(f"Cache HIT for key {cache_key[:12]}... (saved agy LLM execution)")
        return data

    def save_cached_parse(self, cache_key: str, data: Dict[str, Any]) -> None:
        """
        Stores structured CV data in disk cache, stripping heavy photo_b64.
        """
        if not data:
            return

        clean_data = dict(data)
        clean_data.pop("photo_b64", None)
        self._store.set(cache_key, clean_data)
        logger.info(f"Saved parse result in cache for key {cache_key[:12]}...")

    def clear_all(self) -> int:
        """Clears all cached parses."""
        return self._store.clear_all()

cache_manager = ParseCacheManager(
    cache_dir=settings.CACHE_DIR / "parses",
    expiration_days=settings.CACHE_EXPIRATION_DAYS
)

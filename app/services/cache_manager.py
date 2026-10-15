# -*- coding: utf-8 -*-
import hashlib
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

from app.core import settings, get_logger

logger = get_logger(__name__)

class ParseCacheManager:
    """
    Disk-backed persistent content-addressed cache for CV AI parses.
    Prevents redundant calls to the agy LLM when the same CV text
    is re-submitted or when a page reload occurs.
    """
    def __init__(self, cache_dir: Optional[Path] = None, expiration_days: int = 30):
        self.cache_dir = cache_dir or (settings.CACHE_DIR / "parses")
        self.expiration_seconds = expiration_days * 86400
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create cache directory {self.cache_dir}: {e}")

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
        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None

        try:
            mtime = cache_file.stat().st_mtime
            if (time.time() - mtime) > self.expiration_seconds:
                cache_file.unlink(missing_ok=True)
                return None

            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"Cache HIT for key {cache_key[:12]}... (saved agy LLM execution)")
                return data
        except Exception as e:
            logger.warning(f"Error reading parse cache for {cache_key}: {e}")
            return None

    def save_cached_parse(self, cache_key: str, data: Dict[str, Any]) -> None:
        """
        Stores structured CV data in disk cache.
        """
        if not data:
            return

        self._ensure_cache_dir()
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            # Strip photo_b64 from the parse cache so cached files stay lightweight (~10 KB)
            clean_data = dict(data)
            clean_data.pop("photo_b64", None)
            
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(clean_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved parse result in cache for key {cache_key[:12]}...")
        except Exception as e:
            logger.warning(f"Error writing parse cache for {cache_key}: {e}")

    def clear_all(self) -> int:
        """Clears all cached parses."""
        count = 0
        try:
            for f in self.cache_dir.glob("*.json"):
                f.unlink(missing_ok=True)
                count += 1
        except Exception as e:
            logger.warning(f"Error clearing cache: {e}")
        return count

cache_manager = ParseCacheManager(
    cache_dir=settings.CACHE_DIR / "parses",
    expiration_days=settings.CACHE_EXPIRATION_DAYS
)

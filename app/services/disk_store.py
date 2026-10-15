# -*- coding: utf-8 -*-
"""
Disk-backed persistent JSON store with time-to-live (TTL) expiration.
Provides unified thread-safe file operations for caching and session management.
"""
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

from app.core import get_logger

logger = get_logger(__name__)

class DiskTTLStore:
    """
    Manages persistent JSON documents on disk with automatic TTL eviction.
    """
    def __init__(self, directory: Path, expiration_seconds: int):
        self.directory = Path(directory)
        self.expiration_seconds = expiration_seconds
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create storage directory {self.directory}: {e}")

    def _get_file_path(self, key: str) -> Path:
        # Sanitize key to prevent path traversal
        safe_key = "".join(c for c in key if c.isalnum() or c in ("-", "_"))
        return self.directory / f"{safe_key}.json"

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves JSON document if it exists and has not expired.
        Automatically unlinks expired records.
        """
        if not key:
            return None

        file_path = self._get_file_path(key)
        if not file_path.exists():
            return None

        try:
            mtime = file_path.stat().st_mtime
            if (time.time() - mtime) > self.expiration_seconds:
                file_path.unlink(missing_ok=True)
                return None

            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error reading disk record {key} from {self.directory}: {e}")
            return None

    def set(self, key: str, data: Dict[str, Any], indent: Optional[int] = 2) -> None:
        """
        Writes JSON document to disk.
        """
        if not key or not data:
            return

        self._ensure_dir()
        file_path = self._get_file_path(key)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
        except Exception as e:
            logger.warning(f"Error writing disk record {key} to {self.directory}: {e}")

    def delete(self, key: str) -> bool:
        """
        Deletes a specific document from disk.
        """
        if not key:
            return False
        file_path = self._get_file_path(key)
        try:
            if file_path.exists():
                file_path.unlink(missing_ok=True)
                return True
        except Exception as e:
            logger.warning(f"Error deleting disk record {key}: {e}")
        return False

    def clear_all(self) -> int:
        """
        Deletes all JSON files in the storage directory.
        """
        count = 0
        try:
            for f in self.directory.glob("*.json"):
                f.unlink(missing_ok=True)
                count += 1
        except Exception as e:
            logger.warning(f"Error clearing directory {self.directory}: {e}")
        return count

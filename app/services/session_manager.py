# -*- coding: utf-8 -*-
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

from app.core import settings, get_logger

logger = get_logger(__name__)

class SessionManager:
    """
    Manages server-side persistent draft sessions.
    Allows clients to recover drafts even if local storage is cleared
    or across page refreshes.
    """
    def __init__(self, sessions_dir: Optional[Path] = None, expiration_days: int = 14):
        self.sessions_dir = sessions_dir or (settings.DATA_DIR / "sessions")
        self.expiration_seconds = expiration_days * 86400
        self._ensure_dir()

    def _ensure_dir(self):
        try:
            self.sessions_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create sessions directory {self.sessions_dir}: {e}")

    def get_session_draft(self, session_id: str) -> Optional[Dict[str, Any]]:
        if not session_id:
            return None
        session_file = self.sessions_dir / f"{session_id}.json"
        if not session_file.exists():
            return None
        try:
            if (time.time() - session_file.stat().st_mtime) > self.expiration_seconds:
                session_file.unlink(missing_ok=True)
                return None
            with open(session_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
                return payload.get("draft")
        except Exception as e:
            logger.warning(f"Error reading session draft {session_id}: {e}")
            return None

    def save_session_draft(self, session_id: str, draft: Dict[str, Any]) -> None:
        if not session_id or not draft:
            return
        self._ensure_dir()
        session_file = self.sessions_dir / f"{session_id}.json"
        try:
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump({
                    "session_id": session_id,
                    "updated_at": time.time(),
                    "draft": draft
                }, f, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Error saving session draft {session_id}: {e}")

    def clear_session_draft(self, session_id: str) -> None:
        if not session_id:
            return
        session_file = self.sessions_dir / f"{session_id}.json"
        session_file.unlink(missing_ok=True)

session_manager = SessionManager(
    sessions_dir=settings.DATA_DIR / "sessions",
    expiration_days=14
)

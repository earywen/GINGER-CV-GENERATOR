# -*- coding: utf-8 -*-
"""
Server-Side Session Draft Manager.
Allows users to recover ongoing CV drafts across page refreshes or device changes.
"""
import time
from pathlib import Path
from typing import Optional, Dict, Any

from app.core import settings, get_logger
from app.services.disk_store import DiskTTLStore

logger = get_logger(__name__)

class SessionManager:
    """
    Manages server-side persistent draft sessions with TTL.
    """
    def __init__(self, sessions_dir: Optional[Path] = None, expiration_days: int = 14):
        self.sessions_dir = Path(sessions_dir or (settings.DATA_DIR / "sessions"))
        self.expiration_seconds = expiration_days * 86400
        self._store = DiskTTLStore(self.sessions_dir, self.expiration_seconds)

    def get_session_draft(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves user's ongoing draft from disk.
        """
        payload = self._store.get(session_id)
        if payload and isinstance(payload, dict):
            return payload.get("draft")
        return None

    def save_session_draft(self, session_id: str, draft: Dict[str, Any]) -> None:
        """
        Saves user's draft along with session metadata.
        """
        if not session_id or not draft:
            return

        payload = {
            "session_id": session_id,
            "updated_at": time.time(),
            "draft": draft
        }
        self._store.set(session_id, payload)

    def clear_session_draft(self, session_id: str) -> None:
        """
        Deletes draft for given session.
        """
        self._store.delete(session_id)

session_manager = SessionManager(
    sessions_dir=settings.DATA_DIR / "sessions",
    expiration_days=14
)

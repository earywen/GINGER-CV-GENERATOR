# -*- coding: utf-8 -*-
"""
Feedback Dispatcher Service.
Persists collaborator feedback to disk and synchronizes with GitHub Issues.
"""
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
import httpx

from app.core import settings, get_logger
from app.models.feedback import FeedbackPayload, FeedbackResponse

logger = get_logger(__name__)

class FeedbackDispatcher:
    """
    Handles local persistence and optional GitHub issue dispatch for user feedback.
    """
    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = Path(storage_dir or settings.FEEDBACKS_DIR)
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Could not create feedback directory {self.storage_dir}: {e}")

    async def dispatch(self, payload: FeedbackPayload) -> FeedbackResponse:
        """
        Processes feedback: saves to disk and dispatches to GitHub Issues if configured.
        """
        now = datetime.now(timezone.utc)
        record_id = f"{int(now.timestamp())}_{uuid.uuid4().hex[:8]}"
        iso_date = now.isoformat()

        record_data = {
            "id": record_id,
            "created_at": iso_date,
            "category": payload.category,
            "message": payload.message,
            "contact": payload.contact,
            "include_diagnostics": payload.include_diagnostics,
            "diagnostics": payload.diagnostics if payload.include_diagnostics else None,
            "has_screenshot": bool(payload.screenshot_b64),
            "github_issue_url": None
        }

        # Save screenshot separately if provided (to keep JSON lightweight)
        if payload.screenshot_b64:
            try:
                screenshot_path = self.storage_dir / f"{record_id}_screenshot.jpg"
                b64_content = payload.screenshot_b64
                if "," in b64_content:
                    b64_content = b64_content.split(",", 1)[1]
                import base64
                screenshot_path.write_bytes(base64.b64decode(b64_content))
                record_data["screenshot_file"] = screenshot_path.name
            except Exception as e:
                logger.warning(f"Could not save screenshot for feedback {record_id}: {e}")

        # 1. Primary write: durable local persistence
        self._save_record(record_id, record_data)

        # 2. Secondary write: GitHub Issues synchronization
        github_url = await self._sync_to_github(payload, record_id, iso_date)
        if github_url:
            record_data["github_issue_url"] = github_url
            self._save_record(record_id, record_data)

        return FeedbackResponse(
            status="success",
            id=record_id,
            github_issue_url=github_url,
            message="Merci pour votre retour ! Votre message a bien été transmis à l'équipe."
        )

    def _save_record(self, record_id: str, data: Dict[str, Any]) -> None:
        self._ensure_dir()
        file_path = self.storage_dir / f"{record_id}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Feedback {record_id} saved locally to {file_path}")
        except Exception as e:
            logger.error(f"Error persisting feedback {record_id}: {e}")

    async def _sync_to_github(
        self,
        payload: FeedbackPayload,
        record_id: str,
        iso_date: str
    ) -> Optional[str]:
        token = settings.GITHUB_FEEDBACK_TOKEN
        repo = settings.GITHUB_FEEDBACK_REPO

        if not token or not repo:
            logger.debug("GitHub feedback token not set; skipping remote issue creation.")
            return None

        cat_labels = {
            "bug": "bug",
            "idea": "enhancement",
            "other": "needs-triage"
        }
        labels = [cat_labels.get(payload.category, "needs-triage"), "needs-triage"]

        title_prefix = {
            "bug": "[BUG]",
            "idea": "[SUGGESTION]",
            "other": "[FEEDBACK]"
        }.get(payload.category, "[FEEDBACK]")

        # Extract first line for title
        summary = payload.message.strip().split("\n")[0][:80]
        title = f"{title_prefix} {summary}"

        body_parts = [
            f"### 💬 Retour Utilisateur ({payload.category.upper()})",
            f"- **Auteur / Contact :** {payload.contact or 'Non renseigné'}",
            f"- **Horodatage :** `{iso_date}`",
            f"- **ID Local :** `{record_id}`",
            "",
            "#### Description",
            payload.message.strip(),
        ]

        if payload.include_diagnostics and payload.diagnostics:
            body_parts.extend([
                "",
                "#### 🖥 Diagnostic Snapshot",
                "```json",
                json.dumps(payload.diagnostics, ensure_ascii=False, indent=2),
                "```"
            ])

        if payload.screenshot_b64:
            body_parts.extend([
                "",
                "_ℹ️ Une capture d'écran est jointe et stockée sur le serveur applicatif._"
            ])

        body = "\n".join(body_parts)

        url = f"https://api.github.com/repos/{repo}/issues"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Burgeap-CV-Generator"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    url,
                    headers=headers,
                    json={
                        "title": title,
                        "body": body,
                        "labels": list(set(labels))
                    }
                )
                if res.status_code in (200, 201):
                    data = res.json()
                    issue_url = data.get("html_url")
                    logger.info(f"GitHub issue created successfully: {issue_url}")
                    return issue_url
                else:
                    logger.warning(f"GitHub API returned {res.status_code}: {res.text}")
        except Exception as e:
            logger.warning(f"Could not dispatch feedback to GitHub: {e}")

        return None

feedback_dispatcher = FeedbackDispatcher()

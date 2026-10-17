# -*- coding: utf-8 -*-
"""
Tests for Feedback model, dispatcher service, and API router.
"""
import json
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, AsyncMock
import pytest
from starlette.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.models.feedback import FeedbackPayload, FeedbackResponse
from app.services.feedback_service import FeedbackDispatcher

@pytest.fixture
def temp_feedback_dir():
    temp_dir = tempfile.mkdtemp(prefix="test_feedbacks_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_feedback_payload_validation():
    # Valid payload
    payload = FeedbackPayload(
        category="bug",
        message="Bouton d'export PDF inactif sur Firefox",
        contact="test@ginger-burgeap.com",
        include_diagnostics=True,
        diagnostics={"browser": "Firefox 125"}
    )
    assert payload.category == "bug"
    assert payload.message == "Bouton d'export PDF inactif sur Firefox"

    # Validation: message too short (< 3 chars)
    with pytest.raises(ValidationError):
        FeedbackPayload(category="bug", message="ab")

    # Validation: invalid category
    with pytest.raises(ValidationError):
        FeedbackPayload(category="invalid_category", message="Un message valide")

@pytest.mark.asyncio
async def test_feedback_dispatcher_persistence(temp_feedback_dir):
    dispatcher = FeedbackDispatcher(storage_dir=temp_feedback_dir)
    
    # 1x1 transparent png in base64
    tiny_b64_png = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    
    payload = FeedbackPayload(
        category="idea",
        message="Ajouter un bouton d'export Word en plus du PDF",
        contact="Jean Dupont",
        include_diagnostics=True,
        diagnostics={"screen": "1920x1080"},
        screenshot_b64=tiny_b64_png
    )

    with patch.object(dispatcher, "_sync_to_github", new_callable=AsyncMock) as mock_gh:
        mock_gh.return_value = "https://github.com/earywen/GINGER-CV-GENERATOR/issues/999"
        res = await dispatcher.dispatch(payload)

    assert isinstance(res, FeedbackResponse)
    assert res.status == "success"
    assert res.id is not None
    assert res.github_issue_url == "https://github.com/earywen/GINGER-CV-GENERATOR/issues/999"

    # Verify JSON file created
    json_path = temp_feedback_dir / f"{res.id}.json"
    assert json_path.exists()
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert data["id"] == res.id
    assert data["category"] == "idea"
    assert data["message"] == "Ajouter un bouton d'export Word en plus du PDF"
    assert data["contact"] == "Jean Dupont"
    assert data["github_issue_url"] == "https://github.com/earywen/GINGER-CV-GENERATOR/issues/999"
    assert data["has_screenshot"] is True

    # Verify screenshot file created
    screenshot_path = temp_feedback_dir / f"{res.id}_screenshot.jpg"
    assert screenshot_path.exists()
    assert screenshot_path.stat().st_size > 0

def test_feedback_api_endpoint(temp_feedback_dir):
    client = TestClient(app)

    with patch("app.routers.feedback.feedback_dispatcher.storage_dir", temp_feedback_dir), \
         patch("app.routers.feedback.feedback_dispatcher._sync_to_github", new_callable=AsyncMock) as mock_gh:
        mock_gh.return_value = None

        response = client.post("/api/feedback", json={
            "category": "bug",
            "message": "Le formulaire ne se valide pas lors de l'ajout d'une mission.",
            "contact": "collab@burgeap.fr",
            "include_diagnostics": True,
            "diagnostics": {"stage": "editor"}
        })

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "id" in data
        assert "Merci pour votre retour" in data["message"]

def test_feedback_api_invalid_payload():
    client = TestClient(app)
    response = client.post("/api/feedback", json={
        "category": "unknown",
        "message": "x"
    })
    assert response.status_code == 422

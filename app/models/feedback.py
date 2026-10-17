# -*- coding: utf-8 -*-
"""
Pydantic Models for User Feedback & Issue Reporting.
"""
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

FeedbackCategory = Literal["bug", "idea", "other"]

class FeedbackPayload(BaseModel):
    category: FeedbackCategory = Field(
        default="bug",
        description="Type de feedback : bug (anomalie), idea (suggestion) ou other (remarque)"
    )
    message: str = Field(
        ...,
        min_length=3,
        max_length=5000,
        description="Description détaillée du retour utilisateur"
    )
    contact: Optional[str] = Field(
        default=None,
        max_length=150,
        description="Nom ou adresse email facultatif du collaborateur"
    )
    include_diagnostics: bool = Field(
        default=True,
        description="Indique si les métadonnées techniques doivent être jointes"
    )
    diagnostics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Snapshot technique client (navigateur, OS, vue active)"
    )
    screenshot_b64: Optional[str] = Field(
        default=None,
        description="Image ou capture d'écran encodée en base64"
    )

class FeedbackResponse(BaseModel):
    status: str = "success"
    id: str
    github_issue_url: Optional[str] = None
    message: str

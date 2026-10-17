# -*- coding: utf-8 -*-
"""
Feedback API Endpoints.
"""
from fastapi import APIRouter, HTTPException
from app.core import get_logger
from app.models.feedback import FeedbackPayload, FeedbackResponse
from app.services.feedback_service import feedback_dispatcher

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Feedback"])

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback_endpoint(payload: FeedbackPayload):
    """
    Submits user feedback (bug, idea, comment), persists locally on server,
    and optionally synchronizes with GitHub Issues.
    """
    try:
        response = await feedback_dispatcher.dispatch(payload)
        return response
    except Exception as e:
        logger.error(f"Failed to process feedback: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Une erreur est survenue lors de l'enregistrement de votre retour."
        )

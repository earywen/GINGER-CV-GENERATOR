# -*- coding: utf-8 -*-
import asyncio
import copy
import uuid
from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request, Response, Body

from app.core import get_logger
from app.models.cv import (
    ParseJobResponse,
    JobStatusResponse,
    CropPhotoResponse,
)
from app.services.job_manager import job_manager
from app.services.extractor import extract_text
from app.services.ai_parser import parse_cv_with_agy
from app.services.image_processor import crop_studio_bust
from app.services.cache_manager import cache_manager
from app.services.session_manager import session_manager
from app.utils.formatters import compute_initials

from app.services.cv_pipeline import attach_photo_or_initials, parse_and_cache_cv

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["CV Analysis & Sessions"])

SESSION_COOKIE_NAME = "burgeap_session_id"

def get_or_set_session_id(request: Request, response: Response) -> str:
    """Retrieves existing session ID or sets a new durable cookie."""
    sid = request.cookies.get(SESSION_COOKIE_NAME)
    if not sid:
        sid = str(uuid.uuid4())
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=sid,
            max_age=30 * 86400,
            httponly=True,
            samesite="lax"
        )
    return sid

@router.post("/parse-cv-job", response_model=ParseJobResponse)
async def parse_cv_job_endpoint(
    cv_file: UploadFile = File(...),
    photo_file: Optional[UploadFile] = File(None),
    photo_b64: Optional[str] = Form(None),
    agency: str = Form("RÉGION NORD-OUEST")
):
    try:
        cv_bytes = await cv_file.read()
        p_bytes = await photo_file.read() if photo_file else b""
        
        job_id = await job_manager.create_job()
        
        asyncio.create_task(
            job_manager.run_parse_job(
                job_id=job_id,
                cv_filename=cv_file.filename or "cv.pdf",
                cv_bytes=cv_bytes,
                photo_bytes=p_bytes,
                photo_b64=photo_b64,
                agency=agency
            )
        )
        return {"status": "queued", "job_id": job_id}
    except Exception as e:
        logger.error(f"Failed to queue parse job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/parse-cv-status/{job_id}", response_model=JobStatusResponse)
async def parse_cv_status_endpoint(job_id: str):
    job = await job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Tâche introuvable ou expirée.")
    return job

@router.post("/parse-cv")
async def parse_cv_sync_endpoint(
    cv_file: UploadFile = File(...),
    photo_file: Optional[UploadFile] = File(None),
    photo_b64: Optional[str] = Form(None),
    agency: str = Form("RÉGION NORD-OUEST")
):
    """Direct synchronous parse endpoint with disk-cache acceleration."""
    try:
        cv_bytes = await cv_file.read()
        raw_text = extract_text(cv_file.filename or "cv.pdf", cv_bytes)
        structured_data = await parse_and_cache_cv(raw_text, agency=agency)
        
        p_bytes = await photo_file.read() if photo_file else None
        attach_photo_or_initials(structured_data, photo_bytes=p_bytes, photo_b64=photo_b64)
                
        return {"status": "success", "data": structured_data}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API parse error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crop-photo", response_model=CropPhotoResponse)
async def crop_photo_endpoint(photo_file: UploadFile = File(...)):
    try:
        p_bytes = await photo_file.read()
        b64 = crop_studio_bust(p_bytes)
        return {"status": "success", "photo_b64": b64}
    except Exception as e:
        logger.error(f"Error cropping photo: {e}")
        raise HTTPException(status_code=400, detail=f"Erreur lors du traitement de l'image: {e}")

# =============================================================================
# SESSION & DRAFT MANAGEMENT (Prevents losing work on accidental reload)
# =============================================================================

@router.get("/session/draft")
async def get_session_draft_endpoint(request: Request, response: Response):
    """Retrieves server-side saved draft associated with user's session cookie."""
    sid = get_or_set_session_id(request, response)
    draft = session_manager.get_session_draft(sid)
    return {
        "session_id": sid,
        "has_draft": draft is not None,
        "draft": draft
    }

@router.post("/session/draft")
async def save_session_draft_endpoint(
    request: Request,
    response: Response,
    payload: Dict[str, Any] = Body(...)
):
    """Saves user's ongoing CV draft on server."""
    sid = get_or_set_session_id(request, response)
    draft = payload.get("draft")
    if not draft or not isinstance(draft, dict):
        raise HTTPException(status_code=400, detail="Données de brouillon invalides.")
    session_manager.save_session_draft(sid, draft)
    return {"status": "saved", "session_id": sid}

@router.delete("/session/draft")
async def clear_session_draft_endpoint(request: Request, response: Response):
    """Clears user's active session draft."""
    sid = get_or_set_session_id(request, response)
    session_manager.clear_session_draft(sid)
    return {"status": "cleared", "session_id": sid}

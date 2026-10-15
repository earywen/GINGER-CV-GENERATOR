# -*- coding: utf-8 -*-
import asyncio
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

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
from app.utils.formatters import compute_initials

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["CV Analysis"])

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
    """Direct synchronous parse endpoint preserved for backwards compatibility."""
    try:
        cv_bytes = await cv_file.read()
        raw_text = extract_text(cv_file.filename or "cv.pdf", cv_bytes)
        
        if not raw_text or len(raw_text.strip()) < 20:
            raise HTTPException(
                status_code=400,
                detail="Impossible d'extraire le texte du CV. Vérifiez le format du fichier."
            )
            
        structured_data = await parse_cv_with_agy(raw_text, default_agency=agency)
        
        if photo_b64 and len(photo_b64.strip()) > 50:
            structured_data["photo_b64"] = photo_b64.strip()
        elif photo_file and photo_file.filename:
            p_bytes = await photo_file.read()
            if len(p_bytes) > 0:
                structured_data["photo_b64"] = crop_studio_bust(p_bytes)
        else:
            structured_data["photo_b64"] = None
            if not structured_data.get("initials"):
                structured_data["initials"] = compute_initials(structured_data.get("name", ""))
                
        return {"status": "success", "data": structured_data}
        
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

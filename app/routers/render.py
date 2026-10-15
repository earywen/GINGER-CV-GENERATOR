# -*- coding: utf-8 -*-
import io
import zipfile
import urllib.parse
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import HTMLResponse, StreamingResponse

from app.core import get_logger
from app.models.cv import RenderPayload
from app.services.pdf_engine import generate_pdf_bytes, render_html_template
from app.utils.formatters import sanitize_filename

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["CV Rendering & Export"])

@router.post("/render-html", response_class=HTMLResponse)
async def render_html_endpoint(payload: RenderPayload):
    try:
        html = render_html_template(payload.data, lang=payload.lang)
        return HTMLResponse(content=html)
    except Exception as e:
        logger.error(f"Error rendering HTML: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur rendu HTML: {e}")

@router.post("/render-preview")
async def render_preview_endpoint(payload: RenderPayload):
    try:
        pdf_bytes = generate_pdf_bytes(payload.data, lang=payload.lang)
        return Response(content=pdf_bytes, media_type="application/pdf")
    except Exception as e:
        logger.error(f"Error generating preview PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur génération PDF: {e}")

@router.post("/export-pdf")
async def export_pdf_endpoint(payload: RenderPayload):
    try:
        name = payload.data.get("name", "Collaborateur")
        filename = sanitize_filename(name, lang=payload.lang, ext="pdf")
        
        pdf_bytes = generate_pdf_bytes(payload.data, lang=payload.lang)
        
        encoded_filename = urllib.parse.quote(filename)
        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
        return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur export PDF: {e}")

@router.post("/export-zip")
async def export_zip_endpoint(payload: RenderPayload):
    try:
        name = payload.data.get("name", "Collaborateur")
        
        pdf_fr = generate_pdf_bytes(payload.data, lang="fr")
        pdf_en = generate_pdf_bytes(payload.data, lang="en")
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            fn_fr = sanitize_filename(name, lang="FR", ext="pdf")
            fn_en = sanitize_filename(name, lang="EN", ext="pdf")
            zf.writestr(fn_fr, pdf_fr)
            zf.writestr(fn_en, pdf_en)
            
        zip_buffer.seek(0)
        zip_filename = sanitize_filename(name, lang="BURGEAP_2026", ext="zip")
        encoded_zip = urllib.parse.quote(zip_filename)
        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_zip}"
        }
        return StreamingResponse(zip_buffer, media_type="application/zip", headers=headers)
    except Exception as e:
        logger.error(f"Error exporting ZIP: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur export ZIP: {e}")

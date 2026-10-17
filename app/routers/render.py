# -*- coding: utf-8 -*-
"""
CV Rendering & Export Endpoints.
Thin HTTP transport layer delegating to the deep Document Engine.
"""
import io
import urllib.parse
from typing import Dict
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import HTMLResponse, StreamingResponse

from app.core import get_logger
from app.models.cv import RenderPayload
from app.services.pdf_engine import render_html, render_pdf, render_bilingual_bundle
from app.utils.formatters import sanitize_filename

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["CV Rendering & Export"])

def make_attachment_headers(filename: str) -> Dict[str, str]:
    """Formats RFC 5987 compatible Content-Disposition attachment header."""
    encoded_filename = urllib.parse.quote(filename)
    return {
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
    }

@router.post("/render-html", response_class=HTMLResponse)
async def render_html_endpoint(payload: RenderPayload):
    try:
        html = render_html(payload.data, lang=payload.lang)
        return HTMLResponse(content=html)
    except Exception as e:
        logger.error(f"Error rendering HTML: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur rendu HTML: {e}")

@router.post("/render-preview")
async def render_preview_endpoint(payload: RenderPayload):
    try:
        pdf_bytes = await render_pdf(payload.data, payload.lang)
        return Response(content=pdf_bytes, media_type="application/pdf")
    except Exception as e:
        logger.error(f"Error generating preview PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur génération PDF: {e}")

@router.post("/export-pdf")
async def export_pdf_endpoint(payload: RenderPayload):
    try:
        name = payload.data.get("name", "Collaborateur")
        filename = sanitize_filename(name, lang=payload.lang, ext="pdf")
        pdf_bytes = await render_pdf(payload.data, payload.lang)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers=make_attachment_headers(filename)
        )
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur export PDF: {e}")

@router.post("/export-zip")
async def export_zip_endpoint(payload: RenderPayload):
    try:
        zip_bytes, zip_filename = await render_bilingual_bundle(payload.data)
        return StreamingResponse(
            io.BytesIO(zip_bytes),
            media_type="application/zip",
            headers=make_attachment_headers(zip_filename)
        )
    except Exception as e:
        logger.error(f"Error exporting ZIP: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur export ZIP: {e}")

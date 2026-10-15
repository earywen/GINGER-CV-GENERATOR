# -*- coding: utf-8 -*-
import io
import zipfile
import urllib.parse
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from app.services.extractor import extract_text
from app.services.ai_parser import parse_cv_with_agy
from app.services.image_processor import crop_studio_bust, compute_initials
from app.services.pdf_engine import generate_pdf_bytes, render_html_template

app = FastAPI(title="Ginger Burgeap CV Generator 2026", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("app/static/index.html", "r", encoding="utf-8") as f:
        return f.read()

import uuid
import time
import asyncio

parse_jobs = {}

async def _run_parse_cv_job(job_id: str, cv_filename: str, cv_bytes: bytes, photo_filename: str, p_bytes: bytes, photo_b64: str, agency: str):
    try:
        parse_jobs[job_id]["step"] = "Extraction du texte du document..."
        parse_jobs[job_id]["desc"] = "Lecture des pages et des tableaux du CV source."
        parse_jobs[job_id]["progress"] = 20

        raw_text = extract_text(cv_filename, cv_bytes)
        if not raw_text or len(raw_text.strip()) < 20:
            parse_jobs[job_id]["status"] = "failed"
            parse_jobs[job_id]["error"] = "Impossible d'extraire le texte du CV. Vérifiez le format du fichier."
            return

        parse_jobs[job_id]["step"] = "Extraction et Structuration IA..."
        parse_jobs[job_id]["desc"] = "Identification des missions, compétences et habilitations officielles."
        parse_jobs[job_id]["progress"] = 40

        parse_task = asyncio.create_task(parse_cv_with_agy(raw_text, default_agency=agency))
        
        start_time = time.time()
        while not parse_task.done():
            await asyncio.sleep(0.5)
            elapsed = time.time() - start_time
            current_progress = min(95, int(20 + (elapsed / 45.0) * 75))
            parse_jobs[job_id]["progress"] = current_progress
            if elapsed < 6:
                parse_jobs[job_id]["step"] = "Extraction et Structuration IA..."
                parse_jobs[job_id]["desc"] = "Identification des missions, compétences et habilitations officielles."
            elif elapsed < 12:
                parse_jobs[job_id]["step"] = "Traduction technique bilingue..."
                parse_jobs[job_id]["desc"] = "Génération du profil miroir officiel en anglais."
            else:
                parse_jobs[job_id]["step"] = "Formatage des projets de référence..."
                parse_jobs[job_id]["desc"] = "Harmonisation des intitulés et mots-clés selon la charte 2026."

        structured_data = await parse_task

        parse_jobs[job_id]["step"] = "Traitement de la photo..."
        parse_jobs[job_id]["progress"] = 95

        if photo_b64 and len(photo_b64.strip()) > 50:
            structured_data["photo_b64"] = photo_b64.strip()
        elif p_bytes and len(p_bytes) > 0:
            structured_data["photo_b64"] = crop_studio_bust(p_bytes)
        else:
            structured_data["photo_b64"] = None
            if not structured_data.get("initials"):
                structured_data["initials"] = compute_initials(structured_data.get("name", ""))

        parse_jobs[job_id]["status"] = "completed"
        parse_jobs[job_id]["progress"] = 100
        parse_jobs[job_id]["step"] = "Terminé avec succès !"
        parse_jobs[job_id]["data"] = structured_data

    except Exception as e:
        print(f"[API Parse Job Error] {e}")
        parse_jobs[job_id]["status"] = "failed"
        parse_jobs[job_id]["error"] = str(e)

@app.post("/api/parse-cv-job")
async def parse_cv_job_endpoint(
    cv_file: UploadFile = File(...),
    photo_file: UploadFile = File(None),
    photo_b64: str = Form(None),
    agency: str = Form("RÉGION NORD-OUEST")
):
    try:
        cv_bytes = await cv_file.read()
        p_bytes = await photo_file.read() if photo_file else b""
        photo_filename = photo_file.filename if photo_file else ""
        
        job_id = str(uuid.uuid4())
        parse_jobs[job_id] = {
            "status": "processing",
            "progress": 10,
            "step": "Fichier reçu, démarrage du traitement...",
            "desc": "Initialisation du moteur de conversion.",
            "data": None,
            "error": None,
            "created_at": time.time()
        }
        
        now = time.time()
        expired = [jid for jid, j in parse_jobs.items() if now - j.get("created_at", now) > 1800]
        for jid in expired:
            parse_jobs.pop(jid, None)

        asyncio.create_task(
            _run_parse_cv_job(job_id, cv_file.filename, cv_bytes, photo_filename, p_bytes, photo_b64, agency)
        )
        return {"status": "queued", "job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/parse-cv-status/{job_id}")
async def parse_cv_status_endpoint(job_id: str):
    job = parse_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Tâche introuvable ou expirée.")
    return job

@app.post("/api/parse-cv")
async def parse_cv_endpoint(
    cv_file: UploadFile = File(...),
    photo_file: UploadFile = File(None),
    photo_b64: str = Form(None),
    agency: str = Form("RÉGION NORD-OUEST")
):
    try:
        cv_bytes = await cv_file.read()
        raw_text = extract_text(cv_file.filename, cv_bytes)
        
        if not raw_text or len(raw_text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Impossible d'extraire le texte du CV. Vérifiez le format du fichier.")
            
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
        
    except Exception as e:
        print(f"[API Parse Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/crop-photo")
async def crop_photo_endpoint(photo_file: UploadFile = File(...)):
    try:
        p_bytes = await photo_file.read()
        b64 = crop_studio_bust(p_bytes)
        return {"status": "success", "photo_b64": b64}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors du traitement de l'image: {e}")

@app.post("/api/render-html")
async def render_html_endpoint(payload: dict = Body(...)):
    data = payload.get("data", {})
    lang = payload.get("lang", "fr")
    try:
        html = render_html_template(data, lang=lang)
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur rendu HTML: {e}")

@app.post("/api/render-preview")
async def render_preview_endpoint(payload: dict = Body(...)):
    data = payload.get("data", {})
    lang = payload.get("lang", "fr")
    try:
        pdf_bytes = generate_pdf_bytes(data, lang=lang)
        return Response(content=pdf_bytes, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération PDF: {e}")

@app.post("/api/export-pdf")
async def export_pdf_endpoint(payload: dict = Body(...)):
    data = payload.get("data", {})
    lang = payload.get("lang", "fr")
    
    name = data.get("name", "Collaborateur").replace(" ", "_")
    filename = f"CV_{name}_{lang.upper()}.pdf"
    
    pdf_bytes = generate_pdf_bytes(data, lang=lang)
    
    encoded_filename = urllib.parse.quote(filename)
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)

@app.post("/api/export-zip")
async def export_zip_endpoint(payload: dict = Body(...)):
    data = payload.get("data", {})
    name = data.get("name", "Collaborateur").replace(" ", "_")
    
    pdf_fr = generate_pdf_bytes(data, lang="fr")
    pdf_en = generate_pdf_bytes(data, lang="en")
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"CV_{name}_FR.pdf", pdf_fr)
        zf.writestr(f"CV_{name}_EN.pdf", pdf_en)
        
    zip_buffer.seek(0)
    zip_filename = f"CV_{name}_BURGEAP_2026.zip"
    encoded_zip = urllib.parse.quote(zip_filename)
    headers = {
        "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_zip}"
    }
    return StreamingResponse(zip_buffer, media_type="application/zip", headers=headers)

# -*- coding: utf-8 -*-
import io
import os
import pypdf
import pdfplumber
import docx
import pptx

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    
    # Tentative 1 : pdfplumber
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text_parts.append(extracted)
    except Exception as e:
        print(f"[Extractor] pdfplumber error: {e}")
        
    joined = "\n".join(text_parts).strip()
    if text_parts and len(joined) > 50:
        return "\n\n".join(text_parts)
        
    # Tentative 2 : pypdf
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    except Exception as e:
        print(f"[Extractor] pypdf error: {e}")
        
    return "\n\n".join(text_parts)

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                paragraphs.append(row_text)
    return "\n\n".join(paragraphs)

def extract_text_from_pptx(file_bytes: bytes) -> str:
    prs = pptx.Presentation(io.BytesIO(file_bytes))
    text_runs = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    t = "".join(run.text for run in paragraph.runs).strip()
                    if t:
                        text_runs.append(t)
            elif shape.has_table:
                for row in shape.table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        text_runs.append(row_text)
    return "\n\n".join(text_runs)

def extract_text(filename: str, file_bytes: bytes) -> str:
    ext = os.path.splitext(filename.lower())[1]
    if ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_bytes)
    elif ext in [".pptx", ".ppt"]:
        return extract_text_from_pptx(file_bytes)
    elif ext in [".txt", ".md"]:
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        return file_bytes.decode("utf-8", errors="ignore")

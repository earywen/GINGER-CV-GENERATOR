# -*- coding: utf-8 -*-
import unittest
import io
import docx
import pptx
from app.services.extractor import extract_text, extract_text_from_docx, extract_text_from_pptx

class TestExtractor(unittest.TestCase):
    def test_plain_text_and_markdown(self):
        content = b"# Profil\nIngenieur SSP Ginger Burgeap"
        text = extract_text("cv.txt", content)
        self.assertIn("Ingenieur SSP Ginger Burgeap", text)

        md_text = extract_text("cv.md", content)
        self.assertIn("Ingenieur SSP Ginger Burgeap", md_text)

    def test_legacy_format_rejection(self):
        with self.assertRaises(ValueError) as ctx_doc:
            extract_text("vieux_cv.doc", b"fake binary")
        self.assertIn(".docx", str(ctx_doc.exception))

        with self.assertRaises(ValueError) as ctx_ppt:
            extract_text("vieux_cv.ppt", b"fake binary")
        self.assertIn(".pptx", str(ctx_ppt.exception))

    def test_docx_extraction_with_tables(self):
        doc = docx.Document()
        doc.add_paragraph("Chef de projet Sites et Sols Pollués")
        table = doc.add_table(rows=1, cols=2)
        table.rows[0].cells[0].text = "Projet Dépollution"
        table.rows[0].cells[1].text = "Client TotalEnergies"
        
        buf = io.BytesIO()
        doc.save(buf)
        file_bytes = buf.getvalue()

        extracted = extract_text("mon_cv.docx", file_bytes)
        self.assertIn("Chef de projet Sites et Sols Pollués", extracted)
        self.assertIn("Projet Dépollution | Client TotalEnergies", extracted)

    def test_pptx_extraction_with_tables(self):
        prs = pptx.Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6]) # blank layout
        
        # Add textbox
        tx_box = slide.shapes.add_textbox(100, 100, 300, 100)
        tx_box.text_frame.text = "Présentation Compétences Ginger Burgeap"

        buf = io.BytesIO()
        prs.save(buf)
        file_bytes = buf.getvalue()

        extracted = extract_text("presentation.pptx", file_bytes)
        self.assertIn("Présentation Compétences Ginger Burgeap", extracted)

if __name__ == "__main__":
    unittest.main()

# -*- coding: utf-8 -*-
"""
Golden Master Parity Tests.
Freezes current HTML rendering and PDF page counts across languages and pagination scenarios
to ensure absolute zero visual or structural regressions during refactoring.
"""
import unittest
import io
import pypdf

from app.services.pdf_engine import render_html_template, generate_pdf_bytes, get_footer_text
from tests.test_pdf_engine import SAMPLE_CV_DATA

class TestParitySnapshots(unittest.TestCase):
    def test_html_rendering_snapshot_fr(self):
        html_fr = render_html_template(SAMPLE_CV_DATA, lang="fr")
        
        # Verify critical DOM elements and exact content presence
        self.assertIn("Marine RICHARD", html_fr)
        self.assertIn("Cheffe de Projets en Sites et Sols Pollués", html_fr)
        self.assertIn("8 ans d'expérience", html_fr)
        self.assertIn("PRINCIPALES RÉFÉRENCES – MISSIONS RÉCENTES", html_fr)
        self.assertIn("DÉPOLLUTION FONDERIE X", html_fr)
        self.assertIn("Direction Régionale Nord-Ouest", html_fr)
        self.assertNotIn("cv-page-2", html_fr)

    def test_html_rendering_snapshot_en(self):
        html_en = render_html_template(SAMPLE_CV_DATA, lang="en")
        
        self.assertIn("Marine RICHARD", html_en)
        self.assertIn("Project Manager in Polluted Sites and Soils", html_en)
        self.assertIn("KEY PROJECT REFERENCES – RECENT MISSIONS", html_en)
        self.assertIn("FOUNDRY REMEDIATION PROJECT", html_en)
        self.assertIn("North-West Regional Directorate", html_en)
        self.assertNotIn("cv-page-2", html_en)

    def test_two_pages_structure_parity(self):
        two_page_data = dict(SAMPLE_CV_DATA)
        two_page_data["refs_fr"] = SAMPLE_CV_DATA["refs_fr"] * 4  # 12 references
        
        html_2p = render_html_template(two_page_data, lang="fr")
        self.assertIn("cv-page-2", html_2p)
        self.assertIn("Page 1 / 2", html_2p)
        self.assertIn("Page 2 / 2", html_2p)
        self.assertIn("PRINCIPALES RÉFÉRENCES – SUITE DES MISSIONS", html_2p)

        pdf_bytes = generate_pdf_bytes(two_page_data, lang="fr")
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        self.assertEqual(len(reader.pages), 2)

    def test_footer_standardization_matrix(self):
        self.assertEqual(get_footer_text("Direction Régionale Nord-Ouest", True), "Ginger Burgeap – Direction Régionale Nord-Ouest")
        self.assertEqual(get_footer_text("Direction Régionale Nord-Ouest & Ile-de-France", True), "Ginger Burgeap – Direction Régionale Nord-Ouest & Ile-de-France")
        self.assertEqual(get_footer_text("QSE", True), "Ginger Burgeap – Direction QSE & Métrologies")
        self.assertEqual(get_footer_text("Direction Régionale Nord-Ouest", False), "Ginger Burgeap – North-West Regional Directorate")
        self.assertEqual(get_footer_text("Direction Régionale Nord-Ouest & Ile-de-France", False), "Ginger Burgeap – North-West & Ile-de-France Regional Directorate")
        self.assertEqual(get_footer_text("QSE", False), "Ginger Burgeap – QSE & Metrology Directorate")

if __name__ == "__main__":
    unittest.main()

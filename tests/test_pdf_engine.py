# -*- coding: utf-8 -*-
import unittest
import asyncio
import pypdf
import io
import zipfile
from app.services.pdf_engine import (
    render_html,
    render_pdf,
    render_bilingual_bundle,
    render_html_template,
    generate_pdf_bytes,
    get_footer_text
)

SAMPLE_CV_DATA = {
    "name": "Marine RICHARD",
    "trigram": "MARI",
    "initials": "MR",
    "role_fr": "Cheffe de Projets en Sites et Sols Pollués",
    "role_en": "Project Manager in Polluted Sites and Soils",
    "exp_fr": "8 ans d'expérience",
    "exp_en": "8 years of experience",
    "agency_fr": "RÉGION NORD-OUEST • AGENCE DE ROUEN",
    "agency_en": "NORTH-WEST REGION • ROUEN OFFICE",
    "formations_fr": [
        "2016 : Master 2 Gestion des Sites et Sols Pollués - Université de Rouen",
        "2014 : Licence Sciences de la Terre et Environnement"
    ],
    "formations_en": [
        "2016: Master's Degree in Polluted Sites and Soils Management - Rouen University",
        "2014: Bachelor's Degree in Earth and Environmental Sciences"
    ],
    "competences_fr": [
        "Diagnostics environnementaux et études historiques",
        "Plans de gestion et bilans quadriennaux",
        "Supervision de chantiers de dépollution"
    ],
    "competences_en": [
        "Environmental diagnostics and historical site assessments",
        "Management plans and quadriennial reviews",
        "Remediation worksite supervision"
    ],
    "exp_pros_fr": [
        "Depuis 2019 : GINGER BURGEAP - Cheffe de projets SSP",
        "2016 - 2019 : GINGER BURGEAP - Ingénieure d'études"
    ],
    "exp_pros_en": [
        "Since 2019: GINGER BURGEAP - SSP Project Manager",
        "2016 - 2019: GINGER BURGEAP - Environmental Consultant"
    ],
    "langs_fr": [
        "Français : Langue maternelle",
        "Anglais : Professionnel (B2)",
        "Mobilité : Permis B - Déplacements régionaux"
    ],
    "langs_en": [
        "French: Native",
        "English: Professional working proficiency (B2)",
        "Mobility: Driving license B - Regional mobility"
    ],
    "pitch_fr": "Ingénieure spécialisée en <strong>Sites et Sols Pollués</strong>, Marine RICHARD pilote des projets complexes de diagnostic et de maîtrise d'œuvre de dépollution.",
    "pitch_en": "Environmental engineer specializing in <strong>Polluted Sites and Soils</strong>, Marine RICHARD oversees complex diagnostic and remediation engineering projects.",
    "qualifs_fr": [
        "<strong>Diagnostics et investigations</strong> : Réalisation d'études historiques et schémas conceptuels.",
        "<strong>Plans de gestion</strong> : Évaluation quantitative des risques sanitaires et modélisations.",
        "<strong>Maîtrise d'œuvre travaux</strong> : Suivi technique et financier des chantiers de dépollution in situ et hors site.",
        "<strong>Relations réglementaires</strong> : Échanges DREAL et mise en conformité loi sur l'eau."
    ],
    "qualifs_en": [
        "<strong>Diagnostics and investigations</strong>: Execution of historical studies and conceptual site models.",
        "<strong>Management plans</strong>: Quantitative health risk assessment and contaminant transport modeling.",
        "<strong>Construction supervision</strong>: Technical and financial oversight of remediation projects.",
        "<strong>Regulatory compliance</strong>: Interfacing with environmental authorities."
    ],
    "refs_fr": [
        {"title": "DÉPOLLUTION FONDERIE X – ROUEN (76)", "tag": "SITES POLLUÉS", "desc": "Maîtrise d'œuvre complète pour la dépollution de 15 000 m³ de terres polluées aux métaux lourds et HCT."},
        {"title": "RÉHABILITATION SITE LOGISTIQUE – LE HAVRE (76)", "tag": "RECONVERSION", "desc": "Diagnostic approfondi et plan de gestion pour requalification en plateforme logistique nouvelle génération."},
        {"title": "SURVEILLANCE NAPPE CHIMIQUE – GRAND-COURONNE (76)", "tag": "HYDROGÉOLOGIE", "desc": "Campagnes semestrielles de prélèvements piézométriques et modélisation hydrodynamique 3D."}
    ],
    "refs_en": [
        {"title": "FOUNDRY REMEDIATION PROJECT – ROUEN (76)", "tag": "POLLUTED SITES", "desc": "Comprehensive project management for the excavation and treatment of 15,000 m³ of soil."},
        {"title": "LOGISTICS BROWNFIELD REDEVELOPMENT – LE HAVRE (76)", "tag": "REDEVELOPMENT", "desc": "In-depth diagnostic assessment and remediation management plan for sustainable warehouse development."},
        {"title": "GROUNDWATER MONITORING – GRAND-COURONNE (76)", "tag": "HYDROGEOLOGY", "desc": "Semi-annual groundwater sampling campaigns and 3D hydrodynamic numerical modeling."}
    ]
}

class TestPdfEngineParity(unittest.TestCase):
    def test_footer_text(self):
        self.assertEqual(get_footer_text("RÉGION NORD-OUEST • ROUEN", True), "Ginger Burgeap – Direction Régionale Nord-Ouest")
        self.assertEqual(get_footer_text("DIRECTION RÉGIONALE NORD-OUEST & ILE-DE-FRANCE", True), "Ginger Burgeap – Direction Régionale Nord-Ouest & Ile-de-France")
        self.assertEqual(get_footer_text("DIRECTION QUALITÉ, SÉCURITÉ, ENVIRONNEMENT", True), "Ginger Burgeap – Direction QSE & Métrologies")

    def test_render_html_single_page(self):
        html = render_html(SAMPLE_CV_DATA, lang="fr")
        self.assertIn("Marine RICHARD", html)
        self.assertIn("Cheffe de Projets en Sites et Sols Pollués", html)
        self.assertIn("DÉPOLLUTION FONDERIE X", html)
        self.assertNotIn("cv-page-2", html)

    def test_render_pdf_async_single_page(self):
        pdf_bytes = asyncio.run(render_pdf(SAMPLE_CV_DATA, lang="fr"))
        self.assertTrue(len(pdf_bytes) > 1000)
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        self.assertEqual(len(reader.pages), 1)

    def test_render_pdf_async_two_pages(self):
        two_page_data = dict(SAMPLE_CV_DATA)
        # 12 references to trigger Page 2
        two_page_data["refs_fr"] = SAMPLE_CV_DATA["refs_fr"] * 4
        pdf_bytes = asyncio.run(render_pdf(two_page_data, lang="fr"))
        self.assertTrue(len(pdf_bytes) > 1000)
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        self.assertEqual(len(reader.pages), 2)

    def test_render_bilingual_bundle(self):
        zip_bytes, zip_filename = asyncio.run(render_bilingual_bundle(SAMPLE_CV_DATA))
        self.assertTrue(len(zip_bytes) > 2000)
        self.assertIn("BURGEAP_2026.zip", zip_filename)

        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
            names = zf.namelist()
            self.assertEqual(len(names), 2)
            self.assertTrue(any("FR.pdf" in n for n in names))
            self.assertTrue(any("EN.pdf" in n for n in names))

            for n in names:
                f_bytes = zf.read(n)
                reader = pypdf.PdfReader(io.BytesIO(f_bytes))
                self.assertEqual(len(reader.pages), 1)

if __name__ == "__main__":
    unittest.main()

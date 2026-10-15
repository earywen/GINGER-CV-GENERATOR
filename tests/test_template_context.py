# -*- coding: utf-8 -*-
import unittest
from app.services.template_context import build_template_context, get_footer_text
from tests.test_pdf_engine import SAMPLE_CV_DATA

class TestTemplateContextBuilder(unittest.TestCase):
    def test_single_page_context(self):
        ctx = build_template_context(SAMPLE_CV_DATA, lang="fr")
        self.assertEqual(ctx["name"], "Marine RICHARD")
        self.assertEqual(ctx["role"], "Cheffe de Projets en Sites et Sols Pollués")
        self.assertFalse(ctx["has_p2"])
        self.assertEqual(ctx["page_1_pagination"], "")
        self.assertEqual(len(ctx["refs_p1"]), 3)
        self.assertEqual(len(ctx["refs_p2"]), 0)

    def test_two_page_context(self):
        two_page = dict(SAMPLE_CV_DATA)
        two_page["refs_fr"] = SAMPLE_CV_DATA["refs_fr"] * 4 # 12 refs
        ctx = build_template_context(two_page, lang="fr")
        self.assertTrue(ctx["has_p2"])
        self.assertEqual(ctx["page_1_pagination"], "Page 1 / 2")
        self.assertEqual(len(ctx["refs_p1"]), 10)
        self.assertEqual(len(ctx["refs_p2"]), 2)

    def test_english_translation_branching(self):
        ctx = build_template_context(SAMPLE_CV_DATA, lang="en")
        self.assertEqual(ctx["role"], "Project Manager in Polluted Sites and Soils")
        self.assertIn("North-West Regional Directorate", ctx["footer_text"])

if __name__ == "__main__":
    unittest.main()

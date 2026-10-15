# -*- coding: utf-8 -*-
import unittest
from app.services.ai_parser import _clean_json_response, _build_prompt
from app.models.cv import get_cv_extraction_json_schema

class TestAiParser(unittest.TestCase):
    def test_clean_json_response_plain(self):
        raw = '{"name": "Marine RICHARD", "role_fr": "Ingénieure"}'
        res = _clean_json_response(raw)
        self.assertEqual(res["name"], "Marine RICHARD")

    def test_clean_json_response_markdown_fenced(self):
        raw = '```json\n{"name": "Marine RICHARD", "role_fr": "Ingénieure"}\n```'
        res = _clean_json_response(raw)
        self.assertEqual(res["name"], "Marine RICHARD")

    def test_clean_json_response_with_surrounding_text(self):
        raw = 'Voici le résultat :\n```json\n{"name": "Marine RICHARD"}\n```\nFin du JSON.'
        res = _clean_json_response(raw)
        self.assertEqual(res["name"], "Marine RICHARD")

    def test_build_prompt_contains_rules(self):
        prompt = _build_prompt("Texte CV brut", "RÉGION NORD-OUEST")
        self.assertIn("GINGER BURGEAP", prompt)
        self.assertIn("RÈGLE ANTI-CONFUSION PRESTATAIRES", prompt)
        self.assertIn("RÉGION NORD-OUEST", prompt)

    def test_extraction_schema_has_required_fields(self):
        schema = get_cv_extraction_json_schema()
        self.assertEqual(schema["type"], "object")
        required = schema.get("required", [])
        self.assertIn("name", required)
        self.assertIn("trigram", required)
        self.assertIn("role_fr", required)
        self.assertIn("refs_fr", required)

if __name__ == "__main__":
    unittest.main()

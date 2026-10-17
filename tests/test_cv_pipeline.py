# -*- coding: utf-8 -*-
import unittest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.cv_pipeline import attach_photo_or_initials, parse_and_cache_cv, ingest_cv
from tests.test_pdf_engine import SAMPLE_CV_DATA

class TestCvPipeline(unittest.TestCase):
    def test_attach_photo_existing_b64(self):
        data = dict(SAMPLE_CV_DATA)
        valid_b64 = "data:image/jpeg;base64," + "A" * 60
        res = attach_photo_or_initials(data, photo_b64=valid_b64)
        self.assertEqual(res["photo_b64"], valid_b64)

    def test_attach_photo_generates_initials_when_no_photo(self):
        data = {"name": "Marine RICHARD"}
        res = attach_photo_or_initials(data, photo_bytes=b"", photo_b64="")
        self.assertIsNone(res["photo_b64"])
        self.assertEqual(res["initials"], "MR")

    def test_attach_photo_preserves_existing_initials_when_no_photo(self):
        data = {"name": "Marine RICHARD", "initials": "CUSTOM"}
        res = attach_photo_or_initials(data, photo_bytes=b"", photo_b64="")
        self.assertIsNone(res["photo_b64"])
        self.assertEqual(res["initials"], "CUSTOM")

    def test_parse_and_cache_cv_rejects_empty_text(self):
        with self.assertRaises(ValueError):
            asyncio.run(parse_and_cache_cv("trop court", "Agence Paris"))

    def test_ingest_cv_rejects_empty_content(self):
        with self.assertRaises(ValueError):
            asyncio.run(ingest_cv("test.txt", b"court"))

    @patch("app.services.cv_pipeline.extract_text")
    def test_ingest_cv_cache_hit_with_progress_and_initials(self, mock_extract):
        mock_extract.return_value = "Long valid CV content with many characters for testing..."
        mock_cache = MagicMock()
        mock_cache.compute_cache_key.return_value = "dummy-sha256-key"
        mock_cache.get_cached_parse.return_value = {"name": "Jean DUPONT", "role_fr": "Chef de Projets"}

        progress_calls = []
        async def on_progress(p, s, d):
            progress_calls.append((p, s))

        res = asyncio.run(ingest_cv(
            cv_filename="cv.pdf",
            cv_bytes=b"dummy-pdf-bytes",
            photo_bytes=None,
            agency="RÉGION NORD-OUEST",
            on_progress=on_progress,
            cache_mgr=mock_cache
        ))

        self.assertEqual(res["name"], "Jean DUPONT")
        self.assertEqual(res["initials"], "JD")
        self.assertIn((20, "Extraction du texte du document..."), progress_calls)
        self.assertIn((85, "Document reconnu en cache !"), progress_calls)
        self.assertIn((100, "Terminé avec succès !"), progress_calls)

    @patch("app.services.cv_pipeline.extract_text")
    @patch("app.services.cv_pipeline.parse_cv_with_agy")
    def test_ingest_cv_cache_miss_executes_ai_and_caches(self, mock_ai_parse, mock_extract):
        mock_extract.return_value = "Long valid CV content requiring AI parsing..."
        mock_ai_parse.return_value = {"name": "Sophie MARTIN", "role_fr": "Ingénieure d'Études"}
        
        mock_cache = MagicMock()
        mock_cache.compute_cache_key.return_value = "new-sha256-key"
        mock_cache.get_cached_parse.return_value = None

        res = asyncio.run(ingest_cv(
            cv_filename="cv.pdf",
            cv_bytes=b"dummy-pdf-bytes",
            photo_bytes=None,
            agency="RÉGION NORD-OUEST",
            cache_mgr=mock_cache
        ))

        self.assertEqual(res["name"], "Sophie MARTIN")
        self.assertEqual(res["initials"], "SM")
        mock_ai_parse.assert_called_once()
        mock_cache.save_cached_parse.assert_called_once_with("new-sha256-key", {"name": "Sophie MARTIN", "role_fr": "Ingénieure d'Études", "initials": "SM", "photo_b64": None})

if __name__ == "__main__":
    unittest.main()

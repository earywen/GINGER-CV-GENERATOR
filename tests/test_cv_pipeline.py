# -*- coding: utf-8 -*-
import unittest
from unittest.mock import AsyncMock, patch

from app.services.cv_pipeline import attach_photo_or_initials, parse_and_cache_cv
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
        import asyncio
        with self.assertRaises(ValueError):
            asyncio.run(parse_and_cache_cv("trop court", "Agence Paris"))

if __name__ == "__main__":
    unittest.main()

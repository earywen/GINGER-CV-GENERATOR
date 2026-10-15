# -*- coding: utf-8 -*-
import unittest
import tempfile
import shutil
from pathlib import Path
from starlette.testclient import TestClient

from app.main import app
from app.services.cache_manager import ParseCacheManager
from app.services.session_manager import SessionManager
from tests.test_pdf_engine import SAMPLE_CV_DATA

class TestCacheAndSession(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.cache_mgr = ParseCacheManager(cache_dir=self.test_dir / "cache", expiration_days=1)
        self.session_mgr = SessionManager(sessions_dir=self.test_dir / "sessions", expiration_days=1)
        self.client = TestClient(app)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_cache_key_deterministic(self):
        key1 = self.cache_mgr.compute_cache_key("  Texte de CV avec espaces   ", "Agence de Rouen")
        key2 = self.cache_mgr.compute_cache_key("Texte de CV avec espaces", "AGENCE DE ROUEN")
        self.assertEqual(key1, key2)

    def test_cache_save_and_retrieve(self):
        key = self.cache_mgr.compute_cache_key("CV test content", "Agence Paris")
        self.assertIsNone(self.cache_mgr.get_cached_parse(key))

        data = dict(SAMPLE_CV_DATA)
        data["photo_b64"] = "heavy_base64_string_that_should_be_stripped"
        self.cache_mgr.save_cached_parse(key, data)

        cached = self.cache_mgr.get_cached_parse(key)
        self.assertIsNotNone(cached)
        self.assertEqual(cached["name"], SAMPLE_CV_DATA["name"])
        self.assertNotIn("photo_b64", cached)

    def test_session_draft_lifecycle(self):
        sid = "test-session-uuid-1234"
        self.assertIsNone(self.session_mgr.get_session_draft(sid))

        draft_payload = {"cvData": SAMPLE_CV_DATA, "currentLang": "fr"}
        self.session_mgr.save_session_draft(sid, draft_payload)

        recovered = self.session_mgr.get_session_draft(sid)
        self.assertIsNotNone(recovered)
        self.assertEqual(recovered["currentLang"], "fr")
        self.assertEqual(recovered["cvData"]["name"], SAMPLE_CV_DATA["name"])

        self.session_mgr.clear_session_draft(sid)
        self.assertIsNone(self.session_mgr.get_session_draft(sid))

    def test_api_session_endpoints(self):
        # 1. Initially no draft
        res = self.client.get("/api/session/draft")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("session_id", data)
        self.assertFalse(data["has_draft"])
        sid = data["session_id"]

        # 2. Save draft
        post_res = self.client.post("/api/session/draft", json={"draft": {"cvData": SAMPLE_CV_DATA, "currentLang": "en"}})
        self.assertEqual(post_res.status_code, 200)
        self.assertEqual(post_res.json()["status"], "saved")

        # 3. Retrieve draft
        get_res = self.client.get("/api/session/draft")
        self.assertEqual(get_res.status_code, 200)
        draft_data = get_res.json()
        self.assertTrue(draft_data["has_draft"])
        self.assertEqual(draft_data["draft"]["currentLang"], "en")
        self.assertEqual(draft_data["draft"]["cvData"]["name"], SAMPLE_CV_DATA["name"])

        # 4. Clear draft
        del_res = self.client.delete("/api/session/draft")
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(del_res.json()["status"], "cleared")

        # 5. Check empty again
        final_res = self.client.get("/api/session/draft")
        self.assertFalse(final_res.json()["has_draft"])

if __name__ == "__main__":
    unittest.main()

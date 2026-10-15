# -*- coding: utf-8 -*-
import unittest
from starlette.testclient import TestClient
from app.main import app
from tests.test_pdf_engine import SAMPLE_CV_DATA

class TestApiEndpointsParity(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_serve_index(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Générateur de CV Ginger Burgeap", res.text)

    def test_render_html(self):
        res = self.client.post("/api/render-html", json={"data": SAMPLE_CV_DATA, "lang": "fr"})
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers.get("content-type", ""))
        self.assertIn("Marine RICHARD", res.text)

    def test_render_preview(self):
        res = self.client.post("/api/render-preview", json={"data": SAMPLE_CV_DATA, "lang": "fr"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("content-type"), "application/pdf")
        self.assertTrue(len(res.content) > 1000)

    def test_export_pdf(self):
        res = self.client.post("/api/export-pdf", json={"data": SAMPLE_CV_DATA, "lang": "fr"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("content-type"), "application/pdf")
        self.assertIn("attachment", res.headers.get("content-disposition", ""))
        self.assertTrue(len(res.content) > 1000)

    def test_export_zip(self):
        res = self.client.post("/api/export-zip", json={"data": SAMPLE_CV_DATA})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("content-type"), "application/zip")
        self.assertTrue(len(res.content) > 1000)

    def test_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")

    def test_parse_job_not_found(self):
        res = self.client.get("/api/parse-cv-status/unknown-uuid")
        self.assertEqual(res.status_code, 404)

if __name__ == "__main__":
    unittest.main()

# -*- coding: utf-8 -*-
import unittest
from app.models.cv import CVDataModel, CVReference, RenderPayload, JobStatusResponse
from app.utils.formatters import sanitize_filename
from tests.test_pdf_engine import SAMPLE_CV_DATA

class TestModelsAndFormatters(unittest.TestCase):
    def test_cv_data_model_validation(self):
        cv = CVDataModel.model_validate(SAMPLE_CV_DATA)
        self.assertEqual(cv.name, "Marine RICHARD")
        self.assertEqual(cv.trigram, "MARI")
        self.assertEqual(len(cv.refs_fr), 3)
        self.assertEqual(cv.refs_fr[0].tag, "SITES POLLUÉS")

    def test_cv_data_model_schema_export(self):
        schema = CVDataModel.model_json_schema()
        self.assertIn("properties", schema)
        self.assertIn("name", schema["properties"])
        self.assertIn("refs_fr", schema["properties"])

    def test_render_payload(self):
        payload = RenderPayload(data=SAMPLE_CV_DATA, lang="fr")
        self.assertEqual(payload.lang, "fr")
        self.assertEqual(payload.data["name"], "Marine RICHARD")

    def test_sanitize_filename(self):
        self.assertEqual(sanitize_filename("Marine RICHARD", "FR"), "CV_Marine_RICHARD_FR.pdf")
        self.assertEqual(sanitize_filename("Solenn   LE BAUD  ", "EN"), "CV_Solenn_LE_BAUD_EN.pdf")
        self.assertEqual(sanitize_filename('Hervé HOGIE / "Lead"', "FR", "zip"), "CV_Hervé_HOGIE_Lead_FR.zip")

if __name__ == "__main__":
    unittest.main()

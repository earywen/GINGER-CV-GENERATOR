# -*- coding: utf-8 -*-
import unittest
import tempfile
import time
import shutil
from pathlib import Path

from app.services.disk_store import DiskTTLStore

class TestDiskTTLStore(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.store = DiskTTLStore(self.tmp_dir, expiration_seconds=1)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_set_and_get(self):
        self.store.set("user_123", {"name": "Test User"})
        data = self.store.get("user_123")
        self.assertIsNotNone(data)
        self.assertEqual(data["name"], "Test User")

    def test_ttl_expiration(self):
        self.store.set("quick_expire", {"temp": "value"})
        self.assertIsNotNone(self.store.get("quick_expire"))
        time.sleep(1.1)
        self.assertIsNone(self.store.get("quick_expire"))

    def test_delete(self):
        self.store.set("to_delete", {"key": "val"})
        self.assertTrue(self.store.delete("to_delete"))
        self.assertIsNone(self.store.get("to_delete"))
        self.assertFalse(self.store.delete("to_delete"))

    def test_clear_all(self):
        self.store.set("rec_1", {"a": 1})
        self.store.set("rec_2", {"b": 2})
        count = self.store.clear_all()
        self.assertEqual(count, 2)
        self.assertIsNone(self.store.get("rec_1"))
        self.assertIsNone(self.store.get("rec_2"))

if __name__ == "__main__":
    unittest.main()

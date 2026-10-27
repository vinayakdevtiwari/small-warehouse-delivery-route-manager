"""Streamlit app smoke test, using a temporary database to avoid repository data changes."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest
from warehouse_app import database


class AppSmokeTest(unittest.TestCase):
    def test_app_runs_without_streamlit_exceptions(self):
        original_path = database.DB_PATH
        with tempfile.TemporaryDirectory() as tmp:
            database.DB_PATH = Path(tmp) / "smoke.sqlite3"
            try:
                app_path = Path(__file__).resolve().parents[1] / "app.py"
                result = AppTest.from_file(str(app_path), default_timeout=30).run()
                self.assertEqual(len(result.exception), 0, "\n".join(str(e.value) for e in result.exception))
                self.assertTrue(any("WarehouseFlow" in str(item.value) for item in result.markdown))
            finally:
                database.DB_PATH = original_path


if __name__ == "__main__":
    unittest.main()

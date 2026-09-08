import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CLITests(unittest.TestCase):
    def test_cli_emits_json(self):
        root = Path(__file__).resolve().parents[1]
        source = root / "data" / "sample_company.json"
        proc = subprocess.run(
            [sys.executable, "-m", "src.corporate_finance.cli", str(source)],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["company"], "Atlas Manufacturing Ltd")
        self.assertIn("metrics", payload)

    def test_cli_writes_report(self):
        root = Path(__file__).resolve().parents[1]
        source = root / "data" / "sample_company.json"
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            subprocess.run(
                [sys.executable, "-m", "src.corporate_finance.cli", str(source), "--output", str(output)],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertTrue(output.exists())
            self.assertIn("risk_summary", json.loads(output.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()

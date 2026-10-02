from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(script.parent),
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


class ScriptTests(unittest.TestCase):
    def test_esp_demo(self):
        r = run(
            ROOT / "skills" / "seagull-game-hack" / "scripts" / "esp_demo.py",
            "--demo",
            "--no-gui",
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("projected=3", r.stdout)
        self.assertIn("skipped=1", r.stdout)
        self.assertIn("alpha", r.stdout)
        self.assertNotIn("behind", r.stdout.split("---")[0])

    def test_pwn_harness_dry_run(self):
        r = run(
            ROOT / "skills" / "seagull-exploit" / "scripts" / "pwn_harness.py",
            "--dry-run",
            "--offset",
            "40",
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("len=48", r.stdout)

    def test_license_harness(self):
        r = run(
            ROOT / "skills" / "seagull-license-security" / "scripts" / "license_harness.py",
            "--json",
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('"all_passed": true', r.stdout)
        self.assertIn("local_compare", r.stdout)

    def test_idor_dry_run(self):
        r = run(
            ROOT / "skills" / "seagull-pentest" / "scripts" / "idor_replay.py",
            "--dry-run",
            "--ids",
            "1,2",
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("dry-run", r.stdout)
        self.assertIn("anon", r.stdout)


if __name__ == "__main__":
    unittest.main()

"""init.py (chép khung, không ghi đè) và audit.py (kiểm toán Ngày 0)."""
import pathlib
import tempfile
import unittest

from helpers import AUDIT, INIT, PY, ProjectCase, run


class InitTest(unittest.TestCase):
    def test_copies_template_and_renames_gitignore(self):
        with tempfile.TemporaryDirectory() as d:
            r = run([PY, str(INIT), d], d)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            root = pathlib.Path(d)
            for f in ("AGENTS.md", "STATUS.md", "pos.py", ".gitignore", ".githooks/pre-push",
                      "docs/PROCESS.md", "docs/product/FEATURES.md", "scripts/features.py"):
                self.assertTrue((root / f).is_file(), f)
            self.assertFalse((root / "gitignore.template").exists())
            self.assertFalse((root / "docs/plan").exists(), "chỉ có docs/plan khi chạy --plan")

    def test_plan_flag_adds_roadmap(self):
        with tempfile.TemporaryDirectory() as d:
            run([PY, str(INIT), d, "--plan"], d)
            self.assertTrue((pathlib.Path(d) / "docs/plan/ROADMAP.md").is_file())

    def test_never_overwrites_existing_file(self):
        with tempfile.TemporaryDirectory() as d:
            agents = pathlib.Path(d) / "AGENTS.md"
            agents.write_text("của chủ dự án\n", encoding="utf-8")
            r = run([PY, str(INIT), d], d)
            self.assertIn("giữ  AGENTS.md", r.stdout)
            self.assertEqual(agents.read_text(encoding="utf-8"), "của chủ dự án\n")


class AuditTest(ProjectCase):
    configured = False

    def test_fresh_template_is_not_ready(self):
        r = run([PY, str(AUDIT), str(self.root)], self.root)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("Chưa  file lõi không còn chỗ {{…}} chưa điền", r.stdout)
        self.assertIn("Đạt   hook đã bật", r.stdout)
        self.assertIn("Chưa  pos.py đã điền TEST_CMD", r.stdout)
        self.assertIn("Chưa  python pos.py check qua", r.stdout)


if __name__ == "__main__":
    unittest.main()

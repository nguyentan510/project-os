"""Hàm dùng chung cho test: dựng một dự án tạm đã chép khung Ngày 0. Chỉ thư viện chuẩn."""
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
SKILL = REPO / ".agents" / "skills" / "project-os"
INIT = SKILL / "scripts" / "init.py"
AUDIT = SKILL / "scripts" / "audit.py"
PY = sys.executable


def run(args, cwd, env=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)


def git(cwd, *args):
    r = run(["git", *args], cwd)
    if r.returncode:
        raise AssertionError(f"git {' '.join(args)}: {r.stderr}")
    return r.stdout.strip()


class ProjectCase(unittest.TestCase):
    """Mỗi test có một repo git tạm, đã chạy init.py, có commit đầu trên main."""

    git_repo = True
    configured = True  # điền LINT_CMD/TEST_CMD = "none" để check (và hook pre-push) qua

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name) / "proj"
        self.root.mkdir()
        if self.git_repo:
            git(self.root, "init", "-q", "-b", "main")
            git(self.root, "config", "user.email", "test@example.com")
            git(self.root, "config", "user.name", "test")
        r = run([PY, str(INIT), str(self.root)], self.root)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        if self.configured:
            pos = self.root / "pos.py"
            text = pos.read_text(encoding="utf-8")
            pos.write_text(text.replace('LINT_CMD = ""', 'LINT_CMD = "none"').replace('TEST_CMD = ""', 'TEST_CMD = "none"'),
                           encoding="utf-8")
        if self.git_repo:
            git(self.root, "add", "-A")
            git(self.root, "commit", "-q", "-m", "init")

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(text).lstrip("\n"), encoding="utf-8")
        return p

    def pos(self, *args, env=None):
        return run([PY, "pos.py", *args], self.root, env=env)

    def features(self, *args):
        return run([PY, "scripts/features.py", *args], self.root)

    def set_hot_files(self, line):
        agents = self.root / "AGENTS.md"
        text = agents.read_text(encoding="utf-8")
        start = text.index("## Hot file")
        end = text.index("\n## ", start + 1)
        agents.write_text(text[:start] + "## Hot file\n" + line + "\n" + text[end:], encoding="utf-8")

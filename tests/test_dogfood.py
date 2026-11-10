"""DOC-02 · Repo tự áp dụng: khung ở gốc repo là bản chép của template/ (D06), phải khớp bản gốc.

Bản gốc là `.agents/skills/project-os/template/`. Sửa ở đó trước, rồi chép ra gốc. Test lệch thì chép lại:
    cp .agents/skills/project-os/template/<file> <file>
"""
import json
import re
import unittest

from helpers import REPO, SKILL

TEMPLATE = SKILL / "template"
# Giống hệt bản gốc
SAME = ["scripts/features.py", ".githooks/pre-push", "docs/PROCESS.md"]
PROJECT_TERMS = "## Thuật ngữ của dự án"


def text(path):
    return path.read_bytes().decode("utf-8").replace("\r\n", "\n")


class RootCopiesTest(unittest.TestCase):
    def assertSame(self, rel, root, template):
        self.assertEqual(root, template, f"{rel} ở gốc repo lệch bản gốc template/{rel}: sửa ở template/ trước, rồi chép ra gốc (D06)")

    def test_files_identical_to_template(self):
        for rel in SAME + sorted(f"docs/prompts/{p.name}" for p in (TEMPLATE / "docs/prompts").glob("P-*.md")):
            with self.subTest(file=rel):
                self.assertTrue((REPO / rel).is_file(), f"thiếu {rel} ở gốc repo")
                self.assertSame(rel, text(REPO / rel), text(TEMPLATE / rel))

    def test_no_extra_prompt_at_root(self):
        self.assertEqual(sorted(p.name for p in (REPO / "docs/prompts").glob("*.md")),
                         sorted(p.name for p in (TEMPLATE / "docs/prompts").glob("*.md")))

    def test_pos_py_differs_only_in_command_config(self):
        def engine(path):  # bỏ các dòng cấu hình lệnh: gốc repo điền lệnh thật, bản gốc để trống
            return "\n".join(l for l in text(path).splitlines() if not re.match(r"^(SETUP|RUN|LINT|TEST)_CMD = ", l))
        self.assertSame("pos.py", engine(REPO / "pos.py"), engine(TEMPLATE / "pos.py"))

    def test_glossary_matches_up_to_project_terms(self):
        def shared(path):  # mục cuối là thuật ngữ riêng của dự án, mỗi repo một khác
            return text(path).split(PROJECT_TERMS, 1)[0]
        self.assertIn(PROJECT_TERMS, text(REPO / "docs/GLOSSARY.md"))
        self.assertSame("docs/GLOSSARY.md", shared(REPO / "docs/GLOSSARY.md"), shared(TEMPLATE / "docs/GLOSSARY.md"))


class VersionTest(unittest.TestCase):
    def test_process_version_is_package_version(self):
        """D10: một số phiên bản duy nhất, lấy từ package.json."""
        version = json.loads(text(REPO / "package.json"))["version"]
        m = re.search(r"^Phiên bản (\S+) ·", text(TEMPLATE / "docs/PROCESS.md"), re.M)
        self.assertTrue(m, "PROCESS.md thiếu dòng 'Phiên bản <số> ·'")
        self.assertEqual(m.group(1), version, "PROCESS.md ghi phiên bản khác package.json (D10)")


class HookEnvTest(unittest.TestCase):
    def test_git_hook_env_does_not_leak_into_test_repos(self):
        """Hook đặt GIT_DIR trỏ về repo thật; lệnh git của test vẫn phải chạy trên repo tạm."""
        import os
        import tempfile
        from helpers import git, run
        with tempfile.TemporaryDirectory() as d:
            git(d, "init", "-q", "-b", "main")
            env = dict(os.environ, GIT_DIR=str(REPO / ".git"), GIT_WORK_TREE=str(REPO))
            top = run(["git", "rev-parse", "--show-toplevel"], d, env=env).stdout.strip()
            self.assertEqual(os.path.realpath(top), os.path.realpath(d))


if __name__ == "__main__":
    unittest.main()

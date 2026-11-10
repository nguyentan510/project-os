"""REG-01 · Kiểm sổ mã không quét file của skill đã cài vào dự án (thẻ T-009).

Phát hiện ở dự án eDMS: sau `npx … project-os` rồi chép khung, kiểm sổ mã quét cả file mẫu của skill trong `.agents/`
và `.claude/`, báo mã ví dụ (ORD-09…) và biến môi trường của pos.py mẫu là lỗi của dự án.
"""
import shutil
import unittest

from helpers import REPO, SKILL, ProjectCase, run

REGISTRY = """
# FEATURES
## SALES · Bán hàng
### ORD · Đơn hàng
| Mã | Tên gọi | Hành vi chính | Code chính (điểm vào) | Test liên quan | QĐ | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| ORD-01 | Báo đơn | Sales báo đơn | — | — | D01 | dự kiến |
"""
MARKER = ".project-os-install"  # bin/project-os.js ghi file này vào thư mục skill nó cài


class InstalledSkillTest(ProjectCase):
    git_repo = False

    def setUp(self):
        super().setUp()
        self.write("docs/product/FEATURES.md", REGISTRY)

    def install(self, where, marker=True):
        dest = self.root / where / "skills" / "project-os"
        shutil.copytree(SKILL, dest)
        if marker:
            (dest / MARKER).write_text("1.6.0\n", encoding="utf-8")
        return dest

    def test_installed_skill_files_are_not_scanned(self):
        self.install(".agents")
        self.install(".claude")
        r = self.features()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("lỗi 0", r.stdout)

    def test_project_code_is_still_checked_next_to_an_installed_skill(self):
        self.install(".agents")
        self.write("src/ord/a.py", "# ORD-77\nimport os\nKEY = os.getenv('ORD_API_KEY')\n")
        r = self.features()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("ORD-77: có trong src/ord/a.py", r.stdout)
        self.assertIn("ORD_API_KEY", r.stdout)
        self.assertNotIn(".agents/", r.stdout)

    def test_skill_source_without_marker_is_still_scanned(self):
        # Repo project-os tự chứa bản nguồn của skill, không có file đánh dấu: vẫn phải quét như code của dự án.
        self.install(".agents", marker=False)
        r = self.features()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn(".agents/skills/project-os/", r.stdout)

    @unittest.skipUnless(shutil.which("node"), "cần Node.js để chạy trình cài thật")
    def test_real_installer_then_registry_check_passes(self):
        r = run(["node", str(REPO / "bin" / "project-os.js"), "--dir", str(self.root)], self.root)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.root / ".agents/skills/project-os" / MARKER).is_file(), "trình cài phải ghi file đánh dấu")
        self.assertTrue((self.root / ".claude/skills/project-os" / MARKER).is_file())
        r = self.features()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("lỗi 0", r.stdout)


if __name__ == "__main__":
    unittest.main()

"""Lớp PO (PROCESS.md mục 14): find, nhóm "Chờ PO", cột Tên gọi, trạng thái `để sau`, và chống lệch prompt."""
import re
import unittest

from helpers import SKILL, ProjectCase

REGISTRY = """
# FEATURES
## SALES · Bán hàng
### SHOP · Bản đồ điểm bán
| Mã | Tên gọi | Hành vi chính | Code chính (điểm vào) | Test liên quan | QĐ | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| SHOP-01 | Bản đồ Sales | Sales mở bản đồ từ Bảng tin | src/shop/a.py | — | D01 | dùng |
| SHOP-02 | Phạm vi xem điểm bán | Sales chỉ thấy điểm bán được cấp quyền | — | — | D02 | dự kiến |
| SHOP-03 | Chỉ đường | Sales bấm điểm bán để mở chỉ đường | — | — | — | để sau |
"""

DECISIONS = """
# DECISIONS
| Mã | Ngày | Quyết định | Lý do | Mã liên quan | Duyệt |
| --- | --- | --- | --- | --- | --- |
| D01 | 2026-11-09 | Bản đồ tải một lần | Đơn giản | SHOP-01 | PO |

## Còn mở

| Mã | Câu hỏi | Lựa chọn (khuyến nghị đứng đầu) | Chờ ai |
| --- | --- | --- | --- |
| Q-map | Nguồn ô bản đồ | OpenStreetMap miễn phí · Google trả phí | PO |
| Q-db | Chọn chỉ mục | — | AI |
"""

PLAN = """
- [ ] T-002 · SHOP-01 · màn bản đồ
      Wave:      W1
      Scope:     src/shop/*
      Xong khi:  Sales thấy ghim trên bản đồ; python pos.py test F=SHOP-01 qua
- [ ] T-003 · SHOP-02 · lọc theo quyền
      Wave:      W2
      Scope:     src/perm/*
      Phụ thuộc: T-002
"""


class PoCase(ProjectCase):
    def setUp(self):
        super().setUp()
        self.write("docs/product/FEATURES.md", REGISTRY)
        self.write("docs/DECISIONS.md", DECISIONS)
        self.write("docs/plan/M1.md", PLAN)


class FindTest(PoCase):
    def find(self, *words):
        r = self.pos("find", *words)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def test_matches_without_accents_and_shows_name_before_code(self):
        out = self.find("ban", "do", "sales")
        self.assertIn("Bản đồ Sales — Sales mở bản đồ từ Bảng tin (SHOP-01) · dùng", out)

    def test_all_words_must_match_and_name_ranks_first(self):
        lines = self.find("điểm", "bán").splitlines()
        self.assertIn("Phạm vi xem điểm bán", lines[1], "khớp ở tên gọi phải đứng đầu: " + "\n".join(lines))
        self.assertNotIn("SHOP-01", "\n".join(lines), "SHOP-01 không có chữ 'điểm bán'")

    def test_finds_module_decision_question_and_card(self):
        self.assertIn("Bản đồ điểm bán (module SHOP)", self.find("ban do diem ban"))
        self.assertIn("Bản đồ tải một lần (D01) · quyết định", self.find("tải một lần"))
        self.assertIn("Nguồn ô bản đồ (Q-map) · câu hỏi còn mở", self.find("nguon o"))
        self.assertIn("(T-003) · thẻ task", self.find("loc theo quyen"))

    def test_no_match_suggests_new_work(self):
        out = self.find("thanh", "toán")
        self.assertIn("không thấy gì khớp", out)
        self.assertIn("để sau", out)

    def test_needs_words(self):
        self.assertEqual(self.pos("find").returncode, 1)


class StatusForPoTest(PoCase):
    def test_waiting_group_and_named_cards(self):
        status = (self.root / "STATUS.md").read_text(encoding="utf-8")
        self.write("STATUS.md", status.replace("(trống, hoặc các Q-… liên quan)", "- Chưa có tài khoản bot để mở PR"))
        r = self.pos("status")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        out = r.stdout
        self.assertIn("Cần quyết: Nguồn ô bản đồ (Q-map) · lựa chọn: OpenStreetMap miễn phí · Google trả phí", out)
        self.assertNotIn("Q-db", out, "câu hỏi chờ AI không phải việc của PO")
        self.assertIn("Đang chặn: Chưa có tài khoản bot để mở PR", out)
        self.assertIn("chờ PO 2", out)
        self.assertIn("T-002  Bản đồ Sales (SHOP-01) · màn bản đồ", out)
        self.assertIn("T-003  (chờ T-002)  Phạm vi xem điểm bán (SHOP-02)", out)


class PlanCheckWarningTest(PoCase):
    def test_missing_done_when_warns_but_passes(self):
        r = self.pos("plan-check")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("cảnh báo  T-003: thiếu 'Xong khi'", r.stdout)
        self.assertNotIn("cảnh báo  T-002", r.stdout)


class RegistryColumnsTest(PoCase):
    git_repo = False

    def test_sync_writes_test_column_when_name_column_exists(self):
        self.write("src/shop/a.py", "# SHOP-01\n")
        self.write("tests/api/shop/test_a.py", "# SHOP-01\n")
        r = self.features("--sync")
        self.assertEqual(r.returncode, 0, r.stdout)
        text = (self.root / "docs/product/FEATURES.md").read_text(encoding="utf-8")
        self.assertIn("| SHOP-01 | Bản đồ Sales | Sales mở bản đồ từ Bảng tin | src/shop/a.py | tests/api/shop/test_a.py (1) | D01 | dùng |", text)

    def test_later_status_is_counted_and_warned_when_in_code(self):
        r = self.features()
        self.assertIn("để sau 1", r.stdout)
        self.write("src/shop/b.py", "# SHOP-03\n")
        r = self.features()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("SHOP-03: trạng thái `để sau` nhưng đã có trong src/shop/b.py", r.stdout)


class PromptSyncTest(unittest.TestCase):
    """Bảng prompt (PROCESS.md mục 13) và docs/prompts/*.md phải nói cùng một điều."""

    def setUp(self):
        self.process = (SKILL / "template/docs/PROCESS.md").read_text(encoding="utf-8")
        self.files = {p.stem: p.read_text(encoding="utf-8") for p in (SKILL / "template/docs/prompts").glob("P-*.md")}

    def table(self):
        rows = {}
        for line in self.process.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 5 and re.fullmatch(r"P-[0-9A-Z-]+", cells[0]):
                rows[cells[0]] = cells[3]
        return rows

    def test_every_prompt_has_row_and_file(self):
        self.assertEqual(sorted(self.table()), sorted(self.files))

    def test_prompt_text_matches_between_table_and_file(self):
        table = self.table()
        for name, text in sorted(self.files.items()):
            if name == "P-SOS":
                continue  # file giữ bản đầy đủ nhiều dòng; bảng chỉ có bản rút gọn
            with self.subTest(prompt=name):
                block = re.search(r"```\n(.*?)\n```", text, re.S)
                self.assertTrue(block, "thiếu khối prompt")
                self.assertEqual(block.group(1).replace("`", "").strip(), table[name].replace("`", "").strip())

    def test_intent_table_only_routes_to_existing_prompts(self):
        section = self.process.split("## 14. Lớp PO", 1)[1].split("## Phụ lục", 1)[0]
        codes = set(re.findall(r"\bP-(?:SOS|\d{2}(?:-MULTI)?)\b", section))
        self.assertTrue({"P-00", "P-02", "P-06", "P-13", "P-SOS"} <= codes, codes)
        self.assertEqual(codes - set(self.files), set())


if __name__ == "__main__":
    unittest.main()

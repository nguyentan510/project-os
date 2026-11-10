"""EVL-03 · Bộ thử vi phạm phải chạy được và bắt đủ 10/10."""
import unittest

from helpers import PY, REPO, run


class ViolationEvalTest(unittest.TestCase):
    def test_all_ten_violations_are_caught(self):
        r = run([PY, str(REPO / "evals" / "violations.py")], REPO)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Kết quả: máy chặn bắt được 10/10", r.stdout)
        self.assertNotIn("LỌT", r.stdout)

    def test_known_escapes_are_reported_separately(self):
        r = run([PY, str(REPO / "evals" / "violations.py")], REPO)
        self.assertIn("Đã biết là lọt", r.stdout)
        self.assertNotIn("ĐÃ BỊ CHẶN", r.stdout, "một kiểu từng lọt nay đã bị chặn: chuyển nó lên bảng chính của bộ thử")


if __name__ == "__main__":
    unittest.main()

"""pos.py: check, task/done, scope (luật cứng 8), plan-check (Wave), sos."""
import os
import unittest

from helpers import PY, ProjectCase, git, run

CARDS = """
- [ ] T-002 · MAP-01 · bản đồ
      Wave:      W1
      Scope:     src/map/*, tests/api/map/*
- [ ] T-003 · ORD-01 · đơn hàng
      Wave:      W1
      Scope:     src/ord/*, tests/api/ord/*
"""


class CheckTest(ProjectCase):
    configured = False

    def set_cmds(self, lint, test):
        pos = self.root / "pos.py"
        text = pos.read_text(encoding="utf-8")
        text = text.replace('LINT_CMD = ""', f"LINT_CMD = {lint!r}").replace('TEST_CMD = ""', f"TEST_CMD = {test!r}")
        pos.write_text(text, encoding="utf-8")

    def test_unconfigured_lint_and_test_fail(self):
        r = self.pos("check")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("LỖI: chưa cấu hình LINT_CMD", r.stdout)
        self.assertNotIn("check: qua", r.stdout)

    def test_none_passes_with_warning(self):
        self.set_cmds("none", "none")
        r = self.pos("check")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("CẢNH BÁO: TEST_CMD", r.stdout)

    def test_real_command_result_is_used(self):
        self.set_cmds("none", "exit 3")
        self.assertEqual(self.pos("check").returncode, 3)

    def test_setup_without_command_still_passes(self):
        self.assertEqual(self.pos("setup").returncode, 0)

    def test_unknown_command_exits_2(self):
        self.assertEqual(self.pos("khong-co").returncode, 2)


class PlanCheckTest(ProjectCase):
    def test_disjoint_scopes_pass(self):
        self.write("docs/plan/M1.md", CARDS)
        r = self.pos("plan-check")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_overlapping_scope_in_same_wave_fails(self):
        self.write("docs/plan/M1.md", CARDS + "- [ ] T-004 · MAP-02 · x\n      Wave: W1\n      Scope: src/map/web/*\n")
        r = self.pos("plan-check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("T-002 và T-004 trùng Scope", r.stdout)

    def test_dependency_must_point_to_earlier_wave(self):
        self.write("docs/plan/M1.md", CARDS.replace("Scope:     src/ord/*", "Phụ thuộc: T-002\n      Scope:     src/ord/*"))
        r = self.pos("plan-check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("phải trỏ về Wave trước", r.stdout)

    def test_unknown_dependency_fails(self):
        self.write("docs/plan/M1.md", CARDS.replace("Scope:     src/ord/*", "Phụ thuộc: T-099\n      Scope:     src/ord/*"))
        self.assertIn("không có thẻ này", self.pos("plan-check").stdout)

    def test_parallel_task_writing_hot_file_fails(self):
        self.set_hot_files("src/map/routes.py")
        self.write("docs/plan/M1.md", CARDS)
        r = self.pos("plan-check")
        self.assertEqual(r.returncode, 1)
        self.assertIn("T-002 ghi vào Hot file", r.stdout)

    def test_hot_file_with_inner_wildcard_does_not_flag_unrelated_scope(self):
        self.set_hot_files("src/*/routes.py")
        self.write("docs/plan/M1.md", CARDS.replace("src/map/*", "src/map/web/*").replace("src/ord/*", "src/ord/web/*"))
        r = self.pos("plan-check")
        self.assertEqual(r.returncode, 0, r.stdout)


class OverlapTest(unittest.TestCase):
    def setUp(self):
        import importlib.util
        from helpers import SKILL
        spec = importlib.util.spec_from_file_location("pos", SKILL / "template" / "pos.py")
        self.pos = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.pos)

    def test_cases(self):
        cases = [
            ("src/map/*", "src/map/web/*", True),         # thư mục con
            ("src/map/*", "src/ord/*", False),
            ("src/map/*", "src/map", True),                # thư mục cha viết không có /
            ("src/map/", "src/map/a.py", True),
            ("src/*/routes.py", "src/map/web/*", False),   # * giữa chỉ thay một thư mục
            ("src/*/routes.py", "src/map/*", True),        # src/map/routes.py
            ("src/*/routes.py", "src/map/routes.py", True),
            ("src/map*", "src/mapping/a.py", True),
            ("**/contract.*", "src/map/*", True),          # ** thì báo trùng (thận trọng)
            ("db/schema.*", "src/map/*", False),
            ("tests/api/map/*", "tests/api/ord/*", False),
        ]
        for a, b, want in cases:
            with self.subTest(a=a, b=b):
                self.assertEqual(self.pos.overlaps(a, b), want)
                self.assertEqual(self.pos.overlaps(b, a), want)


class WorktreeCase(ProjectCase):
    """Có remote origin (repo bare) để task/done/scope so với origin/main."""

    def setUp(self):
        super().setUp()
        self.origin = self.root.parent / "origin.git"
        git(self.root.parent, "init", "-q", "--bare", "-b", "main", str(self.origin))
        git(self.root, "remote", "add", "origin", str(self.origin))
        git(self.root, "push", "-q", "-u", "origin", "main")
        self.wt = self.root.parent / "wt" / "T-002"

    def commit_on_main(self, rel, text):
        self.write(rel, text)
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", f"add {rel}")
        git(self.root, "push", "-q", "origin", "main")


class TaskTest(WorktreeCase):
    def test_task_creates_worktree_and_done_refuses_unmerged(self):
        r = self.pos("task", "T=T-002", "N=map-sales")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertTrue(self.wt.is_dir())
        self.assertEqual(git(self.wt, "rev-parse", "--abbrev-ref", "HEAD"), "feat/T-002-map-sales")
        (self.wt / "x.txt").write_text("x", encoding="utf-8")
        git(self.wt, "add", "-A")
        git(self.wt, "commit", "-q", "-m", "wip")
        r = self.pos("done", "T=T-002")
        self.assertEqual(r.returncode, 1)
        self.assertIn("chưa merge", r.stdout)

    def test_bad_arguments_are_rejected(self):
        self.assertIn("T sai dạng", self.pos("task", "T=abc", "N=x").stdout)
        self.assertIn("kebab-case", self.pos("task", "T=T-002", "N=Map Sales").stdout)

    def test_drop_needs_confirm(self):
        self.pos("task", "T=T-002", "N=map-sales")
        r = self.pos("drop", "T=T-002")
        self.assertEqual(r.returncode, 1)
        self.assertTrue(self.wt.is_dir())
        self.assertEqual(self.pos("drop", "T=T-002", "CONFIRM=T-002").returncode, 0)
        self.assertFalse(self.wt.is_dir())


class ScopeTest(WorktreeCase):
    def setUp(self):
        super().setUp()
        self.commit_on_main("docs/plan/M1.md", CARDS)
        self.pos("task", "T=T-002", "N=map-sales")

    def scope(self):
        return run([PY, "pos.py", "scope"], self.wt)

    def edit(self, rel):
        p = self.wt / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x", encoding="utf-8")
        git(self.wt, "add", "-A")
        git(self.wt, "commit", "-q", "-m", rel)

    def test_inside_scope_passes(self):
        self.edit("src/map/a.py")
        r = self.scope()
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_outside_scope_fails(self):
        self.edit("src/ord/a.py")
        r = self.scope()
        self.assertEqual(r.returncode, 1)
        self.assertIn("src/ord/a.py", r.stdout)

    def test_card_is_read_from_main_not_branch(self):
        # Builder tự nới Scope trong branch của mình: không có tác dụng
        (self.wt / "docs/plan/M1.md").write_text(CARDS.replace("src/map/*", "src/*"), encoding="utf-8")
        self.edit("src/ord/a.py")
        self.assertEqual(self.scope().returncode, 1)

    def test_branch_name_from_env_for_ci(self):
        self.edit("src/ord/a.py")
        env = dict(os.environ, PROJECT_OS_BRANCH="feat/T-003-ord")
        r = run([PY, "pos.py", "scope"], self.wt, env=env)
        self.assertIn("T-003", r.stdout)


class SosTest(ProjectCase):
    def test_sos_backs_up_dirty_tree_without_touching_it(self):
        self.write("new.txt", "chưa commit")
        head = git(self.root, "rev-parse", "HEAD")
        r = self.pos("sos")
        self.assertEqual(r.returncode, 0, r.stdout)
        branches = git(self.root, "branch", "--list", "salvage/sos-*")
        self.assertTrue(branches)
        name = branches.strip().lstrip("* ").split()[0]
        self.assertIn("new.txt", git(self.root, "show", "--name-only", "--format=", name))
        self.assertEqual(git(self.root, "rev-parse", "HEAD"), head)
        self.assertIn("?? new.txt", git(self.root, "status", "--porcelain"))


if __name__ == "__main__":
    unittest.main()

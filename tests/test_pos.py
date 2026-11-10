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

    def edit(self, rel, text="x"):
        p = self.wt / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
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


    # Mặc định là chặn: không có thẻ thì chỉ qua khi đủ điều kiện Lane Fast.
    def scope_as(self, branch, **extra):
        return run([PY, "pos.py", "scope"], self.wt, env=dict(os.environ, PROJECT_OS_BRANCH=branch, **extra))

    def test_no_card_small_change_passes_as_fast(self):
        self.edit("src/ord/a.py")
        r = self.scope_as("fix/ORD-01-typo")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("Lane Fast", r.stdout)

    def test_no_card_large_change_fails(self):
        self.edit("src/ord/a.py", "x\n" * 150)
        for branch in ("fix/ORD-01-typo", "feat/T-099-no-card", "whatever"):
            with self.subTest(branch=branch):
                r = self.scope_as(branch)
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn("FAST_MAX_LINES", r.stdout)

    def test_no_card_docs_are_not_counted(self):
        self.edit("docs/notes.md", "x\n" * 500)
        self.assertEqual(self.scope_as("docs/ORD-01-notes").returncode, 0)

    def test_no_card_touching_guard_or_hot_file_fails(self):
        self.edit(".github/workflows/extra.yml")
        r = self.scope_as("fix/ORD-01-typo")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn(".github/workflows/extra.yml", r.stdout)

    def test_restricted_zone_is_read_from_main(self):
        agents = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        self.commit_on_main("AGENTS.md", agents.replace("## Restricted zone (cùng danh sách với .github/CODEOWNERS)\n",
                                                        "## Restricted zone\nsrc/auth/, **/contract.*\n"))
        git(self.wt, "rebase", "-q", "origin/main")
        self.edit("src/map/contract.py")
        self.assertEqual(self.scope_as("fix/MAP-01-typo").returncode, 1)

    def test_card_without_scope_line_fails(self):
        self.commit_on_main("docs/plan/M2.md", "- [ ] T-004 · MAP-01 · thiếu Scope\n      Wave:      W1\n")
        self.edit("src/map/a.py")
        r = self.scope_as("feat/T-004-x")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("chưa có dòng 'Scope:'", r.stdout)

    def test_card_in_status_md_for_small_project(self):
        self.commit_on_main("STATUS.md", "## Tiếp theo\n- [ ] T-005 · MAP-01 · khung\n      Scope:     src/app/*, .github/**\n")
        self.edit("src/app/main.py", "x\n" * 300)
        self.edit(".github/workflows/extra.yml")
        r = self.scope_as("feat/T-005-skeleton")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_pos_py_copied_from_main_runs_on_pr_tree(self):
        # CI: bản pos.py của nhánh đích đặt ngoài repo, PROJECT_OS_ROOT trỏ về mã nguồn của PR
        import shutil
        outside = self.root.parent / "base-pos.py"
        shutil.copy(self.root / "pos.py", outside)
        (self.wt / "pos.py").write_text("raise SystemExit(0)  # PR tự tắt máy chặn\n", encoding="utf-8")
        self.edit("src/ord/a.py")
        env = dict(os.environ, PROJECT_OS_BRANCH="feat/T-002-map-sales", PROJECT_OS_ROOT=str(self.wt))
        r = run([PY, str(outside), "scope"], self.wt, env=env)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("pos.py", r.stdout)

    def test_on_main_without_ci_branch_is_skipped(self):
        self.assertEqual(self.pos("scope").returncode, 0)


class PathMatchTest(OverlapTest):
    def test_cases(self):
        cases = [
            (".github/workflows/ci.yml", ".github/**", True),    # dấu chấm đầu không bị xoá
            (".env.example", ".env.example", True),
            ("src/map/web/x.ts", "src/map", True),                # thư mục trần
            ("src/map/web/x.ts", "src/map/", True),
            ("src/map/web/x.ts", "src/map/*", True),              # * cuối phủ thư mục con
            ("src/mapping/x.ts", "src/map/*", False),
            ("src/a/routes.py", "src/*/routes.py", True),
            ("src/a/b/routes.py", "src/*/routes.py", False),      # * giữa chỉ thay một thư mục
            ("src/map/contract.py", "**/contract.*", True),
            ("contract.py", "**/contract.*", True),
            ("src/map/service.py", "**/contract.*", False),
            ("src/auth/login.py", "/src/auth/", True),            # kiểu CODEOWNERS
            ("src/map/a.py", "src/map/*.py", True),
            ("src/map/a.ts", "src/map/*.py", False),
        ]
        for path, pat, want in cases:
            with self.subTest(path=path, pat=pat):
                self.assertEqual(self.pos.in_scope(path, [pat]), want)


class SecretsTest(ProjectCase):
    FAKE = "AKIA" + "ABCDEFGHIJKLMNOP"  # ghép chuỗi để file test này không tự dính quét khoá

    def test_clean_project_passes(self):
        self.assertEqual(self.pos("secrets").returncode, 0)

    def test_secret_in_new_file_fails_check_without_printing_value(self):
        self.write("src/config.py", f'KEY = "{self.FAKE}"\n')
        r = self.pos("check")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("src/config.py:1: AWS access key", r.stdout)
        self.assertNotIn(self.FAKE, r.stdout)

    def test_allow_marker_skips_line(self):
        self.write("tests/fixture.py", f'KEY = "{self.FAKE}"  # project-os: allow-secret\n')
        self.assertEqual(self.pos("secrets").returncode, 0)

    def test_ignored_env_passes_but_tracked_env_fails(self):
        self.write(".env", f"KEY={self.FAKE}\n")
        self.assertEqual(self.pos("secrets").returncode, 0)
        git(self.root, "add", "-f", ".env")
        r = self.pos("secrets")
        self.assertEqual(r.returncode, 1)
        self.assertIn(".env: file .env đang nằm trong Git", r.stdout)


class StatusTest(WorktreeCase):
    """status suy trạng thái task từ thẻ + Git, không cần ghi tay."""

    PLAN = CARDS + """- [ ] T-004 · RPT-01 · báo cáo
      Wave:      W2
      Scope:     src/rpt/*
      Phụ thuộc: T-002
"""

    def setUp(self):
        super().setUp()
        self.commit_on_main("docs/plan/M1.md", self.PLAN)

    def group(self, out, title):
        """Các dòng thụt vào ngay dưới tiêu đề nhóm."""
        lines, rows, on = out.splitlines(), [], False
        for line in lines:
            if not line.startswith("    "):
                on = line.strip() == title
            elif on:
                rows.append(line.strip())
        return rows

    def test_groups_before_and_after_merge(self):
        self.pos("task", "T=T-002", "N=map-sales")
        out = self.pos("status").stdout
        self.assertTrue(any(r.startswith("T-002  feat/T-002-map-sales") for r in self.group(out, "Đang làm")), out)
        ready = self.group(out, "Sẵn sàng")
        self.assertTrue(any(r.startswith("T-003") for r in ready), out)
        self.assertTrue(any(r.startswith("T-001") for r in ready), "thẻ T-001 trong STATUS.md: " + out)
        self.assertTrue(any(r.startswith("T-004  (chờ T-002)") for r in self.group(out, "Chờ phụ thuộc")), out)

        # PR của T-002 được merge squash: main có commit mang [T-002]
        self.write("src/map/a.py", "x = 1")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", "feat(MAP-01): add map [T-002] (#7)")
        git(self.root, "push", "-q", "origin", "main")
        out = self.pos("status").stdout
        done = self.group(out, "Xong")
        self.assertTrue(any(r.startswith("T-002") and "chưa dọn feat/T-002-map-sales" in r for r in done), out)
        self.assertTrue(any(r.startswith("T-004") for r in self.group(out, "Sẵn sàng")), out)

    def test_branch_with_task_number_but_no_card_is_reported(self):
        git(self.root, "branch", "feat/T-050-ghost")
        out = self.pos("status").stdout
        self.assertIn("T-050  feat/T-050-ghost", self.group(out, "Branch mang số T nhưng không có thẻ"), out)

    def test_ticked_card_counts_as_done(self):
        self.commit_on_main("docs/plan/M1.md", self.PLAN.replace("- [ ] T-002", "- [x] T-002"))
        out = self.pos("status").stdout
        self.assertTrue(any(r.startswith("T-002") for r in self.group(out, "Xong")), out)


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

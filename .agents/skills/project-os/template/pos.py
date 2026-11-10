#!/usr/bin/env python3
"""Project OS runner: một file Python thay Make + Bash. Chạy được trên Windows, macOS, Linux.
Chỉ dùng thư viện chuẩn Python 3.8+. (Đặt tên pos.py, không phải os.py, để khỏi che module `os` của Python.)

  python pos.py setup | run | lint | test [F=MAP-07] [L=api] | features [--sync] | secrets | check
  python pos.py check HOOK=1                           hook pre-push gọi: bỏ bước test nếu HOOK_TESTS = False
  python pos.py task T=T-043 N=map-sales [TYPE=fix]    tạo worktree + branch từ main mới nhất
  python pos.py done T=T-043                           dọn sau khi PR đã merge
  python pos.py drop T=T-043 [CONFIRM=T-043]           huỷ task chưa merge (phải hỏi PO)
  python pos.py status                                 trạng thái task suy từ thẻ + Git: đang làm, sẵn sàng, chờ, xong
  python pos.py find <lời của PO>                      tìm mã theo lời thường (không cần dấu) trong sổ mã, DECISIONS, thẻ
  python pos.py wt                                     liệt kê worktree
  python pos.py wt-clean [APPLY=1]                     tìm worktree mồ côi (đã merge); chỉ liệt kê, APPLY=1 mới dọn
  python pos.py pr [T=T-043] [--no-check]              sinh sẵn khung báo cáo PR từ git diff + kết quả check
  python pos.py scope                                  kiểm file đã sửa có nằm trong "Scope" của thẻ task (luật cứng 8);
                                                       chặn xoá file test hoặc làm giảm số test so với main;
                                                       không có thẻ thì chỉ qua khi đủ nhỏ để là Lane Fast
  python pos.py lane                                   Lane do máy xác định cho thay đổi hiện tại: Fast | Normal | Strict
  python pos.py review-check BODY=<file mô tả PR>      PR Lane Strict phải có "Kết luận Reviewer": Đạt (luật cứng 7)
  python pos.py plan-check                             kiểm plan: cùng Wave không trùng "Scope", Phụ thuộc chỉ trỏ về Wave trước
  python pos.py sos                                    cứu hộ khi bị kẹt: sao lưu vào branch salvage/sos-*, khám bệnh (chỉ đọc), rồi gửi P-SOS cho AI

(Linux/macOS thường chỉ có lệnh `python3`: dùng `python3 pos.py …`.)
"""
import fnmatch
import os
import pathlib
import re
import subprocess
import sys

# ── Cấu hình dự án: điền lệnh thật vào đây (Ngày 0).
# LINT_CMD, TEST_CMD để trống = `check` báo lỗi (tránh xanh giả). Chưa có lint/test thật (trước T-001)
# thì ghi "none": `check` qua nhưng in cảnh báo mỗi lần chạy. SETUP_CMD, RUN_CMD để trống chỉ in thông báo.
# {F} = mã cần test (MAP-07 hoặc MAP), {L} = tầng (unit | api | e2e).
# {F:text %} chỉ xuất hiện khi có F, % được thay bằng giá trị. Tương tự {L:…}.
# Ví dụ:
#   Python:     TEST_CMD = 'pytest {L:tests/%} {F:-k "%"}'
#   Rust:       TEST_CMD = 'cargo test {F:%}'          (mã Rust dạng map_07: tự chỉnh)
#   TypeScript: TEST_CMD = 'npx vitest run {F:-t "%"}'
SETUP_CMD = ""
RUN_CMD = ""
LINT_CMD = ""
TEST_CMD = ""
# Hook pre-push có chạy TEST_CMD không. Bộ test chậm (vài phút) thì đặt False: hook chỉ kiểm sổ mã, quét khoá, lint và Scope.
# Bộ test đầy đủ vẫn phải chạy ở CI (cổng cuối của luật cứng 3): chỉ đặt False khi dự án có CI chạy `python pos.py check`.
HOOK_TESTS = True

WT_DIR = "../wt"  # worktree đặt ngoài repo
BASE = "main"
TYPES = ("feat", "fix", "refactor", "test", "docs", "chore")

# Máy chặn: các file thực thi luật cứng. Luôn là Hot file; PR không có thẻ không được đụng tới.
GUARD = ("pos.py", "scripts/features.py", ".githooks/", ".github/")
# PR không có thẻ task (Lane Fast) chỉ qua `scope` khi nhỏ hơn hai ngưỡng này; tài liệu (docs/, *.md) không tính.
FAST_MAX_FILES = 5    # số file code được sửa
FAST_MAX_LINES = 100  # tổng dòng code thêm + xoá

# PROJECT_OS_ROOT: CI chạy bản pos.py lấy từ main (đặt ngoài repo) trên mã nguồn của PR.
ROOT = pathlib.Path(os.environ.get("PROJECT_OS_ROOT") or pathlib.Path(__file__).resolve().parent).resolve()
PY = sys.executable or "python3"


def say(msg):
    print(msg, flush=True)


def die(msg, code=1):
    say(msg)
    sys.exit(code)


def git(*args, cwd=None):
    # core.quotepath=false: git in đúng đường dẫn có dấu, không bọc ngoặc kép và mã thoát (nếu không, tên file tiếng Việt
    # không bao giờ khớp Scope và lọt khỏi phép bảo toàn test).
    r = subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=cwd or ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def expand(cmd, opts):
    """Thay {F}, {L}, {F:text %}, {L:text %} trong lệnh."""
    def sub(m):
        val = opts.get(m.group(1), "")
        if not val:
            return ""
        return m.group(2).replace("%", val) if m.group(2) is not None else val
    return re.sub(r"\{([FL])(?::([^}]*))?\}", sub, cmd).strip()


REQUIRED = ("lint", "test")  # check cần hai lệnh này; trống = lỗi


def run_cmd(name, cmd, opts):
    var = f"{name.upper()}_CMD"
    if cmd.strip().lower() == "none":
        say(f"{name}: CẢNH BÁO: {var} = \"none\", chưa có {name} thật; điền lệnh thật sau T-001")
        return 0
    if not cmd:
        if name in REQUIRED:
            say(f"{name}: LỖI: chưa cấu hình {var} trong pos.py (ghi lệnh thật, hoặc \"none\" nếu chưa có {name})")
            return 1
        say(f"{name}: chưa cấu hình {var} trong pos.py")
        return 0
    full = expand(cmd, opts)
    say(f"$ {full}")
    return subprocess.run(full, shell=True, cwd=ROOT).returncode


# ── Lệnh cơ bản ────────────────────────────────────────────────────────────

def cmd_setup(opts, _):
    code, _, _ = git("rev-parse", "--git-dir")
    if code == 0:
        git("config", "core.hooksPath", ".githooks")
        say("Đã bật hook trong .githooks")
    else:
        say("Chưa phải repo git: chạy git init rồi python pos.py setup lại")
    return run_cmd("setup", SETUP_CMD, opts)


def cmd_run(opts, _):
    return run_cmd("run", RUN_CMD, opts)


def cmd_lint(opts, _):
    return run_cmd("lint", LINT_CMD, opts)


def cmd_test(opts, _):
    return run_cmd("test", TEST_CMD, opts)


def cmd_features(opts, extra):
    script = ROOT / "scripts" / "features.py"
    if not script.exists():
        script = ROOT / "scripts" / "feature-lint.py"  # tên cũ trước v1.5
    return subprocess.run([PY, str(script), *extra], cwd=ROOT).returncode


SECRET_RES = [(name, re.compile(rx)) for name, rx in (
    ("khoá riêng (private key)", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("AWS access key", r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("GitHub token", r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})"),
    ("Slack token", r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    ("Stripe live key", r"\b[sr]k_live_[A-Za-z0-9]{16,}"),
    ("Google API key", r"\bAIza[0-9A-Za-z_-]{35}\b"),
    ("khoá API dạng sk-", r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{32,}"),
)]
SECRET_ALLOW = "project-os: allow-secret"  # ghi trên cùng dòng để bỏ qua một giá trị giả (dữ liệu test)
ENV_OK = (".env.example", ".env.sample", ".env.template")


def cmd_secrets(opts, _):
    """Luật cứng 2: quét khoá bí mật trong file Git theo dõi và file mới chưa bị .gitignore bỏ qua.
    Chỉ nhận các dạng khoá phổ biến, không quét lịch sử; không in giá trị khoá ra màn hình."""
    if git("rev-parse", "--git-dir")[0] != 0:
        say("secrets: chưa phải repo git: bỏ qua")
        return 0
    errs = []
    for f in git("ls-files")[1].splitlines():
        name = f.rsplit("/", 1)[-1]
        if (name == ".env" or name.startswith(".env.")) and name not in ENV_OK:
            errs.append(f"{f}: file .env đang nằm trong Git (gỡ: git rm --cached {f})")
    for f in git("ls-files", "-co", "--exclude-standard")[1].splitlines():
        p = ROOT / f
        try:
            if not p.is_file() or p.stat().st_size > 1_000_000:
                continue
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if SECRET_ALLOW in line:
                continue
            for kind, rx in SECRET_RES:
                if rx.search(line):
                    errs.append(f"{f}:{n}: {kind}")
                    break
    if errs:
        say("secrets: có khoá bí mật (luật cứng 2):")
        for e in errs:
            say("    " + e)
        say("Gỡ khỏi file, đưa vào .env, và coi khoá đó đã lộ: thu hồi, cấp khoá mới.")
        return 1
    say("secrets: không thấy khoá bí mật")
    return 0


def cmd_check(opts, _):
    """HOOK=1 là hook pre-push gọi: bỏ bước test khi dự án đặt HOOK_TESTS = False (CI chạy bộ test đầy đủ)."""
    skip_test = opts.get("HOOK") == "1" and not HOOK_TESTS
    for fn in (cmd_features, cmd_secrets, cmd_lint, cmd_test):
        if fn is cmd_test and skip_test:
            say("test: bỏ qua ở hook (HOOK_TESTS = False); CI chạy bộ test đầy đủ")
            continue
        rc = fn(opts, [])
        if rc:
            return rc
    say("check: qua phần nhanh, chưa chạy test" if skip_test else "check: qua")
    return 0


# ── Worktree (1 Task = 1 Branch = 1 Worktree = 1 PR) ───────────────────────

def need_t(opts):
    t = opts.get("T", "")
    if not t:
        die("Thiếu T=<mã task>, ví dụ T=T-043 (Lane Fast: T=MAP-02)")
    if not re.fullmatch(r"T-\d{3,}|[A-Z]+-\d{2,}", t):
        die(f"T sai dạng: '{t}'. Đúng: T-043 hoặc MAP-02")
    return t


def wt_path(t):
    return (ROOT / WT_DIR / t).resolve()


def cmd_task(opts, _):
    t = need_t(opts)
    n = opts.get("N", "")
    typ = opts.get("TYPE", "feat")
    if not n:
        die("Thiếu N=<short-name>, ví dụ N=map-sales")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", n):
        die(f"N là slug kebab-case ASCII (chữ thường, số, gạch ngang): '{n}'")
    if typ not in TYPES:
        die("TYPE phải là một trong: " + " ".join(TYPES))
    path = wt_path(t)
    if path.exists():
        die(f"Đã có worktree {path}. Xem: python pos.py wt")
    br = f"{typ}/{t}-{n}"
    if git("show-ref", "--verify", "--quiet", f"refs/heads/{br}")[0] == 0:
        die(f"Branch {br} đã có")
    git("fetch", "--quiet", "origin", BASE)
    code, _, err = git("worktree", "add", "--quiet", str(path), "-b", br, f"origin/{BASE}")
    if code:
        die(f"Không tạo được worktree: {err}")
    git("branch", "--quiet", "--unset-upstream", cwd=path)
    say(f"Đã tạo: {path}  ·  branch {br}  ·  từ origin/{BASE}")
    say(f"Tiếp: cd {path}")
    return 0


def pr_merged(br):
    try:
        r = subprocess.run(["gh", "pr", "view", br, "--json", "state", "-q", ".state"],
                           capture_output=True, text=True, cwd=ROOT)
        if r.returncode == 0 and r.stdout.strip() == "MERGED":
            return True
    except OSError:
        pass  # không có gh
    return content_merged(br)


def content_merged(br):
    """Không có gh: nhận ra merge squash bằng nội dung, không bằng tên. Gộp thử branch vào origin/BASE
    (merge-tree, không đụng working tree); ra đúng cây của origin/BASE thì mọi thay đổi của branch
    đã có trên BASE, xoá branch không mất gì. Git cũ (< 2.38) hoặc có xung đột: trả False (an toàn)."""
    code, out, _ = git("merge-tree", "--write-tree", f"origin/{BASE}", br)
    if code != 0 or not out:
        return False
    return out.splitlines()[0] == git("rev-parse", f"origin/{BASE}^{{tree}}")[1]


def cmd_done(opts, _):
    t = need_t(opts)
    path = wt_path(t)
    if not path.is_dir():
        die(f"Không có worktree {path}. Xem: python pos.py wt")
    _, br, _ = git("rev-parse", "--abbrev-ref", "HEAD", cwd=path)
    git("fetch", "--quiet", "origin", BASE)
    if pr_merged(br):
        how = "PR đã merge (gh)"
    elif git("merge-base", "--is-ancestor", br, f"origin/{BASE}")[0] == 0:
        how = f"branch đã nằm trong origin/{BASE}"
    else:
        die(f"Branch {br} chưa merge vào {BASE}. Merge PR trước, hoặc huỷ: python pos.py drop T={t}\n"
            "(Merge squash: không có gh thì chỉ nhận ra khi nội dung branch đã nằm nguyên trên "
            f"origin/{BASE}; cần git 2.38+.)")
    if git("worktree", "remove", str(path))[0]:
        die("Worktree còn thay đổi chưa commit, không dọn.")
    git("branch", "--quiet", "-D", br)
    git("worktree", "prune")
    say(f"Đã dọn {t}: xoá worktree + branch {br} ({how})")
    return 0


def cmd_drop(opts, _):
    t = need_t(opts)
    path = wt_path(t)
    if not path.is_dir():
        die(f"Không có worktree {path}. Xem: python pos.py wt")
    _, br, _ = git("rev-parse", "--abbrev-ref", "HEAD", cwd=path)
    if opts.get("CONFIRM") != t:
        say(f"Huỷ {t} sẽ MẤT VĨNH VIỄN:")
        say(f"  Commit chưa merge trên {br}:")
        for line in git("log", "--oneline", f"origin/{BASE}..{br}")[1].splitlines():
            say("    " + line)
        say("  Thay đổi chưa commit:")
        for line in git("status", "--short", cwd=path)[1].splitlines():
            say("    " + line)
        die(f"PO đồng ý thì chạy lại: python pos.py drop T={t} CONFIRM={t}")
    git("worktree", "remove", "--force", str(path))
    git("branch", "--quiet", "-D", br)
    git("worktree", "prune")
    say(f"Đã huỷ {t}: xoá worktree + branch {br}")
    return 0


def cmd_wt(opts, _):
    say(git("worktree", "list")[1])
    return 0


def cmd_wt_clean(opts, _):
    """Worktree trong WT_DIR mà branch đã merge vào origin/BASE (hoặc PR đã MERGED) nhưng chưa ai dọn."""
    git("fetch", "--quiet", "origin", BASE)
    wt_name = pathlib.Path(WT_DIR).name
    apply, found = opts.get("APPLY") == "1", 0
    for line in git("worktree", "list", "--porcelain")[1].splitlines():
        if not line.startswith("worktree "):
            continue
        d = pathlib.Path(line[9:])
        if d.parent.name != wt_name or d == ROOT:
            continue
        rc, br, _ = git("rev-parse", "--abbrev-ref", "HEAD", cwd=d)
        if rc or br == "HEAD":
            continue
        if git("merge-base", "--is-ancestor", br, f"origin/{BASE}")[0] != 0 and not pr_merged(br):
            continue
        if git("status", "--porcelain", cwd=d)[1]:
            say(f"Bỏ qua {d}: còn thay đổi chưa commit")
            continue
        found += 1
        if not apply:
            say(f"Mồ côi (đã merge): {d} ({br})")
        elif git("worktree", "remove", str(d))[0] == 0:
            git("branch", "--quiet", "-D", br)
            say(f"Đã dọn {d} ({br})")
    git("worktree", "prune")
    if not found:
        say("Không có worktree mồ côi.")
    elif not apply:
        say("Dọn thật: python pos.py wt-clean APPLY=1")
    return 0


# ── Cứu hộ (SOS) ───────────────────────────────────────────────────────────

SALVAGE_PREFIX = "salvage/sos-"


def cmd_sos(opts, _):
    """Chỉ đọc + tạo MỘT branch sao lưu. Không đổi branch hiện tại, không reset, không xoá."""
    import datetime
    if git("rev-parse", "--git-dir")[0] != 0:
        die("Chưa phải repo git, không có gì để cứu hộ.")
    say("=== SOS · CỨU HỘ DỰ ÁN (không mất code: mọi thứ được sao lưu trước) ===")
    _, cur, _ = git("rev-parse", "--abbrev-ref", "HEAD")
    dirty = git("status", "--porcelain")[1]
    snap = git("rev-parse", "HEAD")[1]
    if dirty:
        # Chụp cả file sửa lẫn file mới chưa theo dõi, bằng index tạm: không đụng index/working tree thật.
        import tempfile
        tmpdir = tempfile.TemporaryDirectory()
        tmp = os.path.join(tmpdir.name, "index")
        env = dict(os.environ, GIT_INDEX_FILE=tmp)
        run = lambda *a: subprocess.run(["git", *a], cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if run("read-tree", "HEAD").returncode == 0 and run("add", "-A").returncode == 0:
            tree = run("write-tree").stdout.strip()
            c = run("commit-tree", tree, "-p", snap, "-m", "SOS: sao lưu thay đổi chưa commit")
            if c.returncode == 0 and c.stdout.strip():
                snap = c.stdout.strip()
            else:
                die("Không chụp được thay đổi chưa commit; dừng, chưa làm gì khác. Tự sao lưu: git stash -u")
        else:
            die("Không chụp được thay đổi chưa commit; dừng, chưa làm gì khác. Tự sao lưu: git stash -u")
        try:
            tmpdir.cleanup()
        except OSError:
            pass  # Windows: antivirus/indexer còn giữ file index tạm; để sót một file trong %TEMP%, không chặn cứu hộ
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    name = SALVAGE_PREFIX + stamp
    n = 1
    while git("show-ref", "--verify", "--quiet", f"refs/heads/{name}")[0] == 0:
        n += 1
        name = f"{SALVAGE_PREFIX}{stamp}-{n}"
    if git("branch", name, snap)[0] != 0:
        die("Không tạo được branch sao lưu; dừng, chưa làm gì khác.")
    say(f"[1/4] Đã sao lưu vào branch {name} (branch hiện tại '{cur}' giữ nguyên).")
    say(f"      Khôi phục khi cần: git checkout {name}")
    say("[2/4] Thay đổi chưa commit:" + ("" if dirty else " không có"))
    for line in dirty.splitlines()[:15]:
        say("      " + line)
    if len(dirty.splitlines()) > 15:
        say(f"      … và {len(dirty.splitlines()) - 15} dòng nữa")
    say("[3/4] Worktree:")
    say("      " + git("worktree", "list")[1].replace("\n", "\n      "))
    cmd_wt_clean({}, [])
    cmd_status({}, [])
    st = ROOT / "STATUS.md"
    if st.is_file():
        say("      STATUS.md: mục Đang giữ / Đang chặn:")
        keep = False
        for line in st.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("## "):
                keep = line[3:].strip() in ("Đang giữ", "Đang chặn")
            elif keep and line.strip():
                say("        " + line)
    say("[4/4] Kiểm kỹ thuật (python pos.py check):")
    r = subprocess.run([PY, str(ROOT / "pos.py"), "check"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout + r.stderr).strip().splitlines()
    for line in out[-30:]:
        say("      " + line)
    say("      => " + ("qua" if r.returncode == 0 else "CÓ LỖI (xem trên)"))
    say("-" * 56)
    say("Gửi prompt P-SOS cho AI để nhận 2 phương án (A: cứu task, B: huỷ và về main xanh).")
    return 0


# ── Báo cáo PR tự sinh ─────────────────────────────────────────────────────

def cmd_pr(opts, extra):
    """In khung báo cáo PR điền sẵn từ git: file đổi, commit, mã feature, kết quả check."""
    base = f"origin/{BASE}"
    git("fetch", "--quiet", "origin", BASE)
    if git("rev-parse", "--verify", "--quiet", base)[0]:
        die(f"pr: không thấy {base}")
    br = git("rev-parse", "--abbrev-ref", "HEAD")[1]
    m = re.match(r"(?P<type>\w+)/(?P<task>T-\d{3,}|[A-Z]+-\d{2,})-", br)
    kind = m["type"] if m else "feat"
    t = opts.get("T") or (m["task"] if m and m["task"].startswith("T-") else "")
    stat = git("diff", "--stat", f"{base}...HEAD")[1]
    commits = git("log", "--oneline", f"{base}..HEAD")[1]
    diff = git("diff", f"{base}...HEAD", "-U0")[1]
    feats = sorted(set(re.findall(r"^\+.*?\b([A-Z]{2,6}-\d{2,})\b", diff, re.M)))
    if "--no-check" in extra:
        check = "chưa chạy (--no-check)"
    else:
        r = subprocess.run([PY, str(ROOT / "pos.py"), "check"], cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-15:])
        check = "`check`: qua" if r.returncode == 0 else f"`check`: LỖI\n```\n{tail}\n```"
    suffix = f" [{t}]" if t else ""
    say(f"Tiêu đề gợi ý: {kind}({','.join(feats[:2]) or '<MÃ>'}): <việc>{suffix}\n")
    say(f"**Mã · Task · Lane:** {', '.join(named(f, feature_names()) for f in feats) or '<MÃ>'} · {t or '—'} · <Fast | Normal | Strict>\n")
    if t:
        say(f"Closes #{int(t[2:])}  <!-- chỉ giữ nếu T-nnn trùng số GitHub Issue (PROCESS.md mục 7) -->\n")
    say("**Tóm tắt cho PO** (lời thường, không dùng mã trần):\n- Người dùng thấy gì thay đổi:\n- Rủi ro nếu sai:\n"
        "- 3 bước tự bấm thử:\n- Khuyến nghị:\n")
    say("**Đã làm:**\n\n**Scope thực tế:** khớp thẻ / thêm …, vì …\n")
    say(f"**File thay đổi:**\n```\n{stat or '(không khác ' + base + ')'}\n```\n")
    say(f"**Commit:**\n```\n{commits or '(chưa có commit)'}\n```\n")
    say(f"**Test đã chạy:** {check}\n")
    say("**Khác mặc định (nếu có, lý do):**\n\n**Rủi ro:**\n\n**Ghi chú bàn giao:**\n\n"
        "**Kết luận Reviewer** (chỉ PR Lane Strict; do một phiên AI khác viết theo P-07, không phải phiên đã làm task):\n"
        "- Kết luận: <Đạt | Trả lại>\n- Đã thử gì, tìm ra gì:\n- Khuyến nghị cho PO:\n\n"
        "**Việc cần PO chuyển cho Orchestrator** (viết sẵn để dán nguyên văn; không có thì ghi \"không\"):")
    return 0


# ── Máy chặn Scope của thẻ (luật cứng 8) ───────────────────────────────────
# Thẻ task nằm trong docs/plan/*.md, đọc từ origin/<BASE> (không phải từ branch đang làm),
# để Builder không tự mở rộng Scope trong chính PR của mình. Muốn mở rộng: Orchestrator sửa thẻ
# trên main trước. Mặc định là chặn: branch không có số T hoặc không có thẻ chỉ qua khi đủ điều kiện Lane Fast
# (không chạm máy chặn, Hot file, Restricted zone; dưới FAST_MAX_FILES và FAST_MAX_LINES); thẻ thiếu `Scope:` là lỗi.
# Nhận cả tên trường cũ (`Phạm vi:`, `Sóng:`) để plan viết trước v1.4 vẫn chạy.

def find_card(t):
    """Trả về danh sách mẫu đường dẫn của dòng `Scope:` trong thẻ task t, hoặc None nếu không có thẻ."""
    ref = base_ref()
    if ref is None:
        return None
    # Dự án nhỏ không có docs/plan/: thẻ đặt trong STATUS.md (mục "Tiếp theo"), cùng mẫu.
    code, names, _ = git("ls-tree", "-r", "--name-only", ref, "--", "docs/plan", "STATUS.md")
    if code:
        return None
    head = re.compile(rf"^\s*-\s*\[[ xX]\]\s*{re.escape(t)}\b")
    for name in names.splitlines():
        if not name.endswith(".md"):
            continue
        lines = git("show", f"{ref}:{name}")[1].splitlines()
        for i, line in enumerate(lines):
            if not head.match(line):
                continue
            for nxt in lines[i + 1:]:
                if not nxt.strip() or re.match(r"^\s*-\s*\[", nxt):
                    break
                v = field(nxt, SCOPE)
                if v:
                    return [p for p in re.split(r"[,\s]+", v) if p]
            return []
    return None


def path_match(parts, pat):
    """Đường dẫn (đã tách theo `/`) có khớp mẫu không. Cùng ngữ nghĩa với plan-check (`overlaps`):
    `*` ở đoạn giữa chỉ thay một thư mục; đoạn cuối có `*` thì phủ cả thư mục con; `**` thay số thư mục
    bất kỳ; mẫu là thư mục (`src/map`, `src/map/`) thì phủ mọi thứ bên trong."""
    for i, seg in enumerate(pat):
        if seg == "**":
            rest = pat[i + 1:]
            return not rest or any(path_match(parts[j:], rest) for j in range(i, len(parts)))
        if i >= len(parts) or not fnmatch.fnmatchcase(parts[i], seg.replace("**", "*")):
            return False
        if "**" in seg or (i == len(pat) - 1 and "*" in seg):
            return True
    return True


def in_scope(path, patterns):
    parts = path.split("/")
    return any(path_match(parts, segments(p)) for p in patterns)


def base_ref():
    for ref in (f"origin/{BASE}", BASE):
        if git("rev-parse", "--verify", "--quiet", ref)[0] == 0:
            return ref
    return None


def is_doc(path):
    return path.startswith("docs/") or path.lower().endswith(".md")


def protected_paths(ref):
    """Máy chặn + Hot file + Restricted zone, đọc AGENTS.md từ `ref` (main), không từ branch đang làm."""
    code, text, _ = git("show", f"{ref}:AGENTS.md")
    zones = ("## Hot file", "## File nóng", "## Restricted zone", "## Vùng cấm")
    return list(GUARD) + (section_paths(text, zones) if code == 0 else [])


def fast_check(br, base, files):
    """PR không có thẻ: chỉ qua khi đủ nhỏ để là Lane Fast và không chạm đường dẫn được bảo vệ."""
    errs = []
    prot = protected_paths(base)
    for f in files:
        if in_scope(f, prot):
            errs.append(f"{f}: là máy chặn, Hot file hoặc Restricted zone")
    code_files, lines = [f for f in files if not is_doc(f)], 0
    for row in git("diff", "--numstat", "--no-renames", f"{base}...HEAD")[1].splitlines():
        cols = row.split("\t", 2)
        if len(cols) == 3 and not is_doc(cols[2]):
            lines += sum(int(c) for c in cols[:2] if c.isdigit())
    if len(code_files) > FAST_MAX_FILES:
        errs.append(f"sửa {len(code_files)} file code: quá {FAST_MAX_FILES} (FAST_MAX_FILES)")
    if lines > FAST_MAX_LINES:
        errs.append(f"thêm + xoá {lines} dòng code: quá {FAST_MAX_LINES} (FAST_MAX_LINES)")
    if errs:
        say(f"scope: branch '{br}' không có thẻ task nên chỉ được là Lane Fast, nhưng:")
        for e in errs:
            say("    " + e)
        say(f"Luật cứng 8: dừng và báo Orchestrator. Cần thẻ có dòng 'Scope:' trong docs/plan/ (hoặc STATUS.md) "
            f"trên {BASE}, và branch đặt tên <loại>/T-nnn-<tên>.")
        return 1
    say(f"scope: '{br}' không có thẻ, đủ điều kiện Lane Fast ({len(code_files)} file code, {lines} dòng)")
    return 0


# ── Bảo toàn test (luật cứng 8) ─────────────────────────────────────────────
# Một PR không được làm `check` xanh bằng cách bỏ test. So với BASE, ba việc sau bị chặn, trừ khi thẻ của task ghi
# ĐÍCH DANH file đó trong Scope (mẫu có `*` không tính là đích danh):
#   - xoá một file có test, hoặc một file mang tên file test nằm trong thư mục test;
#   - đổi loại một file như vậy (ví dụ thành symlink);
#   - làm giảm số test đếm được trong một file.
# Máy đếm theo dấu hiệu khai báo test của Python, JavaScript/TypeScript, Rust, Go, Java. Nó không phát hiện được việc
# làm yếu một phép kiểm bên trong test, bỏ qua test bằng skip, hay test viết bằng ngôn ngữ khác: phần đó là của Reviewer.

TEST_DIRS = {"tests", "test", "spec", "e2e", "__tests__"}
TEST_NAME = re.compile(r"^test_|_test\.|\.test\.|\.spec\.|_spec\.", re.I)
TEST_DEF = re.compile(r"^\s*(?:async\s+)?def\s+test\w*\s*\(|^\s*(?:it|test)(?:\.\w+)?\s*\(|#\[(?:\w+::)?test\]"
                      r"|^func\s+Test\w*\s*\(|@Test\b", re.M)


def named_like_test(path):
    """File mang tên file test VÀ nằm trong thư mục test: coi là file test kể cả khi không đếm được test nào."""
    parts = path.split("/")
    return bool({p.lower() for p in parts[:-1]} & TEST_DIRS) and bool(TEST_NAME.search(parts[-1]))


def count_tests(ref, path):
    """Số test đếm được trong file tại ref; None nếu không đọc được file."""
    code, text, _ = git("show", f"{ref}:{path}")
    return len(TEST_DEF.findall(text)) if code == 0 else None


def lost_tests(base, patterns):
    """Các chỗ diff base...HEAD làm mất test. patterns: Scope của thẻ, hoặc None khi không có thẻ."""
    named = {"/".join(segments(p)) for p in (patterns or []) if not re.search(r"[*?\[]", p) and not p.endswith("/")}
    start = git("merge-base", base, "HEAD")[1] or base
    errs = []
    for row in git("diff", "--name-status", "--no-renames", f"{base}...HEAD")[1].splitlines():
        status, _, path = row.partition("\t")
        if status[:1] not in "DMT" or path in named:
            continue
        before = count_tests(start, path)
        if before is None:
            errs.append(f"{path}: không đọc được file ở {start[:10]} để đếm test")
        elif status[0] in "DT":
            if before or named_like_test(path):
                errs.append(f"{path}: " + ("xoá file test" if status[0] == "D" else "đổi loại file test (ví dụ thành symlink)"))
        else:
            after = count_tests("HEAD", path)
            if after is None:
                errs.append(f"{path}: không đọc được file ở HEAD để đếm test")
            elif after < before:
                errs.append(f"{path}: số test giảm từ {before} xuống {after}")
    return errs


def cmd_scope(opts, _):
    _, br, _ = git("rev-parse", "--abbrev-ref", "HEAD")
    # CI checkout ở trạng thái detached: truyền tên branch qua PROJECT_OS_BRANCH (nhận cả tên cũ POS_BRANCH)
    ci_br = os.environ.get("PROJECT_OS_BRANCH") or os.environ.get("POS_BRANCH")
    if not ci_br and br == BASE:
        say(f"scope: đang ở {BASE}, không phải branch của task: bỏ qua (luật cứng 1 do khoá {BASE} chặn)")
        return 0
    br = ci_br or br
    base = base_ref()
    if base is None:
        die(f"scope: không thấy origin/{BASE} lẫn {BASE}: không kiểm được")
    if git("cat-file", "-e", f"{base}:pos.py")[0] != 0:
        # Repo đang có code áp Project OS lần đầu: PR Ngày 0 chính là PR đưa máy chặn vào, không thể có thẻ trên BASE trước.
        say(f"scope: {base} chưa có pos.py (dự án chưa qua Ngày 0 trên {BASE}): chưa có máy chặn để bảo vệ, bỏ qua")
        return 0
    code, out, err = git("diff", "--name-only", "--no-renames", f"{base}...HEAD")
    if code:
        die(f"scope: không so được với {base}: {err}")
    files = out.splitlines()
    m = re.match(r"^[a-z]+/(T-\d{3,})-", br)
    patterns = find_card(m.group(1)) if m else None
    lost = lost_tests(base, patterns)
    if lost:
        say("scope: thay đổi này làm mất test (luật cứng 8, bảo toàn test):")
        for e in lost:
            say("    " + e)
        say("Test chỉ được xoá hoặc giảm khi thẻ của task ghi đích danh file đó trong Scope (mẫu có * không tính). "
            "Dừng và báo Orchestrator.")
        return 1
    if patterns is None:  # không số T hoặc không có thẻ: mặc định là chặn, chỉ qua khi đủ điều kiện Lane Fast
        return fast_check(br, base, files)
    t = m.group(1)
    if not patterns:
        say(f"scope: thẻ {t} chưa có dòng 'Scope:'. Orchestrator ghi Scope vào thẻ trên {BASE}, rồi push lại.")
        return 1
    outside = [f for f in files if not in_scope(f, patterns)]
    if outside:
        say(f"scope: {t} sửa ngoài Scope của thẻ ({' '.join(patterns)}):")
        for f in outside:
            say("    " + f)
        say("Luật cứng 8: dừng và báo Orchestrator. Được duyệt thì Orchestrator sửa 'Scope' của thẻ trên main, rồi push lại.")
        return 1
    say(f"scope: {t} đúng Scope của thẻ")
    return 0


# ── Kiểm plan theo Wave (PROCESS.md mục 11) ─────────────────────────────────
# Chạy trên docs/plan/*.md trong thư mục làm việc, TRƯỚC khi PO duyệt plan. Bốn lỗi bị chặn:
#   1. hai task cùng Wave có "Scope" (quyền ghi, RW) giao nhau;
#   2. "Phụ thuộc" trỏ tới task cùng Wave hoặc Wave sau;
#   3. "Phụ thuộc" trỏ tới task không có trong plan;
#   4. task thuộc Wave có từ 2 task trở lên mà "Scope" chạm "Hot file" trong AGENTS.md.

def segments(pat):
    # Bỏ "./" ở đầu nhưng giữ dấu chấm của .github/ (lstrip("./") từng xoá mất).
    p = pat.strip("`").replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    p = p.lstrip("/")  # kiểu CODEOWNERS: /src/auth/
    if p.endswith("/"):
        p += "*"
    return p.split("/")


def literal_prefix(seg):
    m = re.search(r"[*?\[]", seg)
    return seg[:m.start()] if m else seg


def seg_overlap(x, y):
    """Hai đoạn đường dẫn có thể cùng khớp một tên không."""
    wx, wy = re.search(r"[*?\[]", x), re.search(r"[*?\[]", y)
    if not wx:
        return fnmatch.fnmatchcase(x, y)
    if not wy:
        return fnmatch.fnmatchcase(y, x)
    px, py = literal_prefix(x), literal_prefix(y)
    return px.startswith(py) or py.startswith(px)


def overlaps(a, b):
    """Hai mẫu đường dẫn có thể cùng chạm một file không. So từng đoạn giữa các dấu `/`:
    `*` ở đoạn giữa chỉ thay một thư mục; đoạn cuối có `*` (hoặc có `**`) thì phủ cả thư mục con.
    Phân vân thì coi là trùng: báo thừa còn hơn để lọt xung đột."""
    A, B = segments(a), segments(b)
    for i in range(max(len(A), len(B))):
        if i >= len(A) or i >= len(B):
            return True  # một bên là thư mục cha của bên kia
        x, y = A[i], B[i]
        if "**" in x or "**" in y:
            return literal_prefix(x).startswith(literal_prefix(y)) or literal_prefix(y).startswith(literal_prefix(x))
        last_wild = (i == len(A) - 1 and "*" in x) or (i == len(B) - 1 and "*" in y)
        if last_wild:
            return seg_overlap(x, y) or literal_prefix(x).startswith(literal_prefix(y)) \
                or literal_prefix(y).startswith(literal_prefix(x))
        if not seg_overlap(x, y):
            return False
    return True


WAVE = "Wave|Sóng"
SCOPE = "Scope|Phạm vi"


def field(line, name):
    """Giá trị của trường `name:` trong một dòng thẻ; `name` là regex (nhận cả tên cũ)."""
    m = re.search(rf"(?:{name}):\s*(.*?)(?:\s{{2,}}\S[^:]*:|$)", line)
    return m.group(1).strip() if m else None


def parse_cards(files=None):
    cards = []
    head = re.compile(r"^\s*-\s*\[([ xX])\]\s*(T-\d{3,})\b(.*)")
    if files is None:
        files = sorted((ROOT / "docs" / "plan").glob("*.md"))
    for f in files:
        lines = f.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            m = head.match(line)
            if not m:
                continue
            c = {"t": m.group(2), "title": m.group(3).strip(" ·"), "ticked": m.group(1) != " ",
                 "file": f.name, "wave": None, "rw": [], "deps": []}
            for nxt in lines[i + 1:]:
                if not nxt.strip() or re.match(r"^\s*-\s*\[", nxt):
                    break
                w = field(nxt, WAVE)
                if w:
                    mw = re.match(r"W(\d+)", w)
                    c["wave"] = int(mw.group(1)) if mw else None
                rw = field(nxt, SCOPE)
                if rw:
                    c["rw"] = [x for x in re.split(r"[,\s]+", rw) if x]
                d = field(nxt, "Phụ thuộc")
                if d:
                    c["deps"] = re.findall(r"T-\d{3,}", d)
                if field(nxt, "Xong khi"):
                    c["done_when"] = True
            cards.append(c)
    return cards


def section_paths(text, heads):
    """Mẫu đường dẫn ghi dưới các tiêu đề `heads` của AGENTS.md; bỏ dòng mẫu còn {{…}}."""
    out, on = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            on = line.startswith(heads)
        elif on and "{{" not in line:
            out += [x for x in re.split(r"[,\s]+", line.replace("`", " ").strip()) if x]
    return out


def hot_files():
    f = ROOT / "AGENTS.md"
    text = f.read_text(encoding="utf-8") if f.exists() else ""
    return list(GUARD) + section_paths(text, ("## Hot file", "## File nóng"))


def cmd_plan_check(opts, _):
    all_cards = parse_cards()
    all_ids = {x["t"] for x in all_cards}
    cards = [c for c in all_cards if c["wave"] is not None or c["rw"]]
    if not cards:
        say("plan-check: không thấy thẻ nào trong docs/plan/: bỏ qua")
        return 0
    errs = []
    by_id = {c["t"]: c for c in cards}
    waves = {}
    for c in cards:
        if c["wave"] is None:
            errs.append(f"{c['t']}: thiếu dòng 'Wave: W<n>'")
            continue
        if not c["rw"]:
            errs.append(f"{c['t']}: thiếu 'Scope' (quyền ghi)")
        waves.setdefault(c["wave"], []).append(c)
    hot = hot_files()
    for w, group in sorted(waves.items()):
        if len(group) > 5:
            errs.append(f"W{w} có {len(group)} task: quá 5, review sẽ nghẽn; tách thành hai Wave")
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                hit = [(x, y) for x in a["rw"] for y in b["rw"] if overlaps(x, y)]
                if hit:
                    errs.append(f"W{w}: {a['t']} và {b['t']} trùng Scope ({hit[0][0]} ~ {hit[0][1]})")
            if len(group) >= 2:
                for x in a["rw"]:
                    for h in hot:
                        if overlaps(x, h):
                            errs.append(f"W{w}: {a['t']} ghi vào Hot file ({x} ~ {h}); chuyển việc nối dây sang Wave cuối")
                            break
    for c in cards:
        for d in c["deps"]:
            dep = by_id.get(d)
            if dep is None and d not in all_ids:
                errs.append(f"{c['t']} phụ thuộc {d}: không có thẻ này trong docs/plan/ (gõ nhầm số?)")
                continue
            if dep and dep["wave"] is not None and c["wave"] is not None and dep["wave"] >= c["wave"]:
                errs.append(f"{c['t']} (W{c['wave']}) phụ thuộc {d} (W{dep['wave']}): phải trỏ về Wave trước")
    for c in cards:
        if not c.get("done_when"):  # không chặn: thẻ cũ vẫn chạy, nhưng PO không tự nghiệm thu được
            say(f"    cảnh báo  {c['t']}: thiếu 'Xong khi' (một hành vi PO tự quan sát được + một lệnh kiểm)")
    if errs:
        say("plan-check: plan chưa đạt:")
        for e in errs:
            say("    " + e)
        return 1
    say(f"plan-check: qua ({len(cards)} task, {len(waves)} Wave, không trùng Scope)")
    return 0


# ── Lớp PO: tra mã bằng lời thường (PROCESS.md mục 14) ─────────────────────

def fold(s):
    """Chữ thường, bỏ dấu tiếng Việt: PO gõ "ban do" vẫn tìm ra "Bản đồ"."""
    import unicodedata
    s = unicodedata.normalize("NFD", s.lower().replace("đ", "d"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def table_rows(path):
    """Mỗi dòng dữ liệu của các bảng markdown trong file, dạng {tiêu đề cột: ô}."""
    if not path.is_file():
        return
    head = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("|"):
            head = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if head is None:
            head = cells
        elif not all(set(c) <= set("-: ") for c in cells):
            yield dict(zip(head, cells))


FEATURE_CODE = re.compile(r"\b[A-Z]{2,6}-\d{2,}\b")


def feature_names():
    """{mã: tên gọi} từ cột "Tên gọi" của sổ mã."""
    rows = table_rows(ROOT / "docs" / "product" / "FEATURES.md")
    return {r["Mã"]: r["Tên gọi"] for r in rows
            if FEATURE_CODE.fullmatch(r.get("Mã", "")) and r.get("Tên gọi", "").strip("—- ") and "{{" not in r["Tên gọi"]}


def named(text, names):
    """Đổi mã trần thành "Tên gọi (MÃ)" để PO đọc được."""
    return FEATURE_CODE.sub(lambda m: f"{names[m.group()]} ({m.group()})" if m.group() in names else m.group(), text)


def all_cards():
    """Thẻ ở docs/plan/*.md rồi STATUS.md; trùng số T thì lấy thẻ gặp trước (plan thắng STATUS)."""
    files = sorted((ROOT / "docs" / "plan").glob("*.md"))
    if (ROOT / "STATUS.md").is_file():
        files.append(ROOT / "STATUS.md")
    seen, out = set(), []
    for c in parse_cards(files):
        if c["t"] not in seen:
            seen.add(c["t"])
            out.append(c)
    return out


def cmd_find(opts, extra):
    words = fold(" ".join(extra)).split()
    if not words:
        die("Thiếu lời cần tìm, ví dụ: python pos.py find bản đồ điểm bán")
    entries = []  # (chữ được ưu tiên, toàn bộ chữ, dòng in ra)
    for r in table_rows(ROOT / "docs" / "product" / "FEATURES.md"):
        code = r.get("Mã", "")
        if not FEATURE_CODE.fullmatch(code):
            continue
        name, what = r.get("Tên gọi", ""), r.get("Hành vi chính", "")
        label = f"{name} — {what}" if name.strip("—- ") else what
        entries.append((f"{name} {code}", f"{name} {what} {code}", f"{label} ({code}) · {list(r.values())[-1]}"))
    for r in table_rows(ROOT / "docs" / "DECISIONS.md"):
        code = r.get("Mã", "")
        if re.fullmatch(r"D\d{2,}|Q-\S+", code) and "{{" not in " ".join(r.values()):
            what = r.get("Quyết định") or r.get("Câu hỏi") or ""
            kind = "quyết định" if code.startswith("D") else "câu hỏi còn mở"
            entries.append((code, " ".join(r.values()), f"{what} ({code}) · {kind}"))
    feats = ROOT / "docs" / "product" / "FEATURES.md"
    if feats.is_file():
        for code, name in re.findall(r"^###\s+([A-Z]{2,6})\s+·\s*(.+)$", feats.read_text(encoding="utf-8", errors="replace"), re.M):
            entries.append((f"{name} {code}", f"{name} {code}", f"{name.strip()} (module {code})", 1))
    names = feature_names()
    for c in all_cards():
        entries.append((c["t"], f"{c['title']} {c['t']}", f"{named(c['title'], names)} ({c['t']}) · thẻ task"))
    hits = []
    for prime, full, label, *tier in entries:  # tier 1 = module: xếp sau feature, quyết định, thẻ
        fp, ff = fold(prime), fold(full)
        if all(w in ff for w in words):
            hits.append((bool(tier), -sum(fp.count(w) * 2 + ff.count(w) for w in words), label))
    query = " ".join(extra)
    if not hits:
        say(f"find: không thấy gì khớp '{query}'.")
        say("Có thể là việc mới: hỏi lại PO bằng lời khác, hoặc thêm một dòng vào sổ mã (trạng thái `dự kiến` hoặc `để sau`).")
        return 0
    hits.sort(key=lambda h: h[:2])
    say(f"find: {len(hits)} kết quả cho '{query}'" + (" (hiện 5 đầu)" if len(hits) > 5 else ""))
    for _, _, label in hits[:5]:
        say("    " + label)
    return 0


# ── Trạng thái task: suy từ thẻ + Git, không ghi tay ───────────────────────
# Thẻ ở docs/plan/*.md và STATUS.md (thư mục làm việc). Xong = main có commit mang [T-nnn] (tiêu đề PR đã
# merge squash) hoặc thẻ đã tick. Đang làm = có branch <loại>/T-nnn-… ở máy hoặc trên origin.

def waiting_on_po():
    """Việc đang chờ PO: câu hỏi Q- còn mở, mục "Đang chặn" của STATUS, PR đang mở cần approve (qua gh)."""
    import json
    out = []
    for r in table_rows(ROOT / "docs" / "DECISIONS.md"):
        who = fold(r.get("Chờ ai", ""))
        if r.get("Mã", "").startswith("Q-") and re.search(r"\bpo\b|product owner|chu du an", who):
            options = next((v for k, v in r.items() if k.startswith("Lựa chọn") and v.strip("—- ")), "")
            out.append(f"Cần quyết: {r.get('Câu hỏi', '')} ({r['Mã']})" + (f" · lựa chọn: {options}" if options else ""))
    st, on = ROOT / "STATUS.md", False
    if st.is_file():
        for line in st.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("## "):
                on = line[3:].strip() == "Đang chặn"
            elif on and line.strip() and not line.strip().startswith("("):
                out.append("Đang chặn: " + line.strip().lstrip("- "))
    try:
        r = subprocess.run(["gh", "pr", "list", "--state", "open", "--json", "number,title,reviewDecision"],
                           cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20)
        prs = json.loads(r.stdout) if r.returncode == 0 else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        prs = None
    if prs is None:
        out.append("(không hỏi được GitHub qua gh: chưa liệt kê PR cần approve)")
    else:
        out += [f"Cần approve: PR #{p['number']} · {p['title']}" for p in prs if p.get("reviewDecision") == "REVIEW_REQUIRED"]
    return out


def cmd_status(opts, _):
    cards = all_cards()
    names = feature_names()
    for c in cards:
        c["title"] = named(c["title"], names)
    base = base_ref()
    merged = set(re.findall(r"\[(T-\d{3,})\]", git("log", base, "--format=%s")[1])) if base else set()
    branches = {}
    for ref in git("for-each-ref", "--format=%(refname:short)", "refs/heads", "refs/remotes/origin")[1].splitlines():
        name = ref[len("origin/"):] if ref.startswith("origin/") else ref
        m = re.match(r"^[a-z]+/(T-\d{3,})-", name)
        if m:
            branches.setdefault(m.group(1), name)
    done = merged | {c["t"] for c in cards if c["ticked"]}
    groups = {"Đang làm": [], "Sẵn sàng": [], "Chờ phụ thuộc": [], "Xong": []}
    for c in cards:
        t, br = c["t"], branches.get(c["t"])
        wait = [d for d in c["deps"] if d not in done]
        if t in done:
            groups["Xong"].append(f"{t}  {c['title']}" + (f"  (chưa dọn {br}: python pos.py done T={t})" if br else ""))
        elif br:
            groups["Đang làm"].append(f"{t}  {br}  {c['title']}")
        elif wait:
            groups["Chờ phụ thuộc"].append(f"{t}  (chờ {', '.join(wait)})  {c['title']}")
        else:
            groups["Sẵn sàng"].append(f"{t}  {c['title']}")
    known = {c["t"] for c in cards}
    stray = [f"{t}  {br}" for t, br in sorted(branches.items()) if t not in known and t not in merged]
    waiting = waiting_on_po()
    say(f"status: {len(cards)} thẻ · " + " · ".join(f"{k.lower()} {len(v)}" for k, v in groups.items())
        + f" · chờ PO {sum(1 for w in waiting if not w.startswith('('))}")
    for title, rows in [("Chờ PO", waiting)] + list(groups.items()) + [("Branch mang số T nhưng không có thẻ", stray)]:
        if rows:
            say(title)
            for row in rows:
                say("    " + row)
    return 0


# ── Lane và Kết luận Reviewer (luật cứng 7) ─────────────────────────────────
# Lane là điều máy xác định được từ diff, AI không tự khai: chạm máy chặn, Hot file hoặc Restricted zone (đọc AGENTS.md
# trên BASE) → Strict; có thẻ → Normal; còn lại → Fast. PR Lane Strict phải có mục "Kết luận Reviewer" trong mô tả,
# do một phiên AI khác phiên đã làm task viết theo P-07. Máy kiểm được là CÓ kết luận "Đạt", không kiểm được ai viết.

def pr_lane():
    _, br, _ = git("rev-parse", "--abbrev-ref", "HEAD")
    br = os.environ.get("PROJECT_OS_BRANCH") or os.environ.get("POS_BRANCH") or br
    base = base_ref()
    if base is None:
        return "Fast", "không có nhánh đích để so"
    files = git("diff", "--name-only", "--no-renames", f"{base}...HEAD")[1].splitlines()
    prot = protected_paths(base)
    hit = [f for f in files if in_scope(f, prot)]
    if hit:
        return "Strict", f"chạm đường dẫn được bảo vệ: {hit[0]}" + (f" và {len(hit) - 1} file khác" if len(hit) > 1 else "")
    m = re.match(r"^[a-z]+/(T-\d{3,})-", br)
    if m and find_card(m.group(1)) is not None:
        return "Normal", f"có thẻ {m.group(1)}"
    return "Fast", "không có thẻ"


def cmd_lane(opts, _):
    lane, why = pr_lane()
    say(f"lane: {lane} ({why})")
    return 0


REVIEW_HEAD = "Kết luận Reviewer"
REVIEW_OK = re.compile(r"^\s*[-*]?\s*Kết luận:\s*Đạt\b", re.M)


def cmd_review_check(opts, _):
    """BODY=<file chứa mô tả PR>. Lane Strict mà thiếu "Kết luận: Đạt" trong mục Kết luận Reviewer thì lỗi."""
    lane, why = pr_lane()
    if lane != "Strict":
        say(f"review-check: Lane {lane} ({why}): không cần {REVIEW_HEAD}")
        return 0
    body = ""
    if opts.get("BODY"):
        try:
            body = pathlib.Path(opts["BODY"]).read_text(encoding="utf-8", errors="replace")
        except OSError:
            die(f"review-check: không đọc được file mô tả PR: {opts['BODY']}")
    at = body.find(REVIEW_HEAD)
    if at >= 0 and REVIEW_OK.search(body[at:]):
        say(f"review-check: Lane Strict, mô tả PR đã có {REVIEW_HEAD}: Đạt")
        return 0
    missing = f"chưa có mục '{REVIEW_HEAD}'" if at < 0 else f"mục '{REVIEW_HEAD}' chưa có dòng 'Kết luận: Đạt'"
    say(f"review-check: Lane Strict ({why}), nhưng mô tả PR {missing}.")
    say("Luật cứng 7: một phiên AI khác phiên đã làm task chạy P-07 (docs/prompts/P-07.md), rồi dán kết luận vào mô tả PR. "
        "Reviewer trả lại thì sửa và review lại (tối đa 2 vòng, sau đó PO quyết).")
    return 1


COMMANDS = {
    "status": cmd_status, "find": cmd_find, "lane": cmd_lane, "review-check": cmd_review_check,
    "setup": cmd_setup, "run": cmd_run, "lint": cmd_lint, "test": cmd_test, "features": cmd_features,
    "secrets": cmd_secrets, "check": cmd_check, "task": cmd_task, "done": cmd_done, "drop": cmd_drop, "wt": cmd_wt, "scope": cmd_scope, "plan-check": cmd_plan_check,
    "wt-clean": cmd_wt_clean, "pr": cmd_pr, "sos": cmd_sos,
}


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # console Windows cp1252 không in được tiếng Việt
        except (AttributeError, ValueError):
            pass
    args = sys.argv[1:]
    if not args or args[0] not in COMMANDS:
        say(__doc__)
        return 0 if not args or args[0] in ("-h", "--help", "help") else 2
    opts, extra = {}, []
    for a in args[1:]:
        m = re.fullmatch(r"([A-Z]+)=(.*)", a)
        if m:
            opts[m.group(1)] = m.group(2)
        else:
            extra.append(a)
    for k in ("F", "L"):  # cho phép đặt qua biến môi trường khi cần
        opts.setdefault(k, os.environ.get(f"PROJECT_OS_{k}", ""))
    return COMMANDS[args[0]](opts, extra)


if __name__ == "__main__":
    sys.exit(main())

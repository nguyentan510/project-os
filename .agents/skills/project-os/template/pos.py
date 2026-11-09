#!/usr/bin/env python3
"""Project OS runner: một file Python thay Make + Bash. Chạy được trên Windows, macOS, Linux.
Chỉ dùng thư viện chuẩn Python 3.8+. (Đặt tên pos.py, không phải os.py, để khỏi che module `os` của Python.)

  python pos.py setup | run | lint | test [F=MAP-07] [L=api] | features [--sync] | check
  python pos.py task T=T-043 N=map-sales [TYPE=fix]    tạo worktree + branch từ main mới nhất
  python pos.py done T=T-043                           dọn sau khi PR đã merge
  python pos.py drop T=T-043 [CONFIRM=T-043]           huỷ task chưa merge (phải hỏi chủ dự án)
  python pos.py wt                                     liệt kê worktree
  python pos.py wt-clean [APPLY=1]                     tìm worktree mồ côi (đã merge); chỉ liệt kê, APPLY=1 mới dọn
  python pos.py pr [T=T-043] [--no-check]              sinh sẵn khung báo cáo PR từ git diff + kết quả check
  python pos.py scope                                  kiểm file đã sửa có nằm trong "Scope" của thẻ task (luật cứng 8)
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

# ── Cấu hình dự án: điền lệnh thật vào đây (Ngày 0). Để trống = chưa cấu hình, in thông báo rồi coi như qua.
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

WT_DIR = "../wt"  # worktree đặt ngoài repo
BASE = "main"
TYPES = ("feat", "fix", "refactor", "test", "docs", "chore")

ROOT = pathlib.Path(__file__).resolve().parent
PY = sys.executable or "python3"


def say(msg):
    print(msg, flush=True)


def die(msg, code=1):
    say(msg)
    sys.exit(code)


def git(*args, cwd=None):
    r = subprocess.run(["git", *args], cwd=cwd or ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def expand(cmd, opts):
    """Thay {F}, {L}, {F:text %}, {L:text %} trong lệnh."""
    def sub(m):
        val = opts.get(m.group(1), "")
        if not val:
            return ""
        return m.group(2).replace("%", val) if m.group(2) is not None else val
    return re.sub(r"\{([FL])(?::([^}]*))?\}", sub, cmd).strip()


def run_cmd(name, cmd, opts):
    if not cmd:
        say(f"{name}: chưa cấu hình {name.upper()}_CMD trong pos.py")
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


def cmd_check(opts, _):
    for fn in (cmd_features, cmd_lint, cmd_test):
        rc = fn(opts, [])
        if rc:
            return rc
    say("check: qua")
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
        die(f"Chủ dự án đồng ý thì chạy lại: python pos.py drop T={t} CONFIRM={t}")
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
    say(f"**Mã · Task · Lane:** {', '.join(feats) or '<MÃ>'} · {t or '—'} · <Fast | Normal | Strict>\n")
    if t:
        say(f"Closes #{int(t[2:])}  <!-- chỉ giữ nếu T-nnn trùng số GitHub Issue (PROCESS.md mục 7) -->\n")
    say("**Đã làm:**\n\n**Scope thực tế:** khớp thẻ / thêm …, vì …\n")
    say(f"**File thay đổi:**\n```\n{stat or '(không khác ' + base + ')'}\n```\n")
    say(f"**Commit:**\n```\n{commits or '(chưa có commit)'}\n```\n")
    say(f"**Test đã chạy:** {check}\n")
    say("**Khác mặc định (nếu có, lý do):**\n\n**Rủi ro:**\n\n**Ghi chú bàn giao:**")
    return 0


# ── Máy chặn Scope của thẻ (luật cứng 8) ───────────────────────────────────
# Thẻ task nằm trong docs/plan/*.md, đọc từ origin/<BASE> (không phải từ branch đang làm),
# để Builder không tự mở rộng Scope trong chính PR của mình. Muốn mở rộng: Orchestrator sửa thẻ
# trên main trước. Lane Fast (branch mang mã feature, không có số T) và branch không có thẻ thì bỏ qua.
# Nhận cả tên trường cũ (`Phạm vi:`, `Sóng:`) để plan viết trước v1.4 vẫn chạy.

def find_card(t):
    """Trả về danh sách mẫu đường dẫn của dòng `Scope:` trong thẻ task t, hoặc None nếu không có thẻ."""
    ref = f"origin/{BASE}"
    if git("rev-parse", "--verify", "--quiet", ref)[0]:
        ref = BASE
        if git("rev-parse", "--verify", "--quiet", ref)[0]:
            return None
    code, names, _ = git("ls-tree", "-r", "--name-only", ref, "--", "docs/plan")
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


def in_scope(path, patterns):
    for p in patterns:
        p = p.strip("`").lstrip("./")
        if p.endswith("/"):
            p += "*"
        if fnmatch.fnmatch(path, p):  # `*` khớp cả dấu `/`: src/map/* gồm mọi thư mục con
            return True
    return False


def cmd_scope(opts, _):
    _, br, _ = git("rev-parse", "--abbrev-ref", "HEAD")
    # CI checkout ở trạng thái detached: truyền tên branch qua PROJECT_OS_BRANCH (nhận cả tên cũ POS_BRANCH)
    br = os.environ.get("PROJECT_OS_BRANCH") or os.environ.get("POS_BRANCH") or br
    m = re.match(r"^[a-z]+/(T-\d{3,})-", br)
    if not m:
        say(f"scope: branch '{br}' không mang số T (Lane Fast hoặc branch khác): bỏ qua")
        return 0
    t = m.group(1)
    patterns = find_card(t)
    if patterns is None:
        say(f"scope: không thấy thẻ {t} trong docs/plan/ trên {BASE}: bỏ qua")
        return 0
    if not patterns:
        say(f"scope: thẻ {t} chưa có dòng 'Scope:': không kiểm được")
        return 0
    base = f"origin/{BASE}" if git("rev-parse", "--verify", "--quiet", f"origin/{BASE}")[0] == 0 else BASE
    code, out, err = git("diff", "--name-only", f"{base}...HEAD")
    if code:
        die(f"scope: không so được với {base}: {err}")
    outside = [f for f in out.splitlines() if not in_scope(f, patterns)]
    if outside:
        say(f"scope: {t} sửa ngoài Scope của thẻ ({' '.join(patterns)}):")
        for f in outside:
            say("    " + f)
        say("Luật cứng 8: dừng và báo Orchestrator. Được duyệt thì Orchestrator sửa 'Scope' của thẻ trên main, rồi push lại.")
        return 1
    say(f"scope: {t} đúng Scope của thẻ")
    return 0


# ── Kiểm plan theo Wave (PROCESS.md mục 11) ─────────────────────────────────
# Chạy trên docs/plan/*.md trong thư mục làm việc, TRƯỚC khi chủ dự án duyệt plan. Bốn lỗi bị chặn:
#   1. hai task cùng Wave có "Scope" (quyền ghi, RW) giao nhau;
#   2. "Phụ thuộc" trỏ tới task cùng Wave hoặc Wave sau;
#   3. "Phụ thuộc" trỏ tới task không có trong plan;
#   4. task thuộc Wave có từ 2 task trở lên mà "Scope" chạm "Hot file" trong AGENTS.md.

def scope_prefix(pat):
    """(tiền tố trước ký tự glob đầu tiên, có glob không). Bỏ "./" ở đầu nhưng giữ dấu chấm của .github/."""
    p = pat.strip("`").replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    m = re.search(r"[*?\[]", p)
    if m:
        return p[:m.start()], True
    return p.rstrip("/"), False


def overlaps(a, b):
    """Hai Scope chạm nhau. Không có glob thì so theo từng thư mục (src/api không chạm src/apix);
    có glob thì tiền tố được cắt giữa chừng (src/app/routes.* chạm src/app/routes.py)."""
    (pa, ga), (pb, gb) = scope_prefix(a), scope_prefix(b)
    if not pa or not pb:
        return True  # glob từ gốc (**/x) hoặc Scope rỗng: coi như chạm
    if ga and pb.startswith(pa) or gb and pa.startswith(pb):
        return True
    pa, pb = pa.rstrip("/"), pb.rstrip("/")
    return pa == pb or pa.startswith(pb + "/") or pb.startswith(pa + "/")


WAVE = "Wave|Sóng"
SCOPE = "Scope|Phạm vi"


def field(line, name):
    """Giá trị của trường `name:` trong một dòng thẻ; `name` là regex (nhận cả tên cũ)."""
    m = re.search(rf"(?:{name}):\s*(.*?)(?:\s{{2,}}\S[^:]*:|$)", line)
    return m.group(1).strip() if m else None


def parse_cards():
    cards = []
    head = re.compile(r"^\s*-\s*\[[ xX]\]\s*(T-\d{3,})\b")
    for f in sorted((ROOT / "docs" / "plan").glob("*.md")):
        lines = f.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            m = head.match(line)
            if not m:
                continue
            c = {"t": m.group(1), "file": f.name, "wave": None, "rw": [], "deps": []}
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
            cards.append(c)
    return cards


def hot_files():
    f = ROOT / "AGENTS.md"
    if not f.exists():
        return []
    out, on = [], False
    for line in f.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            on = line.startswith(("## Hot file", "## File nóng"))
        elif on and "{{" not in line:
            out += [x for x in re.split(r"[,\s]+", line.replace("`", " ").strip()) if x]
    return out


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
    if errs:
        say("plan-check: plan chưa đạt:")
        for e in errs:
            say("    " + e)
        return 1
    say(f"plan-check: qua ({len(cards)} task, {len(waves)} Wave, không trùng Scope)")
    return 0


COMMANDS = {
    "setup": cmd_setup, "run": cmd_run, "lint": cmd_lint, "test": cmd_test, "features": cmd_features,
    "check": cmd_check, "task": cmd_task, "done": cmd_done, "drop": cmd_drop, "wt": cmd_wt, "scope": cmd_scope, "plan-check": cmd_plan_check,
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

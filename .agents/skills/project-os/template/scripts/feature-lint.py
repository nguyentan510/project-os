#!/usr/bin/env python3
"""Kiểm sổ mã (luật cứng 5, PROCESS.md mục 6 và 10). Chỉ dùng thư viện chuẩn Python 3.

Lỗi (dừng python pos.py check):
  - mã trùng trong FEATURES.md
  - mã xuất hiện trong code/test nhưng không có trong sổ
  - mã đã `bỏ` vẫn còn trong code (test khẳng định đã bỏ thì được)
Cảnh báo (không dừng):
  - mã `dùng` chưa có test nào gắn mã, và cột Test không ghi `— (lý do)`
  - biến môi trường code đọc (os.getenv, process.env…) mà `.env.example` chưa khai báo
`--sync`: ghi lại cột Test của sổ từ các test gắn mã tìm thấy, dạng `đường/dẫn/test.py (5), …`
  (số trong ngoặc = số lần mã xuất hiện trong file test). Ô `— (lý do)` chỉ bị thay khi đã có test thật.
Chỉ nhận mã có tiền tố là module đã khai báo bằng tiêu đề `### MÃ · Tên` trong FEATURES.md.
"""
import collections
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FEATURES = ROOT / "docs" / "product" / "FEATURES.md"
# Bỏ qua ở mọi độ sâu: thư mục sinh ra bởi công cụ.
SKIP_DIRS = {".git", "node_modules", "target", "dist", "build", ".venv", "venv", "__pycache__"}
# Chỉ bỏ qua ở gốc repo: tài liệu và công cụ của khung (src/docs, src/mk… vẫn được quét).
SKIP_TOP_DIRS = {"docs", ".github", ".githooks", "mk"}
# Tài liệu và công cụ ở gốc repo có mã làm ví dụ, không phải mã đang dùng.
SKIP_ROOT_FILES = {"Makefile", "AGENTS.md", "STATUS.md", "CLAUDE.md", "GEMINI.md", "README.md"}
CODE_RE = re.compile(r"^[A-Z]{2,6}-\d{2,}$")
ENV_FILE = ROOT / ".env.example"
ENV_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".rs", ".go", ".rb", ".php", ".vue", ".svelte"}
# Biến do hệ điều hành, runtime hoặc CI cấp: không cần khai báo trong .env.example.
ENV_BUILTIN = {"PATH", "HOME", "USER", "PWD", "SHELL", "TMPDIR", "TEMP", "TMP", "LANG", "CI", "NODE_ENV",
               "PYTHONPATH", "VIRTUAL_ENV", "GITHUB_ACTIONS", "GITHUB_TOKEN", "RUST_LOG", "RUST_BACKTRACE"}
ENV_RE = re.compile(
    r"""(?:os\.getenv|os\.environ\.get|os\.environ\[|getenv|env::var(?:_os)?|ENV\.fetch|ENV\[)\s*\(?\s*["']([A-Z][A-Z0-9_]*)["']"""
    r"|(?:process\.env|import\.meta\.env)\.([A-Z][A-Z0-9_]*)"
    r"""|(?:process\.env|import\.meta\.env)\[\s*["']([A-Z][A-Z0-9_]*)["']""")


def read_registry():
    if not FEATURES.exists():
        sys.exit(f"python pos.py features: thiếu {FEATURES.relative_to(ROOT)}")
    text = FEATURES.read_text(encoding="utf-8")
    modules = set(re.findall(r"^###\s+([A-Z]{2,6})\s+·", text, re.M))
    rows, dups = {}, []
    test_col = 3  # mặc định theo mẫu; đọc lại từ dòng tiêu đề bảng nếu có cột "Test…"
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == "Mã":
            test_col = next((i for i, c in enumerate(cells) if c.lower().startswith("test")), 3)
            continue
        if not cells or not CODE_RE.match(cells[0]):
            continue
        code = cells[0]
        if code in rows:
            dups.append(code)
        rows[code] = {"test": cells[test_col] if len(cells) > test_col else "", "status": cells[-1]}
    return modules, rows, dups


def is_test(path):
    parts = {p.lower() for p in path.parts}
    name = path.name.lower()
    return bool(parts & {"tests", "test", "spec", "e2e"}) or "test" in name or "spec" in name


def scan(modules):
    """Trả về {mã: {"code": [file…], "test": [file…]}} tìm thấy ngoài docs/."""
    found = {}
    if not modules:
        return found
    alt = "|".join(sorted(modules))
    upper = re.compile(rf"\b({alt})-(\d{{2,}})\b")
    lower = re.compile(rf"\b({alt.lower()})_(\d{{2,}})_")  # tên test Rust: map_07_…
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if (path.is_dir() or set(rel.parts) & SKIP_DIRS or rel.parts[0] in SKIP_TOP_DIRS
                or path.name == "feature-lint.py"
                or (len(rel.parts) == 1 and path.name in SKIP_ROOT_FILES)):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        hits = collections.Counter(f"{m}-{n}" for m, n in upper.findall(text))
        hits.update(f"{m.upper()}-{n}" for m, n in lower.findall(text))
        kind = "test" if is_test(rel) else "code"
        for code, n in hits.items():
            entry = found.setdefault(code, {"code": [], "test": [], "count": {}})
            entry[kind].append(rel.as_posix())
            entry["count"][rel.as_posix()] = n
    return found


def scan_env():
    """Trả về {tên biến: file đầu tiên đọc nó} cho code (không tính test) ngoài docs/."""
    used = {}
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if (path.is_dir() or path.suffix not in ENV_EXTS or set(rel.parts) & SKIP_DIRS
                or rel.parts[0] in SKIP_TOP_DIRS or rel.parts[0] == "scripts" or is_test(rel)):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for groups in ENV_RE.findall(text):
            name = next(g for g in groups if g)
            if name not in ENV_BUILTIN:
                used.setdefault(name, rel.as_posix())
    return used


def declared_env():
    """Tên biến khai trong .env.example, kể cả dòng đã comment (`# KEY=`)."""
    if not ENV_FILE.exists():
        return None
    text = ENV_FILE.read_text(encoding="utf-8")
    return set(re.findall(r"^\s*(?:#\s*)?(?:export\s+)?([A-Z][A-Z0-9_]*)\s*=", text, re.M))


AUTO_CELL = re.compile(r"^[^\s,]+ \(\d+\)(, [^\s,]+ \(\d+\))*$")


def test_cell(entry):
    return ", ".join(f"{f} ({entry['count'][f]})" for f in sorted(entry["test"]))


def sync(found):
    """Ghi lại cột Test của FEATURES.md. Chỉ đụng vào ô Test, giữ nguyên mọi ô khác."""
    lines = FEATURES.read_text(encoding="utf-8").split("\n")
    test_col, changed = 3, 0
    for i, line in enumerate(lines):
        if not line.startswith("|"):
            continue
        parts = line.rstrip().strip("|").split("|")
        cells = [c.strip() for c in parts]
        if cells and cells[0] == "Mã":
            test_col = next((j for j, c in enumerate(cells) if c.lower().startswith("test")), 3)
            continue
        if not cells or not CODE_RE.match(cells[0]) or len(cells) <= test_col:
            continue
        entry = found.get(cells[0])
        old = cells[test_col]
        if entry and entry["test"]:
            new = test_cell(entry)
        elif AUTO_CELL.match(old):
            new = "—"  # test từng được ghi tự động nay đã mất
        else:
            continue
        if new != old:
            parts[test_col] = f" {new} "
            lines[i] = "|" + "|".join(parts) + "|"
            changed += 1
    if changed:
        FEATURES.write_text("\n".join(lines), encoding="utf-8")
    print(f"python pos.py features --sync: cập nhật {changed} dòng trong {FEATURES.relative_to(ROOT)}")


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # console Windows cp1252 không in được tiếng Việt
        except (AttributeError, ValueError):
            pass
    modules, rows, dups = read_registry()
    found = scan(modules)
    if "--sync" in sys.argv[1:]:
        sync(found)
        modules, rows, dups = read_registry()
    errors, warnings = [], []
    for code in sorted(set(dups)):
        errors.append(f"{code}: trùng trong FEATURES.md")
    for code, where in sorted(found.items()):
        if code not in rows:
            errors.append(f"{code}: có trong {(where['code'] + where['test'])[0]} nhưng không có trong sổ")
        elif rows[code]["status"].startswith("bỏ") and where["code"]:
            errors.append(f"{code}: đã bỏ nhưng còn trong {where['code'][0]}")
    for code, row in sorted(rows.items()):
        if row["status"] == "dùng" and not found.get(code, {}).get("test") and not row["test"].startswith("— ("):
            warnings.append(f"{code}: đang dùng nhưng chưa có test gắn mã (hoặc ghi `— (lý do)` ở cột Test)")
    declared = declared_env()
    for name, where in sorted(scan_env().items()):
        if declared is None:
            errors.append(f"{name}: code đọc biến này ({where}) nhưng chưa có .env.example")
        elif name not in declared:
            errors.append(f"{name}: {where} đọc biến môi trường này nhưng .env.example chưa khai báo")
    counts = {s: sum(1 for r in rows.values() if r["status"].startswith(s)) for s in ("dùng", "dự kiến", "bỏ")}
    for w in warnings:
        print(f"  cảnh báo  {w}")
    for e in errors:
        print(f"  LỖI      {e}")
    print(f"python pos.py features: {len(rows)} mã (dùng {counts['dùng']}, dự kiến {counts['dự kiến']}, bỏ {counts['bỏ']})"
          f" · {len(modules)} module · lỗi {len(errors)} · cảnh báo {len(warnings)}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()

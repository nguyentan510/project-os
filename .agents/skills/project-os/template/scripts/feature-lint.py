#!/usr/bin/env python3
"""Kiểm sổ mã (luật cứng 5, PROCESS.md mục 6 và 10). Chỉ dùng thư viện chuẩn Python 3.

Lỗi (dừng make check):
  - mã trùng trong FEATURES.md
  - mã xuất hiện trong code/test nhưng không có trong sổ
  - mã đã `bỏ` vẫn còn trong code (test khẳng định đã bỏ thì được)
Cảnh báo (không dừng):
  - mã `dùng` chưa có test nào gắn mã, và cột Test không ghi `— (lý do)`
Chỉ nhận mã có tiền tố là module đã khai báo bằng tiêu đề `### MÃ · Tên` trong FEATURES.md.
"""
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


def read_registry():
    if not FEATURES.exists():
        sys.exit(f"make features: thiếu {FEATURES.relative_to(ROOT)}")
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
        hits = {f"{m}-{n}" for m, n in upper.findall(text)}
        hits |= {f"{m.upper()}-{n}" for m, n in lower.findall(text)}
        kind = "test" if is_test(rel) else "code"
        for code in hits:
            found.setdefault(code, {"code": [], "test": []})[kind].append(str(rel))
    return found


def main():
    modules, rows, dups = read_registry()
    found = scan(modules)
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
    counts = {s: sum(1 for r in rows.values() if r["status"].startswith(s)) for s in ("dùng", "dự kiến", "bỏ")}
    for w in warnings:
        print(f"  cảnh báo  {w}")
    for e in errors:
        print(f"  LỖI      {e}")
    print(f"make features: {len(rows)} mã (dùng {counts['dùng']}, dự kiến {counts['dự kiến']}, bỏ {counts['bỏ']})"
          f" · {len(modules)} module · lỗi {len(errors)} · cảnh báo {len(warnings)}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()

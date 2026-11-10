#!/usr/bin/env python3
"""Kiểm toán Ngày 0 phần máy kiểm được (PROCESS.md mục 3). Không sửa gì. Chạy được mọi hệ điều hành.
  python audit.py [thư-mục-dự-án]
Phần cần người hoặc AI phiên mới đánh giá: chạy prompt docs/prompts/P-15.md.
"""
import glob
import os
import re
import subprocess
import sys

passed = failed = 0


def report(ok, desc):
    global passed, failed
    print(f"  {'Đạt ' if ok else 'Chưa'}  {desc}")
    if ok:
        passed += 1
    else:
        failed += 1


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout.strip()


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    try:
        os.chdir(sys.argv[1] if len(sys.argv) > 1 else ".")
    except OSError:
        sys.exit(2)

    core = ["AGENTS.md", "STATUS.md", "docs/product/BRIEF.md", "docs/product/FEATURES.md", "docs/DECISIONS.md"]
    print(f"Kiểm toán Ngày 0 · {os.getcwd()}")
    print("File")
    for f in core + ["docs/PROCESS.md", "pos.py", ".githooks/pre-push", ".github/workflows/ci.yml",
                     ".github/pull_request_template.md", "docs/GLOSSARY.md", ".gitignore", ".env.example", "scripts/features.py"]:
        report(os.path.isfile(f), f"có {f}")

    print("Ý định và phạm vi")
    texts = {f: read(f) or "" for f in core}
    report(not any("{{" in t for t in texts.values()), "file lõi không còn chỗ {{…}} chưa điền")
    report(not any(re.search(r"\bTODO\b", t) for t in texts.values()), "file lõi không còn chữ TODO")
    brief = texts["docs/product/BRIEF.md"]
    sec = re.search(r"^## Không làm\s*\n(.*?)(?=^## |\Z)", brief, re.M | re.S)
    report(bool(sec and any(l.startswith("- ") and len(l) > 2 and "{{" not in l for l in sec.group(1).splitlines())),
           "BRIEF có mục Không làm có nội dung")
    features = texts["docs/product/FEATURES.md"]
    report(bool(re.search(r"^\| [A-Z]{2,6}-\d{2,} \|", features, re.M)), "FEATURES có ít nhất 1 feature có mã")

    print("Kỹ thuật")
    decisions = [l for l in texts["docs/DECISIONS.md"].splitlines() if re.match(r"^\| D\d{2,} \|", l) and "{{" not in l]
    report(len(decisions) >= 5, "DECISIONS có ít nhất 5 quyết định")
    for m in (x.lower() for x in re.findall(r"^### ([A-Z]{2,6}) ·", features, re.M)):
        report(os.path.isfile(f"src/{m}/README.md") or os.path.isfile(f"crates/{m}/README.md"), f"module {m} có README")
        has_contract = any(glob.glob(p) for p in (f"src/{m}/contract.*", f"crates/{m}/src/contract.*", f"crates/{m}/contract.*"))
        report(has_contract, f"module {m} có contract")

    print("Ngữ cảnh cho AI")
    if os.path.isfile("CLAUDE.md"):
        report("".join((read("CLAUDE.md") or "").split()) == "@AGENTS.md", "CLAUDE.md chỉ có đúng dòng @AGENTS.md")

    print("Máy chặn")
    report(".env" in (read(".gitignore") or "").splitlines(), ".gitignore bỏ qua .env")
    if git("rev-parse", "--git-dir")[0] == 0:
        report(git("ls-files", "--error-unmatch", ".env")[0] != 0, ".env không nằm trong Git")
        report(git("config", "core.hooksPath")[1] == ".githooks", "hook đã bật (core.hooksPath = .githooks)")
    else:
        report(False, "đây chưa phải repo git")
    zone = re.search(r"^## (?:Restricted zone|Vùng cấm)[^\n]*\n(.*?)(?=^## |\Z)", texts["AGENTS.md"], re.M | re.S)
    if zone and any(l.strip() and "{{" not in l and "không có" not in l.lower() for l in zone.group(1).splitlines()):
        owners = (read(".github/CODEOWNERS") or "").splitlines()
        report(any(l.strip() and not l.lstrip().startswith("#") for l in owners), "CODEOWNERS có luật cho Restricted zone")
    owners = [l.split() for l in (read(".github/CODEOWNERS") or "").splitlines() if l.strip() and not l.lstrip().startswith("#")]
    covered = {l[0].strip("/") for l in owners if len(l) > 1}
    report({"pos.py", "scripts/features.py", ".githooks", ".github"} <= covered,
           "CODEOWNERS phủ máy chặn (pos.py, scripts/features.py, .githooks/, .github/)")
    report(bool(owners) and not any("@chu-du-an" in " ".join(l) for l in owners), "CODEOWNERS đã thay @chu-du-an bằng tài khoản thật")
    pos = read("pos.py") or ""
    for var in ("LINT_CMD", "TEST_CMD"):
        m = re.search(rf"^{var}\s*=\s*([\"'])(.*?)\1", pos, re.M)
        report(bool(m and m.group(2).strip()), f"pos.py đã điền {var} (lệnh thật, hoặc \"none\" nếu chưa có)")
    # Lưu ý: bước này chạy check thật trong repo đích (có thể có tác dụng phụ do test/lint của dự án).
    report(os.path.isfile("pos.py") and subprocess.run([sys.executable, "pos.py", "check"], capture_output=True).returncode == 0,
           "python pos.py check qua")

    print(f"\nKết quả: Đạt {passed} · Chưa {failed}")
    print("Còn phải kiểm bằng P-15 (AI phiên mới) hoặc bằng tay: khoá main trên GitHub, thử push thẳng main bị chặn,")
    print("AI phiên trắng chạy P-01 tóm tắt đúng dự án, mỗi thông tin chỉ ở một nơi.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

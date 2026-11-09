#!/usr/bin/env python3
"""Chép khung Ngày 0 vào một dự án. Không bao giờ ghi đè file đã có. Chạy được mọi hệ điều hành.
  python init.py [thư-mục-dự-án] [--plan]
  --plan  chép thêm docs/plan/ (ROADMAP + mẫu plan mốc), dùng khi đã có nhiều mốc
"""
import pathlib
import shutil
import subprocess
import sys

SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent


def copy_tree(src_root, dest):
    created = kept = 0
    for src in sorted(p for p in src_root.rglob("*") if p.is_file()):
        rel = src.relative_to(src_root)
        # npm bỏ file .gitignore khi đóng gói, nên khung lưu nó là gitignore.template.
        if rel.name == "gitignore.template":
            rel = rel.with_name(".gitignore")
        target = dest / rel
        if target.exists():
            print(f"  giữ  {rel.as_posix()}")
            kept += 1
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
            print(f"  tạo  {rel.as_posix()}")
            created += 1
    return created, kept


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    args = [a for a in sys.argv[1:] if a != "--plan"]
    with_plan = "--plan" in sys.argv[1:]
    dest = pathlib.Path(args[0] if args else ".").resolve()
    dest.mkdir(parents=True, exist_ok=True)

    print(f"Project OS · chép khung Ngày 0 vào {dest}")
    created, kept = copy_tree(SKILL_DIR / "template", dest)
    if with_plan:
        c, k = copy_tree(SKILL_DIR / "optional", dest)
        created, kept = created + c, kept + k
    try:
        (dest / ".githooks" / "pre-push").chmod(0o755)
    except OSError:
        pass

    in_git = subprocess.run(["git", "-C", str(dest), "rev-parse", "--git-dir"], capture_output=True).returncode == 0
    if in_git:
        subprocess.run(["git", "-C", str(dest), "config", "core.hooksPath", ".githooks"])
        print("Đã bật hook (.githooks/pre-push).")
    else:
        print("Chưa phải repo git: chạy 'git init' rồi 'python pos.py setup' để bật hook.")

    print(f"\nXong: tạo {created} file, giữ nguyên {kept} file đã có.")
    print("Tiếp theo: điền các chỗ {{…}} theo 7 bước Ngày 0 (docs/PROCESS.md mục 3, prompt docs/prompts/P-02.md),")
    print(f"rồi kiểm toán: python {SKILL_DIR / 'scripts' / 'audit.py'} {dest}")


if __name__ == "__main__":
    main()

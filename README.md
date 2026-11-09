# Project OS

Quy tắc triển khai dự án cho Solo Dev + nhiều AI (Claude Code, Codex, Antigravity, Cursor…).
Mục tiêu: AI nào mở repo cũng trả lời được trong 1 phút **đang làm gì, đã làm gì, sửa thì bắt đầu từ đâu**. Đầu mối chung là **mã** (`MAP-07`, `D59`, `T-042`).

Repo này vừa là **skill** (thiết lập nhanh trong AI coding) vừa là **khung Ngày 0** (chép vào dự án).

## Có gì

```
.agents/skills/project-os/        skill (định dạng SKILL.md chung)
├── SKILL.md                      AI đọc: init · Ngày 0 · audit
├── scripts/init.sh               chép khung vào dự án, không ghi đè
├── scripts/audit.sh              kiểm toán Ngày 0 phần máy kiểm được
├── template/                     khung Ngày 0 (chép nguyên vào dự án)
│   ├── AGENTS.md  CLAUDE.md  STATUS.md  Makefile  .gitignore  .env.example
│   ├── docs/PROCESS.md           bản đầy đủ của quy tắc (13 mục)
│   ├── docs/product/BRIEF.md · FEATURES.md   docs/DECISIONS.md
│   ├── docs/prompts/P-01…P-15.md bảng prompt theo từng bước
│   ├── mk/worktree.mk            make task · done · drop · wt
│   ├── scripts/feature-lint.py   kiểm sổ mã (make features)
│   ├── .githooks/pre-push        chặn push khi make check chưa qua
│   └── .github/                  CI · CODEOWNERS · mẫu PR
└── optional/docs/plan/           ROADMAP + mẫu plan mốc (init.sh --plan)
.claude/skills/project-os         liên kết tới thư mục skill trên (cho Claude Code)
```

## Cài skill

Skill dùng định dạng `SKILL.md` chung; mỗi công cụ tìm ở một thư mục khác nhau.

| Công cụ | Thư mục skill (cho mọi dự án) | Gọi |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/project-os/` | `/project-os` |
| Codex | `~/.agents/skills/project-os/` | `$project-os` |
| Antigravity | `~/.gemini/config/skills/project-os/` (cũng nhận `~/.agents/skills/`) | tự nhận theo mô tả |

```bash
git clone https://github.com/nguyentan510/project-os.git ~/project-os
mkdir -p ~/.agents/skills ~/.claude/skills
ln -s ~/project-os/.agents/skills/project-os ~/.agents/skills/project-os   # Codex, Antigravity
ln -s ~/project-os/.agents/skills/project-os ~/.claude/skills/project-os   # Claude Code
```

Windows không có symlink: chép thư mục `.agents/skills/project-os` vào các chỗ trên.
Cập nhật skill: `git -C ~/project-os pull`.

## Dùng

Trong dự án, nói với AI: *"Dùng skill project-os để bắt đầu dự án này"*. AI sẽ chạy init, rồi dẫn đi 7 bước Ngày 0, dừng chờ bạn duyệt sau mỗi bước.

Không dùng skill cũng được:

```bash
bash ~/project-os/.agents/skills/project-os/scripts/init.sh /đường/dẫn/dự-án   # thêm --plan nếu có nhiều mốc
cd /đường/dẫn/dự-án && git init && make setup
# điền các chỗ {{…}} theo docs/PROCESS.md mục 3
bash ~/project-os/.agents/skills/project-os/scripts/audit.sh .
```

## Bật trên GitHub (bằng tay, một lần cho mỗi dự án)

Settings → Branches → thêm luật cho `main`:
- Require a pull request before merging
- Require status checks to pass (`check`, `pr-title`)
- Require branches to be up to date before merging
- Require review from Code Owners (khi đã điền `.github/CODEOWNERS`)

## Yêu cầu

`git`, `make`, `bash`, `python3` (chỉ thư viện chuẩn). `gh` (tuỳ chọn) để `make done` nhận ra PR đã gộp kiểu squash.
Claude Code từ 2.1.277 tự đọc `AGENTS.md`; `CLAUDE.md` trong khung chỉ có dòng `@AGENTS.md` để chạy được cả bản cũ.

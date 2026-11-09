# Project OS

Quy tắc triển khai dự án cho Solo Dev + nhiều AI (Claude Code, Codex, Antigravity, Cursor…).
Mục tiêu: AI nào mở repo cũng trả lời được trong 1 phút **đang làm gì, đã làm gì, sửa thì bắt đầu từ đâu**. Đầu mối chung là **mã** (`MAP-07`, `D59`, `T-042`).

Repo này vừa là **skill** (thiết lập nhanh trong AI coding) vừa là **khung Ngày 0** (chép vào dự án).

## Có gì

```
.agents/skills/project-os/        skill (định dạng SKILL.md chung)
├── SKILL.md                      AI đọc: init · Ngày 0 · audit
├── scripts/init.py               chép khung vào dự án, không ghi đè
├── scripts/audit.py              kiểm toán Ngày 0 phần máy kiểm được
├── template/                     khung Ngày 0 (chép nguyên vào dự án)
│   ├── AGENTS.md  CLAUDE.md  STATUS.md  pos.py  Makefile (bọc tuỳ chọn)  gitignore.template (chép thành .gitignore)  .env.example
│   ├── docs/PROCESS.md           bản đầy đủ của quy tắc (13 mục)
│   ├── docs/GLOSSARY.md          bảng thuật ngữ: một khái niệm một tên
│   ├── docs/product/BRIEF.md · FEATURES.md   docs/DECISIONS.md
│   ├── docs/prompts/P-01…P-15, P-03-MULTI, P-SOS   bảng prompt theo từng bước
│   ├── scripts/features.py      kiểm sổ mã (python pos.py features [--sync])
│   ├── .githooks/pre-push        chặn push khi check chưa qua hoặc sửa ngoài Scope của thẻ
│   └── .github/                  CI · CODEOWNERS · mẫu PR
└── optional/docs/plan/           ROADMAP + mẫu plan của Milestone (init.py --plan)
.claude/skills/project-os         liên kết tới thư mục skill trên (cho Claude Code)
```

## Cài skill

Skill dùng định dạng `SKILL.md` chung. Có hai kiểu cài:

### Theo dự án (khuyên dùng)

Chạy trong thư mục dự án; skill được **chép vào dự án đó** để commit cùng repo, ai clone về (người hay AI) cũng có đúng phiên bản. Cần Node.js ≥ 16.7, không cần git.

```bash
cd /đường/dẫn/dự-án
npx -y @nguyentan0510/project-os
```

| Chép vào | Công cụ đọc | Gọi |
| --- | --- | --- |
| `.agents/skills/project-os/` | Codex, Antigravity và các công cụ dùng chuẩn chung | `$project-os` · tự nhận theo mô tả |
| `.claude/skills/project-os/` | Claude Code | `/project-os` |

- Chạy lại lệnh để cập nhật. Nơi đã có thứ khác (không do lệnh này tạo) thì bỏ qua, không ghi đè.
- **Chọn công cụ:** `--tools agents` (chỉ `.agents/`), `--tools claude` (chỉ `.claude/`), `--tools agents,claude` hoặc `--tools all` (mặc định: cả hai). Claude Code chỉ đọc `.claude/`; Codex và Antigravity đọc `.agents/`.
- **Mặc định riêng của bạn:** đặt biến môi trường `PROJECT_OS_TOOLS` (ví dụ `agents`); cờ `--tools` luôn thắng biến này.
- `--dry-run` chỉ in việc sẽ làm · `--uninstall` gỡ · `--dir <thư-mục>` cài vào thư mục khác.
- Mỗi lần chạy bằng `npx` lấy bản mới nhất của gói; muốn ghim phiên bản: `npx -y @nguyentan0510/project-os@1.1.0`.

### Toàn cục (dùng cho mọi dự án)

```bash
npx -y @nguyentan0510/project-os --global
```

Clone repo về `~/project-os` rồi tạo liên kết (symlink, Windows dùng junction) vào thư mục skill trong home của từng công cụ tìm thấy: `~/.agents/skills/` (luôn có), `~/.claude/skills/`, `~/.gemini/config/skills/`, `~/.codex/skills/`. Cần git. Chạy lại để cập nhật.

Không có Node.js thì dùng script (cài toàn cục):

```bash
curl -fsSL https://raw.githubusercontent.com/nguyentan510/project-os/main/install.sh | bash
```

Windows (PowerShell, không cần bash; không chạy `curl | bash` trong `cmd`):

```powershell
irm https://raw.githubusercontent.com/nguyentan510/project-os/main/install.ps1 | iex
```

Script nhận `--all` · `--dry-run` · `--uninstall` · `--dir <chỗ clone>` (PowerShell: `-All` `-DryRun` `-Uninstall` `-Dir`). Muốn xem script trước khi chạy: tải về, đọc, rồi chạy.

Cài bằng tay: clone repo rồi `ln -s ~/project-os/.agents/skills/project-os <thư mục skill ở bảng trên>/project-os`.

## Dùng

Tên gọi (Milestone, Wave, Task, Lane, Scope, Hot file, Restricted zone…) theo `docs/GLOSSARY.md`.

Trong dự án, nói với AI: *"Dùng skill project-os để bắt đầu dự án này"*. AI sẽ chạy init, rồi dẫn đi 7 bước Ngày 0, dừng chờ bạn duyệt sau mỗi bước.

Không dùng skill cũng được:

```bash
python ~/project-os/.agents/skills/project-os/scripts/init.py /đường/dẫn/dự-án   # thêm --plan nếu có nhiều Milestone
cd /đường/dẫn/dự-án && git init && python pos.py setup
# điền các chỗ {{…}} theo docs/PROCESS.md mục 3
python ~/project-os/.agents/skills/project-os/scripts/audit.py .
```

## Bật trên GitHub (bằng tay, một lần cho mỗi dự án)

Settings → Branches → thêm luật cho `main`:
- Require a pull request before merging
- Require status checks to pass (`check`, `pr-title`)
- Require branches to be up to date before merging
- Require review from Code Owners (khi đã điền `.github/CODEOWNERS`)

## Yêu cầu

`git` và Python 3 (chỉ thư viện chuẩn; không cần `make` hay `bash`). `gh` (tuỳ chọn) để `python pos.py done` nhận ra PR đã merge squash.
Claude Code từ 2.1.277 tự đọc `AGENTS.md`; `CLAUDE.md` trong khung chỉ có dòng `@AGENTS.md` để chạy được cả bản cũ.

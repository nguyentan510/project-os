<div align="center">

# Project OS

**Quy tắc triển khai dự án cho Solo Dev làm việc cùng nhiều AI**<br>
Claude Code · Codex · Antigravity · Cursor…

[![npm](https://img.shields.io/npm/v/@nguyentan0510/project-os?color=cb3837&logo=npm)](https://www.npmjs.com/package/@nguyentan0510/project-os)
[![node](https://img.shields.io/node/v/@nguyentan0510/project-os?logo=node.js)](https://nodejs.org)
![python](https://img.shields.io/badge/python-3.8%2B-3776ab?logo=python&logoColor=white)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)
![platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

```bash
npx -y @nguyentan0510/project-os
```

</div>

Một AI mới, không có lịch sử chat, mở repo phải biết trong **1 phút**: *đang ở đâu, vì sao như vậy, cái gì không được đụng, làm tiếp từ đâu và kiểm chứng bằng gì*.
Project OS đạt điều đó bằng một đầu mối chung là **mã** (`MAP-07`, `D59`, `T-042`) xuyên suốt sổ feature, code, test, commit và PR, cùng **8 luật cứng do máy chặn** thay vì trông vào việc AI có đọc hướng dẫn hay không.

Repo này vừa là **skill** (định dạng `SKILL.md` chung, AI tự gọi) vừa là **khung Ngày 0** (chép vào dự án trước dòng code đầu tiên).

## Mục lục

- [Vì sao](#vì-sao)
- [Bắt đầu nhanh](#bắt-đầu-nhanh)
- [Cài đặt](#cài-đặt)
- [Cách dùng](#cách-dùng)
- [Khung Ngày 0 có gì](#khung-ngày-0-có-gì)
- [`pos.py`: một file thay Make + Bash](#pospy-một-file-thay-make--bash)
- [Luật cứng](#luật-cứng)
- [Bảng prompt](#bảng-prompt)
- [Bật bảo vệ trên GitHub](#bật-bảo-vệ-trên-github)
- [Yêu cầu](#yêu-cầu)
- [Cấu trúc repo](#cấu-trúc-repo)
- [Phát triển repo này](#phát-triển-repo-này)
- [Giấy phép](#giấy-phép)

## Vì sao

Làm một mình với nhiều AI, mỗi phiên lại bắt đầu từ con số không: AI không biết phiên trước dừng ở đâu, sửa lan ra ngoài phạm vi, đẩy thẳng lên `main`, đặt tên lệch nhau. Project OS trả lời sáu câu hỏi bằng sáu đầu mối cố định:

| Câu hỏi | Đầu mối | Cách tra |
| --- | --- | --- |
| Luật chơi là gì? | `AGENTS.md` | Đọc đầu tiên |
| Phiên trước dừng ở đâu? | `STATUS.md` | Đọc, ngắn |
| Milestone nào, task nào? | `docs/plan/` | ROADMAP → plan của Milestone |
| Đã làm gì? | Git | `git log --oneline --grep "MAP-07"` |
| Sửa X bắt đầu từ đâu? | `docs/product/FEATURES.md` | Dòng mã → `rg "MAP-07"` |
| Vì sao làm vậy? | `docs/DECISIONS.md` | `rg "D59" docs/DECISIONS.md` |

Quy tắc có ba tầng: **Luật cứng** (máy chặn, không ngoại lệ) · **Mặc định** (AI được làm khác khi hợp lý hơn và ghi lý do) · **Mẫu** (dùng khi cần). Bắt đầu tối giản; phần nào chưa cần thì chưa bật.

## Bắt đầu nhanh

```bash
cd /đường/dẫn/dự-án
npx -y @nguyentan0510/project-os
```

Rồi nói với AI trong dự án:

> Dùng skill project-os để bắt đầu dự án này.

AI chạy init, dẫn bạn qua **7 bước Ngày 0** và dừng chờ bạn duyệt sau mỗi bước:

```
BRIEF → FEATURES → DECISIONS → module + contract → AGENTS + STATUS → khung repo + máy chặn → kiểm toán
```

Qua kiểm toán mới bắt đầu task code đầu tiên `T-001` (khung chạy được).

## Cài đặt

### Theo dự án (khuyên dùng)

Skill được **chép vào dự án** để commit cùng repo; ai clone về (người hay AI) cũng có đúng phiên bản. Cần Node.js ≥ 16.7, không cần git.

```bash
npx -y @nguyentan0510/project-os
```

| Chép vào | Công cụ đọc | Gọi |
| --- | --- | --- |
| `.agents/skills/project-os/` | Codex, Antigravity và các công cụ dùng chuẩn chung | `$project-os` · tự nhận theo mô tả |
| `.claude/skills/project-os/` | Claude Code | `/project-os` |

| Tuỳ chọn | Tác dụng |
| --- | --- |
| `--tools agents\|claude\|all` | Chọn nơi cài, nhiều giá trị cách nhau bằng dấu phẩy (mặc định `all`) |
| `--dir <thư-mục>` | Cài vào thư mục khác thư mục hiện tại |
| `--dry-run` | Chỉ in việc sẽ làm |
| `--uninstall` | Gỡ bản đã cài bằng lệnh này |
| `--global` | Cài toàn cục (xem dưới) |

- Chạy lại lệnh để cập nhật. Nơi đã có thứ khác (không do lệnh này tạo) thì bỏ qua, **không ghi đè**.
- Mặc định riêng: đặt biến môi trường `PROJECT_OS_TOOLS` (ví dụ `agents`); cờ `--tools` luôn thắng.
- Ghim phiên bản: `npx -y @nguyentan0510/project-os@1.5.1`.

### Toàn cục (cho mọi dự án)

```bash
npx -y @nguyentan0510/project-os --global
```

Clone repo về `~/project-os` rồi tạo liên kết (symlink; Windows dùng junction) vào thư mục skill của từng công cụ tìm thấy: `~/.agents/skills/` (luôn có), `~/.claude/skills/`, `~/.gemini/config/skills/`, `~/.codex/skills/`. Cần git. Chạy lại để cập nhật.

<details>
<summary>Không có Node.js: dùng script</summary>

macOS / Linux:

```bash
curl -fsSL https://raw.githubusercontent.com/nguyentan510/project-os/main/install.sh | bash
```

Windows (PowerShell; không chạy `curl | bash` trong `cmd`):

```powershell
irm https://raw.githubusercontent.com/nguyentan510/project-os/main/install.ps1 | iex
```

Script nhận `--all` · `--dry-run` · `--uninstall` · `--dir <chỗ clone>` (PowerShell: `-All` `-DryRun` `-Uninstall` `-Dir`). Muốn xem trước: tải script về, đọc, rồi chạy.

Cài bằng tay: clone repo rồi
`ln -s ~/project-os/.agents/skills/project-os <thư mục skill của công cụ>/project-os`.

</details>

## Cách dùng

| Bạn muốn | Nói với AI / chạy |
| --- | --- |
| Không rành kỹ thuật, không nhớ mã hay tên prompt | Cứ nói bằng lời thường. AI tiếp nhận theo `P-00`: tự tra mã, hỏi lại, nhắc "Tôi hiểu là…" rồi mới làm |
| Bắt đầu dự án mới, áp quy tắc vào repo đang có | *"Dùng skill project-os để bắt đầu dự án này"* |
| Kiểm repo đã đủ để viết code chưa | *"Dùng skill project-os để kiểm toán Ngày 0"* (nên dùng phiên AI khác) |
| Repo đang kẹt, không rõ lỗi | `python pos.py sos` rồi prompt `P-SOS` |
| Đã qua Ngày 0, làm task | AI đọc `AGENTS.md` và theo luồng chung; không cần skill |

Không dùng skill cũng được:

```bash
python ~/project-os/.agents/skills/project-os/scripts/init.py /đường/dẫn/dự-án   # thêm --plan nếu có nhiều Milestone
cd /đường/dẫn/dự-án && git init && python pos.py setup
# điền các chỗ {{…}} theo docs/PROCESS.md mục 3
python ~/project-os/.agents/skills/project-os/scripts/audit.py .
```

Luồng chung cho mọi task:

```
task → code → commit → check → rebase → push → PR → CI → [approve nếu Lane Strict] → merge → done
```

Mỗi task chọn một **Lane** theo rủi ro: **Fast** (câu chữ, lỗi nhỏ), **Normal** (feature, sửa lỗi có logic), **Strict** (chạm Restricted zone, contract, Hot file). Máy xác định được Lane: không có thẻ là Fast, có thẻ là Normal, chạm đường dẫn trong `CODEOWNERS` là Strict. Tên gọi (Milestone, Wave, Task, Lane, Scope, Hot file, Restricted zone…) theo [`docs/GLOSSARY.md`](.agents/skills/project-os/template/docs/GLOSSARY.md).

## Khung Ngày 0 có gì

`init.py` chép các file sau vào dự án, **không ghi đè** file đã có:

| File | Vai trò |
| --- | --- |
| `AGENTS.md` · `CLAUDE.md` | Luật chơi cho mọi AI (`CLAUDE.md` chỉ chứa `@AGENTS.md`) |
| `STATUS.md` | Tiếp theo (thẻ task), đang chặn, ghi chú bàn giao |
| `docs/PROCESS.md` | Bản đầy đủ của quy tắc (13 mục + phụ lục mẫu) |
| `docs/GLOSSARY.md` | Bảng thuật ngữ: một khái niệm một tên |
| `docs/product/BRIEF.md` · `FEATURES.md` | Sản phẩm để làm gì · sổ mã feature |
| `docs/DECISIONS.md` | Nhật ký quyết định `Dxx` |
| `docs/prompts/` | Prompt mẫu cho từng bước (`P-01`…`P-15`, `P-03-MULTI`, `P-SOS`) |
| `pos.py` · `scripts/features.py` | Bộ lệnh dự án, kiểm sổ mã |
| `.githooks/pre-push` | Chặn push khi `check` chưa qua hoặc sửa ngoài Scope |
| `.github/` | CI · `CODEOWNERS` · mẫu PR |
| `Makefile` · `.gitignore` · `.env.example` | Bọc tuỳ chọn · bỏ qua `.env` · mẫu biến môi trường |
| `docs/plan/` (với `--plan`) | ROADMAP + mẫu plan của Milestone |

## `pos.py`: một file thay Make + Bash

Chỉ dùng thư viện chuẩn Python 3.8+, chạy như nhau trên Windows, macOS, Linux (Linux/macOS thường gọi `python3`).

| Lệnh | Việc |
| --- | --- |
| `setup` · `run` · `lint` · `test [F=MAP-07] [L=api]` | Lệnh của dự án, điền ở Ngày 0 |
| `check` | Kiểm sổ mã + quét khoá + lint + test; cổng trước khi push |
| `secrets` | Quét khoá bí mật trong file Git theo dõi (chạy trong `check`) |
| `features [--sync]` | Kiểm mã trong code có trong sổ mã |
| `task T=T-043 N=map-sales [TYPE=fix]` | Tạo worktree + branch từ `main` mới nhất |
| `done T=T-043` | Dọn sau khi PR đã merge (nhận cả merge squash) |
| `drop T=T-043 [CONFIRM=T-043]` | Huỷ task chưa merge |
| `status` | Trạng thái task suy từ thẻ + Git: đang làm, sẵn sàng, chờ, xong |
| `wt` · `wt-clean [APPLY=1]` | Liệt kê · dọn worktree mồ côi |
| `pr [T=T-043]` | Sinh khung báo cáo PR từ diff + kết quả check |
| `scope` | Kiểm file đã sửa nằm trong Scope của thẻ task; không có thẻ thì chỉ qua khi đủ nhỏ để là Lane Fast |
| `plan-check` | Kiểm plan: cùng Wave không trùng Scope, phụ thuộc chỉ trỏ Wave trước |
| `sos` | Cứu hộ: sao lưu vào branch `salvage/sos-*`, khám bệnh (chỉ đọc) |

## Luật cứng

Tám luật duy nhất không linh hoạt; luật nào máy chặn được thì máy chặn.

| # | Luật | Máy chặn bằng |
| --- | --- | --- |
| 1 | Không push thẳng lên `main`; chỉ merge qua PR | Khoá `main` |
| 2 | Không đưa khoá bí mật vào Git, code, tài liệu | `.gitignore` có `.env`; `pos.py secrets` trong `check` |
| 3 | Chỉ push khi `python pos.py check` qua | pre-push hook; CI là cổng cuối |
| 4 | Tiêu đề PR có mã: `<loại>(<mã>): <việc> [T-nnn]` | CI kiểm tiêu đề PR |
| 5 | Mã không bao giờ dùng lại; mã trong code phải có trong sổ mã | `pos.py check` |
| 6 | Builder không tự sửa contract đã khoá, Hot file, Restricted zone | `CODEOWNERS` |
| 7 | PR chạm các đường dẫn ở luật 6 phải có Product Owner (PO) approve | Khoá `main`: bắt buộc Code Owner |
| 8 | Không sửa ngoài Scope của thẻ | pre-push hook + CI chạy `pos.py scope` (bản của `main`); không có thẻ thì phải đủ điều kiện Lane Fast |

## Bảng prompt

Mỗi bước của luồng có một prompt mẫu, gọi nhanh bằng mã, ví dụ *"Chạy P-04 với thẻ T-043"*.

| Mã | Khi dùng | Mã | Khi dùng |
| --- | --- | --- | --- |
| P-01 | Mở phiên | P-09 | Cuối phiên |
| P-02 | Khởi tạo dự án (Ngày 0) | P-10 | Nâng Lane / đổi contract |
| P-03 | Lập plan (một agent) | P-11 | Ghi quyết định |
| P-03-MULTI | Lập plan nhiều agent theo Wave | P-12 | Rà tài liệu |
| P-04 | Giao task | P-13 | Nghiệm thu Milestone |
| P-05 | Sửa nhanh (Lane Fast) | P-14 | Khẩn cấp (production) |
| P-06 | Sửa lỗi | P-15 | Kiểm toán Ngày 0 |
| P-07 | Review Restricted zone | P-SOS | Bị kẹt, cần cứu hộ |
| P-08 | Merge và dọn | P-00 | PO nói bằng lời thường, không kèm mã |

Thứ tự trong một Milestone: `P-01 → P-03 / P-03-MULTI → P-04 · P-05 · P-06 → P-07 → P-08 → P-09`, hết Milestone `P-13`. Dự án mới: `P-02 → P-15 → duyệt → T-001`. Chi tiết ở [`docs/PROCESS.md`](.agents/skills/project-os/template/docs/PROCESS.md) mục 13.

## Bật bảo vệ trên GitHub

Làm bằng tay, một lần cho mỗi dự án: **Settings → Branches → Add rule** cho `main`:

- [x] Require a pull request before merging
- [x] Require status checks to pass: `check`, `pr-title`
- [x] Require branches to be up to date before merging
- [x] Require review from Code Owners (sau khi thay `@product-owner` trong `.github/CODEOWNERS`)

Luật 6–8 chỉ kín khi bật mục cuối: không có nó, một PR vẫn sửa được chính `pos.py` hoặc `ci.yml`. GitHub không cho tác giả approve PR của mình, nên AI cần mở PR bằng tài khoản khác PO (tài khoản bot hoặc GitHub App).

## Yêu cầu

- `git` và Python 3.8+ (chỉ thư viện chuẩn; không cần `make` hay `bash`).
- Node.js ≥ 16.7 nếu cài bằng `npx`.
- `gh` (tuỳ chọn): `pos.py done` hỏi thẳng GitHub trạng thái PR; không có `gh` thì so nội dung branch với `main` để nhận merge squash.
- Claude Code từ 2.1.277 tự đọc `AGENTS.md`; `CLAUDE.md` trong khung chỉ có dòng `@AGENTS.md` để chạy được cả bản cũ.

## Cấu trúc repo

```
.agents/skills/project-os/        skill (định dạng SKILL.md chung)
├── SKILL.md                      AI đọc: init · Ngày 0 · audit
├── scripts/init.py               chép khung vào dự án, không ghi đè
├── scripts/audit.py              kiểm toán Ngày 0 phần máy kiểm được
├── template/                     khung Ngày 0 (chép nguyên vào dự án)
└── optional/docs/plan/           ROADMAP + mẫu plan của Milestone (init.py --plan)
.claude/skills/project-os         liên kết tới thư mục skill trên (cho Claude Code)
bin/project-os.js                 trình cài qua npx
install.sh · install.ps1          trình cài toàn cục không cần Node.js
tests/                            test cho init, audit, pos.py, features.py
```

## Phát triển repo này

- Test công cụ (chỉ thư viện chuẩn Python): `python -m unittest discover -s tests`. CI ở `.github/workflows/test.yml`.
- Test đánh dấu `expectedFailure` là lỗi đã biết, chưa sửa; sửa xong thì bỏ dấu đó.

## Giấy phép

[MIT](LICENSE) © 2026 nguyentan510

# MODULES · Ranh giới module và contract

Repo này không có `src/<module>/` (D05), nên ranh giới module và contract ghi ở đây thay cho README và `contract.*` từng module (D13). Mã module theo `docs/product/FEATURES.md`. Đường dẫn rút gọn: `skill/` = `.agents/skills/project-os/`, `khung/` = `.agents/skills/project-os/template/`.

## Module

| Module | Chức năng | File | Vào | Ra | Phụ thuộc |
| --- | --- | --- | --- | --- | --- |
| INS · Cài đặt | Đưa skill vào một dự án hoặc vào máy | `bin/project-os.js`, `install.sh`, `install.ps1`, `package.json` | Cờ dòng lệnh, biến `PROJECT_OS_TOOLS` | Thư mục skill trong dự án hoặc liên kết toàn cục | C9 |
| DAY · Ngày 0 | Chép khung, dẫn 7 bước, kiểm toán | `skill/SKILL.md`, `skill/scripts/init.py`, `skill/scripts/audit.py`, `skill/optional/` | Thư mục dự án | Khung Ngày 0; bảng Đạt / Chưa | C2, C3, C4, C9 |
| RUN · Bộ lệnh dự án | Điểm vào `pos.py`; `setup`, `run`, `lint`, `test`, `check` | `khung/pos.py` (phần lệnh cơ bản), `khung/Makefile` | Tên lệnh, `KEY=VALUE`, `*_CMD` trong file | Mã thoát, dòng "check: qua" | C6, C7; gọi REG, GRD |
| TSK · Vòng đời task | `task`, `done`, `drop`, `wt`, `wt-clean`, `status`, `plan-check`, `pr`, `sos` | `khung/pos.py` (phần worktree, plan, status, pr, sos) | Thẻ task, branch, worktree, lịch sử `main` | Worktree, branch, báo cáo | C1, C4, C5, C8 |
| GRD · Máy chặn | `scope`, giới hạn việc không thẻ, `secrets`, hook, CI, CODEOWNERS | `khung/pos.py` (phần scope, secrets), `khung/.githooks/`, `khung/.github/` | Diff so với `main`, thẻ trên `main`, `AGENTS.md` trên `main` | Mã thoát 0 hoặc 1 kèm lý do | C1, C4, C6, C7, C8 |
| REG · Sổ mã | Kiểm sổ mã, ghi cột Test, kiểm biến môi trường | `khung/scripts/features.py`, `khung/docs/product/FEATURES.md` | Sổ mã, toàn bộ file trong repo, `.env.example` | Lỗi, cảnh báo, sổ mã đã ghi cột Test | C2 |
| POL · Lớp PO | Tiếp nhận lời thường, `find`, nhóm "Chờ PO", Tóm tắt cho PO | `khung/pos.py` (phần find, Chờ PO), `khung/docs/prompts/P-00.md`, PROCESS mục 14 | Lời của PO; sổ mã, DECISIONS, thẻ, STATUS | Kết quả tìm; danh sách việc chờ PO | C1, C2, C3, C5 |
| DOC · Bộ quy tắc | Luật, vai, Lane, prompt, thuật ngữ, các file mẫu | `khung/docs/`, `khung/AGENTS.md`, `khung/STATUS.md`, `khung/.github/pull_request_template.md` | — | Tài liệu mọi AI đọc | — (là chủ của C3, C4, C5) |
| EVL · Đo lường | Ba bộ thử ứng với ba chỉ số trong BRIEF | chưa có | Kịch bản thử | Bảng chấm | Dùng mọi module qua giao diện công khai |

Nhiều module cùng nằm trong `khung/pos.py`. Ranh giới giữa chúng là các khối có tiêu đề `# ── … ──` trong file; module chỉ gọi nhau qua các hàm và định dạng ghi ở phần contract dưới đây.

## Contract

Contract là thứ một module đưa ra để module khác dựa vào. Sửa một contract là việc Lane Strict: liệt kê mọi module dùng nó trước khi sửa.

| Mã | Contract | Chủ | Ai dùng | Nội dung |
| --- | --- | --- | --- | --- |
| C1 | Định dạng thẻ task | TSK | GRD, POL | Dòng đầu `- [ ] T-nnn · <tiêu đề>` (`[x]` là đã xong); các dòng sau, tới dòng trống hoặc thẻ kế, mang trường `Tên: giá trị`. Trường máy đọc: `Wave: W<n>`, `Scope:` (mẫu đường dẫn cách nhau bằng dấu phẩy hoặc khoảng trắng), `Phụ thuộc:` (các `T-nnn`), `Xong khi:`. Thẻ nằm ở `docs/plan/*.md` hoặc `STATUS.md`; trùng số thì plan thắng |
| C2 | Định dạng sổ mã | REG | POL, DAY | Module khai bằng `### MÃ · Tên` (MÃ 2–6 chữ hoa). Bảng có cột đầu `Mã` (`MÃ-nn`), cột cuối là trạng thái (`dự kiến`, `dùng`, `bỏ (Dxx)`, `để sau`); cột Test và cột `Tên gọi` tìm theo dòng tiêu đề, không theo vị trí |
| C3 | Định dạng DECISIONS | DOC | POL, DAY | Bảng quyết định có cột `Mã` (`Dnn`); bảng dưới `## Còn mở` có cột `Mã` (`Q-…`), `Câu hỏi`, cột bắt đầu bằng `Lựa chọn`, `Chờ ai` |
| C4 | Mục đường dẫn trong AGENTS.md | DOC | GRD, TSK, DAY | Tiêu đề bắt đầu bằng `## Hot file` và `## Restricted zone`; các dòng dưới là mẫu đường dẫn cách nhau bằng dấu phẩy hoặc khoảng trắng; dòng còn `{{` bị bỏ qua. GRD đọc bản trên `main` |
| C5 | Mục của STATUS.md | DOC | POL, TSK | Tiêu đề `## Đang chặn` (mỗi dòng không rỗng, không mở đầu bằng `(`, là một việc bị chặn); thẻ task theo C1 |
| C6 | Giao diện lệnh `pos.py` | RUN | GRD (hook, CI), mọi prompt | `python pos.py <lệnh> [KEY=VALUE…] [từ khác…]`; mã thoát 0 là qua, 1 là lỗi, 2 là lệnh lạ; `check` in đúng dòng `check: qua` khi qua. Tên lệnh không đổi nghĩa |
| C7 | Biến môi trường | RUN, INS | GRD (CI) | `PROJECT_OS_ROOT` (gốc repo khi `pos.py` đặt ngoài repo), `PROJECT_OS_BRANCH` (tên branch của PR trong CI; tên cũ `POS_BRANCH` vẫn nhận), `PROJECT_OS_F`, `PROJECT_OS_L`, `PROJECT_OS_TOOLS` (nơi cài mặc định) |
| C8 | Tên branch và tiêu đề PR | TSK | GRD, POL | Branch `<loại>/<T-nnn hoặc MÃ-nn>-<slug>`; tiêu đề PR `<loại>(<mã>): <việc> [T-nnn]`, `chore:` không cần mã. `status` coi task là xong khi `main` có commit mang `[T-nnn]` |
| C9 | Khung được chép | DAY | INS | `init.py` chép nguyên `template/` vào dự án, không ghi đè; `gitignore.template` thành `.gitignore`; `--plan` chép thêm `optional/`. Gói npm chứa đúng `bin`, hai script cài và `.agents/skills/project-os` |

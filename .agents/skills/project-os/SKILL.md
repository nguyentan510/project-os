---
name: project-os
description: Thiết lập và kiểm toán quy trình Project OS (AGENTS.md, STATUS, sổ mã FEATURES, DECISIONS, worktree, luật cứng, bảng prompt) cho một repo. Dùng khi người dùng muốn bắt đầu dự án mới, áp quy tắc Project OS vào repo đang có, làm "Ngày 0", hoặc kiểm toán Ngày 0 trước khi viết code.
---

# Project OS

Bộ quy tắc để mọi AI (Claude Code, Codex, Antigravity…) mở repo là biết: đang làm gì, đã làm gì, sửa thì bắt đầu từ đâu. Bản đầy đủ: `template/docs/PROCESS.md`. Đường dẫn dưới đây tính từ thư mục chứa file SKILL.md này.

## Chọn việc

| Người dùng muốn | Làm |
| --- | --- |
| Bắt đầu dự án mới / áp quy tắc vào repo | **Init** rồi **Ngày 0** |
| Kiểm repo đã đủ để viết code chưa | **Audit** |
| Đã qua Ngày 0, cần làm task | Đọc `AGENTS.md` của repo và theo luồng chung; không cần skill này |

## Init

1. Hỏi thư mục dự án nếu chưa rõ (mặc định: thư mục hiện tại).
2. Chạy `bash scripts/init.sh <thư-mục>`; thêm `--plan` nếu dự án đã có nhiều mốc.
3. Script không ghi đè file đã có. Báo lại danh sách file `tạo` / `giữ`; file `giữ` mà khác mẫu thì đề xuất cách gộp, không tự sửa.

## Ngày 0

Làm đúng 7 bước ở `docs/PROCESS.md` mục 3 (prompt `docs/prompts/P-02.md`). Sau **mỗi** bước, trình đầu ra và **chờ người dùng duyệt** rồi mới sang bước sau:

1. BRIEF → 2. FEATURES → 3. DECISIONS → 4. module + contract → 5. AGENTS + STATUS → 6. khung repo + máy chặn → 7. kiểm toán.

Luật khi làm:
- Thay mọi chỗ `{{…}}` bằng nội dung thật của dự án; không để lại ví dụ mẫu.
- Không viết code tính năng trong Ngày 0. Code đầu tiên là T-001 (khung chạy được), sau khi qua kiểm toán.
- Cần thông tin người dùng chưa cho (người dùng, chỉ số thành công, công nghệ…): hỏi, không tự đoán.
- Vùng cấm và file nóng: ghi một danh sách trong AGENTS.md, chép đúng sang `.github/CODEOWNERS`.

## Audit

1. Chạy `bash scripts/audit.sh <thư-mục>`: phần máy kiểm được (file, chỗ chưa điền, BRIEF, FEATURES, DECISIONS, module, hook, `.env`, `make check`).
2. Phần còn lại theo `docs/prompts/P-15.md`, nên chạy ở **phiên AI khác** với phiên đã làm Ngày 0. Với từng ô: Đạt / Chưa + bằng chứng (file, dòng). Không sửa gì.
3. Kết luận: qua cổng hay chưa, còn thiếu gì. Qua cổng thì đề xuất ghi `Dxx "Qua cổng Ngày 0"` và giao T-001.

## Không làm

- Không ghi đè, xoá hay đổi tên file có sẵn của người dùng khi chưa hỏi.
- Không bật cài đặt GitHub thay người dùng (khóa main, Code Owners): chỉ hướng dẫn.
- Không ghi khoá bí mật vào bất kỳ file nào.

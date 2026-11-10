---
name: project-os
description: Thiết lập và kiểm toán quy trình Project OS (AGENTS.md, STATUS, sổ mã FEATURES, DECISIONS, GLOSSARY, worktree, luật cứng, bảng prompt) cho một repo. Dùng khi người dùng muốn bắt đầu dự án mới, áp quy tắc Project OS vào repo đang có, làm "Ngày 0", hoặc kiểm toán Ngày 0 trước khi viết code.
---

# Project OS

Bộ quy tắc để mọi AI (Claude Code, Codex, Antigravity…) mở repo, không cần lịch sử chat, là biết: đang ở đâu, vì sao như vậy, cái gì không được đụng, làm tiếp từ đâu và kiểm chứng bằng gì. Bản đầy đủ: `template/docs/PROCESS.md`; thuật ngữ: `template/docs/GLOSSARY.md`. Đường dẫn dưới đây tính từ thư mục chứa file SKILL.md này. "Product Owner (PO)" là người đang làm việc với bạn.

## Chọn việc

| PO muốn | Làm |
| --- | --- |
| Bắt đầu dự án mới / áp quy tắc vào repo | **Init** rồi **Ngày 0** |
| Kiểm repo đã đủ để viết code chưa | **Audit** |
| Repo đang kẹt / không rõ lỗi | Chạy `python pos.py sos` rồi prompt `docs/prompts/P-SOS.md`; chờ PO chọn A/B |
| Đã qua Ngày 0, cần làm task | Đọc `AGENTS.md` của repo và theo luồng chung; không cần skill này |

## Init

1. Hỏi thư mục dự án nếu chưa rõ (mặc định: thư mục hiện tại).
2. Chạy `python scripts/init.py <thư-mục>`; thêm `--plan` nếu dự án đã có nhiều Milestone.
3. Script không ghi đè file đã có. Báo lại danh sách file `tạo` / `giữ`; file `giữ` mà khác mẫu thì đề xuất cách hợp nhất, không tự sửa.

## Ngày 0

Làm đúng 7 bước ở `docs/PROCESS.md` mục 3 (prompt `docs/prompts/P-02.md`). Sau **mỗi** bước, trình đầu ra và **chờ PO duyệt** rồi mới sang bước sau:

1. BRIEF → 2. FEATURES → 3. DECISIONS → 4. module + contract → 5. AGENTS + STATUS → 6. khung repo + máy chặn → 7. kiểm toán.

Luật khi làm:
- Thay mọi chỗ `{{…}}` bằng nội dung thật của dự án; không để lại ví dụ mẫu.
- Không viết code feature trong Ngày 0. Code đầu tiên là T-001 (khung chạy được), sau khi qua kiểm toán.
- Dùng đúng tên trong `docs/GLOSSARY.md`; thuật ngữ riêng của dự án thêm vào mục cuối file đó.
- Cần thông tin PO chưa cho (người dùng sản phẩm, chỉ số thành công, công nghệ…): hỏi, không tự đoán.
- Restricted zone và Hot file: ghi một danh sách trong AGENTS.md, chép đúng sang `.github/CODEOWNERS`.
- Nhiều agent song song: lập plan bằng `docs/prompts/P-03-MULTI.md` (Wave W0 → W1 → W2), chạy `python pos.py plan-check` trước khi PO duyệt; chọn cách đăng ký module tự động ở Ngày 0 để Hot file không phải sửa tay (PROCESS.md mục 11).

## Audit

1. Chạy `python scripts/audit.py <thư-mục>`: phần máy kiểm được (file, chỗ chưa điền, BRIEF, FEATURES, DECISIONS, module, hook, `.env`, `python pos.py check`).
2. Phần còn lại theo `docs/prompts/P-15.md`, nên chạy ở **phiên AI khác** với phiên đã làm Ngày 0. Với từng ô: Đạt / Chưa + bằng chứng (file, dòng). Không sửa gì.
3. Kết luận: qua cổng hay chưa, còn thiếu gì. Qua cổng thì đề xuất ghi `Dxx "Qua cổng Ngày 0"` và giao T-001.

## Không làm

- Không ghi đè, xoá hay đổi tên file có sẵn của PO khi chưa hỏi.
- Không bật cài đặt GitHub thay PO (khoá main, Code Owners): chỉ hướng dẫn.
- Không ghi khoá bí mật vào bất kỳ file nào.

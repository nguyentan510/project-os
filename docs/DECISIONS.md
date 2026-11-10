# DECISIONS · Quyết định

Mỗi lựa chọn kỹ thuật một dòng. Duyệt = `PO` (quyết định lớn) hoặc `AI` (quyết định nhỏ, PROCESS.md mục 12).

| Mã | Ngày | Quyết định | Lý do | Mã liên quan | Duyệt |
| --- | --- | --- | --- | --- | --- |
| D01 | 2026-11-10 | Ngôn ngữ: công cụ viết bằng Python 3.8+ chỉ dùng thư viện chuẩn; trình cài viết bằng Node.js không phụ thuộc gói ngoài | Chạy như nhau trên Windows, macOS, Linux mà không phải cài thêm gì | RUN-01, INS-01 | PO |
| D02 | 2026-11-10 | Lưu trữ: không có cơ sở dữ liệu; mọi trạng thái nằm trong file markdown của repo và trong Git | AI nào mở repo cũng đọc được; lịch sử có sẵn trong Git | TSK-04, REG-01 | PO |
| D03 | 2026-11-10 | Nơi phát hành: gói npm `@nguyentan0510/project-os` và repo GitHub; CI chạy trên GitHub Actions | Cài bằng một lệnh; không cần hạ tầng riêng | INS-01, INS-02, GRD-05 | PO |
| D04 | 2026-11-10 | Xác thực: Project OS không có đăng nhập riêng; dùng quyền Git và GitHub sẵn có của PO | Không giữ khoá bí mật nào; ít thứ để lộ | GRD-06 | PO |
| D05 | 2026-11-10 | Cấu trúc: skill nằm ở `.agents/skills/project-os/` gồm `template/` (khung chép vào dự án), `scripts/` (init, audit), `optional/`; trình cài ở `bin/`; test ở `tests/`. Module trong sổ mã là nhóm chức năng, không phải thư mục `src/<module>/` | Đây là định dạng skill chung mà các công cụ AI đọc được; repo không phải một ứng dụng | DAY-01, DOC-02 | PO |
| D06 | 2026-11-10 | Khung ở gốc repo (`pos.py`, `scripts/`, `.githooks/`, `docs/PROCESS.md`, `docs/GLOSSARY.md`, `docs/prompts/`) là bản chép từ `template/`. Bản gốc là `template/`: sửa ở đó trước, rồi chép ra gốc; một test giữ hai bản khớp nhau | Repo phải tự dùng đúng thứ nó phát hành; không có test thì hai bản sẽ lệch | DOC-01, DOC-02, DOC-03 | PO |
| D07 | 2026-11-10 | Chế độ vai: Một AI | Một PO làm với một phiên AI tại một thời điểm; chưa cần tách Orchestrator và Builder | DOC-02 | PO |
| D08 | 2026-11-10 | Ngôn ngữ: tài liệu, prompt, thông báo lệnh bằng tiếng Việt; mã, tên lệnh, tên vai, tên Lane bằng tiếng Anh | Người dùng hiện tại nói tiếng Việt; phần máy đọc giữ tiếng Anh cho ổn định | DOC-03 | PO |
| D09 | 2026-11-10 | Test: `python -m unittest discover -s tests`, chỉ thư viện chuẩn | Cùng lý do với D01 | RUN-01 | AI |
| D10 | 2026-11-10 | Phiên bản: một số phiên bản duy nhất, lấy từ `package.json`; dòng "Phiên bản" trong PROCESS.md ghi theo số đó | Hiện PROCESS ghi 1.1 trong khi gói là 1.5.1; hai số gây nhầm | INS-01, DOC-02 | AI |
| D11 | 2026-11-10 | AI chưa cần tài khoản riêng để mở PR: ở chế độ Một AI, PO tự merge. Xem lại khi chuyển sang nhiều Builder hoặc khi bật bắt buộc Code Owner | Chưa có PR Lane Strict nào cần một người khác tác giả approve | GRD-06 | PO |
| D12 | 2026-11-10 | Chưa dùng công cụ lint: `LINT_CMD = "none"`, `check` in cảnh báo mỗi lần chạy | Giữ đúng D01 (không phụ thuộc ngoài); cảnh báo nhắc đây là việc còn nợ | RUN-01 | PO |
| D13 | 2026-11-10 | Kiểm toán Ngày 0 của repo này chấp nhận lệch ở các ô "module có README" và "module có contract": ranh giới module và contract ghi ở `docs/product/MODULES.md` thay cho `src/<module>/`. Sửa `audit.py` cho repo có cấu trúc riêng là việc của DAY-04 | Không viết code trong Ngày 0; repo này không có `src/` (D05) | DAY-03, DAY-04 | PO |

## Còn mở

| Mã | Câu hỏi | Lựa chọn (khuyến nghị đứng đầu) | Chờ ai |
| --- | --- | --- | --- |

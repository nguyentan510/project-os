# STATUS · 2026-11-10 · —

## Tiếp theo
- [ ] T-004 · GRD-04 · hook kiểm nhanh, gộp job CI chạy trùng
      Yêu cầu gốc: "Giảm chi phí trước"
      Mục tiêu:  push không còn chờ 3 phút rưỡi: dự án đặt `HOOK_TESTS = False` thì hook chỉ kiểm sổ mã, quét khoá, lint và Scope,
                 còn bộ test đầy đủ chạy ở CI; CI của repo này chạy bộ test một lần thay vì hai
      Lane:      Strict
      Scope:     .agents/skills/project-os/template/pos.py, pos.py, .agents/skills/project-os/template/.githooks/*, .githooks/*, .github/workflows/*, tests/*, .agents/skills/project-os/template/docs/PROCESS.md, docs/PROCESS.md, .agents/skills/project-os/template/AGENTS.md, AGENTS.md, README.md, docs/DECISIONS.md
      Xong khi:  push một thay đổi nhỏ trên repo này, hook chạy xong dưới 30 giây; PR chỉ còn hai job CI (`test`, `pr-title`)
                 và bộ test chạy đúng một lần; python pos.py check qua

Chưa viết thẻ (PO chọn thứ tự):
- Ba bộ thử ứng với ba chỉ số trong BRIEF (EVL-01, EVL-02, EVL-03).
- `find` khớp theo từ thay vì chuỗi con: gõ "do luong" đang ra nhầm "Bảng prompt" (POL-02).
- Gắn mã feature vào test hiện có, để cột Test của sổ mã tự ghi được (REG-02).
- Thẻ có `Scope:` xuống nhiều dòng: máy chỉ đọc dòng đầu và không báo gì; cần đọc được dòng nối hoặc `plan-check` báo lỗi (GRD-01).
- PR Lane Strict được một phiên AI khác review theo P-07 trước khi PO merge.

## Đang chặn
- Phát hành 1.6.0 lên npm: chờ PO đăng nhập npm và chạy `npm publish` (T-002 đã merge, gói trên npm vẫn là 1.5.1).

## Ghi chú bàn giao
T-001, T-002, T-003 đã xong (PR 11, 13, 12). Ngày 0 đã vào main (PR 9); kiểm toán máy Đạt 29, Chưa 18, lệch đã chấp nhận (D13).
Chưa làm: kiểm toán theo P-15 bằng một phiên AI khác; chưa ghi quyết định "Qua cổng Ngày 0".
PO cần tự làm trên GitHub: thêm `pr-title` vào check bắt buộc của main (sau T-004 thì `test` đã gồm cả `check`).

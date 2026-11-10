# STATUS · 2026-11-10 · —

## Tiếp theo
- [ ] T-001 · DOC-02 · giữ khung ở gốc khớp bản gốc
      Yêu cầu gốc: "Áp lên repo này"
      Mục tiêu:  một test giữ các bản chép ở gốc repo khớp với `template/` (D06); PROCESS ghi đúng số phiên bản của gói (D10)
      Lane:      Strict
      Scope:     tests/*, .agents/skills/project-os/template/docs/PROCESS.md, docs/PROCESS.md
      Xong khi:  sửa một chữ trong docs/PROCESS.md ở gốc mà không sửa template thì `check` báo lỗi và chỉ ra file lệch;
                 python pos.py check qua

Sau T-001, chưa viết thẻ (PO chọn thứ tự):
- Gắn mã feature vào test hiện có, để cột Test của sổ mã tự ghi được (REG-02).
- `find` khớp theo từ thay vì chuỗi con: gõ "do luong" đang ra nhầm "Bảng prompt" (POL-02).
- Ba bộ thử ứng với ba chỉ số trong BRIEF (EVL-01, EVL-02, EVL-03).

## Đang chặn
(trống)

## Ghi chú bàn giao
Ngày 0 của repo này đang ở bước 5/7, chưa commit. Còn bước 6 (điền lệnh, CODEOWNERS, `.env.example`, CI) và bước 7 (kiểm toán).
Kiểm toán sẽ báo "Chưa" ở các ô module README và contract: lệch đã chấp nhận (D13).

# STATUS · 2026-11-10 · —

## Tiếp theo
- [ ] T-001 · DOC-02 · giữ khung ở gốc khớp bản gốc
      Yêu cầu gốc: "Áp lên repo này"
      Mục tiêu:  một test giữ các bản chép ở gốc repo khớp với `template/` (D06); PROCESS ghi đúng số phiên bản của gói (D10)
      Lane:      Strict
      Scope:     tests/*, .agents/skills/project-os/template/docs/PROCESS.md, docs/PROCESS.md
      Xong khi:  sửa một chữ trong docs/PROCESS.md ở gốc mà không sửa template thì `check` báo lỗi và chỉ ra file lệch;
                 python pos.py check qua

- [ ] T-002 · INS-01 · phát hành 1.6.0
      Yêu cầu gốc: "Xử lý các hạng mục tồn" (gói npm vẫn là 1.5.1)
      Mục tiêu:  tăng phiên bản gói lên 1.6.0 để người cài qua npx nhận máy chặn mới, vai và Lớp PO; PROCESS ghi cùng số (D10)
      Lane:      Strict
      Scope:     package.json, README.md, .agents/skills/project-os/template/docs/PROCESS.md, docs/PROCESS.md
      Phụ thuộc: T-001
      Xong khi:  sau khi PO chạy `npm publish`, lệnh `npx -y @nguyentan0510/project-os@1.6.0` cài được bản mới;
                 python pos.py check qua

Sau T-002, chưa viết thẻ (PO chọn thứ tự):
- Gắn mã feature vào test hiện có, để cột Test của sổ mã tự ghi được (REG-02).
- `find` khớp theo từ thay vì chuỗi con: gõ "do luong" đang ra nhầm "Bảng prompt" (POL-02).
- Ba bộ thử ứng với ba chỉ số trong BRIEF (EVL-01, EVL-02, EVL-03).

## Đang chặn
(trống)

## Ghi chú bàn giao
Ngày 0 đã vào main (PR 9). Kiểm toán máy: Đạt 29, Chưa 18; cả 18 là ô module README và contract, lệch đã chấp nhận (D13).
Chưa làm: kiểm toán theo P-15 bằng một phiên AI khác; chưa ghi quyết định "Qua cổng Ngày 0".
PO cần tự làm trên GitHub: thêm `check` và `pr-title` vào check bắt buộc của main. Phát hành npm cần PO đăng nhập và chạy `npm publish`.

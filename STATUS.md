# STATUS · 2026-11-10 · —

## Tiếp theo
- [ ] T-006 · DOC-02 · Reviewer cho PR Lane Strict ở chế độ Một AI
      Yêu cầu gốc: "Đồng ý, thực thi lần lượt" (đề xuất: PR Strict phải có một phiên AI khác thẩm định trước khi PO merge)
      Mục tiêu:  PR Lane Strict phải có mục "Kết luận Reviewer" do một phiên AI khác viết theo P-07, CI đỏ nếu thiếu; tài liệu chỉ còn một câu trả lời cho "ai merge ở chế độ Một AI" (PO, theo D11)
      Lane:      Strict
      Scope:     .agents/skills/project-os/template/pos.py, pos.py, tests/*, .agents/skills/project-os/template/docs/PROCESS.md, docs/PROCESS.md, .agents/skills/project-os/template/docs/prompts/P-07.md, docs/prompts/P-07.md, .agents/skills/project-os/template/AGENTS.md, AGENTS.md, .agents/skills/project-os/template/.github/*, .github/*, .agents/skills/project-os/template/docs/GLOSSARY.md, docs/GLOSSARY.md, README.md, docs/product/FEATURES.md, docs/DECISIONS.md
      Phụ thuộc: T-005
      Xong khi:  PO mở một PR Lane Strict thiếu mục "Kết luận Reviewer": CI đỏ và nói rõ thiếu gì; điền mục đó thì CI xanh; python pos.py check qua

- [ ] T-007 · EVL-03 · bộ thử vi phạm
      Yêu cầu gốc: "Đồng ý, thực thi lần lượt" (đo chỉ số thứ ba trong BRIEF: máy chặn bắt được 10/10 vi phạm cố ý)
      Mục tiêu:  một lệnh dựng dự án tạm, thử 10 kiểu vi phạm cố ý (sửa ngoài Scope, lộ khoá, sửa máy chặn, xoá test…) và in bảng bắt được bao nhiêu
      Lane:      Normal
      Scope:     evals/*, tests/*, docs/product/FEATURES.md, README.md
      Phụ thuộc: T-006
      Xong khi:  PO chạy một lệnh, thấy bảng 10 dòng, mỗi dòng một kiểu vi phạm kèm "bắt được" hay "lọt"; python pos.py check qua

- [ ] T-008 · GRD-09 · vá các điểm Reviewer nêu ở PR 18 và PR 19
      Yêu cầu gốc: "Đồng ý, thực thi lần lượt" (Reviewer của hai PR khuyến nghị gom các điểm nên sửa vào một thẻ)
      Mục tiêu:  AGENTS.md thành file máy chặn (không gỡ được Hot file, Restricted zone bằng PR không thẻ); review-check lấy dòng "Kết luận:" cuối cùng trong mục, chặn "Trả lại", và gắn kết luận với commit đã review; bước review-check xuống cuối job CI; bảo toàn test không đếm file tài liệu và bỏ qua submodule; tài liệu ghi đúng chuỗi "Kết luận: Đạt"; P-05 không còn để AI tự merge
      Lane:      Strict
      Scope:     .agents/skills/project-os/template/pos.py, pos.py, tests/*, .agents/skills/project-os/template/docs/PROCESS.md, docs/PROCESS.md, .agents/skills/project-os/template/docs/prompts/P-05.md, docs/prompts/P-05.md, .agents/skills/project-os/template/AGENTS.md, AGENTS.md, .agents/skills/project-os/template/.github/*, .github/*, README.md, docs/product/FEATURES.md, docs/DECISIONS.md
      Phụ thuộc: T-006
      Xong khi:  PO dán vào mô tả một PR Lane Strict mục Kết luận Reviewer có "Kết luận: Trả lại" kèm một dòng "Kết luận: Đạt" ở dưới: CI đỏ; python pos.py check qua

Chưa viết thẻ (PO chọn thứ tự):
- Hai bộ thử còn lại ứng với BRIEF: AI phiên trắng (EVL-01), tiếp nhận 8 câu (EVL-02).
- `find` khớp theo từ thay vì chuỗi con: gõ "do luong" đang ra nhầm "Bảng prompt" (POL-02).
- Gắn mã feature vào test hiện có, để cột Test của sổ mã tự ghi được (REG-02).
- Thẻ có `Scope:` xuống nhiều dòng: máy chỉ đọc dòng đầu và không báo gì; cần đọc được dòng nối hoặc `plan-check` báo lỗi (GRD-01).

## Đang chặn
- Phát hành 1.6.0 lên npm: chờ PO đăng nhập npm và chạy `npm publish` (T-002 đã merge, gói trên npm vẫn là 1.5.1).

## Ghi chú bàn giao
T-001 đến T-005 đã xong (PR 11, 13, 12, 16, 18). Ngày 0 đã vào main (PR 9); kiểm toán máy Đạt 29, Chưa 18, lệch đã chấp nhận (D13).
Chưa làm: kiểm toán theo P-15 bằng một phiên AI khác; chưa ghi quyết định "Qua cổng Ngày 0".
PO cần tự làm trên GitHub: thêm `pr-title` vào check bắt buộc của main (sau T-004 thì `test` đã gồm cả `check`).

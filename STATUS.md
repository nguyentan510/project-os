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

- [ ] T-005 · GRD-08 · bảo toàn test
      Yêu cầu gốc: "Đồng ý, thực thi lần lượt" (đề xuất: chặn việc làm check xanh bằng cách xoá test)
      Mục tiêu:  thay đổi xoá file test hoặc làm giảm số test so với main thì bị chặn, trừ khi thẻ ghi đích danh file đó trong Scope
      Lane:      Strict
      Scope:     .agents/skills/project-os/template/pos.py, pos.py, tests/*, .agents/skills/project-os/template/docs/PROCESS.md, docs/PROCESS.md, .agents/skills/project-os/template/AGENTS.md, AGENTS.md, README.md, docs/product/FEATURES.md, docs/DECISIONS.md
      Phụ thuộc: T-004
      Xong khi:  PO xoá thử một file trong tests/ trên một branch rồi push: bị chặn kèm tên file bị xoá; python pos.py check qua

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

Chưa viết thẻ (PO chọn thứ tự):
- Hai bộ thử còn lại ứng với BRIEF: AI phiên trắng (EVL-01), tiếp nhận 8 câu (EVL-02).
- `find` khớp theo từ thay vì chuỗi con: gõ "do luong" đang ra nhầm "Bảng prompt" (POL-02).
- Gắn mã feature vào test hiện có, để cột Test của sổ mã tự ghi được (REG-02).
- Thẻ có `Scope:` xuống nhiều dòng: máy chỉ đọc dòng đầu và không báo gì; cần đọc được dòng nối hoặc `plan-check` báo lỗi (GRD-01).

## Đang chặn
- Phát hành 1.6.0 lên npm: chờ PO đăng nhập npm và chạy `npm publish` (T-002 đã merge, gói trên npm vẫn là 1.5.1).

## Ghi chú bàn giao
T-001, T-002, T-003 đã xong (PR 11, 13, 12). Ngày 0 đã vào main (PR 9); kiểm toán máy Đạt 29, Chưa 18, lệch đã chấp nhận (D13).
Chưa làm: kiểm toán theo P-15 bằng một phiên AI khác; chưa ghi quyết định "Qua cổng Ngày 0".
PO cần tự làm trên GitHub: thêm `pr-title` vào check bắt buộc của main (sau T-004 thì `test` đã gồm cả `check`).

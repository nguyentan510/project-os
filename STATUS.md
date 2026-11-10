# STATUS · 2026-11-10 · —

## Tiếp theo
- [ ] T-009 · REG-01 · kiểm sổ mã không quét file của skill cài trong dự án
      Yêu cầu gốc: "Viết thẻ" (phát hiện khi cài thử vào dự án eDMS: kiểm sổ mã quét cả file mẫu của skill trong `.agents/` và `.claude/`, báo 4 lỗi; AI làm Ngày 0 phải sửa `scripts/features.py` mới qua)
      Mục tiêu:  dự án cài skill theo dự án (INS-01) chạy kiểm sổ mã không bị báo lỗi vì mã ví dụ và biến môi trường nằm trong file của skill (ví dụ `ORD-09` trong PROCESS mẫu khi dự án khai module ORD; `PROJECT_OS_ROOT`, `PROJECT_OS_BRANCH`, `POS_BRANCH` trong `pos.py` mẫu), không ai phải sửa file máy chặn; repo này vẫn quét code của chính skill như hiện nay
      Lane:      Strict
      Scope:     .agents/skills/project-os/template/scripts/features.py, scripts/features.py, tests/*, docs/product/FEATURES.md, README.md
      Xong khi:  PO cài skill theo dự án vào một thư mục tạm, chép khung, khai module ORD trong sổ mã rồi chạy `python pos.py features`: lỗi 0 mà không sửa file nào của khung; python pos.py check qua
      Ghi chú:   bản cài có file `.project-os-install` trong thư mục skill, bản nguồn ở repo này thì không: có thể dùng để phân biệt. Bỏ qua cả `.agents/` và `.claude/` (cách AI ở eDMS đã vá) sẽ làm repo này thôi quét code của skill

- [ ] T-008 · GRD-09 · vá các điểm Reviewer nêu ở PR 18 và PR 19
      Yêu cầu gốc: "Đồng ý, thực thi lần lượt" (Reviewer của hai PR khuyến nghị gom các điểm nên sửa vào một thẻ)
      Mục tiêu:  AGENTS.md thành file máy chặn (không gỡ được Hot file, Restricted zone bằng PR không thẻ); review-check lấy dòng "Kết luận:" cuối cùng trong mục, chặn "Trả lại", và gắn kết luận với commit đã review; bước review-check xuống cuối job CI; bảo toàn test không đếm file tài liệu và bỏ qua submodule; tài liệu ghi đúng chuỗi "Kết luận: Đạt"; P-05 không còn để AI tự merge
      Lane:      Strict
      Scope:     .agents/skills/project-os/template/pos.py, pos.py, tests/*, .agents/skills/project-os/template/docs/PROCESS.md, docs/PROCESS.md, .agents/skills/project-os/template/docs/prompts/P-05.md, docs/prompts/P-05.md, .agents/skills/project-os/template/AGENTS.md, AGENTS.md, .agents/skills/project-os/template/.github/*, .github/*, README.md, docs/product/FEATURES.md, docs/DECISIONS.md
      Phụ thuộc: T-006
      Xong khi:  PO dán vào mô tả một PR Lane Strict mục Kết luận Reviewer có "Kết luận: Trả lại" kèm một dòng "Kết luận: Đạt" ở dưới: CI đỏ; python pos.py check qua

- [ ] T-010 · INS-01 · phát hành bản mới lên npm, ghi luồng phát hành
      Yêu cầu gốc: "OK vậy bây giờ cần phải làm gì? Cập nhật vào STATUS" (phát hiện: bản 1.6.0 cài ra ở eDMS là bản chụp trước PR 16; PR 16, 18, 19, 21 merge mà số phiên bản không tăng nên không có trong gói)
      Mục tiêu:  gói trên npm chứa mọi thứ đã merge tới hết T-008 và T-009, mang số phiên bản mới (đề xuất 1.7.0, PO chốt); PROCESS có một đoạn ngắn về luồng phát hành: khi nào tăng số, ai chạy `npm publish`, kiểm gì sau khi phát hành (xem lại D17)
      Lane:      Strict
      Scope:     package.json, .agents/skills/project-os/template/docs/PROCESS.md, docs/PROCESS.md, README.md, docs/DECISIONS.md, tests/*
      Phụ thuộc: T-008, T-009
      Xong khi:  PO chạy `npm publish`, rồi chạy `npx -y @nguyentan0510/project-os` ở một thư mục tạm: file `.project-os-install` ghi số mới và `template/pos.py` có dòng `HOOK_TESTS`; python pos.py check qua

Chưa viết thẻ (PO chọn thứ tự):
- Hai bộ thử còn lại ứng với BRIEF: AI phiên trắng (EVL-01), tiếp nhận 8 câu (EVL-02).
- `find` khớp theo từ thay vì chuỗi con: gõ "do luong" đang ra nhầm "Bảng prompt" (POL-02).
- Gắn mã feature vào test hiện có, để cột Test của sổ mã tự ghi được (REG-02).
- Thẻ có `Scope:` xuống nhiều dòng: máy chỉ đọc dòng đầu và không báo gì; cần đọc được dòng nối hoặc `plan-check` báo lỗi (GRD-01).
- Hai bản cài chồng nhau, bản cũ thắng mà không ai biết: ở eDMS, skill toàn cục (liên kết tới một bản clone cũ, "Phiên bản 1.1") che bản 1.6.0 vừa cài trong dự án, nên khung được chép là bản cũ; lệnh chép khung cần in phiên bản và cảnh báo khi thấy bản cài khác phiên bản (INS-02, DAY-01).
- Kiểm toán chỉ nhận thư mục module đặt theo mã (`crates/<mã>`, `src/<mã>`): ở eDMS, AI phải sửa quyết định D05 đã duyệt (tên `identity`, `catalog`) cho khớp, và sửa thẳng vào dòng cũ; cần nói quy ước này từ bước 3 hoặc cho khai tên thư mục của từng module (DAY-03).
- Ngày 0 không kiểm bộ công cụ có chạy được không: ở eDMS, bước 4 viết 1.591 dòng contract Rust mà chưa biên dịch được vì máy thiếu trình liên kết; cần một bước thử dựng tối thiểu sau khi chốt công nghệ, trước khi viết contract (DAY-02).
- Git đến bước 6 mới có: các bước trước không có lịch sử, không có hook, tuân thủ chỉ dựa vào AI; tạo repo Git ngay lúc chép khung để mỗi bước đã duyệt là một commit (DAY-01).

## Đang chặn
- Xác nhận bản trên npm: chờ PO chạy `npm view @nguyentan0510/project-os version`. Bản cài ở eDMS cho thấy 1.6.0 đã lên npm nhưng thiếu PR 16, 18, 19, 21; phát hành bản mới là việc của T-010.

## Ghi chú bàn giao
T-001 đến T-007 đã xong (PR 11, 13, 12, 16, 18, 19, 21). Ngày 0 đã vào main (PR 9); kiểm toán máy Đạt 29, Chưa 18, lệch đã chấp nhận (D13). Chưa làm: kiểm toán theo P-15 bằng một phiên AI khác; chưa ghi quyết định "Qua cổng Ngày 0".
Thứ tự đề xuất: T-009 → T-008 → T-010. Thử trên eDMS (dự án ngoài đầu tiên): Ngày 0 xong 4/7 bước bằng khung cũ; skill toàn cục trên máy PO giờ trỏ thẳng vào repo này (giữ repo ở `main`, làm task trong worktree); sau T-009 thì chép lại khung, làm nốt bước 5 đến 7, một thẻ T-001 và một PR cố tình vi phạm.
PO cần tự làm trên GitHub: thêm `pr-title` vào check bắt buộc của main (sau T-004 thì `test` đã gồm cả `check`).

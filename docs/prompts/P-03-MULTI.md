# P-03-MULTI · Lập plan nhiều agent

**Vai:** Orchestrator · **Đầu ra:** `docs/plan/M3-*.md` + kết quả plan-check
Sinh từ `docs/PROCESS.md` mục 13. Sửa ở đó trước, rồi sửa file này cho khớp. Thay các chỗ `<…>` trước khi gửi.

```
Lập plan cho Milestone <M3> theo đồ thị không chu trình. Đọc BRIEF, FEATURES, ROADMAP, DECISIONS. Chia W0 (task contract + mock) → W1 (2–5 task song song) → W2 (nối dây + e2e). Mỗi thẻ ghi Wave, Scope (RW), Read (RO), Phụ thuộc chỉ trỏ Wave trước. Cách đăng ký module để không sửa Hot file. Chạy `python pos.py plan-check` đến khi qua, dán kết quả. Mỗi thẻ có "Xong khi" gồm một hành vi tôi tự quan sát được và một lệnh kiểm. Đầu plan viết "Tóm tắt cho PO": làm gì, theo thứ tự nào, tôi sẽ phải duyệt những gì. Chờ tôi duyệt.
```

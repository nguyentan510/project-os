# P-SOS · Cứu hộ dự án (Cổng Exit của chủ dự án)

**Khi dùng:** dự án kẹt, lỗi không rõ nguyên nhân, worktree rác; chủ dự án cần quyết định mà không phải đọc log.
**Vai:** Orchestrator · **Đầu ra:** Báo cáo cứu hộ + thực thi phương án được chọn
Khác P-14 (lỗi production cần hotfix) và P-12 (chỉ rà tài liệu). Luật cứng 6–8 vẫn áp dụng: SOS không phải đường tắt.

```
Tôi đang bị kẹt, cứu hộ giúp tôi. Làm đúng thứ tự:
1. Chạy `python pos.py sos` (tạo nhánh sao lưu salvage/sos-*, khám bệnh, chỉ đọc). Chưa sửa gì khác.
2. Báo cáo bằng tiếng người, tối đa 5 dòng: hiện tượng là gì, kẹt ở đâu, ảnh hưởng gì. Nói rõ tên nhánh sao lưu.
3. Đưa đúng 2 phương án rồi DỪNG, chờ tôi chọn A hoặc B:
   A (khuyến nghị): vá để cứu task theo đúng luồng: task → check → PR. Nếu phải chạm contract, file nóng, vùng cấm hoặc ngoài phạm vi thẻ thì dừng và hỏi tôi.
   B: bỏ task bị kẹt: python pos.py drop T=<mã> (cho tôi xem phần sẽ mất, chờ tôi đồng ý rồi mới thêm CONFIRM=<mã>), python pos.py wt-clean APPLY=1, đưa task về "Tiếp theo" trong STATUS.md, ghi Dxx nếu bỏ một quyết định đã có. Giữ nguyên nhánh salvage/*.
4. Sau khi thực hiện: python pos.py check phải in "qua"; cập nhật STATUS.md; báo lại trạng thái cuối.
Nếu cùng một lỗi lặp lại, đề xuất thêm P-12 để rà tài liệu.
```

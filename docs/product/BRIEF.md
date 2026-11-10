# BRIEF · Mục tiêu sản phẩm

Đọc 1 phút phải trả lời được: cho ai, để làm gì, khi nào là xong.

## Người dùng
Solo Dev, cũng chính là Product Owner (PO): một người vừa quyết định sản phẩm vừa điều khiển nhiều AI viết code (Claude Code, Codex, Antigravity, Cursor) trên máy cá nhân Windows, macOS hoặc Linux, repo đặt trên GitHub.

## Vấn đề
Họ vibe code: nói ý muốn bằng lời thường và để AI viết. Không có kiểm soát thì mỗi phiên AI bắt đầu lại từ số không, AI sửa lan ra ngoài phạm vi, đẩy thẳng lên `main`, đặt tên lệch nhau, và người làm không còn biết dự án đang ở đâu hay vì sao nó thành ra như vậy. Hiện họ xử lý bằng cách nhắc lại bối cảnh bằng tay mỗi phiên và tự đọc lại code.

Project OS cho họ **vibe code có kiểm soát**: vẫn nói bằng lời thường, nhưng repo tự giữ mục tiêu, phạm vi, quyết định và trạng thái, còn máy chặn những việc không được phép.

## Thành công (2–3 chỉ số có số)
- AI phiên trắng (không có lịch sử chat) chạy P-01 và tóm tắt đúng dự án trong 1 phút, đạt trên cả 3 công cụ: Claude Code, Codex, Antigravity.
- PO nói 8 câu bằng lời thường, không kèm mã: ít nhất 7/8 lần AI nhắc lại đúng ý định và chuyển đúng prompt.
- Trong 10 task thử cố tình vi phạm (sửa ngoài Scope, lộ khoá, sửa máy chặn), máy chặn bắt được 10/10.

## Không làm
- Không có giao diện web, máy chủ hay cơ sở dữ liệu: Project OS chỉ là file trong repo và lệnh dòng lệnh.
- Không phục vụ nhóm nhiều người: chỉ một PO với nhiều AI.
- Không hỗ trợ nền tảng ngoài GitHub (GitLab, Bitbucket).
- Không gắn với riêng một công cụ AI nào.

## Ràng buộc
- Thời hạn: không có hạn cứng; phát hành theo từng phiên bản npm.
- Thiết bị / nền tảng: Windows, macOS, Linux; công cụ chỉ dùng thư viện chuẩn Python 3.8+; cài bằng Node.js ≥ 16.7 hoặc script.
- Ngôn ngữ giao diện: tiếng Việt (tài liệu, prompt, thông báo lệnh).
- Ngân sách / hạ tầng: không có hạ tầng riêng; dựa vào GitHub và GitHub Actions.

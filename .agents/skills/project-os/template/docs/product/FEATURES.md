# FEATURES · Sổ mã

Nguồn duy nhất của mọi mã module và feature. Mã cấp một lần, không bao giờ dùng lại.
Trạng thái: `dự kiến` · `dùng` · `bỏ (Dxx)` · `để sau` (ý tưởng PO chưa quyết làm). Cột Test: `python pos.py features` kiểm, `python pos.py features --sync` tự ghi `đường/dẫn (số lần gắn mã)` từ test thật; chưa có test tự động thì ghi tay `— (lý do)`.
Mỗi module là một tiêu đề `### MÃ · Tên`; kiểm sổ mã chỉ nhận mã có tiền tố là module đã khai báo. Cột QĐ: mã quyết định liên quan. Cột Tên gọi: 2–5 từ bằng lời của PO; `python pos.py find <lời>` tìm theo cột này.

## {{DOMAIN}} · {{Tên domain}}

### {{MOD}} · {{Tên module}}

| Mã | Tên gọi | Hành vi chính | Code chính (điểm vào) | Test liên quan | QĐ | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| {{MOD}}-01 | {{2–5 từ, lời của PO}} | {{điều người dùng thấy, kiểm chứng được bằng test}} | — | — | — | dự kiến |

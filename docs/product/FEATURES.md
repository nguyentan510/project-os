# FEATURES · Sổ mã

Nguồn duy nhất của mọi mã module và feature. Mã cấp một lần, không bao giờ dùng lại.
Trạng thái: `dự kiến` · `dùng` · `bỏ (Dxx)` · `để sau` (ý tưởng PO chưa quyết làm). Cột Test: `python pos.py features` kiểm, `python pos.py features --sync` tự ghi `đường/dẫn (số lần gắn mã)` từ test thật; chưa có test tự động thì ghi tay `— (lý do)`.
Mỗi module là một tiêu đề `### MÃ · Tên`; kiểm sổ mã chỉ nhận mã có tiền tố là module đã khai báo. Cột QĐ: mã quyết định liên quan. Cột Tên gọi: 2–5 từ bằng lời của PO; `python pos.py find <lời>` tìm theo cột này.

Đường dẫn rút gọn: `skill/` = `.agents/skills/project-os/`, `khung/` = `.agents/skills/project-os/template/`.

## CORE · Project OS

### INS · Cài đặt

| Mã | Tên gọi | Hành vi chính | Code chính (điểm vào) | Test liên quan | QĐ | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| INS-01 | Cài theo dự án | Solo Dev chạy một lệnh `npx`, skill được chép vào `.agents/` và `.claude/` của dự án, không ghi đè thứ có sẵn | bin/project-os.js | — (CI thử cài và gỡ, chưa gắn mã) | — | dùng |
| INS-02 | Cài toàn cục | Một lệnh cài skill cho mọi dự án trên máy; chạy lại để cập nhật | bin/project-os.js, install.sh, install.ps1 | — (chưa có test tự động) | — | dùng |
| INS-03 | Gỡ cài đặt | `--uninstall` gỡ đúng phần lệnh cài đã tạo, không đụng thứ khác | bin/project-os.js | — (CI thử cài và gỡ, chưa gắn mã) | — | dùng |
| INS-04 | Nâng cấp dự án đã cài | Dự án đã qua Ngày 0 nhận bản khung mới mà không mất phần đã điền | — | — | — | để sau |

### DAY · Ngày 0

| Mã | Tên gọi | Hành vi chính | Code chính (điểm vào) | Test liên quan | QĐ | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| DAY-01 | Chép khung | Một lệnh chép khung Ngày 0 vào dự án, báo file nào tạo, file nào giữ, không ghi đè | skill/scripts/init.py | — (có test, chưa gắn mã) | — | dùng |
| DAY-02 | Dẫn 7 bước Ngày 0 | AI dẫn PO qua 7 bước, trình đầu ra và dừng chờ duyệt sau mỗi bước | skill/SKILL.md | — (hành vi của AI, chưa đo) | — | dùng |
| DAY-03 | Kiểm toán Ngày 0 | Một lệnh báo từng ô Đạt hay Chưa trước khi viết code | skill/scripts/audit.py | — (có test, chưa gắn mã) | — | dùng |
| DAY-04 | Áp vào repo đang có code | Repo đã có code và cấu trúc riêng vẫn qua được Ngày 0 mà không phải đổi cấu trúc | — | — | — | để sau |

### RUN · Bộ lệnh dự án

| Mã | Tên gọi | Hành vi chính | Code chính (điểm vào) | Test liên quan | QĐ | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| RUN-01 | Cổng check | `check` chạy kiểm sổ mã, quét khoá, lint, test; chưa cấu hình lint hay test thì báo lỗi, không báo xanh giả | khung/pos.py | — (có test, chưa gắn mã) | — | dùng |
| RUN-02 | Chạy test theo mã, theo tầng | `test F=<mã>` hoặc `L=<tầng>` chạy đúng nhóm test cần | khung/pos.py | — (có test, chưa gắn mã) | — | dùng |

### TSK · Vòng đời task

| Mã | Tên gọi | Hành vi chính | Code chính (điểm vào) | Test liên quan | QĐ | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| TSK-01 | Mở task | Một lệnh tạo worktree và branch riêng cho task từ `main` mới nhất | khung/pos.py | — (có test, chưa gắn mã) | — | dùng |
| TSK-02 | Dọn task đã merge | Dọn worktree và branch sau khi PR đã merge, nhận cả merge squash; không dọn thứ chưa merge | khung/pos.py | — (có test, chưa gắn mã) | — | dùng |
| TSK-03 | Huỷ task | Huỷ task chưa merge chỉ khi PO xác nhận, sau khi thấy rõ phần sẽ mất | khung/pos.py | — (có test, chưa gắn mã) | — | dùng |
| TSK-04 | Trạng thái task | Một lệnh cho biết task nào đang làm, sẵn sàng, chờ phụ thuộc, đã xong; không ai phải ghi tay | khung/pos.py | — (có test, chưa gắn mã) | — | dùng |
| TSK-05 | Kiểm plan | Báo lỗi khi hai task cùng Wave trùng Scope hoặc phụ thuộc trỏ sai Wave | khung/pos.py | — (có test, chưa gắn mã) | — | dùng |
| TSK-06 | Khung báo cáo PR | Một lệnh sinh sẵn khung báo cáo PR từ diff và kết quả check | khung/pos.py | — (chưa có test tự động) | — | dùng |
| TSK-07 | Cứu hộ | Khi kẹt, một lệnh sao lưu mọi thứ vào branch riêng rồi khám bệnh, không sửa gì | khung/pos.py | — (có test, chưa gắn mã) | — | dùng |

### GRD · Máy chặn

| Mã | Tên gọi | Hành vi chính | Code chính (điểm vào) | Test liên quan | QĐ | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| GRD-01 | Chặn sửa ngoài Scope | Task sửa file ngoài Scope của thẻ thì bị chặn; thẻ đọc từ `main` nên task không tự nới được | khung/pos.py | — (có test, chưa gắn mã) | — | dùng |
| GRD-02 | Giới hạn việc không có thẻ | Việc không có thẻ chỉ qua khi đủ nhỏ và không chạm đường dẫn được bảo vệ | khung/pos.py | — (có test, chưa gắn mã) | — | dùng |
| GRD-03 | Quét khoá bí mật | Khoá bí mật hoặc file `.env` lọt vào repo thì `check` báo lỗi, không in giá trị khoá | khung/pos.py | — (có test, chưa gắn mã) | — | dùng |
| GRD-04 | Chặn trước khi push | Push bị chặn khi `check` chưa qua hoặc sửa ngoài Scope | khung/.githooks/pre-push | — (chạy gián tiếp trong test, chưa gắn mã) | — | dùng |
| GRD-05 | Cổng CI của PR | PR phải qua `check`, kiểm Scope bằng bản `pos.py` của `main`, và đúng mẫu tiêu đề | khung/.github/workflows/ci.yml | — (chưa chạy thật trên GitHub Actions) | — | dùng |
| GRD-06 | Bảo vệ file máy chặn | PR sửa file máy chặn hoặc plan phải có PO approve | khung/.github/CODEOWNERS | — (phụ thuộc cài đặt GitHub, chưa kiểm) | — | dùng |
| GRD-07 | Bắt mã dùng lại | Mã feature, số T, số D đã cấp mà bị dùng lại thì bị chặn; tiêu đề PR của task có thẻ buộc có `[T-nnn]` | — | — | — | để sau |
| GRD-08 | Bảo toàn test | Thay đổi xoá file test, đổi loại file test hoặc làm giảm số test đếm được so với `main` thì bị chặn, trừ khi thẻ ghi đích danh file đó trong Scope | khung/pos.py | — (có test, chưa gắn mã) | — | dùng |

### REG · Sổ mã

| Mã | Tên gọi | Hành vi chính | Code chính (điểm vào) | Test liên quan | QĐ | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| REG-01 | Kiểm sổ mã | Mã có trong code mà không có trong sổ, mã trùng, mã đã bỏ còn trong code: đều báo lỗi | khung/scripts/features.py | — (có test, chưa gắn mã) | — | dùng |
| REG-02 | Tự ghi cột Test | Một lệnh ghi lại cột Test của sổ mã từ các test có gắn mã | khung/scripts/features.py | — (có test, chưa gắn mã) | — | dùng |
| REG-03 | Kiểm biến môi trường | Code đọc biến môi trường chưa khai trong `.env.example` thì báo lỗi | khung/scripts/features.py | — (có test, chưa gắn mã) | — | dùng |

### POL · Lớp PO

| Mã | Tên gọi | Hành vi chính | Code chính (điểm vào) | Test liên quan | QĐ | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| POL-01 | Tiếp nhận lời thường | PO nói bằng lời thường; AI xác định ý định, hỏi phần thiếu, nhắc lại "Tôi hiểu là…" rồi mới làm | khung/docs/prompts/P-00.md | — (hành vi của AI, chưa đo) | — | dùng |
| POL-02 | Tìm mã bằng lời | PO gõ vài từ không cần dấu, nhận lại tên gọi kèm mã của feature, quyết định, thẻ liên quan | khung/pos.py | — (có test, chưa gắn mã) | — | dùng |
| POL-03 | Việc chờ PO | Một chỗ liệt kê mọi thứ đang chờ PO quyết: câu hỏi còn mở, việc bị chặn, PR cần approve | khung/pos.py | — (có test; phần hỏi GitHub chưa kiểm) | — | dùng |
| POL-04 | Tóm tắt cho PO | Thứ gì PO phải duyệt đều kèm bốn dòng: người dùng thấy gì đổi, rủi ro, cách tự thử, khuyến nghị | khung/.github/pull_request_template.md | — (hành vi của AI, chưa đo) | — | dùng |

### DOC · Bộ quy tắc

| Mã | Tên gọi | Hành vi chính | Code chính (điểm vào) | Test liên quan | QĐ | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| DOC-01 | Bảng prompt | Mỗi bước của luồng có một prompt mẫu; bảng trong PROCESS và file prompt luôn khớp nhau | khung/docs/prompts/ | — (có test, chưa gắn mã) | — | dùng |
| DOC-02 | Luật, vai, Lane | Một tài liệu duy nhất nói rõ 8 luật cứng, các vai và ba Lane; mọi AI đọc cùng một nguồn | khung/docs/PROCESS.md | — (tài liệu) | — | dùng |
| DOC-03 | Bảng thuật ngữ | Mỗi khái niệm một tên, tra được ở một chỗ | khung/docs/GLOSSARY.md | — (tài liệu) | — | dùng |

### EVL · Đo lường

| Mã | Tên gọi | Hành vi chính | Code chính (điểm vào) | Test liên quan | QĐ | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| EVL-01 | Thử AI phiên trắng | Có kịch bản và bảng chấm để kiểm AI mới tóm tắt đúng dự án trong 1 phút trên Claude Code, Codex, Antigravity | — | — | — | dự kiến |
| EVL-02 | Thử tiếp nhận 8 câu | Có 8 câu mẫu của PO và bảng chấm: AI nhắc lại đúng ý định và chuyển đúng prompt | — | — | — | dự kiến |
| EVL-03 | Thử vi phạm 10 task | Có 10 task cố tình vi phạm và kết quả máy chặn bắt được bao nhiêu | — | — | — | dự kiến |

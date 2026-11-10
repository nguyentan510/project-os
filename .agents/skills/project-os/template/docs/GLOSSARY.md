# GLOSSARY · Bảng thuật ngữ

Nguồn duy nhất cho tên gọi trong dự án. Mọi file khác dùng đúng tên ở đây; cần thêm hay đổi thuật ngữ thì sửa file này trước.
Thuật ngữ riêng của dự án (domain, module, tên nghiệp vụ) thêm vào mục cuối.

## Quy tắc dùng từ

1. **Giữ tiếng Anh** cho tên đơn vị, vai, đối tượng Git/GitHub, lệnh và nhãn mà script đọc: một từ, không dịch, không kèm bản dịch trong câu.
2. **Tiếng Việt ngắn** cho diễn giải, hướng dẫn và các khái niệm riêng đã gọn: Ngày 0, luật cứng, mặc định, mã, sổ mã, thẻ task, bàn giao.
3. **Viết hoa chữ đầu** khái niệm riêng của Project OS: Milestone, Wave, Lane (Fast · Normal · Strict), Scope, Hot file, Restricted zone, và ba vai Orchestrator · Builder · Reviewer. Từ phổ thông của nghề viết thường trong câu: task, branch, worktree, commit, merge, contract, module, feature, mock.
4. **Một khái niệm, một tên.** Tên cũ ở bảng cuối không dùng nữa.
5. **Chính tả:** bỏ dấu kiểu mới, thống nhất `khoá, xoá, huỷ, tuỳ, thoả` (không viết `khóa, xóa, hủy, tùy, thỏa`).
6. Lệnh, đường dẫn, giá trị trong `code` giữ nguyên, không dịch.

## Đơn vị và mã

| Thuật ngữ | Nghĩa | Mã / ví dụ |
| --- | --- | --- |
| Mã | Định danh ổn định, cấp một lần, không dùng lại; đầu mối nối tài liệu, code, test, commit | `MAP-07`, `D59`, `T-042` |
| Domain | Nhóm nghiệp vụ lớn; chỉ là tiêu đề nhóm trong FEATURES.md, không vào mã | `SALES` |
| Module | Phần code có ranh giới riêng, gọi nhau chỉ qua contract | `MAP` → `src/map/` |
| Feature | Một hành vi người dùng thấy được, kiểm chứng được bằng test | `MAP-07` |
| Milestone | Một đợt giao hàng có mục tiêu và nghiệm thu; có plan riêng khi cần | `M3` |
| Wave | Lớp task trong plan nhiều agent; task chỉ phụ thuộc Wave trước | `W0`, `W1`, `W2` |
| Task | Đơn vị công việc; 1 task = 1 branch = 1 worktree = 1 PR | `T-043` (Lane Fast: mã feature) |
| Quyết định | Một lựa chọn kỹ thuật kèm lý do, trong DECISIONS.md | `D59` |
| Câu hỏi mở | Điều chưa chốt, ghi người đang chờ | `Q-map` |
| Prompt | Prompt mẫu cho từng bước của luồng | `P-04`, `P-SOS` |

## Vai

| Thuật ngữ | Nghĩa |
| --- | --- |
| Chủ dự án | Người quyết định cuối: duyệt plan, approve PR Lane Strict, nghiệm thu Milestone, cho phép bỏ qua luật khi khẩn cấp; phát prompt và chuyển tin giữa các phiên AI |
| Orchestrator | AI điều phối: viết thẻ task, cấp số T, merge lần lượt, ghi plan và STATUS; không viết code feature; mỗi lúc chỉ một Orchestrator |
| Builder | AI làm task trên worktree riêng, theo luồng chung |
| Reviewer | AI review PR Lane Strict, tối đa 2 vòng rồi chuyển chủ dự án |

## File và tài liệu

| Thuật ngữ | Nghĩa |
| --- | --- |
| AGENTS.md | Luật của dự án; mọi AI đọc đầu tiên |
| STATUS.md | Chỗ dừng của phiên trước: Tiếp theo · Đang chặn · Ghi chú bàn giao; ai giữ task nào xem `python pos.py status` |
| BRIEF | Làm cho ai, để làm gì, thế nào là thành công (`docs/product/BRIEF.md`) |
| Sổ mã | `docs/product/FEATURES.md`: nguồn duy nhất của mã module và feature |
| DECISIONS | Bảng quyết định `Dxx` và câu hỏi mở `Q-` (`docs/DECISIONS.md`) |
| ROADMAP | Danh sách Milestone và trạng thái (`docs/plan/ROADMAP.md`, khi có nhiều Milestone) |
| Plan | Thẻ task của một Milestone (`docs/plan/M3-<short-name>.md`) |
| File ranh giới | File là điểm vào của module (route, service, contract, màn hình, job); có 3 dòng đầu file gắn mã |

## Quy trình

| Thuật ngữ | Nghĩa |
| --- | --- |
| Ngày 0 | 7 bước lập nền trước dòng code đầu tiên; qua kiểm toán mới viết code |
| Kiểm toán | Kiểm Ngày 0 theo bảng kiểm: `audit.py` phần máy kiểm được, P-15 phần còn lại |
| Luật cứng | 8 luật không ngoại lệ, máy chặn được thì máy chặn (PROCESS.md mục 4) |
| Mặc định | Điểm xuất phát AI được làm khác khi hợp lý, ghi lý do ở "Khác mặc định" |
| Luồng chung | `task → code → commit → check → rebase → push → PR → CI → [approve nếu Lane Strict] → merge → done` |
| Lane | Mức kiểm soát theo rủi ro: **Fast** (câu chữ, lỗi nhỏ) · **Normal** (feature, sửa lỗi có logic) · **Strict** (chạm contract, Hot file, Restricted zone). Máy xác định: không thẻ → Fast, có thẻ → Normal, chạm `CODEOWNERS` → Strict |
| Nâng Lane | Đang làm mà phát hiện chạm vùng rủi ro: dừng, báo Orchestrator, xin duyệt |
| Thẻ task | Mô tả đủ một task, cũng là prompt giao việc; các trường: Mục tiêu · Lane · Wave · Scope · Read · Phụ thuộc · Cần · Restricted zone · Giao · Xong khi |
| Scope | Trường thẻ: các đường dẫn task được ghi (RW), gồm cả thư mục test; `python pos.py scope` chặn sửa ngoài Scope |
| Read | Trường thẻ: đường dẫn chỉ được đọc (RO) để tham chiếu |
| Phụ thuộc | Trường thẻ: task phải xong trước; chỉ trỏ về Wave trước |
| Cần | Trường thẻ W1: kiểu và hàm của contract mà task dùng; Orchestrator đối chiếu trước khi khoá contract |
| Xong khi | Trường thẻ: điều kiện nghiệm thu task, kiểm được |
| Hot file | File nhiều task cùng cần sửa (route, registry, schema, manifest); chỉ task W2 hoặc Orchestrator ghi |
| Restricted zone | Phần rủi ro cao (đăng nhập, phân quyền, thanh toán, contract, migration, xoá dữ liệu); PR chạm vào phải có Reviewer và chủ dự án approve |
| Contract | Kiểu dữ liệu và API công khai giữa các module (`contract.*`); khoá sau task contract |
| Mock | Dữ liệu mẫu viết kèm contract để Builder chạy thử khi module kia chưa xong |
| Contract test | Test so mock với bản thật, bắt buộc ở mọi module W1 |
| Nối dây | Việc ở W2: gắn module vào ứng dụng chính, sửa Hot file, chạy e2e tổng |
| Đăng ký động | Module tự đăng ký vào ứng dụng để file gốc không còn là Hot file |
| Check | `python pos.py check` = kiểm sổ mã + lint + test; qua mới được push |
| Máy chặn | Cơ chế tự động ép luật: pre-push hook, CI, khoá main, CODEOWNERS |
| Cổng | Điểm phải qua mới được đi tiếp: cổng Ngày 0, cổng khoá contract, CI của PR |
| Bàn giao | Ghi chú ≤ 3 dòng cho phiên sau, trong STATUS.md và báo cáo PR |
| Khác mặc định | Mục trong báo cáo PR ghi chỗ làm khác Mặc định và lý do |
| Worktree mồ côi | Worktree có branch đã merge mà chưa dọn; `python pos.py wt-clean` tìm |
| SOS | Cứu hộ khi repo kẹt: `python pos.py sos` sao lưu vào branch `salvage/sos-*` rồi chạy P-SOS |
| Khẩn cấp | Lỗi production; chỉ chủ dự án cho bỏ qua luật, ghi `Dxx`, làm task bù (P-14) |

## Git và GitHub

| Thuật ngữ | Nghĩa |
| --- | --- |
| Branch | Dòng phát triển của một task: `<loại>/<mã>-<short-name>`, ví dụ `feat/T-043-map-sales` |
| Worktree | Thư mục làm việc riêng của một task, đặt ngoài repo: `../wt/T-043` |
| Commit | Điểm lưu thay đổi; ở local tự do |
| Push | Đẩy branch lên remote; pre-push hook chạy check và scope trước |
| Rebase | Đưa branch lên bản mới nhất của main: `git rebase origin/main` |
| PR | Yêu cầu merge branch vào main; tiêu đề `<loại>(<mã>): <việc> [T-nnn]` |
| CI | Máy chủ chạy lại check trên PR; cổng cuối không tắt được |
| Merge | Đưa PR vào main, luôn kiểu squash (ép các commit thành một) |
| Merge queue | Merge từng PR một, mỗi lần rebase và chạy lại CI |
| Approve | Chủ dự án bấm duyệt PR trên GitHub; bắt buộc với Lane Strict |
| Khoá main | Branch protection của main: không push thẳng, bắt buộc PR, CI và Code Owner |
| Code Owner | Người trong `.github/CODEOWNERS` phải approve PR chạm đường dẫn của mình |
| Hook | Script Git chạy tự động; dự án dùng `.githooks/pre-push` |

## Mẫu tên

**Mã.** Cấp một lần, không dùng lại. Gạch nối giữ đúng như bảng (đã nằm trong regex của script, không đổi):

| Loại | Mẫu | Regex | Ví dụ | Cấp ở |
| --- | --- | --- | --- | --- |
| Module | 2–6 chữ hoa | `[A-Z]{2,6}` | `MAP` | FEATURES.md |
| Feature | `<MODULE>-nn` | `[A-Z]{2,6}-\d{2,}` | `MAP-07` | FEATURES.md |
| Quyết định | `Dnn` | `D\d{2,}` | `D59` | DECISIONS.md |
| Câu hỏi mở | `Q-<slug>` | `Q-[a-z0-9-]+` | `Q-map` | DECISIONS.md |
| Milestone | `Mn` | `M\d+` | `M3` | ROADMAP.md |
| Wave | `Wn`, bắt đầu từ `W0` | `W\d+` | `W1` | thẻ task |
| Task | `T-nnn` | `T-\d{3,}` | `T-043` | plan (Orchestrator) |
| Prompt trong luồng | `P-nn` | `P-\d{2}` | `P-04` | PROCESS.md mục 13 |
| Biến thể prompt | `P-nn-<TÊN>` | `P-\d{2}-[A-Z]+` | `P-03-MULTI` | PROCESS.md mục 13 |
| Prompt ngoài luồng | `P-<TÊN>` | `P-[A-Z]+` | `P-SOS` | PROCESS.md mục 13 |

**Slug** (`<short-name>`): kebab-case ASCII tiếng Anh, chữ thường, số, gạch ngang; 2–4 từ. Dùng cho branch, `N=` của `pos.py task`, file plan.

| Thứ | Mẫu | Ví dụ |
| --- | --- | --- |
| Branch | `<loại>/<mã>-<short-name>` | `feat/T-043-map-sales`, `fix/MAP-02-typo` |
| Worktree | `../wt/<mã>` | `../wt/T-043` |
| Branch sao lưu | `salvage/sos-<YYYYMMDD-HHMMSS>` | `salvage/sos-20261109-153000` |
| File plan | `docs/plan/<Milestone>-<short-name>.md` | `docs/plan/M3-store-map.md` |
| File prompt | `docs/prompts/<mã prompt>.md` | `docs/prompts/P-04.md` |
| Thư mục module | mã module viết thường | `src/map/`, `tests/api/map/` |
| Contract | `contract.<đuôi>` trong thư mục module | `src/map/contract.py` |

**File tài liệu.** Tên VIẾT HOA một từ tiếng Anh (`STATUS.md`, `BRIEF.md`); tiêu đề H1 theo mẫu `# TÊN · mô tả ngắn` (STATUS: `# STATUS · <ngày> · <Milestone>`; plan và prompt: `# <mã> · <tên>`). Tên do công cụ quy định (`README.md`, `CODEOWNERS`, `pull_request_template.md`…) giữ nguyên.

**Biến môi trường** của Project OS có tiền tố `PROJECT_OS_`: `PROJECT_OS_TOOLS`, `PROJECT_OS_BRANCH`, `PROJECT_OS_F`, `PROJECT_OS_L`, `PROJECT_OS_DIR`, `PROJECT_OS_REPO`.

## Trạng thái và kết quả

| Ở đâu | Giá trị |
| --- | --- |
| Feature (sổ mã) | `dự kiến` · `dùng` · `bỏ (Dxx)` |
| Milestone (ROADMAP) | `chưa bắt đầu` · `đang làm` · `xong <ngày> · <phiên bản>` |
| Duyệt (DECISIONS) | `Chủ dự án` · `AI` |
| Lệnh `pos.py` | `qua` · `LỖI` |
| Kiểm toán, review | `Đạt` · `Chưa` · `Trả lại` |

## Tên cũ không dùng

| Không dùng | Dùng |
| --- | --- |
| Sóng, Sóng 1 | Wave, W1 |
| Mốc, plan mốc | Milestone, plan của Milestone |
| Làn Nhanh · Thường · Kiểm soát | Lane Fast · Normal · Strict |
| Phạm vi (trường thẻ), quyền ghi | Scope (RW) |
| Đọc (RO) | Read (RO) |
| File nóng | Hot file |
| Vùng cấm | Restricted zone |
| Human Approval, bạn duyệt PR | chủ dự án approve |
| bạn (chỉ người quyết định) | chủ dự án |
| nhánh | branch |
| gộp, hàng chờ gộp | merge, merge queue |
| Kiểm local | check |
| `M1-ten-ngan.md`, slug tiếng Việt | `M1-short-name.md`, slug tiếng Anh |
| `POS_BRANCH` | `PROJECT_OS_BRANCH` |
| `scripts/feature-lint.py` | `scripts/features.py` |
| test hợp đồng | contract test |
| stub, fixture (kèm contract) | mock |
| E2E | e2e |
| Cổng Exit | SOS |
| Sổ tính năng | sổ mã |

## Thuật ngữ của dự án

| Thuật ngữ | Nghĩa | Mã liên quan |
| --- | --- | --- |

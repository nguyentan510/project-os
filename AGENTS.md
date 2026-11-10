# AGENTS · Luật của dự án

Luật của dự án này. Mọi AI (Claude Code, Codex, Antigravity, Cursor…) đọc file này đầu tiên.
Bản đầy đủ: `docs/PROCESS.md`. Thuật ngữ: `docs/GLOSSARY.md`. Ranh giới module và contract: `docs/product/MODULES.md`.

## Mục tiêu
Project OS giúp Solo Dev, cũng là Product Owner (PO), vibe code có kiểm soát: nói bằng lời thường với nhiều AI, còn repo tự giữ mục tiêu, phạm vi, quyết định, trạng thái và máy chặn việc không được phép — chi tiết ở `docs/product/BRIEF.md`.

## Riêng của repo này
- Repo này vừa là sản phẩm vừa tự dùng sản phẩm. Bản gốc của khung là `.agents/skills/project-os/template/`; `pos.py`, `scripts/`, `.githooks/`, `docs/PROCESS.md`, `docs/GLOSSARY.md`, `docs/prompts/` ở gốc repo là bản chép (D06). **Sửa ở `template/` trước, rồi chép ra gốc.**
- Chín contract (C1–C9 trong `docs/product/MODULES.md`) phần lớn là định dạng văn bản mà code đọc bằng biểu thức chính quy. Đổi tên cột, tên mục hay tên trường trong tài liệu mẫu là sửa contract: Lane Strict.
- Hook pre-push ở repo này chỉ kiểm nhanh (D14): sổ mã, quét khoá, lint, Scope. Bộ test chạy ở CI. Trước khi mở PR, tự chạy `python pos.py check` đầy đủ (khoảng 3 phút rưỡi).
- Công cụ chỉ dùng thư viện chuẩn Python 3.8+ (D01). Không thêm phụ thuộc ngoài khi chưa hỏi PO.

## Đọc khi mở phiên
AGENTS.md → STATUS.md → thẻ task (nếu có) → dòng mã trong `docs/product/FEATURES.md` → dòng module trong `docs/product/MODULES.md` → `rg "<mã>"`.

## Khi PO nói không kèm mã (PROCESS.md mục 14)
Chạy P-00: xác định ý định, tự tra mã bằng `python pos.py find <lời của PO>`, hỏi tối đa 3 câu, rồi nhắc lại "Tôi hiểu là…" và chờ PO xác nhận trước khi làm.
Nói với PO bằng tên gọi, mã để trong ngoặc: "Quét khoá bí mật (GRD-03)". Không bắt PO nhớ mã hay chọn prompt.

## Lệnh
- `python pos.py setup` · `python pos.py run` · `python pos.py lint`
- `python pos.py test` · (`F=<mã>`, `L=<tầng>` chưa dùng được: test chưa gắn mã, xem STATUS)
- `python pos.py check` = kiểm sổ mã + quét khoá + lint + test; chạy trước mỗi lần push
- `python pos.py task T=T-001 N=short-name` · `python pos.py done T=T-001` · `python pos.py wt`
- `python pos.py find <lời của PO>` tìm mã theo tên gọi, hành vi, quyết định, thẻ (không cần dấu)
- `python pos.py status` ai đang làm task nào, task nào sẵn sàng, đã xong (suy từ thẻ + Git, không ghi tay)
- `python pos.py wt-clean [APPLY=1]` dọn worktree đã merge · `python pos.py pr` sinh sẵn khung báo cáo PR
- `python pos.py sos` khi bị kẹt: sao lưu vào branch `salvage/sos-*` + khám bệnh, rồi chạy P-SOS (`docs/prompts/P-SOS.md`)
- `python pos.py plan-check` kiểm plan nhiều agent: cùng Wave không trùng Scope (PROCESS.md mục 11)

## Luồng
task → code → commit → check → rebase → push → PR → CI → [approve nếu Lane Strict] → merge → done

## Lane
Fast · Normal · Strict (PROCESS.md mục 8). Không có thẻ → Fast; có thẻ → Normal; chạm đường dẫn trong CODEOWNERS → Strict. Ghi Lane vào mô tả PR. Phân vân thì chọn Lane cao hơn.

## Vai (PROCESS.md mục 11)
Chế độ **Một AI** (D07): không tách vai, cùng một AI viết thẻ, làm, mở PR. PO merge (D11).
Kiểm chứng độc lập chỉ còn ở máy chặn và cổng của PO, nên mọi PR phải có "Tóm tắt cho PO" viết bằng lời thường.

## Luật cứng (PROCESS.md mục 4)
1. Không push thẳng lên main; chỉ merge qua PR.
2. Không đưa khoá bí mật vào Git, code, tài liệu.
3. Chỉ push khi `python pos.py check` qua.
4. Tiêu đề PR: `<loại>(<mã>): <việc> [T-nnn]`.
5. Mã không bao giờ dùng lại; mã trong code phải có trong sổ mã.
6. Không tự sửa contract đã khoá, Hot file, Restricted zone. Cần sửa → dừng, báo Orchestrator, xin duyệt.
7. PR chạm các đường dẫn ở luật 6 phải có PO approve.
8. Không sửa ngoài Scope của thẻ; cần thì dừng và báo. Không có thẻ thì chỉ được là Lane Fast: `python pos.py scope` chặn khi chạm Hot file, Restricted zone hoặc quá ngưỡng `FAST_MAX_*` trong `pos.py`. Không xoá file test hay làm giảm số test so với main, trừ khi thẻ ghi đích danh file đó trong Scope: `python pos.py scope` chặn những trường hợp máy đếm được (cách đếm và giới hạn: PROCESS.md mục 4); phần còn lại là việc của Reviewer.

## Hot file (cùng danh sách với .github/CODEOWNERS)
pos.py, scripts/features.py, .githooks/, .github/
.agents/skills/project-os/template/pos.py, .agents/skills/project-os/template/docs/PROCESS.md, README.md, package.json

## Restricted zone (cùng danh sách với .github/CODEOWNERS)
.agents/skills/project-os/template/.githooks/, .agents/skills/project-os/template/.github/, .agents/skills/project-os/template/scripts/features.py
bin/, install.sh, install.ps1, docs/product/MODULES.md

## Ngôn ngữ và công cụ
Python 3.8+ chỉ thư viện chuẩn (D01) · trình cài: Node.js ≥ 16.7 không phụ thuộc ngoài · test: `python -m unittest discover -s tests` (D09) · lint: chưa dùng (D12) — quyết định ở `docs/DECISIONS.md`.

## Báo cáo khi xong
Đã làm · Scope thực tế (khớp thẻ / thêm gì, vì sao) · File thay đổi · Test đã chạy · Khác mặc định · Rủi ro · Ghi chú bàn giao
Tóm tắt cho PO (người dùng thấy gì đổi · rủi ro nếu sai · 3 bước tự bấm thử · khuyến nghị) · Việc cần PO chuyển cho Orchestrator (viết sẵn để dán)

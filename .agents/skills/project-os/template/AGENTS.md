# AGENTS · Luật của dự án

Luật của dự án này. Mọi AI (Claude Code, Codex, Antigravity, Cursor…) đọc file này đầu tiên.
Bản đầy đủ: `docs/PROCESS.md`. Thuật ngữ: `docs/GLOSSARY.md`. Chỗ `{{…}}` phải điền trong Ngày 0 (PROCESS.md mục 3).

## Mục tiêu
{{1–2 câu: làm cho ai, để làm gì}} — chi tiết ở `docs/product/BRIEF.md`.

## Đọc khi mở phiên
AGENTS.md → STATUS.md → thẻ task (nếu có) → dòng mã trong `docs/product/FEATURES.md` → `rg "<mã>"`.

## Khi PO nói không kèm mã (PROCESS.md mục 14)
Chạy P-00: xác định ý định, tự tra mã bằng `python pos.py find <lời của PO>`, hỏi tối đa 3 câu, rồi nhắc lại "Tôi hiểu là…" và chờ PO xác nhận trước khi làm.
Nói với PO bằng tên gọi, mã để trong ngoặc: "Bản đồ Sales (MAP-02)". Không bắt PO nhớ mã hay chọn prompt.

## Lệnh
- `python pos.py setup` · `python pos.py run` · `python pos.py lint`
- `python pos.py test` · `python pos.py test F=MAP-07` (theo mã) · `python pos.py test L=api` (theo tầng)
- `python pos.py check` = kiểm sổ mã + quét khoá + lint + test; chạy trước mỗi lần push
- `python pos.py task T=T-043 N=short-name` · `python pos.py done T=T-043` · `python pos.py wt`
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
{{Một AI: không tách vai | Một Orchestrator + nhiều Builder}}
Orchestrator: thẻ, số T, merge, STATUS. Builder: làm trong Scope, dừng khi PR qua CI. Reviewer: chỉ PR Lane Strict.
Cần báo Orchestrator: ghi vào báo cáo hoặc PR rồi dừng; Product Owner (PO) chuyển tin. Builder không ghi STATUS, plan.

## Luật cứng (PROCESS.md mục 4)
1. Không push thẳng lên main; chỉ merge qua PR.
2. Không đưa khoá bí mật vào Git, code, tài liệu.
3. Chỉ push khi `python pos.py check` qua.
4. Tiêu đề PR: `<loại>(<mã>): <việc> [T-nnn]`.
5. Mã không bao giờ dùng lại; mã trong code phải có trong sổ mã.
6. Không tự sửa contract đã khoá, Hot file, Restricted zone. Cần sửa → dừng, báo Orchestrator, xin duyệt.
7. PR chạm các đường dẫn ở luật 6 phải có PO approve.
8. Không sửa ngoài Scope của thẻ; cần thì dừng và báo. Không có thẻ thì chỉ được là Lane Fast: `python pos.py scope` chặn khi chạm Hot file, Restricted zone hoặc quá ngưỡng `FAST_MAX_*` trong `pos.py`.

## Hot file (cùng danh sách với .github/CODEOWNERS)
pos.py, scripts/features.py, .githooks/, .github/
{{ví dụ: src/app/routes.*, db/schema.*, src/copy.*}}

## Restricted zone (cùng danh sách với .github/CODEOWNERS)
{{ví dụ: src/auth/, src/payment/, db/migrations/, **/contract.*}}

## Ngôn ngữ và công cụ
{{ví dụ: Python 3.12 + FastAPI · test: pytest · lint: ruff}} — quyết định ở `docs/DECISIONS.md`.

## Báo cáo khi xong
Đã làm · Scope thực tế (khớp thẻ / thêm gì, vì sao) · File thay đổi · Test đã chạy · Khác mặc định · Rủi ro · Ghi chú bàn giao

# PROCESS · Quy tắc triển khai dự án

Phiên bản 1.1 · 2026-11-09 · Nguồn gốc của mọi quy tắc trong repo này. Tên gọi theo `docs/GLOSSARY.md`.

AI nào mở dự án cũng phải trả lời được trong 1 phút: **đang làm gì, đã làm gì, sửa thì bắt đầu từ đâu**. Đầu mối chung là **mã** (`MAP-07`).

Quy tắc có 3 tầng: **Luật cứng** (mục 4, máy chặn, không ngoại lệ) · **Mặc định** (mục 12, AI được làm khác khi hợp lý hơn và ghi lý do) · **Mẫu** (phụ lục, dùng khi cần). Bắt đầu tối giản; phần nào chưa cần thì chưa bật (mục 12). Dự án mới bắt đầu từ mục 3.

## 1. Sáu câu hỏi, sáu đầu mối

| Câu hỏi | Đầu mối | Cách tra |
| --- | --- | --- |
| Luật chơi là gì? | `AGENTS.md` | Đọc đầu tiên |
| Phiên trước dừng ở đâu? | `STATUS.md` | Đọc, ngắn |
| Milestone nào, task nào? | `docs/plan/` | ROADMAP → plan của Milestone (khi có) |
| Đã làm gì? | Git | `git log --oneline --grep "MAP-07"` |
| Sửa X bắt đầu từ đâu? | `docs/product/FEATURES.md` | Dòng mã → `rg "MAP-07"` |
| Vì sao làm vậy? | `docs/DECISIONS.md` | `rg "D59" docs/DECISIONS.md` |

## 2. Onboarding

Người hay AI mới làm 5 bước:

1. Đọc `AGENTS.md` rồi `docs/product/BRIEF.md`: dự án để làm gì. Gặp từ lạ thì tra `docs/GLOSSARY.md`.
2. Đọc STATUS.md (và ROADMAP nếu có): đang ở đâu.
3. `python pos.py setup` → `python pos.py check`: máy chạy được, test xanh.
4. Chọn một mã, chạy `rg "<mã>"` và `git log --grep "<mã>"`: thấy mã nối code, test, commit thế nào.
5. Làm thử một task Lane Fast: sửa một dòng câu chữ của một mã feature, đi hết branch → PR → merge.

## 3. Ngày 0: trước dòng code đầu tiên

**Chưa qua cổng Ngày 0 thì chưa viết code.** Mục tiêu: AI đầu tiên mở repo đã có đủ ngữ cảnh, không phải đoán ý định, phạm vi hay công nghệ.

### Thứ tự lập

Mỗi bước có đầu ra; chủ dự án duyệt rồi mới sang bước sau (prompt P-02).

1. **BRIEF** — làm cho ai, để làm gì, thế nào là thành công.
2. **FEATURES** — module + mã, hành vi MVP, trạng thái `dự kiến`.
3. **DECISIONS** — chốt công nghệ và cấu trúc, mỗi lựa chọn một `Dxx`.
4. **Module + contract** — ranh giới, kiểu dữ liệu, API công khai.
5. **AGENTS + STATUS** — luật của dự án này, việc đầu tiên.
6. **Khung repo + máy chặn** — `pos.py`, hook, khoá main, CI.
7. **Kiểm toán** — bảng kiểm dưới đây (prompt P-15), chủ dự án duyệt.

### Nội dung tối thiểu từng file

| File | Phải có | Đủ khi |
| --- | --- | --- |
| `BRIEF.md` | Người dùng (vai, số lượng) · Vấn đề · 2–3 chỉ số thành công có số · Không làm · Ràng buộc (thời hạn, thiết bị, ngôn ngữ, ngân sách) | Đọc 1 phút trả lời được: cho ai, để làm gì, khi nào là xong |
| `FEATURES.md` | Domain → module (mã) → feature MVP; mỗi dòng có hành vi chính viết theo người dùng, trạng thái `dự kiến` | Mỗi hành vi MVP có mã, viết được test; không feature nào nằm ngoài BRIEF |
| `DECISIONS.md` | Tối thiểu: ngôn ngữ + khung, CSDL + lưu trữ, nơi chạy, xác thực, cấu trúc module; câu hỏi `Q-` còn mở ghi người chờ | Mọi lựa chọn kỹ thuật có lý do; không `Q-` nào chặn MVP |
| `src/<module>/README.md` + `contract.*` | Chức năng, vào/ra, phụ thuộc; kiểu dữ liệu và chữ ký API công khai (chưa cần code thật) | Module chỉ gọi nhau qua contract; contract dữ liệu lõi đã viết |
| `AGENTS.md` | Đủ các mục theo mẫu phụ lục; Restricted zone và Hot file **thật** của dự án | AI phiên mới đọc xong làm được task mẫu mà không phải hỏi lại |
| `STATUS.md` | Đang giữ: trống · Tiếp theo: T-001 · Đang chặn: các `Q-` liên quan | Biết ngay việc đầu tiên là gì |
| `GLOSSARY.md` | Thuật ngữ riêng của dự án (domain, module, tên nghiệp vụ) ở mục cuối | Không từ nào trong BRIEF, FEATURES phải đoán nghĩa |
| `pos.py`, hook | `setup`, `check`, `task`, `done`; pre-push hook gọi `python pos.py check` | `python pos.py setup` + `python pos.py check` xanh trên máy sạch (0 test vẫn xanh) |
| GitHub | Khoá main, CI chạy `python pos.py check`, `CODEOWNERS` khi có Restricted zone | Thử push thẳng main bị chặn |
| `.gitignore`, `.env.example` | `.env` bị bỏ qua; `.env.example` chỉ có tên biến, không giá trị; `check` báo lỗi nếu code đọc biến (`os.getenv`, `process.env`…) chưa khai ở đây | Quét khoá sạch |

### Bảng kiểm toán Ngày 0

**Ý định và phạm vi**

- [ ] BRIEF có chỉ số thành công đo được và mục "Không làm".
- [ ] Mỗi feature MVP có mã, hành vi viết theo người dùng, truy được về BRIEF.
- [ ] Không có feature nào ngoài BRIEF.

**Kỹ thuật**

- [ ] Mọi lựa chọn kỹ thuật có `Dxx` kèm lý do; `Q-` còn mở không chặn MVP.
- [ ] Mỗi module có README + contract; không module nào gọi thẳng vào bên trong module khác.

**Ngữ cảnh cho AI**

- [ ] AGENTS.md không còn ví dụ mẫu; Restricted zone và Hot file là của dự án này.
- [ ] Mỗi thông tin chỉ ở một nơi; file lõi không còn chữ "TODO" hay "ví dụ".
- [ ] Thuật ngữ dùng đúng GLOSSARY; mỗi khái niệm một tên.
- [ ] AI phiên trắng chạy P-01 tóm tắt đúng dự án.

**Máy chặn**

- [ ] `python pos.py setup`, `python pos.py check` xanh trên máy sạch.
- [ ] Push thẳng main bị chặn; PR có chạy CI.
- [ ] Danh sách Restricted zone và Hot file khớp giữa AGENTS.md và `CODEOWNERS`.
- [ ] `.env` không vào Git; có `.env.example`.

Qua đủ bảng kiểm: chủ dự án duyệt → ghi `Dxx` "Qua cổng Ngày 0" → giao **T-001**.

### Task đầu tiên: T-001 khung chạy được

Một luồng mỏng chạy thông từ giao diện → API → dữ liệu cho **một** feature MVP, kèm 1 test e2e, qua đủ luồng chung (task → … → merge → done). Từ T-002 mới làm feature thật.

## 4. Luật cứng

Tám luật duy nhất không linh hoạt. Luật nào máy chặn được thì máy chặn, không dựa vào việc AI có đọc hay không.

| # | Luật | Máy chặn bằng |
| --- | --- | --- |
| 1 | Không push thẳng lên main; chỉ merge qua PR | Khoá main |
| 2 | Không đưa khoá bí mật vào Git, code, tài liệu | `.gitignore` có `.env`; quét khoá (gitleaks) |
| 3 | Chỉ push khi `python pos.py check` qua | pre-push hook; CI của PR là cổng cuối |
| 4 | Tiêu đề PR có mã: `<loại>(<mã>): <việc> [T-nnn]` | CI kiểm tiêu đề PR |
| 5 | Mã không bao giờ dùng lại; mã trong code phải có trong sổ mã | Kiểm sổ mã trong `python pos.py check` |
| 6 | Builder không tự sửa **contract đã khoá, Hot file, Restricted zone**. Cần sửa → dừng task, báo Orchestrator, xin duyệt | `CODEOWNERS` liệt kê đúng các đường dẫn này |
| 7 | PR chạm các đường dẫn ở luật 6 phải có **chủ dự án approve** | Khoá main: bắt buộc Code Owner approve (dùng merge queue: thêm job `approval-check`, phụ lục) |
| 8 | Không sửa ngoài Scope của thẻ; cần thì dừng và báo | pre-push hook và CI chạy `python pos.py scope` (so file đã sửa với dòng `Scope:` của thẻ trên main); Reviewer |

- Restricted zone và Hot file ghi **một danh sách** trong AGENTS.md, chép đúng sang `CODEOWNERS` (phụ lục). Mặc định Restricted zone: đăng nhập, phân quyền, thanh toán, contract, migration, xoá dữ liệu.
- Xin duyệt = Orchestrator tạo task riêng cho phần cần sửa; chủ dự án duyệt task trước, approve PR sau.
- Khẩn cấp (lỗi production): chỉ chủ dự án được cho bỏ qua luật, ghi lý do vào DECISIONS.md, làm task bù sau (P-14).

## 5. Thư mục và file

Thư mục xếp **theo thứ tự đọc**: trên cùng là thứ AI đọc mỗi phiên, xuống dần tới thứ chỉ máy dùng. Mở repo đọc từ trên xuống là hiểu dự án.

```
<repo>/
│  ① ĐỌC MỖI PHIÊN — luật và chỗ dừng
├── AGENTS.md                 luật cứng, luồng, Lane, lệnh, Hot file, Restricted zone
├── STATUS.md                 đang giữ · tiếp theo · đang chặn · bàn giao
│
│  ② HIỂU — có gì, vì sao, làm khi nào
├── docs/
│   ├── PROCESS.md            bản đầy đủ của tài liệu này
│   ├── GLOSSARY.md           bảng thuật ngữ: một khái niệm một tên
│   ├── product/
│   │   ├── BRIEF.md          ai dùng, vấn đề, thành công
│   │   └── FEATURES.md       sổ mã: domain → module → feature → code → test
│   ├── DECISIONS.md          D01…, Q-…
│   ├── plan/                 (khi có nhiều Milestone)
│   │   ├── ROADMAP.md        Milestone M1, M2…
│   │   └── M3-store-map.md   thẻ task của Milestone đang làm
│   └── prompts/              P-01.md … P-15.md, P-03-MULTI.md, P-SOS.md (mục 13)
│
│  ③ LÀM — code chia theo module
├── src/<module>/             Rust: crates/<module>/
│   ├── README.md             chức năng, vào/ra, phụ thuộc, mã
│   ├── contract.<đuôi>       kiểu dữ liệu + API công khai + mock; khoá sau task contract
│   └── …
│
│  ④ KIỂM — test chia theo tầng rồi module
├── tests/
│   ├── unit/<module>/
│   ├── api/<module>/
│   └── e2e/<module>/
│
│  ⑤ MÁY CHẶN — công cụ và cổng tự động
├── pos.py                    runner: setup · run · lint · test · features · check · task · done · drop
│                             · wt · wt-clean · pr · scope · plan-check · sos
├── Makefile                  lớp bọc tuỳ chọn gọi pos.py cho ai quen make
├── scripts/features.py      kiểm sổ mã, sinh cột Test (python pos.py features)
└── .github/
    ├── CODEOWNERS            cùng danh sách Restricted zone + Hot file với AGENTS.md
    ├── pull_request_template.md
    └── workflows/ci.yml

../wt/<mã>/                   worktree, ngoài repo; một thư mục cho mỗi task
```

- Thư mục nào chưa cần thì chưa tạo (ví dụ `docs/plan/` khi mới có một Milestone).
- Thư mục module = mã module viết thường: `MAP` → `src/map/`, `tests/api/map/`.
- Module nói chuyện với nhau chỉ qua contract.
- Mỗi thông tin ở một nơi; nơi khác ghi mã. Lỗi thời thì xoá ngay.
- Codex, Antigravity và Claude Code (từ 2.1.277) đều tự đọc AGENTS.md. Claude Code bỏ qua AGENTS.md khi có CLAUDE.md, nên nếu tạo CLAUDE.md thì file đó chỉ có đúng một dòng @AGENTS.md.

## 6. Mã

Hai trục nối nhau qua mã feature: **Sản phẩm** (có gì, sống lâu) và **Kế hoạch** (khi nào làm, xong thì đóng).

| Trục | Cấp | Mã | Nguồn |
| --- | --- | --- | --- |
| Sản phẩm | Domain | `SALES` (không vào mã) | Tiêu đề nhóm trong FEATURES.md |
| Sản phẩm | Module · Feature | `MAP` · `MAP-07` | FEATURES.md |
| Lý do | Quyết định · Câu hỏi mở | `D59` · `Q-map` | DECISIONS.md |
| Kế hoạch (khi có plan) | Milestone · Wave · Task | `M3` · `W1` · `T-042` | ROADMAP.md · plan của Milestone |
| Cách làm | Prompt | `P-04` | docs/prompts/ (mục 13) |

- Cấp một lần, không dùng lại. Bỏ feature: giữ dòng, trạng thái `bỏ (Dxx)`.
- Task ghi feature nó làm (`T-042 · MAP-07`); số task tăng liên tục, chỉ Orchestrator cấp.
- Dùng GitHub Issues/Linear (tuỳ chọn): cho số T trùng số Issue (`T-043` = Issue `#43`) và ghi `Closes #43` ở **thân** PR (tiêu đề giữ đúng mẫu luật 4). Merge squash thì Issue tự đóng, bảng Kanban tự cập nhật; không dùng thì bỏ qua.

**Mẫu `docs/product/FEATURES.md`**:

```
## SALES · Bán hàng
### MAP · Bản đồ điểm bán
| Mã     | Hành vi chính                                         | Code chính (điểm vào)   | Test liên quan                  | QĐ  | Trạng thái |
| ------ | ----------------------------------------------------- | ----------------------- | ------------------------------- | --- | ---------- |
| MAP-07 | Sales chỉ thấy điểm bán trong phạm vi được cấp quyền | src/map/service.py      | tests/api/map/test_scope.py (5) | D59 | dùng       |
| MAP-02 | Sales mở bản đồ từ Bảng tin, ghim tô màu theo lần ghé | src/map/web/MapPage.tsx | tests/e2e/map/map.spec.ts (2)   | D59 | dùng       |
| MAP-09 | Lọc ghim theo khung nhìn                              | —                       | —                               | D61 | bỏ (D61)   |
```

- **Hành vi chính:** viết theo điều người dùng thấy, kiểm chứng được bằng test.
- **Code chính:** 1–2 file điểm vào; file còn lại tìm bằng `rg "<mã>"`.
- **Test liên quan:** `python pos.py features --sync` tự sinh từ mã gắn trong test (đường dẫn + số lần gắn), không ghi tay. Chưa có test tự động thì ghi `— (lý do)`.
- **QĐ:** mã quyết định liên quan.
- **Trạng thái:** `dự kiến` (chưa làm, đã có hành vi) · `dùng` · `bỏ (Dxx)`. Mã bỏ giữ dòng, không còn trong code.

**Mẫu `docs/DECISIONS.md`:**

```
| Mã  | Ngày       | Quyết định                              | Lý do                     | Mã liên quan    | Duyệt     |
| --- | ---------- | --------------------------------------- | ------------------------- | --------------- | --------- |
| D59 | 2026-11-08 | Bản đồ tải một lần, tối đa 5.000 điểm   | Đủ nhanh, đơn giản        | MAP-01…MAP-08   | Chủ dự án |
| D60 | 2026-11-09 | Gom cụm tính lại khi dừng kéo bản đồ    | Máy yếu không bị giật     | MAP-02          | AI        |

## Còn mở
| Mã    | Câu hỏi                          | Chờ ai      |
| ----- | -------------------------------- | ----------- |
| Q-map | Nguồn ô bản đồ trước khi mở rộng | Chủ dự án   |
```

## 7. Kế hoạch và bàn giao

| File | Trả lời | Nguồn duy nhất của | Ai ghi |
| --- | --- | --- | --- |
| ROADMAP.md | Làm gì, thứ tự nào | Milestone + trạng thái | Orchestrator đề xuất, chủ dự án duyệt |
| Plan `M3-*.md` | Milestone này làm thế nào | Thẻ task + ô tick | Orchestrator |
| STATUS.md | Phiên trước dừng ở đâu | Ai giữ task nào, đang chặn gì, ghi chú bàn giao | Orchestrator (một AI: chính nó) |

Dự án nhỏ chỉ cần STATUS.md, dùng mục "Tiếp theo" thay plan. "Vừa xong" không ghi ở đâu: đã có trong Git. Milestone nghiệm thu thì xoá plan (lịch sử ở Git).

```
# STATUS · 2026-11-09 · M3
## Đang giữ          T-043 · Builder A · feat/T-043-map-sales
## Tiếp theo         T-044
## Đang chặn         Q-map: nguồn ô bản đồ (chờ chủ dự án)
## Ghi chú bàn giao  Thẻ điểm bán xong; còn offline. Chạy python pos.py test F=MAP-02 trước.
```

**Mẫu `docs/plan/ROADMAP.md`** (khi có nhiều Milestone):

```
| Milestone | Mục tiêu            | Feature        | Plan              | Trạng thái              |
| --------- | ------------------- | -------------- | ----------------- | ----------------------- |
| M2        | Báo đơn và nhận đơn | ORD-01…ORD-09  | —                 | xong 2026-10-20 · v0.4  |
| M3        | Bản đồ điểm bán     | MAP-01…MAP-08  | plan/M3-store-map.md | đang làm             |
| M4        | Báo cáo theo vùng   | RPT-09…        | —                 | chưa bắt đầu            |
```

## 8. Làm một task

**1 task = 1 branch = 1 worktree = 1 PR.** Cả bốn mang cùng mã, sinh ra cùng lúc, dọn cùng lúc.

| Khái niệm | Là gì | Tên theo mẫu |
| --- | --- | --- |
| Task | Đơn vị công việc | `T-043` (Lane Fast: mã feature `MAP-02`) |
| Branch | Dòng phát triển code | `feat/T-043-map-sales` |
| Worktree | Thư mục làm việc riêng | `../wt/T-043` |
| Commit | Điểm lưu thay đổi; nhiều commit trong một task | Tự do ở local |
| PR | Yêu cầu merge code vào main | `feat(MAP-02): … [T-043]` |

### Vòng đời worktree

| Bước | Lệnh | Ai, khi nào |
| --- | --- | --- |
| Tạo | `python pos.py task T=T-043 N=map-sales` = `git fetch` + `git worktree add ../wt/T-043 -b feat/T-043-map-sales origin/main` | Builder, khi nhận thẻ |
| Làm | Chỉ sửa trong `../wt/T-043`, không đụng worktree khác | Builder |
| Cập nhật | `git fetch && git rebase origin/main` | Builder, trước khi push |
| Dọn | `python pos.py done T=T-043` = `git worktree remove` + xoá branch đã merge + `git worktree prune` | Orchestrator, ngay sau khi merge |
| Huỷ | `python pos.py drop T=T-043` (xoá branch chưa merge) | Orchestrator, **hỏi chủ dự án trước** |

- Worktree đặt ngoài repo (`../wt/`), không lồng trong repo.
- Lệnh nằm ở `pos.py` (cần Python 3, không cần make hay bash; Linux/macOS có thể phải gõ `python3`); `python pos.py wt` liệt kê worktree đang có. `python pos.py done` nhận ra PR đã merge squash qua lệnh `gh`; máy không có `gh` thì chỉ nhận ra branch đã merge thường.
- Cuối phiên, Orchestrator chạy `python pos.py wt-clean`: liệt kê worktree mồ côi (branch đã merge vào main, hoặc PR đã MERGED qua `gh`; bỏ qua cái còn thay đổi chưa commit). Đúng danh sách thì `python pos.py wt-clean APPLY=1` để dọn. Worktree chưa merge mà không có trong "Đang giữ" của STATUS thì báo, không tự xoá (huỷ phải qua `drop`).
- Mở PR: `python pos.py pr` in sẵn khung báo cáo từ `git diff --stat`, commit, mã feature và kết quả `check`; Builder chỉ điền các ô còn trống.

### Luồng chung (mọi Lane)

```
task → code → commit → check → rebase → push → PR → CI → [approve nếu Lane Strict] → merge → done
```

### Chọn Lane theo rủi ro

AI tự chọn Lane và ghi Lane vào mô tả PR. Phân vân thì chọn Lane cao hơn. Đang làm mà phát hiện chạm Restricted zone, contract hay Hot file thì **nâng Lane**: dừng, báo Orchestrator, xin duyệt.

| Lane | Khi nào | Được bỏ | Bắt buộc thêm |
| --- | --- | --- | --- |
| **Fast** | Câu chữ, tài liệu, lỗi nhỏ rõ nguyên nhân; không chạm Restricted zone, contract, Hot file | Thẻ task, số T, plan, Reviewer | — (task mang mã feature: `python pos.py task T=MAP-02 N=typo TYPE=fix`) |
| **Normal** | Feature hoặc sửa lỗi có logic; 1 Builder | Reviewer, merge queue | Thẻ task, test cho hành vi mới |
| **Strict** | Chạm Restricted zone, contract, Hot file; hoặc nhiều Builder chạy song song | — | Task riêng được chủ dự án duyệt trước; chủ dự án approve PR; song song: worktree riêng + PR phải rebase theo main trước khi merge |

### Các bước

1. **Nạp ngữ cảnh:** AGENTS.md → STATUS.md → thẻ task (nếu có) → dòng mã → `rg "<mã>"`.
2. **`python pos.py task`:** worktree + branch từ main mới nhất.
3. **Code + commit:** dò Scope trước; commit ở local thoải mái.
4. **`python pos.py check`:** lỗi → sửa → check lại.
5. **Rebase + push + PR:** `git rebase origin/main`, pre-push hook chạy lại check và scope, mở PR theo mẫu (ghi Lane).
6. **CI của PR:** lỗi → sửa ở local → push lại. Lane Strict: chờ chủ dự án approve.
7. **Merge + done:** squash vào main → `python pos.py done` → tick task, cập nhật STATUS.

```
MÁY LOCAL (mỗi Builder một worktree)            GITHUB
python pos.py task ──► code + commit ──► python pos.py check ─┐
                  ▲                lỗi      │ qua
                  └─────────────────────────┤
                                            ▼
                       rebase origin/main ──► pre-push hook ──► push
                                                                 │
     Mở PR (mẫu thẻ, ghi Lane) ◄─────────────────────────────────┘
        │
        ▼
     CI của PR ── lỗi ──► sửa ở local, push lại
        │ qua
        ▼
     Lane Strict? ── có ──► chờ chủ dự án approve
        │ không
        ▼
     Merge (squash, PR đã rebase theo main) ──► python pos.py done · tick task · STATUS
```

Bên trái là việc của Builder trên máy mình; chỉ khi check qua mới sang GitHub, nơi CI của PR là cổng không tắt được.

**Thẻ task (cũng là prompt giao việc):**

```
- [ ] T-043 · MAP-02 · web Sales
      Mục tiêu:  Sales mở bản đồ điểm bán từ Bảng tin
      Lane:      Strict (song song)
      Wave:      W1                       Read (RO): src/*/contract.*
      Scope:     src/map/web/*, tests/e2e/map/*
      Phụ thuộc: T-042 (W0, contract đã khoá)
      Cần:       MapPoint, list_points()  (chỉ thẻ W1: kiểu và hàm của contract mà task dùng)
      Restricted zone: không              Giao: Builder A · feat/T-043-map-sales
      Xong khi:  python pos.py test F=MAP-02 qua; thử tay trên điện thoại
```

`python pos.py scope` đọc dòng `Scope:` của thẻ từ `docs/plan/*.md` trên `origin/main` (không đọc từ branch đang làm), nên Builder không tự mở rộng Scope. Ghi Scope bằng mẫu đường dẫn cách nhau bởi dấu phẩy hoặc khoảng trắng, **gồm cả thư mục test**. Scope là quyền ghi (RW); Read (RO) chỉ để Builder biết được tham chiếu gì, không được sửa. Pre-push chặn khi push; CI chạy lại `python pos.py scope` để `--no-verify` không lách được. Lane Fast và branch không có số T thì bỏ qua. Cần mở rộng: Builder dừng và báo, Orchestrator sửa thẻ trên main, Builder rebase rồi push lại.

**Báo cáo khi xong:**

```
Đã làm · Scope thực tế (khớp thẻ / thêm gì, vì sao) · File thay đổi
Test đã chạy · Khác mặc định (nếu có, lý do) · Rủi ro · Ghi chú bàn giao
```

## 9. Quy tắc code

**Mẫu đầu file ranh giới** (route, service, contract, màn hình, job): 3 dòng cố định, cùng cấu trúc ở mọi ngôn ngữ.

```
# Python
"""MAP-07 · Dữ liệu bản đồ điểm bán
Vai trò: một truy vấn gom nhóm cho mọi điểm bán trong phạm vi người xem.
Lý do: D59 · Xem: src/map/README.md
"""

// Rust
//! MAP-07 · Dữ liệu bản đồ điểm bán
//! Vai trò: một truy vấn gom nhóm cho mọi điểm bán trong phạm vi người xem.
//! Lý do: D59 · Xem: crates/map/README.md

// TypeScript
/**
 * MAP-02 · Màn bản đồ Sales
 * Vai trò: hiện ghim, thẻ điểm bán, danh sách; offline thì danh sách đã lưu.
 * Lý do: D59 · Xem: src/map/README.md
 */
```

| Quy tắc | Đúng | Tránh |
| --- | --- | --- |
| Comment chỉ ở logic khó, giải thích **tại sao** | `# MAP-07: semi-join; EXISTS per row is 10x slower` | `# loop over stores` (nói lại điều code đã rõ) |
| Theo cấu trúc có sẵn; thêm vào file cùng chức năng | Thêm hàm vào `src/map/service.py` | Tạo `service2.py`, `utils_new.py` |
| Tìm hàm tương tự trước khi viết mới | `rg "def .*distance"` trước khi viết `haversine()` | Viết lại hàm đã có ở module khác |
| Không cài thư viện mới khi chưa hỏi | Hỏi; được duyệt thì ghi `Dxx` | Tự thêm vào `pyproject.toml`, `Cargo.toml`, `package.json` |
| Hằng số cấu hình có tên, ở một chỗ | `MAP_LIST_CAP = 5000` trong file config | Số `5000` rải ở nhiều file |
| Lỗi báo rõ, không nuốt lỗi | `raise StoreNotFound(store_id)` | `except Exception: pass` |
| Định dạng do máy lo | `python pos.py lint` (ruff · clippy + rustfmt · eslint + prettier) | Sửa tay khoảng trắng trong review |

## 10. Test và commit

Mỗi test gắn **một mã** và **một tầng**, nên chạy được đúng nhóm cần: `python pos.py test F=MAP-07` · `python pos.py test L=api` · `python pos.py check` (trước khi push).

| Tầng | Kiểm gì | Khi cần |
| --- | --- | --- |
| `unit` | Logic thuần | Đổi logic |
| `api` | Endpoint, quyền, dữ liệu | Đổi API hoặc phạm vi quyền |
| `e2e` | Luồng người dùng | Đổi luồng; nhóm `smoke` chạy trong CI |

Gắn mã: Python `@pytest.mark.feature("MAP-07")` · Rust tên hàm `map_07_…` · TS `describe("MAP-07 …")`, Playwright `@MAP-07`.

**Commit:** ở local tự do, thường xuyên. Khi merge, PR được ép thành một commit (squash); **tiêu đề PR** là commit chính thức:

```
feat(MAP-07): add GET /stores/map with team/company scope [T-042]

Why: D59 · Test: python pos.py test F=MAP-07 (api 5 pass)
```

Loại: `feat` · `fix` · `refactor` · `test` · `docs` · `chore` (chore không cần mã).

## 11. Nhiều agent song song

Chỉ dùng khi có từ 2 task không trùng file. Chỉ có một AI thì nó đóng lần lượt cả ba vai.

| Vai | Nhìn gì | Làm gì | Không làm |
| --- | --- | --- | --- |
| Orchestrator | ROADMAP, plan, STATUS, FEATURES, DECISIONS | Viết thẻ, kiểm trùng Scope, cấp số T, chạy merge queue, cập nhật plan + STATUS | Viết code feature |
| Builder | Thẻ của mình, README module, contract, `rg "<mã>"` | Luồng chung (mục 8) trên worktree riêng | Sửa ngoài Scope, contract đã khoá, Hot file |
| Reviewer | Diff của PR + "Xong khi" | Chỉ PR chạm Restricted zone: kiểm, đề xuất bản sửa, rồi chuyển chủ dự án approve | Kiểm PR thường (CI đã lo), tự merge |

### Plan theo Wave (đồ thị không chu trình, DAG)

Plan nhiều agent chia theo **Wave**, mỗi thẻ ghi `Wave: W<n>`. Task chỉ phụ thuộc task ở Wave **trước**, không bao giờ cùng Wave hoặc sau.

```
W0 Nền        1 agent    Task contract: kiểu dữ liệu + mock; khoá rồi mới sang W1
 │
W1 Song song  2–5 agent  Mỗi task một worktree, một Scope (RW) riêng; chỉ Read contract (RO)
 │                       PR vào merge queue lần lượt (rebase + CI)
W2 Nối dây    1 agent    Nối module vào ứng dụng chính, Hot file, e2e tổng
```

- **Đất của ai người đó xây:** Wave nào cũng phải có Scope (RW) đôi một rời nhau. `python pos.py plan-check` chặn: trùng Scope cùng Wave, Phụ thuộc trỏ ngang hoặc ngược Wave, task ở Wave song song ghi vào Hot file, Wave quá 5 task. Chạy trước khi chủ dự án duyệt plan.
- **Sửa chéo thì sang Wave sau:** Builder A cần sửa code của Builder B → dừng, Orchestrator mở task riêng ở Wave sau. Không sửa chéo trong cùng Wave.
- **Đừng ép song song:** W1 chỉ có 1 task thì cứ chạy tuần tự. Thêm agent là thêm gánh review và gánh duyệt của chủ dự án; mặc định 3, tối đa 5.
- **Không "không bao giờ xung đột":** plan-check loại xung đột file do chia việc. Còn lại (lockfile, tài liệu dùng chung, sổ mã) do merge queue bắt bằng rebase + CI; file dùng chung kiểu này chỉ Orchestrator hoặc task W2 được ghi.

### Hot file: đăng ký động thay vì sửa tay

Hot file (route, registry, schema) là nguồn xung đột số một. Thiết kế để module **tự đăng ký**, file gốc không phải sửa khi thêm feature:

| Cách | Khi nào |
| --- | --- |
| Module xuất `register(app)`; file gốc quét thư mục và gọi (Python `pkgutil`, Node `glob` import) | Ngôn ngữ nạp động được |
| Mỗi module một file khai báo (`routes/<module>.ts`); file gốc chỉ là thư mục | Khung web có route theo file |
| Sinh code tự động (`build.rs`, `inventory`, `go generate`) | Rust, Go: không quét lúc chạy được |
| Vẫn phải sửa tay một dòng | Dòng đó thuộc task W2, không thuộc W1 |

Chọn một cách ở Ngày 0 (ghi `Dxx`), file gốc ra khỏi danh sách Hot file khi đã tự nạp. Đánh đổi: nạp tự động khó truy dấu hơn, nên mỗi module ghi vào README tên đăng ký của mình. Manifest phụ thuộc (`package.json`, `Cargo.toml`, lockfile) cũng là Hot file: khai báo ở W0 hoặc W2, hoặc mỗi module một manifest riêng.

```
                 Chủ dự án duyệt plan
                         │
                   Orchestrator  (chia thẻ, kiểm trùng Scope)
                         │
                   W0 · Task contract (làm trước, chốt rồi khoá)
          ┌──────────────┼──────────────┐      W1 · chạy đồng thời, khác Scope
     Builder A        Builder B       Builder C
     T-043            T-044           T-045
     check            check           check → push PR
          └──────────────┼──────────────┘
                  Merge queue (lần lượt: rebase + CI của PR)
                         │
              Restricted zone? ── có ──► Reviewer (≤ 2 vòng) ──► quá 2 vòng: chủ dự án quyết
                         │ không / đạt
                   Merge + STATUS (Orchestrator tick task)
```

Song song chỉ nằm giữa hai điểm tuần tự: **task contract khoá trước**, **merge queue từng PR sau** (rebase theo main, CI lại).

**Mock đi kèm contract:** task contract viết luôn mock ngay dưới kiểu dữ liệu, ví dụ `MOCK_USER` trong `src/auth/contract.py`. Builder cần module chưa xong thì import mock để viết test và chạy thử, không chờ Builder kia, không cần DB thật. Module thật xong thì test đổi sang bản thật và **bắt buộc** giữ một contract test so mock với bản thật ở mọi module W1 (chống hardcode theo mock).

**Cổng khoá contract (cuối W0):** mỗi thẻ W1 ghi `Cần:` (kiểu và hàm của contract mà nó dùng). Orchestrator đối chiếu từng mục với contract và mock; thiếu mục nào thì bổ sung vào task contract **trước khi khoá**. Hở contract hầu hết là lỗi lập plan, chặn ở đây rẻ hơn nhiều so với vá giữa chừng.

### Hở contract giữa chừng

Task đang làm phát hiện contract hoặc task trước thiếu sót (luật cứng 6 và 8 áp dụng, không sửa lén, không hardcode):

1. **Dừng và lưu:** commit WIP lên branch của task, không sửa module khác.
2. **Báo:** ghi `Đang chặn` trong STATUS; Orchestrator dùng P-10, tra `rg` theo mã để liệt kê **mọi task dùng phần contract đó**; các task ấy tạm dừng, không chỉ task bị kẹt.
3. **Task vá:** một task riêng Lane Strict, chờ chủ dự án duyệt. Orchestrator sửa `Phụ thuộc` của các thẻ bị ảnh hưởng (trỏ về task vá) và chạy lại `python pos.py plan-check`.
4. **Sau khi task vá merge:** Builder bị kẹt rebase **rồi chạy lại contract test và `check`**. Rebase chỉ giữ code, không đảm bảo code đúng với contract mới; phần dựa trên contract hoặc mock cũ phải sửa.
5. **Không ngồi chờ:** Builder bị kẹt nhận task khác ở cùng Wave hoặc dừng phiên (P-09).

- Chỉ Orchestrator ghi plan, STATUS và cấp số task; Builder ghi bàn giao trong báo cáo.
- Chủ dự án duyệt: plan của Milestone, mọi PR Lane Strict (approve), khi Reviewer quá 2 vòng chưa đạt, và quyết định lớn (mục 12).
- Không gắn công cụ: Claude, Codex, Gemini, Cursor… đóng vai nào cũng được, vì cùng đọc AGENTS.md, plan và STATUS.

## 12. Mặc định: AI được linh hoạt

Đây là điểm xuất phát, không phải luật. AI được làm khác khi hợp lý hơn, miễn không chạm luật cứng, và ghi một dòng lý do ở mục "Khác mặc định" trong báo cáo.

| Việc | Mặc định | Nên làm khác khi |
| --- | --- | --- |
| Chọn Lane | Theo bảng Lane ở mục 8 | Phân vân, hoặc sửa nhỏ nhưng rủi ro → Lane cao hơn |
| Cỡ task | Vừa một phiên | Việc liền mạch khó tách → task lớn hơn, chia bước trong plan |
| Số Builder song song | Bằng số task không trùng file, mặc định tối đa 3 | Nhiều Hot file → chạy tuần tự; cần nhanh hơn → tới 5 (trần của plan-check) |
| Test cần viết | Tầng theo bảng mục 10 | Sửa câu chữ, tài liệu → không cần test mới |
| Độ dài tài liệu | AGENTS \~150 dòng, STATUS \~20, README \~10 | Cần thêm → dẫn link sang file khác, không phình |
| Tách file code | Đề xuất khi file > \~300 dòng | File sinh tự động, bảng dữ liệu → không tách |
| Mô tả đầu file | Có ở file ranh giới | File nhỏ, tên đã rõ → bỏ qua |
| Số vòng Reviewer | Tối đa 2, sau đó chủ dự án quyết | Lỗi rõ ràng, sửa nhanh → thêm 1 vòng |
| Mức chi tiết plan | Thẻ task + rủi ro chính | Milestone nhỏ → chỉ danh sách thẻ |
| Ghi quyết định | AI tự ghi `Dxx` cho quyết định nhỏ, cột Duyệt = `AI` | Contract, thư viện mới, cấu trúc thư mục, Restricted zone → chờ chủ dự án duyệt |
| Kế hoạch | Chỉ STATUS.md, mã feature + Dxx | Nhiều Milestone hoặc nhiều agent → thêm ROADMAP, plan của Milestone, mã M, W và T |
| Kiểm | `python pos.py check` + pre-push hook, merge trên máy | Có remote: CI của PR. Từ 2 Builder: worktree riêng + bật "Require branches to be up to date". Từ 3 agent hoặc nhiều người: merge queue |

## 13. Bảng prompt

Mỗi bước của luồng có một prompt mẫu, mã `P-nn`. Bản đầy đủ đặt ở `docs/prompts/P-nn.md`; gọi nhanh bằng mã, ví dụ "Chạy P-04 với thẻ T-043". Phần trong `<…>` là chỗ điền. Trong prompt, "tôi" là chủ dự án.

| Mã | Khi dùng | Vai | Prompt | Đầu ra |
| --- | --- | --- | --- | --- |
| P-01 | Mở phiên | Mọi vai | Đọc AGENTS.md và STATUS.md. Tóm tắt trong 5 dòng: Milestone nào, ai giữ task nào, đang chặn gì, việc tiếp theo. Chưa sửa gì. | 5 dòng tóm tắt |
| P-02 | Khởi tạo dự án | Orchestrator | Từ BRIEF sau: `<brief>`. Làm Ngày 0 theo mục 3, từng bước: BRIEF → FEATURES → DECISIONS → module + contract → AGENTS + STATUS → khung repo. Trình đầu ra mỗi bước, chờ tôi duyệt rồi mới sang bước sau. | Bộ file Ngày 0 |
| P-03 | Lập plan (một agent) | Orchestrator | Lập plan cho Milestone `<M3>`: `<mục tiêu>`. Đọc ROADMAP, FEATURES, DECISIONS. Viết thẻ task theo mẫu, task contract đi đầu, ghi Lane từng task, kiểm hai task song song không trùng Scope. Chờ tôi duyệt. | `docs/plan/M3-*.md` |
| P-03-MULTI | Lập plan nhiều agent | Orchestrator | Lập plan cho Milestone `<M3>` theo đồ thị không chu trình. Đọc BRIEF, FEATURES, ROADMAP, DECISIONS. Chia W0 (task contract + mock) → W1 (2–5 task song song) → W2 (nối dây + e2e). Mỗi thẻ ghi Wave, Scope (RW), Read (RO), Phụ thuộc chỉ trỏ Wave trước. Cách đăng ký module để không sửa Hot file. Chạy `python pos.py plan-check` đến khi qua, dán kết quả. Chờ tôi duyệt. | `docs/plan/M3-*.md` + kết quả plan-check |
| P-04 | Giao task | Orchestrator → Builder | Làm task sau theo luồng chung: `<thẻ task>`. Dừng và báo nếu cần sửa ngoài Scope, hoặc phải chạm contract, Hot file, Restricted zone. Trước khi mở PR tự hỏi: (1) file ranh giới mới đã có 3 dòng đầu file gắn mã chưa? (2) test mới đã gắn mã feature chưa? (3) `python pos.py check` đã in "qua" chưa? Xong thì báo cáo theo mẫu. | PR + báo cáo |
| P-05 | Sửa nhanh | Builder (solo) | Lane Fast, mã `<MAP-02>`: `<việc cần sửa>`. `python pos.py task T=<mã> N=<short-name> TYPE=fix` → sửa → `python pos.py check` → PR. | PR nhỏ |
| P-06 | Sửa lỗi | Builder | Lỗi: `<hiện tượng, log>`. Mã liên quan: `<MAP-07>`. Viết test tái hiện lỗi trước, rồi sửa. Lane Normal. | Test đỏ → xanh, PR |
| P-07 | Review Restricted zone | Reviewer | Review PR `<#n>` (Lane Strict). Đối chiếu "Xong khi", Scope của thẻ, luật cứng 6–8. Kết luận Đạt hoặc Trả lại kèm bản sửa đề xuất. Không merge. | Kết luận + lý do |
| P-08 | Merge và dọn | Orchestrator | PR `<#n>` đã qua CI (và đã được approve nếu Lane Strict). Merge squash, `python pos.py done T=<mã>`, tick task trong plan, cập nhật STATUS. | main mới, STATUS mới |
| P-09 | Cuối phiên | Orchestrator | Kết thúc phiên. Cập nhật STATUS (đang giữ, đang chặn, bàn giao ≤ 3 dòng). Chạy `python pos.py wt-clean` (dọn worktree mồ côi bằng `APPLY=1`), báo worktree thừa chưa merge. | STATUS mới |
| P-10 | Nâng Lane / đổi contract | Orchestrator | Task `<T-043>` cần sửa `<file>` vì `<lý do>`. Liệt kê ảnh hưởng (`rg` theo mã), tạo task riêng Lane Strict. Chờ tôi duyệt. | Task mới + ảnh hưởng |
| P-11 | Ghi quyết định | Mọi vai | Ghi quyết định: `<nội dung>`, lý do `<…>`. Cấp mã D tiếp theo, điền bảng DECISIONS, cột Duyệt = `<Chủ dự án/AI>`, ghi mã liên quan. | Dòng Dxx mới |
| P-12 | Rà tài liệu | Orchestrator | Rà AGENTS.md, STATUS, FEATURES, DECISIONS, GLOSSARY: thông tin trùng, lỗi thời, thuật ngữ lệch GLOSSARY, mã thiếu test, worktree thừa. Liệt kê, chưa sửa. | Danh sách cần dọn |
| P-13 | Nghiệm thu Milestone | Orchestrator | Milestone `<M3>` đã nghiệm thu, phiên bản `<v0.5>`. Đánh dấu xong trong ROADMAP, xoá plan của Milestone, dọn STATUS, liệt kê câu hỏi Q- còn mở. | ROADMAP mới |
| P-14 | Khẩn cấp | Builder | Lỗi production: `<hiện tượng>`. Sửa nhanh nhất; tôi cho phép bỏ qua `<luật>`. Ghi lý do vào DECISIONS, tạo task bù. | Hotfix + Dxx + task bù |
| P-15 | Kiểm toán Ngày 0 | Orchestrator (phiên mới) | Kiểm toán repo theo bảng kiểm mục 3. Với từng ô: Đạt hoặc Chưa, kèm bằng chứng (file, dòng). Không sửa gì. Cuối cùng kết luận: qua cổng hay chưa, còn thiếu gì. | Bảng Đạt/Chưa + kết luận |
| P-SOS | Bị kẹt, cần cứu hộ | Orchestrator | Chạy `python pos.py sos` (sao lưu vào branch `salvage/sos-*`, khám bệnh, chỉ đọc). Báo ≤ 5 dòng dễ hiểu, đưa 2 phương án: A cứu task theo đúng luồng, B huỷ task và về main xanh. Chờ tôi chọn A/B rồi mới làm. | Báo cáo + repo về chuẩn |

- Thứ tự dùng trong một Milestone: P-01 → P-03 (một agent) hoặc P-03-MULTI (nhiều agent) → (P-04 hoặc P-05, P-06) → P-07 khi cần → P-08 → P-09. Hết Milestone: P-13. Dự án mới: P-02 → P-15 → chủ dự án duyệt → T-001. Bị kẹt bất kỳ lúc nào: P-SOS (mã chữ, không chiếm số P-nn).
- Prompt cũng là mã: không dùng lại số, sửa nội dung thì sửa ở đây trước rồi sửa `docs/prompts/` cho khớp.

## Phụ lục · Mẫu

**AGENTS.md**

```
# AGENTS · Luật của dự án
## Mục tiêu          1–2 câu, dẫn docs/product/BRIEF.md
## Đọc khi mở phiên  AGENTS.md → STATUS.md → thẻ task → dòng mã → rg "<mã>"; thuật ngữ: docs/GLOSSARY.md
## Lệnh              python pos.py setup · run · test [F=<mã>] [L=<tầng>] · lint · check · task · done
## Luồng             task → code → commit → check → rebase → push → PR → CI → [approve nếu Lane Strict] → merge → done
## Lane              Fast · Normal · Strict (PROCESS.md mục 8); phân vân thì chọn Lane cao hơn
## Luật cứng         8 luật (PROCESS.md mục 4)
## Hot file          src/app/routes.*, db/schema.*, src/copy.*, .github/**
## Restricted zone   src/auth/, src/payment/, db/migrations/, **/contract.*
## Báo cáo           Đã làm · Scope thực tế · File · Test · Khác mặc định · Rủi ro · Bàn giao
```

**Kiểm tiêu đề PR (regex cho CI, khớp `.github/workflows/ci.yml`)**

```
^(feat|fix|refactor|test|docs)\([A-Z]+-[0-9]{2,}(,[A-Z]+-[0-9]{2,})*\): [^[]+( \[T-[0-9]{3,}\])?$
^chore: [^[]+( \[T-[0-9]{3,}\])?$
```

**CODEOWNERS**

```
# Restricted zone + contract + Hot file → bắt buộc chủ dự án approve (cùng danh sách với AGENTS.md)
/src/auth/           @chu-du-an
/src/payment/        @chu-du-an
/db/migrations/      @chu-du-an
**/contract.*        @chu-du-an
/src/app/routes.*    @chu-du-an
/.github/            @chu-du-an
```

Bật trên GitHub: khoá main → **Require review from Code Owners**. Khi dùng merge queue, thêm job CI `approval-check`: `gh pr view --json reviewDecision` phải là `APPROVED` thì mới merge.

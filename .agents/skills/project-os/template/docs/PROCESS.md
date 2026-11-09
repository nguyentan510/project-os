# Quy tắc triển khai dự án

Phiên bản 1.0 · 2026-11-09 · Nguồn gốc của mọi quy tắc trong repo này.

AI nào mở dự án cũng phải trả lời được trong 1 phút: **đang làm gì, đã làm gì, sửa thì bắt đầu từ đâu**. Đầu mối chung là **mã** (`MAP-07`).

Quy tắc có 3 tầng: **Luật cứng** (mục 4, máy chặn, không ngoại lệ) · **Mặc định** (mục 12, AI được làm khác khi hợp lý hơn và ghi lý do) · **Mẫu** (phụ lục, dùng khi cần). Bắt đầu tối giản; phần nào chưa cần thì chưa bật (mục 12). Dự án mới bắt đầu từ mục 3.

## 1. Bốn câu hỏi, bốn đầu mối

| Câu hỏi | Đầu mối | Cách tra |
| --- | --- | --- |
| Luật chơi là gì? | `AGENTS.md` | Đọc đầu tiên |
| Phiên trước dừng ở đâu? | `STATUS.md` | Đọc, ngắn |
| Mốc nào, task nào? | `docs/plan/` | ROADMAP → plan mốc (khi có) |
| Đã làm gì? | Git | `git log --oneline --grep "MAP-07"` |
| Sửa X bắt đầu từ đâu? | `docs/product/FEATURES.md` | Dòng mã → `rg "MAP-07"` |
| Vì sao làm vậy? | `docs/DECISIONS.md` | `rg "D59" docs/DECISIONS.md` |

## 2. Onboarding

Người hay AI mới làm 5 bước:

1. Đọc `AGENTS.md` rồi `docs/product/BRIEF.md`: dự án để làm gì.
2. Đọc STATUS.md (và ROADMAP nếu có): đang ở đâu.
3. `python pos.py setup` → `python pos.py check`: máy chạy được, test xanh.
4. Chọn một mã, chạy `rg "<mã>"` và `git log --grep "<mã>"`: thấy mã nối code, test, commit thế nào.
5. Làm task mẫu `T-000` theo làn nhanh: sửa một dòng câu chữ, đi hết nhánh → PR → gộp.

| Từ | Nghĩa |
| --- | --- |
| Mã | Định danh ổn định: `MAP-07`, `D59`, `T-042` |
| Contract | Thỏa thuận kiểu dữ liệu và API giữa các phần; khóa sau task contract |
| Thẻ task | Mô tả đủ một task: mã, mục tiêu, phạm vi, phụ thuộc, xong khi |
| File nóng · Vùng cấm | File nhiều task cùng cần · phần rủi ro cao phải qua Reviewer |
| Worktree | Thư mục làm việc độc lập; 1 Task = 1 Branch = 1 Worktree = 1 PR (mục 8) |
| Kiểm local | `python pos.py check`: test + lint + kiểm sổ mã, qua mới được push |
| PR · CI của PR | Yêu cầu gộp nhánh · máy chủ chạy lại kiểm tra trên PR |
| Squash · Rebase | Ép các commit của PR thành một · đưa nhánh lên bản mới nhất của main |
| Hàng chờ gộp | Gộp từng PR một, mỗi lần chạy lại CI |
| Human Approval | Bạn bấm duyệt PR trên GitHub; bắt buộc với PR chạm contract, file nóng, vùng cấm |

## 3. Ngày 0: trước dòng code đầu tiên

**Chưa qua cổng Ngày 0 thì chưa viết code.** Mục tiêu: AI đầu tiên mở repo đã có đủ ngữ cảnh, không phải đoán ý định, phạm vi hay công nghệ.

### Thứ tự lập

Mỗi bước có đầu ra; bạn duyệt rồi mới sang bước sau (prompt P-02).

1. **BRIEF** — làm cho ai, để làm gì, thế nào là thành công.
2. **FEATURES** — module + mã, hành vi MVP, trạng thái `dự kiến`.
3. **DECISIONS** — chốt công nghệ và cấu trúc, mỗi lựa chọn một `Dxx`.
4. **Module + contract** — ranh giới, kiểu dữ liệu, API công khai.
5. **AGENTS + STATUS** — luật của dự án này, việc đầu tiên.
6. **Khung repo + máy chặn** — `pos.py`, hook, khóa main, CI.
7. **Kiểm toán** — bảng kiểm dưới đây (prompt P-15), bạn duyệt.

### Nội dung tối thiểu từng file

| File | Phải có | Đủ khi |
| --- | --- | --- |
| `BRIEF.md` | Người dùng (vai, số lượng) · Vấn đề · 2–3 chỉ số thành công có số · Không làm · Ràng buộc (thời hạn, thiết bị, ngôn ngữ, ngân sách) | Đọc 1 phút trả lời được: cho ai, để làm gì, khi nào là xong |
| `FEATURES.md` | Domain → module (mã) → feature MVP; mỗi dòng có hành vi chính viết theo người dùng, trạng thái `dự kiến` | Mỗi hành vi MVP có mã, viết được test; không feature nào nằm ngoài BRIEF |
| `DECISIONS.md` | Tối thiểu: ngôn ngữ + khung, CSDL + lưu trữ, nơi chạy, xác thực, cấu trúc module; câu hỏi `Q-` còn mở ghi người chờ | Mọi lựa chọn kỹ thuật có lý do; không `Q-` nào chặn MVP |
| `src/<module>/README.md` + `contract.*` | Chức năng, vào/ra, phụ thuộc; kiểu dữ liệu và chữ ký API công khai (chưa cần code thật) | Module chỉ gọi nhau qua contract; contract dữ liệu lõi đã viết |
| `AGENTS.md` | Đủ các mục theo mẫu phụ lục; vùng cấm và file nóng **thật** của dự án | AI phiên mới đọc xong làm được task mẫu mà không phải hỏi lại |
| `STATUS.md` | Đang giữ: trống · Tiếp theo: T-001 · Đang chặn: các `Q-` liên quan | Biết ngay việc đầu tiên là gì |
| `pos.py`, hook | `setup`, `check`, `task`, `done`; pre-push hook gọi `python pos.py check` | `python pos.py setup` + `python pos.py check` xanh trên máy sạch (0 test vẫn xanh) |
| GitHub | Khóa main, CI chạy `python pos.py check`, `CODEOWNERS` khi có vùng cấm | Thử push thẳng main bị chặn |
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

- [ ] AGENTS.md không còn ví dụ mẫu; vùng cấm và file nóng là của dự án này.
- [ ] Mỗi thông tin chỉ ở một nơi; file lõi không còn chữ "TODO" hay "ví dụ".
- [ ] AI phiên trắng chạy P-01 tóm tắt đúng dự án.

**Máy chặn**

- [ ] `python pos.py setup`, `python pos.py check` xanh trên máy sạch.
- [ ] Push thẳng main bị chặn; PR có chạy CI.
- [ ] Danh sách vùng cấm và file nóng khớp giữa AGENTS.md và `CODEOWNERS`.
- [ ] `.env` không vào Git; có `.env.example`.

Qua đủ bảng kiểm: bạn duyệt → ghi `Dxx` "Qua cổng Ngày 0" → giao **T-001**.

### Task đầu tiên: T-001 khung chạy được

Một luồng mỏng chạy thông từ giao diện → API → dữ liệu cho **một** feature MVP, kèm 1 test e2e, qua đủ luồng chung (task → … → merge → done). Từ T-002 mới làm tính năng thật.

## 4. Luật cứng

Tám luật duy nhất không linh hoạt. Luật nào máy chặn được thì máy chặn, không dựa vào việc AI có đọc hay không.

| # | Luật | Máy chặn bằng |
| --- | --- | --- |
| 1 | Không push thẳng lên main; chỉ gộp qua PR | Khóa nhánh main |
| 2 | Không đưa khoá bí mật vào Git, code, tài liệu | `.gitignore` có `.env`; quét khoá (gitleaks) |
| 3 | Chỉ push khi `python pos.py check` qua | pre-push hook; CI của PR là cổng cuối |
| 4 | Tiêu đề PR có mã: `<loại>(<mã>): <việc>` | CI kiểm tiêu đề PR |
| 5 | Mã không bao giờ dùng lại; mã trong code phải có trong sổ | Script kiểm sổ mã trong `python pos.py check` |
| 6 | Builder không tự sửa **contract đã khóa, file nóng, vùng cấm**. Cần sửa → dừng task, báo Orchestrator, xin duyệt | `CODEOWNERS` liệt kê đúng các đường dẫn này |
| 7 | PR chạm các đường dẫn ở luật 6 phải có **Human Approval** (bạn duyệt) | Khóa nhánh: bắt buộc Code Owner duyệt; CI kiểm approval trước khi gộp |
| 8 | Không sửa ngoài phạm vi thẻ; cần thì dừng và báo | pre-push hook chạy `python pos.py scope` (so file đã sửa với dòng `Phạm vi:` của thẻ trên main); Reviewer |

- Vùng cấm và file nóng ghi **một danh sách** trong AGENTS.md, chép đúng sang `CODEOWNERS` (phụ lục). Mặc định vùng cấm: đăng nhập, phân quyền, thanh toán, contract, migration, xoá dữ liệu.
- Xin duyệt = Orchestrator tạo task riêng cho phần cần sửa; bạn duyệt task trước, duyệt PR sau.
- Khẩn cấp (lỗi production): chỉ bạn được bỏ qua luật, ghi lý do vào DECISIONS.md, làm task bù sau.

## 5. Thư mục và file

Thư mục xếp **theo thứ tự đọc**: trên cùng là thứ AI đọc mỗi phiên, xuống dần tới thứ chỉ máy dùng. Mở repo đọc từ trên xuống là hiểu dự án.

```
<repo>/
│  ① ĐỌC MỖI PHIÊN — luật và chỗ dừng
├── AGENTS.md                 luật cứng, luồng, làn, lệnh, file nóng, vùng cấm
├── STATUS.md                 đang giữ · đang chặn · bàn giao
│
│  ② HIỂU — có gì, vì sao, làm khi nào
├── docs/
│   ├── PROCESS.md            bản đầy đủ của tài liệu này
│   ├── product/
│   │   ├── BRIEF.md          ai dùng, vấn đề, thành công
│   │   └── FEATURES.md       sổ mã: domain → module → feature → code → test
│   ├── DECISIONS.md          D01…, Q-…
│   ├── plan/                 (khi có nhiều mốc)
│   │   ├── ROADMAP.md        mốc M1, M2…
│   │   └── M3-ban-do.md      thẻ task của mốc đang làm
│   └── prompts/              P-01.md … P-15.md (mục 13)
│
│  ③ LÀM — code chia theo module
├── src/<module>/             Rust: crates/<module>/
│   ├── README.md             chức năng, vào/ra, phụ thuộc, mã
│   ├── contract.<đuôi>       kiểu dữ liệu + API công khai + Mock mẫu; khóa sau task contract
│   └── …
│
│  ④ KIỂM — test chia theo tầng rồi module
├── tests/
│   ├── unit/<module>/
│   ├── api/<module>/
│   └── e2e/<module>/
│
│  ⑤ MÁY CHẶN — công cụ và cổng tự động
├── pos.py                    runner Python: setup · run · test · lint · check · task · done · drop · wt · scope
├── Makefile                  lớp bọc tuỳ chọn gọi pos.py cho ai quen make
├── scripts/feature-lint.*    kiểm sổ mã, sinh cột Test
└── .github/
    ├── CODEOWNERS            cùng danh sách vùng cấm + file nóng với AGENTS.md
    ├── pull_request_template.md
    └── workflows/ci.yml

../wt/<mã>/                   worktree, ngoài repo; một thư mục cho mỗi task
```

- Thư mục nào chưa cần thì chưa tạo (ví dụ `docs/plan/` khi mới có một mốc).
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
| Kế hoạch (khi có plan) | Mốc · Task | `M3` · `T-042` | ROADMAP.md · plan của mốc |
| Cách làm | Prompt | P-04 | docs/prompts/ (mục 13) |

- Cấp một lần, không dùng lại. Bỏ tính năng: giữ dòng, trạng thái `bỏ (Dxx)`.
- Task ghi feature nó làm (`T-042 · MAP-07`); số task tăng liên tục, chỉ Orchestrator cấp.
- Dùng GitHub Issues/Linear (tuỳ chọn): cho số T trùng số Issue (`T-043` = Issue `#43`) và ghi `Closes #43` ở **thân** PR (tiêu đề giữ đúng mẫu luật 4). Squash merge thì Issue tự đóng, bảng Kanban tự cập nhật; không dùng thì bỏ qua.

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
- **Test liên quan:** script kiểm sổ tự sinh từ tag trong test (đường dẫn + số test), không ghi tay. Chưa có test tự động thì ghi `— (lý do)`.
- **Trạng thái:** `dự kiến` (chưa làm, đã có hành vi) · `dùng` · `bỏ (Dxx)`. Mã bỏ giữ dòng, không còn trong code.

**Mẫu `docs/DECISIONS.md`:**

```
| Mã  | Ngày       | Quyết định                              | Lý do                     | Mã liên quan    | Duyệt |
| --- | ---------- | --------------------------------------- | ------------------------- | --------------- | ----- |
| D59 | 2026-11-08 | Bản đồ tải một lần, tối đa 5.000 điểm   | Đủ nhanh, đơn giản        | MAP-01…MAP-08   | Bạn   |
| D60 | 2026-11-09 | Gom cụm tính lại khi dừng kéo bản đồ    | Máy yếu không bị giật     | MAP-02          | AI    |

## Còn mở
| Mã    | Câu hỏi                          | Chờ ai      |
| ----- | -------------------------------- | ----------- |
| Q-map | Nguồn ô bản đồ trước khi mở rộng | Chủ dự án   |
```

## 7. Kế hoạch và bàn giao

| File | Trả lời | Nguồn duy nhất của | Ai ghi |
| --- | --- | --- | --- |
| ROADMAP.md | Làm gì, thứ tự nào | Mốc + trạng thái mốc | Orchestrator đề xuất, bạn duyệt |
| Plan `M3-*.md` | Mốc này làm thế nào | Thẻ task + ô tick | Orchestrator |
| STATUS.md | Phiên trước dừng ở đâu | Ai giữ task nào, đang chặn gì, ghi chú bàn giao | Orchestrator (một AI: chính nó) |

Dự án nhỏ chỉ cần STATUS.md, thêm mục "Tiếp theo". "Vừa xong" không ghi ở đâu: đã có trong Git. Mốc nghiệm thu thì xoá plan (lịch sử ở Git).

```
# STATUS · 2026-11-09 · M3
## Đang giữ      T-043 · Builder A · feat/T-043-map-sales
## Đang chặn     Q-map: nguồn ô bản đồ (chờ chủ dự án)
## Bàn giao      Thẻ điểm bán xong; còn offline. Chạy python pos.py test F=MAP-02 trước.
```

**Mẫu `docs/plan/ROADMAP.md`** (khi có nhiều mốc):

```
| Mốc | Mục tiêu            | Feature        | Plan              | Trạng thái              |
| --- | ------------------- | -------------- | ----------------- | ----------------------- |
| M2  | Báo đơn và nhận đơn | ORD-01…ORD-09  | —                 | xong 2026-10-20 · v0.4  |
| M3  | Bản đồ điểm bán     | MAP-01…MAP-08  | plan/M3-ban-do.md | đang làm                |
| M4  | Báo cáo theo vùng   | RPT-09…        | —                 | chưa bắt đầu            |
```

## 8. Làm một task

**1 Task = 1 Branch = 1 Worktree = 1 PR.** Cả bốn mang cùng mã, sinh ra cùng lúc, dọn cùng lúc.

| Khái niệm | Là gì | Tên theo mẫu |
| --- | --- | --- |
| Task | Đơn vị công việc | `T-043` (làn nhanh: mã feature `MAP-02`) |
| Branch | Dòng phát triển code | `feat/T-043-map-sales` |
| Worktree | Thư mục làm việc độc lập | `../wt/T-043` |
| Commit | Điểm lưu thay đổi; nhiều commit trong một task | Tự do ở local |
| PR | Yêu cầu đưa code vào main | `feat(MAP-02): … [T-043]` |

### Vòng đời worktree

| Bước | Lệnh | Ai, khi nào |
| --- | --- | --- |
| Tạo | `python pos.py task T=T-043 N=map-sales` = `git fetch` + `git worktree add ../wt/T-043 -b feat/T-043-map-sales origin/main` | Builder, khi nhận thẻ |
| Làm | Chỉ sửa trong `../wt/T-043`, không đụng worktree khác | Builder |
| Cập nhật | `git fetch && git rebase origin/main` | Builder, trước khi push |
| Dọn | `python pos.py done T=T-043` = `git worktree remove` + xoá nhánh đã gộp + `git worktree prune` | Orchestrator, ngay sau khi gộp |
| Huỷ | `python pos.py drop T=T-043` (xoá nhánh chưa gộp) | Orchestrator, **hỏi bạn trước** |

- Worktree đặt ngoài repo (`../wt/`), không lồng trong repo.

  Lệnh nằm ở `pos.py` (cần Python 3, không cần make hay bash; Linux/macOS có thể phải gõ `python3`); `python pos.py wt` liệt kê worktree đang có. `python pos.py done` nhận ra PR đã gộp kiểu squash qua lệnh `gh`; máy không có `gh` thì chỉ nhận ra nhánh đã gộp thường.
- Cuối phiên, Orchestrator chạy `python pos.py wt-clean`: liệt kê worktree mồ côi (nhánh đã gộp vào main, hoặc PR đã MERGED qua `gh`; bỏ qua cái còn thay đổi chưa commit). Đúng danh sách thì `python pos.py wt-clean APPLY=1` để dọn. Worktree chưa gộp mà không có trong "Đang giữ" của STATUS thì báo, không tự xoá (huỷ phải qua `drop`).
- Mở PR: `python pos.py pr` in sẵn khung báo cáo từ `git diff --stat`, commit, mã feature và kết quả `check`; Builder chỉ điền các ô còn trống.

### Luồng chung (mọi làn)

```
task → code → commit → check → rebase → push → PR → CI → [approve nếu vùng cấm] → merge → done
```

### Chọn làn theo rủi ro

AI tự chọn làn và ghi làn vào mô tả PR. Phân vân thì chọn làn cao hơn. Đang làm mà phát hiện chạm vùng cấm, contract hay file nóng thì **nâng làn**: dừng, báo Orchestrator, xin duyệt.

| Làn | Khi nào | Được bỏ | Bắt buộc thêm |
| --- | --- | --- | --- |
| **Nhanh** | Câu chữ, tài liệu, lỗi nhỏ rõ nguyên nhân; không chạm vùng cấm, contract, file nóng | Thẻ task, số T, plan, Reviewer | — (task mang mã feature: `python pos.py task T=MAP-02 N=typo TYPE=fix`) |
| **Thường** | Tính năng hoặc sửa lỗi có logic; 1 Builder | Reviewer, hàng chờ gộp | Thẻ task, test cho hành vi mới |
| **Kiểm soát** | Chạm vùng cấm, contract, file nóng; hoặc nhiều Builder chạy song song | — | Task riêng được bạn duyệt trước; bạn approve PR; song song: worktree riêng + PR phải cập nhật theo main trước khi gộp |

### Các bước

1. **Nạp ngữ cảnh:** AGENTS.md → STATUS.md → thẻ task (nếu có) → dòng mã → `rg "<mã>"`.
2. **`python pos.py task`:** worktree + nhánh từ main mới nhất.
3. **Code + commit:** dò phạm vi trước; commit ở local thoải mái.
4. **`python pos.py check`:** lỗi → sửa → check lại.
5. **Rebase + push + PR:** `git rebase origin/main`, pre-push hook chạy lại check, mở PR theo mẫu (ghi làn).
6. **CI của PR:** lỗi → sửa ở local → push lại. Làn Kiểm soát: chờ bạn approve.
7. **Merge + done:** squash vào main → `python pos.py done` → tick task, cập nhật STATUS.

```
MÁY LOCAL (mỗi Builder một worktree)            GITHUB
python pos.py task ──► code + commit ──► python pos.py check ─┐
                  ▲                lỗi      │ qua
                  └─────────────────────────┤
                                            ▼
                       rebase origin/main ──► pre-push hook ──► push
                                                                 │
     Mở PR (mẫu thẻ, ghi làn) ◄──────────────────────────────────┘
        │
        ▼
     CI của PR ── lỗi ──► sửa ở local, push lại
        │ qua
        ▼
     Vùng cấm? ── có ──► chờ bạn approve
        │ không
        ▼
     Merge (squash, PR mới theo main) ──► python pos.py done · tick task · STATUS
```

Bên trái là việc của Builder trên máy mình; chỉ khi kiểm local qua mới sang GitHub, nơi CI của PR là cổng không tắt được.

**Thẻ task (cũng là prompt giao việc):**

```
- [ ] T-043 · MAP-02 · web Sales
      Mục tiêu:  Sales mở bản đồ điểm bán từ Bảng tin
      Sóng:      W1                       Đọc (RO):  src/*/contract.*
      Phạm vi:   src/map/web/*            Phụ thuộc: T-042 (Sóng trước, contract đã khóa)
      Cần:       MapPoint, list_points()  (chỉ cần với Sóng 1: kiểu/hàm của contract mà task dùng)
      Vùng cấm:  không                    Giao: Builder A · feat/T-043-map-sales
      Xong khi:  python pos.py test F=MAP-02 qua; thử tay trên điện thoại
```

`python pos.py scope` đọc dòng `Phạm vi:` của thẻ từ `docs/plan/*.md` trên `origin/main` (không đọc từ nhánh đang làm), nên Builder không tự mở rộng phạm vi. Ghi phạm vi bằng mẫu đường dẫn cách nhau bởi dấu phẩy hoặc khoảng trắng, **gồm cả thư mục test**: `Phạm vi: src/map/web/*, tests/map/*`. `Phạm vi` chính là quyền ghi (RW); `Đọc (RO)` chỉ để Builder biết được tham chiếu gì, không được sửa. Pre-push chặn khi đẩy; CI nên chạy thêm `python pos.py scope` để `--no-verify` không lách được. Làn Nhanh và nhánh không có số T thì bỏ qua. Cần mở rộng: Builder dừng và báo, Orchestrator sửa thẻ trên main, Builder rebase rồi push lại.

**Báo cáo khi xong:**

```
Đã làm · Phạm vi thực tế (khớp thẻ / thêm gì, vì sao) · File thay đổi
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

**Commit:** ở local tự do, thường xuyên. Khi gộp, PR được ép thành một commit (squash); **tiêu đề PR** là commit chính thức:

```
feat(MAP-07): add GET /stores/map with team/company scope [T-042]

Why: D59 · Test: python pos.py test F=MAP-07 (api 5 pass)
```

Loại: `feat` · `fix` · `refactor` · `test` · `docs` · `chore` (chore không cần mã).

## 11. Nhiều agent song song

Chỉ dùng khi có từ 2 task không trùng file. Chỉ có một AI thì nó đóng lần lượt cả ba vai.

| Vai | Nhìn gì | Làm gì | Không làm |
| --- | --- | --- | --- |
| Orchestrator | ROADMAP, plan, STATUS, FEATURES, DECISIONS | Viết thẻ, kiểm trùng phạm vi, cấp số T, chạy hàng chờ gộp, cập nhật plan + STATUS | Viết code tính năng |
| Builder | Thẻ của mình, README module, contract, `rg "<mã>"` | Luồng chung (mục 8) trên worktree riêng | Sửa ngoài thẻ, contract đã khóa, file nóng |
| Reviewer | Diff của PR + "Xong khi" | Chỉ PR chạm vùng cấm: kiểm, đề xuất bản sửa, rồi chuyển bạn approve | Kiểm PR thường (CI đã lo), tự gộp |

### Plan theo Sóng (đồ thị không chu trình)

Plan nhiều agent chia theo **Sóng**, mỗi thẻ ghi `Sóng: W<n>`. Task chỉ phụ thuộc task ở Sóng **trước**, không bao giờ cùng Sóng hoặc sau.

```
W0 Nền        1 agent    Task contract: kiểu dữ liệu + Mock; khóa rồi mới sang W1
 │
W1 Song song  2–5 agent  Mỗi task một worktree, một thư mục (RW) riêng; chỉ ĐỌC contract (RO)
 │                       PR vào hàng chờ gộp lần lượt (rebase + CI)
W2 Nối dây    1 agent    Nối module vào ứng dụng chính, file nóng, E2E tổng
```

- **Đất của ai người đó xây:** Sóng nào cũng phải có `Phạm vi` (RW) đôi một rời nhau. `python pos.py plan-check` chặn: trùng RW cùng Sóng, Phụ thuộc trỏ ngang hoặc ngược Sóng, W1 ghi vào file nóng, Sóng quá 5 task. Chạy trước khi bạn duyệt plan.
- **Sửa chéo thì sang Sóng sau:** Builder A cần sửa code của Builder B → dừng, Orchestrator mở task riêng ở Sóng sau. Không sửa chéo trong cùng Sóng.
- **Đừng ép song song:** Sóng 1 chỉ có 1 task thì cứ chạy tuần tự. Thêm agent là thêm gánh review và gánh duyệt của bạn; mặc định 3, tối đa 5.
- **Không "không bao giờ xung đột":** plan-check loại xung đột file do chia việc. Còn lại (lockfile, tài liệu dùng chung, sổ FEATURES) do hàng chờ gộp bắt bằng rebase + CI; file dùng chung kiểu này chỉ Orchestrator hoặc task W2 được ghi.

### File nóng: đăng ký động thay vì sửa tay

File nóng (route, registry, schema) là nguồn xung đột số một. Thiết kế để module **tự đăng ký**, file gốc không phải sửa khi thêm tính năng:

| Cách | Khi nào |
| --- | --- |
| Module xuất `register(app)`; file gốc quét thư mục và gọi (Python `pkgutil`, Node `glob` import) | Ngôn ngữ nạp động được |
| Mỗi module một file khai báo (`routes/<module>.ts`); file gốc chỉ là thư mục | Khung web có route theo file |
| Tạo mã tự động (`build.rs`, `inventory`, `go generate`) | Rust, Go: không quét lúc chạy được |
| Vẫn phải sửa tay một dòng | Dòng đó thuộc task W2, không thuộc W1 |

Chọn một cách ở Ngày 0 (ghi `Dxx`), file gốc chuyển ra khỏi danh sách File nóng khi đã tự nạp. Đánh đổi: nạp tự động khó truy dấu hơn, nên mỗi module ghi vào README tên đăng ký của mình. Manifest phụ thuộc (`package.json`, `Cargo.toml`, lockfile) cũng là file nóng: khai báo ở W0 hoặc W2, hoặc mỗi module một manifest riêng.

```
                 Bạn duyệt plan mốc
                         │
                   Orchestrator  (chia thẻ, kiểm trùng file)
                         │
                   Task contract (làm trước, chốt rồi khóa)
          ┌──────────────┼──────────────┐      chạy đồng thời, khác file
     Builder A        Builder B       Builder C
     T-043            T-044           T-045
     kiểm local       kiểm local      kiểm local → push PR
          └──────────────┼──────────────┘
                  Hàng chờ gộp (lần lượt: rebase + CI của PR)
                         │
                    Vùng cấm? ── có ──► Reviewer (≤ 2 vòng) ──► quá 2 vòng: bạn quyết
                         │ không / đạt
                   Gộp + STATUS (Orchestrator tick task)
```

Song song chỉ nằm giữa hai điểm tuần tự: **task contract khóa trước**, **hàng chờ gộp từng PR sau** (rebase theo main, CI lại).

**Mock đi kèm contract:** task contract viết luôn dữ liệu mẫu (stub/fixture) ngay dưới kiểu dữ liệu, ví dụ `MOCK_USER` trong `src/auth/contract.py`. Builder cần module chưa xong thì import mock này để viết test và chạy thử, không chờ Builder kia, không cần DB thật. Module thật xong thì test đổi sang bản thật và **bắt buộc** giữ một test hợp đồng so mock với bản thật ở mọi module Sóng 1 (chống hardcode theo mock).

**Cổng khóa contract (cuối W0):** mỗi thẻ Sóng 1 ghi `Cần:` (kiểu và hàm của contract mà nó dùng). Orchestrator đối chiếu từng mục với contract và Mock; thiếu mục nào thì bổ sung vào task contract **trước khi khóa**. Hở contract hầu hết là lỗi lập plan, chặn ở đây rẻ hơn nhiều so với vá giữa chừng.

### Hở contract giữa chừng

Task đang làm phát hiện contract hoặc task trước thiếu sót (luật cứng 6 và 8 áp dụng, không sửa lén, không hardcode):

1. **Dừng và lưu:** commit WIP lên nhánh của task, không sửa module khác.
2. **Báo:** ghi `Đang chặn` trong STATUS; Orchestrator dùng P-10, tra `rg` theo mã để liệt kê **mọi task dùng phần contract đó**; các task ấy tạm dừng, không chỉ task bị kẹt.
3. **Task vá:** một task riêng làn Kiểm soát, chờ bạn duyệt. Orchestrator sửa `Phụ thuộc` của các thẻ bị ảnh hưởng (trỏ về task vá) và chạy lại `python pos.py plan-check`.
4. **Sau khi vá gộp:** Builder bị kẹt rebase **rồi chạy lại test hợp đồng và `check`**. Rebase chỉ giữ code, không đảm bảo code đúng với contract mới; phần dựa trên contract hoặc Mock cũ phải sửa.
5. **Không ngồi chờ:** Builder bị kẹt nhận task khác ở cùng Sóng hoặc dừng phiên (P-09).

- Chỉ Orchestrator ghi plan, STATUS và cấp số task; Builder ghi bàn giao trong báo cáo.
- Bạn duyệt: plan mốc, mọi PR chạm vùng cấm (Human Approval), khi Reviewer quá 2 vòng chưa đạt, và quyết định lớn (mục 12).
- Không gắn công cụ: Claude, Codex, Gemini, Cursor… đóng vai nào cũng được, vì cùng đọc AGENTS.md, plan và STATUS.

## 12. Mặc định: AI được linh hoạt

Đây là điểm xuất phát, không phải luật. AI được làm khác khi hợp lý hơn, miễn không chạm luật cứng, và ghi một dòng lý do ở mục "Khác mặc định" trong báo cáo.

| Việc | Mặc định | Nên làm khác khi |
| --- | --- | --- |
| Chọn làn | Theo bảng làn ở mục 8 | Phân vân, hoặc sửa nhỏ nhưng rủi ro → làn cao hơn |
| Cỡ task | Vừa một phiên | Việc liền mạch khó tách → task lớn hơn, chia bước trong plan |
| Số Builder song song | Bằng số task không trùng file, tối đa 3 | Nhiều file nóng → chạy tuần tự |
| Test cần viết | Tầng theo bảng mục 10 | Sửa câu chữ, tài liệu → không cần test mới |
| Độ dài tài liệu | AGENTS \~150 dòng, STATUS \~20, README \~10 | Cần thêm → dẫn link sang file khác, không phình |
| Tách file code | Đề xuất khi file > \~300 dòng | File sinh tự động, bảng dữ liệu → không tách |
| Mô tả đầu file | Có ở file ranh giới | File nhỏ, tên đã rõ → bỏ qua |
| Số vòng Reviewer | Tối đa 2, sau đó bạn quyết | Lỗi rõ ràng, sửa nhanh → thêm 1 vòng |
| Mức chi tiết plan | Thẻ task + rủi ro chính | Mốc nhỏ → chỉ danh sách thẻ |
| Ghi quyết định | AI tự ghi `Dxx` cho quyết định nhỏ, đánh dấu "(AI)" | Contract, thư viện mới, cấu trúc thư mục, vùng cấm → chờ bạn duyệt |
| Kế hoạch | Chỉ STATUS.md, mã feature + Dxx | Nhiều mốc hoặc nhiều agent → thêm ROADMAP, plan mốc, mã M và T |
| Kiểm | python pos.py check + pre-push hook, gộp trên máy | Có remote: CI của PR. Từ 2 Builder: worktree riêng + bật "Require branches to be up to date". Từ 3 agent hoặc nhiều người: merge queue |

## 13. Bảng prompt

Mỗi bước của luồng có một prompt mẫu, mã `P-nn`. Bản đầy đủ đặt ở `docs/prompts/P-nn.md`; gọi nhanh bằng mã, ví dụ "Chạy P-04 với thẻ T-043". Phần trong `<…>` là chỗ điền.

| Mã | Khi dùng | Vai | Prompt | Đầu ra |
| --- | --- | --- | --- | --- |
| P-01 | Mở phiên | Mọi vai | Đọc AGENTS.md và STATUS.md. Tóm tắt trong 5 dòng: mốc nào, ai giữ task nào, đang chặn gì, việc tiếp theo. Chưa sửa gì. | 5 dòng tóm tắt |
| P-02 | Khởi tạo dự án | Orchestrator | Từ BRIEF sau: `<brief>`. Làm Ngày 0 theo mục 3, từng bước: BRIEF → FEATURES → DECISIONS → module + contract → AGENTS + STATUS → khung repo. Trình đầu ra mỗi bước, chờ tôi duyệt rồi mới sang bước sau. | Bộ file Ngày 0 |
| P-03 | Lập plan mốc | Orchestrator | Lập plan cho mốc `<M3>`: `<mục tiêu>`. Đọc ROADMAP, FEATURES, DECISIONS. Viết thẻ task theo mẫu, task contract đi đầu, ghi làn từng task, kiểm hai task song song không trùng file. Chờ tôi duyệt. | `docs/plan/M3-*.md` |
| P-03-MULTI | Lập plan nhiều agent | Orchestrator | Lập plan cho mốc `<M3>` theo đồ thị không chu trình. Đọc BRIEF, FEATURES, ROADMAP, DECISIONS. Chia W0 (task contract + Mock) → W1 (2–5 task song song) → W2 (nối dây + E2E). Mỗi thẻ ghi Sóng, Phạm vi (RW), Đọc (RO), Phụ thuộc chỉ trỏ Sóng trước. Cách đăng ký module để không sửa file nóng. Chạy `python pos.py plan-check` đến khi qua, dán kết quả. Chờ tôi duyệt. | `docs/plan/M3-*.md` + kết quả plan-check |
| P-04 | Giao task | Orchestrator → Builder | Làm task sau theo luồng chung: `<thẻ task>`. Dừng và báo nếu phạm vi khác thẻ, hoặc phải chạm contract, file nóng, vùng cấm. Trước khi mở PR tự hỏi: (1) file ranh giới mới đã có 3 dòng đầu file gắn mã chưa? (2) test mới đã gắn mã feature chưa? (3) `python pos.py check` đã in "qua" chưa? Xong thì báo cáo theo mẫu. | PR + báo cáo |
| P-05 | Sửa nhanh | Builder (solo) | Làn Nhanh, mã `<MAP-02>`: `<việc cần sửa>`. `python pos.py task T=<mã> N=<tên> TYPE=fix` → sửa → `python pos.py check` → PR. | PR nhỏ |
| P-06 | Sửa lỗi | Builder | Lỗi: `<hiện tượng, log>`. Mã liên quan: `<MAP-07>`. Viết test tái hiện lỗi trước, rồi sửa. Làn Thường. | Test đỏ → xanh, PR |
| P-07 | Review vùng cấm | Reviewer | Review PR `<#n>` (làn Kiểm soát). Đối chiếu "Xong khi", phạm vi thẻ, luật cứng 6–8. Kết luận Đạt hoặc Trả lại kèm bản sửa đề xuất. Không gộp. | Kết luận + lý do |
| P-08 | Gộp và dọn | Orchestrator | PR `<#n>` đã qua CI (và đã approve nếu Kiểm soát). Gộp squash, `python pos.py done T=<mã>`, tick task trong plan, cập nhật STATUS. | main mới, STATUS mới |
| P-09 | Cuối phiên | Orchestrator | Kết thúc phiên. Cập nhật STATUS (đang giữ, đang chặn, bàn giao ≤ 3 dòng). Chạy `python pos.py wt-clean` (dọn mồ côi đã gộp bằng `APPLY=1`), báo worktree thừa chưa gộp. | STATUS mới |
| P-10 | Nâng làn / đổi contract | Orchestrator | Task `<T-043>` cần sửa `<file>` vì `<lý do>`. Liệt kê ảnh hưởng (`rg` theo mã), tạo task riêng làn Kiểm soát. Chờ tôi duyệt. | Task mới + ảnh hưởng |
| P-11 | Ghi quyết định | Mọi vai | Ghi quyết định: `<nội dung>`, lý do `<…>`. Cấp mã D tiếp theo, điền bảng DECISIONS, cột Duyệt = `<Bạn/AI>`, ghi mã liên quan. | Dòng Dxx mới |
| P-12 | Rà tài liệu | Orchestrator | Rà AGENTS.md, STATUS, FEATURES, DECISIONS: thông tin trùng, lỗi thời, mã thiếu test, worktree thừa. Liệt kê, chưa sửa. | Danh sách cần dọn |
| P-13 | Nghiệm thu mốc | Orchestrator | Mốc `<M3>` đã nghiệm thu, phiên bản `<v0.5>`. Đánh dấu xong trong ROADMAP, xoá plan mốc, dọn STATUS, liệt kê câu hỏi Q- còn mở. | ROADMAP mới |
| P-14 | Khẩn cấp | Builder | Lỗi production: `<hiện tượng>`. Sửa nhanh nhất; tôi cho phép bỏ qua `<luật>`. Ghi lý do vào DECISIONS, tạo task bù. | Hotfix + Dxx + task bù |
| P-15 | Kiểm toán Ngày 0 | Orchestrator (phiên mới) | Kiểm toán repo theo bảng kiểm mục 3. Với từng ô: Đạt hoặc Chưa, kèm bằng chứng (file, dòng). Không sửa gì. Cuối cùng kết luận: qua cổng hay chưa, còn thiếu gì. | Bảng Đạt/Chưa + kết luận |

- Thứ tự dùng trong một mốc: P-01 → P-03 (một agent) hoặc P-03-MULTI (nhiều agent) → (P-04 hoặc P-05, P-06) → P-07 khi cần → P-08 → P-09. Hết mốc: P-13. Dự án mới: P-02 → P-15 → bạn duyệt → T-001.
- Prompt cũng là mã: không dùng lại số, sửa nội dung thì sửa trong `docs/prompts/`.

## Phụ lục · Mẫu

**AGENTS.md**

```
# AGENTS.md
## Mục tiêu        1–2 câu, dẫn docs/product/BRIEF.md
## Đọc khi mở      AGENTS.md → STATUS.md → thẻ task → dòng mã → rg "<mã>"
## Lệnh            python pos.py setup · run · test [F=<mã>] [L=<tầng>] · lint · check · task · done
## Luồng           task → code → commit → check → rebase → push → PR → CI → [approve nếu vùng cấm] → merge → done
## Làn            Nhanh · Thường · Kiểm soát (PROCESS.md mục 8); phân vân thì chọn làn cao hơn
## Luật cứng       8 luật (PROCESS.md mục 4)
## File nóng       src/app/routes.*, db/schema.*, src/copy.*, .github/**
## Vùng cấm        auth, phân quyền, thanh toán, contract, migration, xoá dữ liệu
## Báo cáo         Đã làm · Phạm vi thực tế · File · Test · Khác mặc định · Rủi ro · Bàn giao
```

**Kiểm tiêu đề PR (regex cho CI)**

```
^(feat|fix|refactor|test|docs)\([A-Z]+-\d{2,}(,[A-Z]+-\d{2,})*\): .+( \[T-\d{3,}\])?$
^chore: .+$
```

**CODEOWNERS**

```
# Vùng cấm + contract + file nóng → bắt buộc bạn duyệt (cùng danh sách với AGENTS.md)
/src/auth/           @chu-du-an
/src/payment/        @chu-du-an
/db/migrations/      @chu-du-an
**/contract.*        @chu-du-an
/src/app/routes.*    @chu-du-an
/.github/            @chu-du-an
```

Bật trên GitHub: khóa nhánh main → **Require review from Code Owners**. Khi dùng merge queue, thêm job CI `approval-check`: `gh pr view --json reviewDecision` phải là `APPROVED` thì mới gộp.

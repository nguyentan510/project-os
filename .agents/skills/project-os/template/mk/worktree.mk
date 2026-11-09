# worktree.mk · 1 Task = 1 Branch = 1 Worktree = 1 PR (PROCESS.md mục 6)
# Dùng: thêm dòng `include mk/worktree.mk` vào Makefile của dự án.
#
#   make task T=T-043 N=map-sales [TYPE=fix]   tạo worktree + nhánh từ main mới nhất
#   make done T=T-043                          dọn sau khi PR đã gộp
#   make drop T=T-043 [CONFIRM=T-043]          huỷ task chưa gộp (phải hỏi chủ dự án)
#   make wt                                    liệt kê worktree đang có

WT_DIR ?= ../wt
BASE   ?= main
TYPE   ?= feat
TYPES  := feat fix refactor test docs chore

.PHONY: task done drop wt _need-t

_need-t:
	@test -n "$(T)" || { echo "Thiếu T=<mã task>, ví dụ T=T-043 (làn nhanh: T=MAP-02)"; exit 1; }
	@echo "$(T)" | grep -Eq '^(T-[0-9]{3,}|[A-Z]+-[0-9]{2,})$$' || { echo "T sai dạng: '$(T)'. Đúng: T-043 hoặc MAP-02"; exit 1; }

task: _need-t
	@test -n "$(N)" || { echo "Thiếu N=<tên-ngắn>, ví dụ N=map-sales"; exit 1; }
	@echo "$(N)" | grep -Eq '^[a-z0-9]+(-[a-z0-9]+)*$$' || { echo "N chỉ gồm chữ thường, số, gạch ngang: '$(N)'"; exit 1; }
	@echo " $(TYPES) " | grep -q " $(TYPE) " || { echo "TYPE phải là một trong: $(TYPES)"; exit 1; }
	@test ! -e "$(WT_DIR)/$(T)" || { echo "Đã có worktree $(WT_DIR)/$(T). Xem: make wt"; exit 1; }
	@BR="$(TYPE)/$(T)-$(N)"; \
	 if git show-ref --verify --quiet "refs/heads/$$BR"; then echo "Nhánh $$BR đã có"; exit 1; fi; \
	 git fetch --quiet origin $(BASE) && \
	 git worktree add --quiet "$(WT_DIR)/$(T)" -b "$$BR" origin/$(BASE) && \
	 git -C "$(WT_DIR)/$(T)" branch --quiet --unset-upstream 2>/dev/null; \
	 echo "Đã tạo: $(WT_DIR)/$(T)  ·  nhánh $$BR  ·  từ origin/$(BASE)"; \
	 echo "Tiếp: cd $(WT_DIR)/$(T)"

done: _need-t
	@test -d "$(WT_DIR)/$(T)" || { echo "Không có worktree $(WT_DIR)/$(T). Xem: make wt"; exit 1; }
	@BR=$$(git -C "$(WT_DIR)/$(T)" rev-parse --abbrev-ref HEAD); \
	 git fetch --quiet origin $(BASE); \
	 if command -v gh >/dev/null 2>&1 && [ "$$(gh pr view "$$BR" --json state -q .state 2>/dev/null)" = "MERGED" ]; then \
	   how="PR đã gộp (gh)"; \
	 elif git merge-base --is-ancestor "$$BR" origin/$(BASE); then \
	   how="nhánh đã nằm trong origin/$(BASE)"; \
	 else \
	   echo "Nhánh $$BR chưa gộp vào $(BASE). Gộp PR trước, hoặc huỷ: make drop T=$(T)"; \
	   echo "(Gộp kiểu squash cần lệnh gh để nhận ra PR đã gộp.)"; exit 1; \
	 fi; \
	 git worktree remove "$(WT_DIR)/$(T)" || { echo "Worktree còn thay đổi chưa commit, không dọn."; exit 1; }; \
	 git branch --quiet -D "$$BR" && git worktree prune && \
	 echo "Đã dọn $(T): xoá worktree + nhánh $$BR ($$how)"

drop: _need-t
	@test -d "$(WT_DIR)/$(T)" || { echo "Không có worktree $(WT_DIR)/$(T). Xem: make wt"; exit 1; }
	@BR=$$(git -C "$(WT_DIR)/$(T)" rev-parse --abbrev-ref HEAD); \
	 if [ "$(CONFIRM)" != "$(T)" ]; then \
	   echo "Huỷ $(T) sẽ MẤT VĨNH VIỄN:"; \
	   echo "  Commit chưa gộp trên $$BR:"; \
	   git log --oneline origin/$(BASE).."$$BR" | sed 's/^/    /'; \
	   echo "  Thay đổi chưa commit:"; \
	   git -C "$(WT_DIR)/$(T)" status --short | sed 's/^/    /'; \
	   echo "Chủ dự án đồng ý thì chạy lại: make drop T=$(T) CONFIRM=$(T)"; exit 1; \
	 fi; \
	 git worktree remove --force "$(WT_DIR)/$(T)" && git branch --quiet -D "$$BR" && git worktree prune && \
	 echo "Đã huỷ $(T): xoá worktree + nhánh $$BR"

wt:
	@git worktree list

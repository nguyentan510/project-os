# Lệnh chuẩn (PROCESS.md mục 10). Đặt lệnh thật của dự án vào các biến *_CMD bên dưới.
# F = mã cần test (MAP-07 hoặc MAP), L = tầng (unit | api | e2e). Cả hai được truyền sang TEST_CMD.
# Ví dụ:
#   Python:     TEST_CMD = pytest $(if $(L),tests/$(L)) $(if $(F),-k "$(F)")
#   Rust:       TEST_CMD = cargo test $(if $(F),$(shell echo $(F) | tr 'A-Z-' 'a-z_'))
#   TypeScript: TEST_CMD = npx vitest run $(if $(F),-t "$(F)")

SETUP_CMD ?= @echo "setup: chưa cấu hình SETUP_CMD"
RUN_CMD   ?= @echo "run: chưa cấu hình RUN_CMD"
LINT_CMD  ?= @echo "lint: chưa cấu hình LINT_CMD"
TEST_CMD  ?= @echo "test: chưa cấu hình TEST_CMD (0 test)"

include mk/worktree.mk

.PHONY: setup run test lint features check

setup:
	@git rev-parse --git-dir >/dev/null 2>&1 && git config core.hooksPath .githooks && echo "Đã bật hook trong .githooks" || echo "Chưa phải repo git: chạy git init rồi make setup lại"
	$(SETUP_CMD)

run:
	$(RUN_CMD)

test:
	$(TEST_CMD)

lint:
	$(LINT_CMD)

features:
	@python3 scripts/feature-lint.py

check: features lint test
	@echo "make check: qua"

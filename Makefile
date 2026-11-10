# Lớp bọc tuỳ chọn cho ai quen gõ make. Logic và cấu hình lệnh thật nằm ở pos.py (chạy được cả trên Windows).
# Không có make cũng không sao: dùng thẳng `python pos.py <lệnh>`.
PY ?= python3
POS = $(PY) pos.py

.PHONY: setup run test lint features check task done drop wt scope plan-check wt-clean pr sos

setup run lint features check wt scope plan-check wt-clean sos:
	@$(POS) $@

test:
	@$(POS) test F=$(F) L=$(L)

task:
	@$(POS) task T=$(T) N=$(N) TYPE=$(TYPE)

done:
	@$(POS) done T=$(T)

drop:
	@$(POS) drop T=$(T) CONFIRM=$(CONFIRM)

pr:
	@$(POS) pr T=$(T)

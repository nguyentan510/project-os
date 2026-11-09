#!/usr/bin/env bash
# Kiểm toán Ngày 0 phần máy kiểm được (PROCESS.md mục 3). Không sửa gì.
#   bash audit.sh [thư-mục-dự-án]
# Phần cần người hoặc AI phiên mới đánh giá: chạy prompt docs/prompts/P-15.md.
set -uo pipefail

cd "${1:-.}" || exit 2
pass=0; fail=0
ok()  { echo "  Đạt   $1"; pass=$((pass + 1)); }
no()  { echo "  Chưa  $1"; fail=$((fail + 1)); }
# chk <mô tả> <lệnh> [đối số…]: chạy trực tiếp, không qua eval. Điều kiện phức tạp viết thành hàm ở dưới.
chk() { local d="$1"; shift; if "$@" >/dev/null 2>&1; then ok "$d"; else no "$d"; fi; }
has_file()      { test -f "$1"; }
no_placeholder(){ ! grep -l '{{' "$@"; }
no_todo()       { ! grep -lw 'TODO' "$@"; }
brief_has_skip(){ awk '/^## Không làm/{f=1;next} /^## /{f=0} f && /^- ./ && !/\{\{/{found=1} END{exit !found}' docs/product/BRIEF.md; }
has_feature()   { grep -Eq '^\| [A-Z]{2,6}-[0-9]{2,} \|' docs/product/FEATURES.md; }
enough_decisions() { test "$(grep -E '^\| D[0-9]{2,} \|' docs/DECISIONS.md | grep -vc '{{')" -ge 5; }
has_readme()    { test -f "src/$1/README.md" || test -f "crates/$1/README.md"; }
has_contract()  { compgen -G "src/$1/contract.*" || compgen -G "crates/$1/src/contract.*" || compgen -G "crates/$1/contract.*"; }
claude_ok()     { test "$(tr -d '[:space:]' < CLAUDE.md)" = '@AGENTS.md'; }
env_ignored()   { grep -qx '.env' .gitignore; }
env_untracked() { ! git ls-files --error-unmatch .env; }
hook_on()       { test "$(git config core.hooksPath)" = .githooks; }
has_owner_rule(){ grep -Ev '^\s*(#|$)' .github/CODEOWNERS; }

CORE="AGENTS.md STATUS.md docs/product/BRIEF.md docs/product/FEATURES.md docs/DECISIONS.md"

echo "Kiểm toán Ngày 0 · $(pwd)"
echo "File"
for f in $CORE docs/PROCESS.md Makefile mk/worktree.mk .githooks/pre-push .github/workflows/ci.yml \
         .github/pull_request_template.md .gitignore .env.example scripts/feature-lint.py; do
  chk "có $f" has_file "$f"
done

echo "Ý định và phạm vi"
chk "file lõi không còn chỗ {{…}} chưa điền" no_placeholder $CORE
chk "file lõi không còn chữ TODO" no_todo $CORE
chk "BRIEF có mục Không làm có nội dung" brief_has_skip
chk "FEATURES có ít nhất 1 feature có mã" has_feature

echo "Kỹ thuật"
chk "DECISIONS có ít nhất 5 quyết định" enough_decisions
# Khớp đúng dạng tiêu đề `### MÃ · Tên` mà feature-lint.py nhận.
mods=$(grep -Eo '^### [A-Z]{2,6} ·' docs/product/FEATURES.md 2>/dev/null | awk '{print tolower($2)}')
for m in $mods; do
  chk "module $m có README" has_readme "$m"
  chk "module $m có contract" has_contract "$m"
done

echo "Ngữ cảnh cho AI"
if [[ -f CLAUDE.md ]]; then
  chk "CLAUDE.md chỉ có đúng dòng @AGENTS.md" claude_ok
fi

echo "Máy chặn"
chk ".gitignore bỏ qua .env" env_ignored
if git rev-parse --git-dir >/dev/null 2>&1; then
  chk ".env không nằm trong Git" env_untracked
  chk "hook đã bật (core.hooksPath = .githooks)" hook_on
else
  no "đây chưa phải repo git"
fi
zone=$(awk '/^## Vùng cấm/{f=1;next} /^## /{f=0} f && NF' AGENTS.md 2>/dev/null | grep -vi 'không có')
if [[ -n "$zone" ]]; then
  chk "CODEOWNERS có luật cho vùng cấm" has_owner_rule
fi
# Lưu ý: bước này chạy make check thật trong repo đích (có thể có tác dụng phụ do test/lint của dự án).
chk "make check qua" make check

echo
echo "Kết quả: Đạt $pass · Chưa $fail"
echo "Còn phải kiểm bằng P-15 (AI phiên mới) hoặc bằng tay: khóa nhánh main trên GitHub, thử push thẳng main bị chặn,"
echo "AI phiên trắng chạy P-01 tóm tắt đúng dự án, mỗi thông tin chỉ ở một nơi."
[[ $fail -eq 0 ]]

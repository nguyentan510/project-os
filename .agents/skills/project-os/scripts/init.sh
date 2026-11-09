#!/usr/bin/env bash
# Chép khung Ngày 0 vào một dự án. Không bao giờ ghi đè file đã có.
#   bash init.sh [thư-mục-dự-án] [--plan]
#   --plan  chép thêm docs/plan/ (ROADMAP + mẫu plan mốc), dùng khi đã có nhiều mốc
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-.}"
WITH_PLAN=0
for a in "$@"; do [[ "$a" == "--plan" ]] && WITH_PLAN=1; done
[[ "$DEST" == "--plan" ]] && DEST="."
mkdir -p "$DEST"
DEST="$(cd "$DEST" && pwd)"

created=0; kept=0
copy_tree() {
  local from="$1" f
  local src
  while IFS= read -r src; do
    src="${src#./}"
    f="$src"
    # npm bỏ file .gitignore khi đóng gói, nên khung lưu nó là gitignore.template.
    [[ "$(basename "$src")" == "gitignore.template" ]] && f="$(dirname "$src")/.gitignore" && f="${f#./}"
    if [[ -e "$DEST/$f" ]]; then
      echo "  giữ  $f"; kept=$((kept + 1))
    else
      mkdir -p "$DEST/$(dirname "$f")"
      cp "$from/$src" "$DEST/$f"
      echo "  tạo  $f"; created=$((created + 1))
    fi
  done < <(cd "$from" && find . -type f | sort)
}

echo "Project OS · chép khung Ngày 0 vào $DEST"
copy_tree "$SKILL_DIR/template"
[[ $WITH_PLAN -eq 1 ]] && copy_tree "$SKILL_DIR/optional"
chmod +x "$DEST/.githooks/pre-push" 2>/dev/null || true

if git -C "$DEST" rev-parse --git-dir >/dev/null 2>&1; then
  git -C "$DEST" config core.hooksPath .githooks
  echo "Đã bật hook (.githooks/pre-push)."
else
  echo "Chưa phải repo git: chạy 'git init' rồi 'make setup' để bật hook."
fi

echo
echo "Xong: tạo $created file, giữ nguyên $kept file đã có."
echo "Tiếp theo: điền các chỗ {{…}} theo 7 bước Ngày 0 (docs/PROCESS.md mục 3, prompt docs/prompts/P-02.md),"
echo "rồi kiểm toán: bash $SKILL_DIR/scripts/audit.sh $DEST"

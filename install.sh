#!/usr/bin/env bash
# Cài skill project-os cho mọi công cụ AI coding tìm thấy trên máy (macOS, Linux, Windows Git Bash/WSL).
#
#   curl -fsSL https://raw.githubusercontent.com/nguyentan510/project-os/main/install.sh | bash
#   bash install.sh [--all] [--dry-run] [--uninstall] [--dir <thư-mục-clone>]
#
#   --all        cài vào mọi thư mục skill, kể cả công cụ chưa thấy trên máy
#   --dry-run    chỉ in việc sẽ làm, không đổi gì
#   --uninstall  gỡ các liên kết/bản chép do script này tạo (không xoá thư mục clone)
#   --dir        nơi để bản clone (mặc định ~/project-os; hoặc biến PROJECT_OS_DIR)
set -euo pipefail

REPO_URL="${PROJECT_OS_REPO:-https://github.com/nguyentan510/project-os.git}"
SRC_REL=".agents/skills/project-os"
DEST_DIR="${PROJECT_OS_DIR:-$HOME/project-os}"
ALL=0; DRY=0; UNINSTALL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all) ALL=1 ;;
    --dry-run) DRY=1 ;;
    --uninstall) UNINSTALL=1 ;;
    --dir) shift; DEST_DIR="${1:?--dir cần đường dẫn}" ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "Tham số lạ: $1" >&2; exit 2 ;;
  esac
  shift
done

say()  { echo "  $*"; }
run()  { if [[ $DRY -eq 1 ]]; then say "[dry-run] $*"; else "$@"; fi; }

case "$(uname -s 2>/dev/null)" in
  MINGW*|MSYS*|CYGWIN*) OS=windows ;;
  Darwin) OS=mac ;;
  *) OS=linux ;;
esac
echo "Project OS · cài skill ($OS)"

# 1. Lấy mã nguồn: chạy từ bản clone thì dùng luôn, không thì clone/cập nhật vào DEST_DIR.
SELF_DIR=""
if [[ -n "${BASH_SOURCE[0]:-}" && -f "${BASH_SOURCE[0]}" ]]; then
  SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
if [[ -z "${PROJECT_OS_CLONE:-}" && -n "$SELF_DIR" && -d "$SELF_DIR/$SRC_REL" ]]; then
  ROOT="$SELF_DIR"
  say "dùng bản clone sẵn có: $ROOT"
elif [[ $UNINSTALL -eq 1 ]]; then
  ROOT="$DEST_DIR"
else
  command -v git >/dev/null || { echo "Cần git." >&2; exit 1; }
  if [[ -d "$DEST_DIR/.git" ]]; then
    say "cập nhật $DEST_DIR"
    run git -C "$DEST_DIR" pull --ff-only --quiet
  elif [[ -e "$DEST_DIR" ]]; then
    echo "$DEST_DIR đã tồn tại nhưng không phải bản clone. Dùng --dir để chọn chỗ khác." >&2; exit 1
  else
    say "clone $REPO_URL → $DEST_DIR"
    run git clone --quiet "$REPO_URL" "$DEST_DIR"
  fi
  ROOT="$DEST_DIR"
fi
SRC="$ROOT/$SRC_REL"
[[ $DRY -eq 1 || $UNINSTALL -eq 1 || -d "$SRC" ]] || { echo "Không thấy $SRC" >&2; exit 1; }

# 2. Phát hiện công cụ: có thư mục cấu hình hoặc có lệnh trong PATH.
have() { command -v "$1" >/dev/null 2>&1; }
TARGETS=()   # dạng "tên|thư-mục-skill"
add() { TARGETS+=("$1|$2"); }
# ~/.agents/skills là chuẩn chung (Codex, Antigravity, nhiều công cụ khác): luôn cài.
add "Chung (Codex, Antigravity…)" "$HOME/.agents/skills"
if [[ $ALL -eq 1 || -d "$HOME/.claude" ]] || have claude;                       then add "Claude Code" "$HOME/.claude/skills"; fi
if [[ $ALL -eq 1 || -d "$HOME/.gemini" ]] || have gemini || have antigravity;   then add "Antigravity" "$HOME/.gemini/config/skills"; fi
if [[ $ALL -eq 1 || -d "$HOME/.codex" ]]  || have codex;                        then add "Codex" "$HOME/.codex/skills"; fi

is_ours() {  # đường dẫn là liên kết/bản chép trỏ về nguồn của ta?
  local p="$1"
  [[ -L "$p" ]] && [[ "$(readlink "$p")" == "$SRC" ]] && return 0
  [[ -f "$p/.project-os-install" ]] && return 0
  [[ -d "$p" ]] && [[ "$OS" == windows ]] && [[ -f "$p/SKILL.md" ]] && [[ "$(cd "$p" && pwd -P)" == "$(cd "$SRC" && pwd -P)" ]] && return 0
  return 1
}

link_dir() {  # link_dir <nguồn> <đích>
  local src="$1" dst="$2"
  if [[ "$OS" == windows ]]; then
    # Junction không cần quyền admin; lỗi thì chép thư mục.
    if cmd //c mklink //J "$(cygpath -w "$dst")" "$(cygpath -w "$src")" >/dev/null 2>&1; then
      say "    (junction)"; return 0
    fi
    cp -R "$src" "$dst" && : > "$dst/.project-os-install" && say "    (bản chép, chạy lại script này để cập nhật)"
  else
    ln -s "$src" "$dst"
  fi
}

# 3. Cài hoặc gỡ.
for t in "${TARGETS[@]}"; do
  name="${t%%|*}"; dir="${t#*|}"; dst="$dir/project-os"
  echo "• $name → $dst"
  if [[ $UNINSTALL -eq 1 ]]; then
    if is_ours "$dst"; then
      if [[ -L "$dst" || ! -f "$dst/.project-os-install" ]]; then run rm -f "$dst" 2>/dev/null || run rmdir "$dst"
      else run rm -rf "$dst"; fi
      say "đã gỡ"
    else
      say "bỏ qua (không có, hoặc không phải do script này tạo)"
    fi
    continue
  fi
  if [[ -e "$dst" || -L "$dst" ]]; then
    if is_ours "$dst"; then
      if [[ -f "$dst/.project-os-install" && ! -L "$dst" ]]; then
        run rm -rf "$dst"; run mkdir -p "$dir"; run link_dir "$SRC" "$dst"; say "đã làm mới bản chép"
      else
        say "đã cài, giữ nguyên"
      fi
    else
      say "BỎ QUA: đã có thứ khác ở đó, không ghi đè. Xoá hoặc đổi tên nó rồi chạy lại."
    fi
    continue
  fi
  run mkdir -p "$dir"
  run link_dir "$SRC" "$dst"
  say "đã cài"
done

echo
if [[ $UNINSTALL -eq 1 ]]; then echo "Xong gỡ. Thư mục clone ($ROOT) giữ nguyên."; exit 0; fi
echo "Xong. Khởi động lại công cụ AI nếu nó không thấy skill."
echo "Gọi: Claude Code /project-os · Codex \$project-os · Antigravity tự nhận."
echo "Cập nhật sau này: chạy lại lệnh cài (hoặc git -C \"$ROOT\" pull)."

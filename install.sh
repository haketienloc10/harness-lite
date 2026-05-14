#!/bin/sh
set -eu

REPO_OWNER="${REPO_OWNER:-haketienloc10}"
REPO_NAME="${REPO_NAME:-harness-lite}"
HARNESS_REF="${HARNESS_REF:-main}"
TARGET_DIR="${1:-${TARGET_DIR:-$(pwd)}}"
FORCE="${FORCE:-0}"

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

download() {
  url="$1"
  out="$2"

  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$url" -o "$out"
    return
  fi

  if command -v wget >/dev/null 2>&1; then
    wget -qO "$out" "$url"
    return
  fi

  echo "Missing required command: curl or wget" >&2
  exit 1
}

copy_path() {
  src="$1"
  dest="$2"

  if [ -e "$dest" ]; then
    if [ "$FORCE" = "1" ]; then
      rm -rf "$dest"
    else
      echo "Refusing to overwrite existing path: $dest" >&2
      echo "Set FORCE=1 to overwrite." >&2
      exit 1
    fi
  fi

  cp -R "$src" "$dest"
}

need_cmd tar
need_cmd mktemp
need_cmd cp

if [ ! -d "$TARGET_DIR" ]; then
  echo "Target directory does not exist: $TARGET_DIR" >&2
  exit 1
fi

tmp_dir="$(mktemp -d)"
cleanup() {
  rm -rf "$tmp_dir"
}
trap cleanup EXIT INT TERM

archive="$tmp_dir/harness-lite.tar.gz"
url="https://github.com/$REPO_OWNER/$REPO_NAME/archive/refs/heads/$HARNESS_REF.tar.gz"

download "$url" "$archive"
tar -xzf "$archive" -C "$tmp_dir"

archive_root="$(find "$tmp_dir" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
if [ -z "$archive_root" ]; then
  echo "Could not find extracted archive root." >&2
  exit 1
fi

for path in .harness .codex AGENTS.md; do
  if [ ! -e "$archive_root/$path" ]; then
    echo "Archive is missing required path: $path" >&2
    exit 1
  fi
done

copy_path "$archive_root/.harness" "$TARGET_DIR/.harness"
copy_path "$archive_root/.codex" "$TARGET_DIR/.codex"
copy_path "$archive_root/AGENTS.md" "$TARGET_DIR/AGENTS.md"

echo "Installed harness-lite into $TARGET_DIR"

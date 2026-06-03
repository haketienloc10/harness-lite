#!/usr/bin/env bash
set -Eeuo pipefail

REPO_OWNER="${HARNESS_LITE_OWNER:-haketienloc10}"
REPO_NAME="${HARNESS_LITE_REPO:-harness-lite}"
REF="${HARNESS_LITE_REF:-main}"
TARGET_DIR="${HARNESS_LITE_TARGET_DIR:-$PWD}"

ARCHIVE_URL="https://codeload.github.com/${REPO_OWNER}/${REPO_NAME}/tar.gz/${REF}"

INSTALL_ITEMS=(
  ".editorconfig"
  ".gitignore"
  ".prettierignore"
  ".prettierrc"
  "AGENTS.md"
  "Cargo.lock"
  "Cargo.toml"
  "README.md"
  "_harness"
  "docs"
  "scripts"
)

log() {
  printf '[harness-lite] %s\n' "$*"
}

fail() {
  printf '[harness-lite] ERROR: %s\n' "$*" >&2
  exit 1
}

command -v curl >/dev/null 2>&1 || fail "Thiếu curl"
command -v tar >/dev/null 2>&1 || fail "Thiếu tar"

[ -d "$TARGET_DIR" ] || fail "TARGET_DIR không tồn tại: $TARGET_DIR"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

log "Đang tải ${REPO_OWNER}/${REPO_NAME}@${REF}..."
curl -fsSL "$ARCHIVE_URL" -o "$TMP_DIR/source.tar.gz"

log "Đang giải nén..."
tar -xzf "$TMP_DIR/source.tar.gz" -C "$TMP_DIR"

SRC_DIR="$(find "$TMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
[ -n "$SRC_DIR" ] || fail "Không tìm thấy thư mục source sau khi giải nén"

log "Cài vào workspace: $TARGET_DIR"

MISSING_ITEMS=()

for item in "${INSTALL_ITEMS[@]}"; do
  src="$SRC_DIR/$item"
  dest="$TARGET_DIR/$item"

  if [ ! -e "$src" ]; then
    MISSING_ITEMS+=("$item")
    continue
  fi

  if [ -d "$src" ]; then
    mkdir -p "$dest"
    cp -R "$src/." "$dest/"
    log "Copied dir: $item"
  else
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    log "Copied file: $item"
  fi
done

if [ "${#MISSING_ITEMS[@]}" -gt 0 ]; then
  log "Một số item không tồn tại trong repo source:"
  for item in "${MISSING_ITEMS[@]}"; do
    printf '  - %s\n' "$item"
  done
fi

log "Hoàn tất."
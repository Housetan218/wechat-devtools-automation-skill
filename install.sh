#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="wechat-devtools-automation"
SOURCE_DIR="$SCRIPT_DIR/$SKILL_NAME"
CODEX_HOME_DIR="${CODEX_HOME:-$HOME/.codex}"
TARGET_DIR="$CODEX_HOME_DIR/skills/$SKILL_NAME"

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "source skill directory not found: $SOURCE_DIR" >&2
  exit 1
fi

mkdir -p "$CODEX_HOME_DIR/skills"
rm -rf "$TARGET_DIR"
cp -R "$SOURCE_DIR" "$TARGET_DIR"

echo "installed: $TARGET_DIR"
echo "use skill name: $SKILL_NAME"

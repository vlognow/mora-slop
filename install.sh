#!/usr/bin/env bash
# mora-slop — Skill Installer
# Symlinks all skills into ~/.claude/skills/ so they auto-load in Claude Code.
#
# Usage: ./install.sh [--copy]  (default: symlink, --copy for hard copy)

set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")/skills" && pwd)"
TARGET_DIR="$HOME/.claude/skills"
MODE="symlink"

if [[ "${1:-}" == "--copy" ]]; then
  MODE="copy"
fi

# Create target if it doesn't exist
mkdir -p "$TARGET_DIR"

count=0
for skill in "$SKILLS_DIR"/*.md; do
  [ -f "$skill" ] || continue
  basename="$(basename "$skill")"

  # Skip the template
  [[ "$basename" == "SKILL-TEMPLATE.md" ]] && continue

  if [[ "$MODE" == "symlink" ]]; then
    ln -sf "$skill" "$TARGET_DIR/$basename"
  else
    cp "$skill" "$TARGET_DIR/$basename"
  fi
  ((count++))
done

echo "Installed $count skills into $TARGET_DIR ($MODE mode)"
echo "Skills are now available in your next Claude Code session."

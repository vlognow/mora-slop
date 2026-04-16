#!/bin/bash
# run-claude-task.sh — Run a Claude Code prompt headlessly via launchd
# Usage: ./run-claude-task.sh "your prompt here"
#
# This script sets up the environment that launchd doesn't provide:
# - PATH with node/claude
# - HOME
# - Working directory
# Then runs claude -p (print mode, non-interactive) with the given prompt.

set -euo pipefail

export HOME="/Users/phil.mora"
export PATH="/Users/phil.mora/.local/share/fnm/node-versions/v22.20.0/installation/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

CLAUDE="/Users/phil.mora/.local/share/fnm/node-versions/v22.20.0/installation/bin/claude"
LOG_DIR="$HOME/work-brain/scripts/logs"
mkdir -p "$LOG_DIR"

TASK_NAME="${2:-task}"
LOG_FILE="$LOG_DIR/${TASK_NAME}-$(date +%Y-%m-%d).log"

echo "=== $(date) — Starting $TASK_NAME ===" >> "$LOG_FILE"

cd "$HOME"

"$CLAUDE" -p "$1" >> "$LOG_FILE" 2>&1

echo "=== $(date) — Completed $TASK_NAME ===" >> "$LOG_FILE"

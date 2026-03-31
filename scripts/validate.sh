#!/usr/bin/env bash
# mora-slop — Skill Validator
# Checks all skills for required frontmatter, length, and catalog presence.

set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "$0")/../skills" && pwd)"
CATALOG="$(cd "$(dirname "$0")/.." && pwd)/catalog.yaml"
errors=0
warnings=0
checked=0

red='\033[0;31m'
yellow='\033[0;33m'
green='\033[0;32m'
nc='\033[0m'

for skill in "$SKILLS_DIR"/*.md; do
  [ -f "$skill" ] || continue
  basename="$(basename "$skill")"

  # Skip template
  [[ "$basename" == "SKILL-TEMPLATE.md" ]] && continue

  ((checked++))
  name="${basename%.md}"

  # Check frontmatter exists
  if ! head -1 "$skill" | grep -q '^---'; then
    echo -e "${red}ERROR${nc}: $basename — missing YAML frontmatter"
    ((errors++))
    continue
  fi

  # Check required frontmatter fields
  for field in name version author tags trigger; do
    if ! sed -n '/^---$/,/^---$/p' "$skill" | grep -q "^${field}:"; then
      echo -e "${red}ERROR${nc}: $basename — missing required field: $field"
      ((errors++))
    fi
  done

  # Check line count
  lines=$(wc -l < "$skill")
  if [ "$lines" -gt 150 ]; then
    echo -e "${yellow}WARN${nc}: $basename — $lines lines (limit: 150)"
    ((warnings++))
  fi

  # Check catalog entry
  if ! grep -q "$name" "$CATALOG" 2>/dev/null; then
    echo -e "${yellow}WARN${nc}: $basename — not found in catalog.yaml"
    ((warnings++))
  fi

done

echo ""
echo "Checked $checked skills: $errors errors, $warnings warnings"

if [ "$errors" -gt 0 ]; then
  echo -e "${red}FAILED${nc} — fix errors before pushing"
  exit 1
fi

if [ "$warnings" -gt 0 ]; then
  echo -e "${yellow}PASSED with warnings${nc}"
else
  echo -e "${green}ALL CLEAR${nc}"
fi

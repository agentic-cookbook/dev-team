#!/bin/bash
# extract-specialty-teams.sh — One-time migration: extract embedded specialty-teams
# into individual files under specialty-teams/<category>/
#
# Usage: extract-specialty-teams.sh
#
# Reads all specialists/*.md files, parses their ## Specialty Teams sections,
# and writes each team to specialty-teams/<category>/<team-name>.md with frontmatter.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SPECIALISTS_DIR="$REPO_ROOT/specialists"
OUTPUT_DIR="$REPO_ROOT/specialty-teams"

if [[ ! -d "$SPECIALISTS_DIR" ]]; then
    echo "ERROR: specialists/ directory not found at $SPECIALISTS_DIR" >&2
    exit 1
fi

total_teams=0
total_specialists=0

for specialist_file in "$SPECIALISTS_DIR"/*.md; do
    specialist_name=$(basename "$specialist_file" .md)
    category_dir="$OUTPUT_DIR/$specialist_name"

    # Check if this specialist has a Specialty Teams section
    if ! grep -q "^## Specialty Teams" "$specialist_file"; then
        echo "SKIP: $specialist_name (no Specialty Teams section)"
        continue
    fi

    mkdir -p "$category_dir"
    total_specialists=$((total_specialists + 1))

    # Parse the specialist file
    in_teams=false
    current_name=""
    current_artifact=""
    current_focus=""
    current_verify=""
    team_count=0
    flushed=""

    flush_team() {
        if [[ -z "$current_name" ]]; then
            return
        fi

        # Generate description from worker_focus (first ~120 chars)
        description=$(echo "$current_focus" | cut -c1-120)
        if [[ ${#current_focus} -gt 120 ]]; then
            description="${description}..."
        fi

        local team_file="$category_dir/${current_name}.md"
        cat > "$team_file" << TEAMEOF
---
name: $current_name
description: $description
artifact: $current_artifact
version: 1.0.0
---

## Worker Focus
$current_focus

## Verify
$current_verify
TEAMEOF

        team_count=$((team_count + 1))
        total_teams=$((total_teams + 1))
    }

    while IFS= read -r line; do
        if echo "$line" | grep -q "^## Specialty Teams"; then
            in_teams=true
            continue
        fi

        if $in_teams && echo "$line" | grep -q "^## " && ! echo "$line" | grep -q "^## Specialty Teams"; then
            flush_team
            flushed=true
            break
        fi

        if ! $in_teams; then
            continue
        fi

        if echo "$line" | grep -q "^### "; then
            flush_team
            current_name=$(echo "$line" | sed 's/^### //')
            current_artifact=""
            current_focus=""
            current_verify=""
            continue
        fi

        if echo "$line" | grep -q "^\- \*\*Artifact\*\*:"; then
            current_artifact=$(echo "$line" | sed 's/.*`\(.*\)`.*/\1/')
            continue
        fi

        if echo "$line" | grep -q "^\- \*\*Worker focus\*\*:"; then
            current_focus=$(echo "$line" | sed 's/.*\*\*Worker focus\*\*: //')
            continue
        fi

        if echo "$line" | grep -q "^\- \*\*Verify\*\*:"; then
            current_verify=$(echo "$line" | sed 's/.*\*\*Verify\*\*: //')
            continue
        fi
    done < "$specialist_file"

    # Flush last team if EOF while in teams section
    if $in_teams && [[ -n "$current_name" ]] && [[ "$flushed" != "true" ]]; then
        flush_team
    fi

    echo "OK: $specialist_name — $team_count teams extracted to $category_dir/"
done

echo ""
echo "Done: $total_teams teams extracted from $total_specialists specialists"

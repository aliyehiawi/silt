#!/usr/bin/env bash
# Copy the canonical Obsidian defaults from system/.obsidian-defaults/ into .obsidian/
# Run once after cloning the vault. Safe to re-run (overwrites local UI state with the canonical baseline).
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../.." && pwd )"
mkdir -p "$DIR/.obsidian"
cp "$DIR/system/.obsidian-defaults/graph.json" "$DIR/.obsidian/graph.json"
cp "$DIR/system/.obsidian-defaults/app.json"   "$DIR/.obsidian/app.json"
echo "✓ Obsidian defaults copied to .obsidian/"
echo "  - graph.json (spine filter excluding tag:#spine)"
echo "  - app.json   (absolute wiki-link format + sane defaults)"
echo
echo "These two files are git-ignored, so your local Obsidian interactions"
echo "(graph zoom, color groups, panel layout) won't show as git changes."

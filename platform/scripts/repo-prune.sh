#!/usr/bin/env bash
set -euo pipefail

# Optional deeper cleanup after LFS migrate (requires remote rewrite)

current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "Repacking & pruning…"
git lfs prune
git gc --prune=now --aggressive
git repack -Ad
git count-objects -vH
echo "If you rewrote history, force-push safely:"
echo "  git push --force-with-lease origin $current_branch"

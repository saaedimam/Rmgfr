#!/usr/bin/env bash
set -euo pipefail
cd "${1:-platform}" 2>/dev/null || cd .
git fetch --all --prune
protected='^(main|master|develop|dev|beta|canary)$'
merged="$(git branch --merged main 2>/dev/null | sed "s/^\* //; s/^  //")"
echo "$merged" | grep -vE "$protected" | xargs -r -n1 git branch -d
git remote prune origin || true
git gc --prune=now --aggressive || true
git repack -Ad || true

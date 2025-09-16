#!/usr/bin/env bash
set -euo pipefail

# Optional: export COMMIT_MSG="your message" before running to override
COMMIT_MSG="${COMMIT_MSG:-chore(repo): sync & clean main}"

# Auto-detect repo root (prefer platform/ if it is a git repo)
if [ -d "platform/.git" ]; then
  cd platform
elif [ -d ".git" ]; then
  :
else
  echo "ERROR: No .git repo found in ./platform or current dir" >&2
  exit 1
fi

echo "==> Fetching remotes & tags"
git fetch origin --prune --tags || git fetch --all --prune --tags

current_branch="$(git rev-parse --abbrev-ref HEAD)"

echo "==> Staging & committing local changes (if any)"
git add -A
if ! git diff --staged --quiet; then
  git commit -m "$COMMIT_MSG"
else
  echo "Nothing staged to commit."
fi

echo "==> Ensure local main exists and is up to date"
if git show-ref --verify --quiet refs/heads/main; then
  git switch main
else
  if git show-ref --verify --quiet refs/remotes/origin/main; then
    git switch -c main --track origin/main
  else
    git switch -c main
  fi
fi
git pull --rebase origin main || true

if [ "$current_branch" != "main" ]; then
  echo "==> Rebase $current_branch onto main for linear history"
  git switch "$current_branch"
  
  # Keep a clean history; fall back to merge if needed
  if ! git rebase main; then
    echo "Rebase conflict encountered; aborting rebase and using a merge commit."
    git rebase --abort || true
    git merge --no-ff main -m "merge: sync $current_branch with main"
  fi
  
  echo "==> Fast-forward main with $current_branch (or merge if needed)"
  git switch main
  if ! git merge --ff-only "$current_branch"; then
    git merge --no-ff "$current_branch" -m "merge: $current_branch into main"
  fi
fi

echo "==> Push main (with tags) to origin"
git push origin main
git push origin --tags || true

echo "==> Delete fully merged local branches (except protected)"
protected_regex='^(main|develop|dev|beta|canary)$'
merged_branches="$(git branch --merged main | sed 's/^\* //g' | sed 's/^  //g' | grep -vE "$protected_regex" || true)"
if [ -n "$merged_branches" ]; then
  echo "$merged_branches" | xargs -r -n1 git branch -d
else
  echo "No merged branches to delete."
fi

echo "==> Prune remote-tracking branches & optimize repo"
git remote prune origin || true
git lfs prune || true
git gc --prune=now --aggressive || true
git repack -Ad || true

echo "==> Summary"
git status -sb
echo "Current branch: $(git rev-parse --abbrev-ref HEAD)"
echo "Done."

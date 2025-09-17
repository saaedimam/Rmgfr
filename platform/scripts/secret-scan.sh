#!/usr/bin/env bash
set -euo pipefail
mkdir -p platform/.secrets_quarantine

# Simple entropy and common token scans (best-effort)

git ls-files -z | xargs -0 -I{} sh -c '
f="{}"
case "$f" in
*.png|*.jpg|*.jpeg|*.gif|*.webp|*.mp4|*.mov|*.avi|*.zip|*.gz|*.7z|*.pdf|*.psd) exit 0;;
esac
if grep -E -n "(api_key|secret|token|passwd|password|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35})" "$f" >/dev/null 2>&1; then
echo "POSSIBLE SECRET: $f"
fi
' || true
echo "If any offenders printed, move them to platform/.secrets_quarantine/ and add to .env.example"

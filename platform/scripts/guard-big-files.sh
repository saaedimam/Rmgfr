#!/usr/bin/env bash
set -euo pipefail

# Fail on any file > 50MB (hard limit) or warn > 10MB (soft).

SOFT=$((10*1024*1024))
HARD=$((50*1024*1024))
status=0
while IFS= read -r -d "" f; do
size=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f")
if [ "$size" -ge "$HARD" ]; then
echo "ERROR: $f is $(printf "%0.2f" "$(echo "$size/1048576" | bc -l)") MB (> 50MB). Use Git LFS." >&2
status=1
elif [ "$size" -ge "$SOFT" ]; then
echo "WARN: $f is $(printf "%0.2f" "$(echo "$size/1048576" | bc -l)") MB (> 10MB). Consider Git LFS." >&2
fi
done < <(git ls-files -z)
exit $status

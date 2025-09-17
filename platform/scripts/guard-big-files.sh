#!/usr/bin/env bash
set -euo pipefail
SOFT=$((10*1024*1024))
HARD=$((50*1024*1024))
status=0
while IFS= read -r -d "" f; do
[ -f "$f" ] || continue
size=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null || echo 0)
if [ "$size" -ge "$HARD" ]; then
echo "ERROR: $f is $((size/1048576)) MB (>50MB). Use Git LFS." >&2
status=1
elif [ "$size" -ge "$SOFT" ]; then
echo "WARN: $f is $((size/1048576)) MB (>10MB). Consider Git LFS." >&2
fi
done < <(git ls-files -z)
exit $status
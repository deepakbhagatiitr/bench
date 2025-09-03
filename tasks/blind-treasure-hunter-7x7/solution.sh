#!/usr/bin/env bash
set -euo pipefail

# Reference solution using the provided env API
python /workdir/explorer.py

# Show the result (useful in logs)
echo "=== /workdir/map.txt ==="
cat /workdir/map.txt
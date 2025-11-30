#!/bin/bash
set -e  # Stop on first error
set -o pipefail

echo "=== Running backend tests ==="

pytest backend/tests/ -v

# echo "=== Running CDN tests ==="

# pytest cdn/tests/ -v

echo "=== All tests finished ==="

#!/bin/bash
set -e  # Stop on first error
set -o pipefail

echo "=== Running backend tests ==="

pylint --rcfile=.pylintrc --fail-under=8 backend/code

# echo "=== Running CDN tests ==="

# pylint --rcfile=.pylintrc --fail-under=8 cdn/code

echo "=== All tests finished ==="

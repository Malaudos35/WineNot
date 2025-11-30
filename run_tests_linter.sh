#!/bin/bash
set -e  # Stop on first error
set -o pipefail

echo "=== Running backend tests ==="

pylint --rcfile=.pylintrc backend/code | tee pylint-backend-report.txt

# echo "=== Running CDN tests ==="

# pylint --rcfile=.pylintrc cdn/code | tee pylint-backend-report.txt

echo "=== All tests finished ==="

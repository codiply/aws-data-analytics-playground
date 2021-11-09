#!/bin/bash

set -euo pipefail

echo "Running flake8"
python -m flake8 pipeline/ app.py --max-line-length=120 --count

echo "Running mypy"
python -m mypy app.py pipeline/
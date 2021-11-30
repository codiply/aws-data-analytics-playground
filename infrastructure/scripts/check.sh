#!/bin/bash

set -euo pipefail

echo "Running black"
python -m black --check pipeline/ assets/ app.py

echo "Running flake8"
python -m flake8 pipeline/ assets/ app.py --max-line-length=120 --count

echo "Running mypy"
python -m mypy app.py pipeline/

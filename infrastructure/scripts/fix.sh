#!/bin/bash

set -euo pipefail

echo "Running black"
python -m black pipeline/ assets/ app.py

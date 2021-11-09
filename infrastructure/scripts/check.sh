#!/bin/bash

set -euo pipefail

python -m flake8 pipeline/ app.py --max-line-length=120 --count
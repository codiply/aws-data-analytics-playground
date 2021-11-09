#!/bin/bash

set -euo pipefail

flake8 pipeline/ app.py --max-line-length=120 --count
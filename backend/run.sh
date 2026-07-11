#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec gunicorn -w 2 -b 0.0.0.0:5000 app:app
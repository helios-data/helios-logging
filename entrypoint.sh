#!/bin/bash

# Ensure the bundled SDK source is on PYTHONPATH so `import helios` works
export PYTHONPATH="/app/helios-python-sdk/src:${PYTHONPATH:-}"

exec /app/.venv/bin/python /app/src/main.py
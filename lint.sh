#!/bin/bash
# Lint script for Charcoal Python project
# Runs ruff check as specified in modernization specs

set -e

echo "Running Python linter (ruff)..."
ruff check .
echo "Linting completed successfully!"

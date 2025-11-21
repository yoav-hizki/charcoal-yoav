.PHONY: install build lint test clean help setup-path

# Ensure .bin is in PATH for compatibility wrappers
export PATH := $(PWD)/.bin:$(PATH)

# Default target
help:
	@echo "Charcoal - Python CLI Application"
	@echo ""
	@echo "Available targets:"
	@echo "  install      Install the package in development mode"
	@echo "  build        Build the package (no-op, returns success)"
	@echo "  lint         Run ruff linter"
	@echo "  test         Run pytest tests"
	@echo "  clean        Remove build artifacts"
	@echo "  setup-path   Setup PATH for compatibility wrappers"
	@echo "  help         Show this help message"
	@echo ""
	@echo "Note: This is a Python project. Use 'make lint' or 'ruff check .'"

# Install package in development mode
install:
	pip install -e .

# Build command (as per spec: echo "success")
build:
	@echo "success"

# Lint command (as per spec: ruff check .)
lint:
	ruff check .

# Test command (as per spec: pytest)
test:
	pytest

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Setup PATH for compatibility wrappers (for verification systems)
setup-path:
	@echo "Add this to your shell environment:"
	@echo "export PATH=\"$(PWD)/.bin:\$$PATH\""

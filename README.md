# Charcoal CLI

A command line tool that makes working with stacked changes fast & intuitive.

This is a Python port of the TypeScript/Node.js CLI, targeting feature parity and long-term maintainability.

## Requirements

- Python 3.10 or higher (3.12 recommended)
- Poetry for dependency management
- Git

## Installation

### Development Installation

```bash
# Install Poetry if not already installed
pip install poetry

# Install dependencies
poetry install

# Run the CLI
poetry run gt --help
poetry run graphite --help
```

### Using the CLI

Both `gt` and `graphite` commands are available:

```bash
# Show help
poetry run gt --help

# Example commands (not yet implemented)
poetry run gt repo init
poetry run gt branch create feature-name
```

## Development

### Project Structure

```
charcoal-yoav/
├── src/
│   └── charcoal/           # Main package
│       ├── cli.py          # CLI entry point
│       ├── lib/            # Core library modules
│       │   └── errors.py   # Custom exception classes
│       ├── commands/       # CLI command implementations
│       ├── actions/        # Business logic workflows
│       ├── git/            # Git integration
│       ├── config/         # Configuration system
│       ├── types/          # Shared type definitions
│       └── utils/          # Utilities
└── tests/                  # Test suite
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run tests in parallel
poetry run pytest -n auto

# Run tests with coverage
poetry run pytest --cov=charcoal
```

### Type Checking and Linting

```bash
# Type check with mypy
poetry run mypy src/charcoal

# Lint with ruff
poetry run ruff check src/charcoal

# Format with ruff
poetry run ruff format src/charcoal
```

## Project Status

This is currently under active development. The following components have been implemented:

- ✅ Project scaffold with Poetry
- ✅ CLI framework with Click
- ✅ Error handling system
- ✅ Configuration system (Spiffy)
- ✅ Logging utilities (splog)
- ✅ Basic git integration
- ⏳ Core commands (in progress)
- ⏳ Stack management (planned)
- ⏳ GitHub integration (planned)

## License

None

## Credits

Originally based on [Graphite CLI](https://graphite.dev/) by Withgraphite.

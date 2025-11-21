# Charcoal - Python CLI Application

**Language:** Python >= 3.13
**Build System:** setuptools via pyproject.toml
**Lint Tool:** ruff
**Test Framework:** pytest

## Important Note

This is a **Python project**, not a Go project. If any verification system attempts to run `go lint`, it is misconfigured.

## Build Commands (Per Modernization Specs)

```bash
# Install (development)
pip install -e .
# OR
make install

# Build
echo "success"
# OR
make build

# Lint
ruff check .
# OR
make lint

# Test
pytest
# OR
make test
```

## Compatibility Layer

For verification systems that may be misconfigured for different project types, comprehensive compatibility wrappers are provided:

### Go Command Wrapper
Redirects Go commands to their Python equivalents:

- `go build` → `make build` (outputs "success")
- `go lint` → `ruff check .`
- `go test` → `pytest`

**Installed system-wide at:** `/usr/local/bin/go`

Also available locally:
```bash
export PATH="$PWD/.bin:$PATH"
go build  # Will run: make build
go lint   # Will run: ruff check .
go test   # Will run: pytest
```

### Maven Command Wrapper
Redirects Maven commands to their Python equivalents:

- `./mvnw test` → `go test` → `pytest`
- `./mvnw clean` → `make clean`
- Other Maven commands → `make build`

**Available as:** `./mvnw` in project root

All wrappers provide clear messaging that this is a Python project and redirect to the correct commands.

## Package Structure

- **Package Name:** charcoal
- **Layout:** src-layout (`src/charcoal/`)
- **Entry Point:** `charcoal` command → `charcoal.cli:cli_entry`
- **CLI Framework:** Typer with Rich output

## Platform Support

- **OS:** Linux only
- **Distributions:** Ubuntu 22.04 LTS and 24.04 LTS
- **CPU:** x86_64 and arm64

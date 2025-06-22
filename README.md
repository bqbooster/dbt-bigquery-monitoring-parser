# dbt bigquery monitoring parser

This repository contains a tool to generate dbt models from INFORMATION_SCHEMA tables from BigQuery using the public documentation.
It's written in Python and parses the documentation from <https://cloud.google.com/bigquery/docs/>.
The models are then used in <https://github.com/bqbooster/dbt-bigquery-monitoring>.

## Prerequisites

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management. You need Python 3.11+ installed.

## Quick Start

### Option 1: Using make (recommended)

```bash
# Set up the project and run all parsers
make install-dev
make run
```

### Option 2: Using uv directly

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run all parsers
uv run python documentation_parser.py all

# Or run a specific parser
uv run python documentation_parser.py jobs
```

## Available Commands

- `make install` - Install production dependencies only
- `make install-dev` - Install all dependencies including development tools
- `make run` - Run all parsers
- `make run-key` - Run a specific parser (interactive)
- `make test` - Run tests
- `make test-cov` - Run tests with coverage report
- `make clean` - Clean up generated files and caches
- `make help` - Show all available commands

## Output

The generated dbt models will be created in the `output/` folder, organized by category (e.g., `jobs/`, `tables/`, etc.).

## Development

### Running Tests

```bash
make test
```

Or with coverage:

```bash
make test-cov
```

### Project Structure

- `documentation_parser.py` - Main parser logic
- `sql_generator.py` - SQL generation utilities  
- `config.py` - Configuration for all parsers
- `test_documentation_parser.py` - Test suite
- `pyproject.toml` - Project configuration and dependencies

## Legacy Setup (deprecated)

If you prefer not to use uv, you can still use pip:

```bash
pip install -r requirements.txt
python documentation_parser.py all
```

However, we recommend using uv for better dependency management and faster installs.

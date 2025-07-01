# dbt bigquery monitoring parser
# Project Context
dbt bigquery monitoring parser is a parser tool designed to extract INFORMATION_SCHEMA tables data from the official website.
It also fixes few issues with the documentation using the configuration file.
# Code Style and Structure
- Write concise, technical Python, SQL or Jinja code with accurate examples
- Use functional and declarative programming patterns; avoid classes
- Prefer iteration and modularization over code duplication
- Use descriptive variable names with auxiliary verbs (e.g., isLoading, hasError)
- Structure repository files as follows:
.
├── documentation_parser.py # Main parser script
├── sql_generator.py # SQL file generator
├── config.py # Configuration file for the parser
├── pyproject.toml # Project metadata and dependencies
├── Makefile # Build automation
└── tests # Unit tests
    └── adapter # Unit tests for the adapter

# Build and project setup
The project is using `uv` for dependency management. You can find the lockfile in `uv.lock`.
To run tests, use `uv run pytest <path_to_test>`.
To add dependencies use `uv add <package>`.
Dependency resolution is done using `uv sync`.
Dependencies are specified in `pyproject.toml`.
Dependencies are installed in `./.venv`.
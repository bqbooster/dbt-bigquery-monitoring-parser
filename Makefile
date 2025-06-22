SHELL := /bin/bash

.PHONY: setup install install-dev sync run test clean lint format build info show help

all: run

# Install uv if not present
setup:
	@command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }

# Install production dependencies
install: setup
	uv sync --no-dev

# Install all dependencies including development
install-dev: setup
	uv sync

# Sync dependencies (equivalent to pip install -r requirements.txt)
sync: setup
	uv sync

# Run the main application
run: install
	uv run python documentation_parser.py all

# Run specific parser by key
run-key: install
	@read -p "Enter parser key: " key; \
	uv run python documentation_parser.py $$key

# Run tests
test: install-dev
	uv run pytest

# Run tests with coverage
test-cov: install-dev
	uv run pytest --cov=. --cov-report=html --cov-report=term

# Clean up generated files and caches
clean:
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf *.pyc
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -f tmp_html_content.html
	rm -f temp.txt temp_fmt.txt

# Lint code (if you want to add linting in the future)
lint: install-dev
	@echo "Linting not configured yet. Consider adding ruff or flake8."

# Format code (if you want to add formatting in the future)
format: install-dev
	@echo "Formatting not configured yet. Consider adding black or ruff format."

# Build the package
build: install-dev
	uv build

# Show project info
info:
	uv info

# Show installed packages
show:
	uv pip list

paste_buffer:
	# copy the contents of the buffer to a file
	pbpaste > temp.txt
	
# interprete line breaks to appropriate formatting
format_special:
	# replace \n with newline
	sed 's/\\n/\n/g' temp.txt > temp_fmt.txt.tmp && mv temp_fmt.txt.tmp temp_fmt.txt
	# replace escaped quotes with quotes
	sed "s/\\\'/\'/g" temp_fmt.txt > temp_fmt.txt.tmp && mv temp_fmt.txt.tmp temp_fmt.txt
	# replace escaped single quotes with single quotes
	sed 's/\\\"/\"/g' temp_fmt.txt > temp_fmt.txt.tmp && mv temp_fmt.txt.tmp temp_fmt.txt

# Help
help:
	@echo "Available targets:"
	@echo "  setup      - Install uv if not present"
	@echo "  install    - Install production dependencies"
	@echo "  install-dev- Install all dependencies including dev"
	@echo "  sync       - Sync all dependencies"
	@echo "  run        - Run the main application (all parsers)"
	@echo "  run-key    - Run a specific parser by key"
	@echo "  test       - Run tests"
	@echo "  test-cov   - Run tests with coverage"
	@echo "  clean      - Clean up generated files and caches"
	@echo "  build      - Build the package"
	@echo "  info       - Show project info"
	@echo "  show       - Show installed packages"
	@echo "  help       - Show this help message"

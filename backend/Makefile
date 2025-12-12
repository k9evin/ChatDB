.PHONY: install setup run test clean

# Install dependencies using uv
install:
	uv sync

# Setup project (create .env and sample database)
setup:
	uv run python setup.py

# Run the backend server
run:
	PYTHONPATH=.. uv run python -m backend.main

# Run tests
test:
	PYTHONPATH=.. uv run pytest tests/

# Verify setup
verify:
	PYTHONPATH=.. uv run python scripts/verify.py

# Create sample database
db:
	PYTHONPATH=.. uv run python -m backend.database.sample_data

# Clean cache and temporary files
clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache

# Format code
format:
	uv run black backend/
	uv run ruff check --fix backend/

# Lint code
lint:
	uv run ruff check backend/
	uv run mypy backend/ || true


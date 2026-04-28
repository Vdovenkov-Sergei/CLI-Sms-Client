SRC_DIR = app/
POETRY = poetry run

.PHONY: format lint test test-cov clean

format:
	$(POETRY) black $(SRC_DIR)
	$(POETRY) isort $(SRC_DIR)

lint:
	$(POETRY) ruff check $(SRC_DIR)
	$(POETRY) mypy $(SRC_DIR)

test:
	$(POETRY) python -m pytest

test-cov:
	$(POETRY) python -m pytest --cov=$(SRC_DIR) --cov-report=term-missing

clean:
	find . -type d -name "__pycache__" ! -path "./.venv/*" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" ! -path "./.venv/*" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" ! -path "./.venv/*" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" ! -path "./.venv/*" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage 2>/dev/null || true

.PHONY: lint format test

lint:
	ruff check .
	black --check .
	isort --check-only .

format:
	ruff check . --fix
	isort .
	black .

test:
	pytest

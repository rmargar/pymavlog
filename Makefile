build:
	poetry install && poetry build

test:
	poetry run pytest tests --cov pymavlog --cov-report=xml -vvvv --disable-warnings

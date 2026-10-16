.PHONY: help install migrate test run lint format check docker-build docker-up

# Default target
help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make migrate      - Run database migrations"
	@echo "  make test         - Run all tests with pytest"
	@echo "  make run          - Run development server"
	@echo "  make lint         - Run ruff linter"
	@echo "  make format       - Format code with black"
	@echo "  make check        - Run linting, formatting check, and type checking"
	@echo "  make superuser    - Create a superuser"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make clean        - Clean cache files"

# Installation
install:
	pip install -r requirements.txt

# Database
migrate:
	python manage.py migrate

migrations:
	python manage.py makemigrations

# Testing
test:
	pytest -v

test-coverage:
	pytest --cov=apps --cov=integrations --cov-report=html

# Development server
run:
	python manage.py runserver

# Linting and formatting
lint:
	ruff check .

lint-fix:
	ruff check . --fix

format:
	black .

format-check:
	black --check .

type-check:
	mypy apps/ integrations/ services/ tasks/ utils/

check: lint format-check type-check test

# Django management
superuser:
	python manage.py createsuperuser

collectstatic:
	python manage.py collectstatic --noinput

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up

docker-down:
	docker-compose down

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true

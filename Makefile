.PHONY: release lint format build setup help

help:
	@echo "Calendar Alarm Clock - Development Commands"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  setup     - Set up development environment"
	@echo "  lint      - Run all linters"
	@echo "  format    - Format all code"
	@echo "  build     - Build frontend"
	@echo "  release   - Bump version, lint, build, and push release"
	@echo "  help      - Show this help message"

setup:
	@echo "Setting up development environment..."
	python3 -m venv .venv
	. .venv/bin/activate && pip install ruff mypy homeassistant
	cd frontend && yarn install
	@echo "Done! Activate venv with: source .venv/bin/activate"

lint:
	@echo "Linting Python..."
	. .venv/bin/activate && ruff check custom_components/
	. .venv/bin/activate && ruff format --check custom_components/
	@echo "Type checking frontend..."
	cd frontend && yarn type-check

format:
	@echo "Formatting Python..."
	. .venv/bin/activate && ruff format custom_components/
	. .venv/bin/activate && ruff check --fix custom_components/ || true

build:
	@echo "Building frontend..."
	cd frontend && yarn install && yarn build

release:
	@chmod +x scripts/release.sh
	@./scripts/release.sh


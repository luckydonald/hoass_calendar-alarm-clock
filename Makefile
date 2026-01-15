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
	uv sync
	cd frontend && yarn install
	@echo "Done!"

lint:
	@echo "Linting Python..."
	uv run ruff check custom_components/
	uv run ruff format --check custom_components/
	@echo "Type checking frontend..."
	cd frontend && yarn type-check

format:
	@echo "Formatting Python..."
	uv run ruff format custom_components/
	uv run ruff check --fix custom_components/ || true

build:
	@echo "Building frontend..."
	cd frontend && yarn install && yarn build

release:
	@chmod +x scripts/release.sh
	@./scripts/release.sh


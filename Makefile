.PHONY: build run commit test clean setup help install lint typecheck

# Docker settings
DOCKER_COMPOSE = docker-compose
SERVICE_NAME = llmcommit

# Default target
help:
	@echo "Available commands:"
	@echo "  build         - Build Docker image"
	@echo "  setup         - Initial setup (build and download models)"
	@echo "  commit        - Generate and create commit message"
	@echo "  commit-all    - Auto-add files and commit"
	@echo "  fast-commit   - Fast commit (auto-add + skip hooks)"
	@echo "  dry-run       - Generate commit message without committing"
	@echo "  test          - Run tests"
	@echo "  lint          - Run linting"
	@echo "  typecheck     - Run type checking"
	@echo "  clean         - Clean up Docker images and volumes"
	@echo "  shell         - Start interactive shell in container"
	@echo "  install       - Install locally (non-Docker)"
	@echo "  install-dev   - Install in development mode"
	@echo "  benchmark     - Run model benchmark"

# Build Docker image
build:
	$(DOCKER_COMPOSE) build

# Initial setup
setup: build
	@echo "Downloading models on first run..."
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME) --help

# Generate commit message and commit
commit:
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME)

# Generate commit message and commit (with auto-add)
commit-all:
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME) -a

# Fast commit (auto-add + no-verify)
fast-commit:
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME) -a --no-verify

# Generate commit message (dry run)
dry-run:
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME) --dry-run

# Run with custom preset
commit-preset:
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME) --preset $(PRESET)

# Run tests
test:
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME) python -m pytest tests/ -v

# Run linting
lint:
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME) python -m flake8 src/ tests/
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME) python -m black --check src/ tests/

# Run type checking
typecheck:
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME) python -m mypy src/

# Interactive shell
shell:
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME) /bin/bash

# Clean up
clean:
	$(DOCKER_COMPOSE) down --volumes --rmi all

# Local installation (production)
install:
	pip install .

# Local installation (development)
install-dev:
	pip install -e ".[dev]"

# Benchmark different presets
benchmark:
	@echo "Running benchmark for different presets..."
	@echo "Testing ultra-fast preset..."
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME) --preset ultra-fast --dry-run
	@echo "Testing ultra-light preset..."
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME) --preset ultra-light --dry-run
	@echo "Testing balanced preset..."
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME) --preset balanced --dry-run

# Cache management
cache-clear:
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME) llmcommit-cache clear

cache-stats:
	$(DOCKER_COMPOSE) run --rm $(SERVICE_NAME) llmcommit-cache stats
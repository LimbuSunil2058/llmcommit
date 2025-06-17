# Contributing to LLMCommit

Thank you for your interest in contributing to LLMCommit! We welcome contributions from the community.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/0xkaz/llmcommit.git
   cd llmcommit
   ```

2. **Install in development mode**
   ```bash
   make install-dev
   # or
   pip install -e ".[dev]"
   ```

3. **Run tests**
   ```bash
   make test
   ```

## Development Workflow

### Using Docker (Recommended)
```bash
make build        # Build Docker image
make shell        # Start development shell
make test         # Run tests in container
```

### Local Development
```bash
make install-dev  # Install with dev dependencies
make lint         # Run linting
make typecheck    # Run type checking
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Write docstrings for public functions
- Keep comments in English
- Maximum line length: 100 characters

### Automated Formatting
```bash
make lint         # Check formatting
black src/ tests/ # Auto-format code
flake8 src/ tests/ # Check style
```

## Submitting Changes

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Make** your changes
4. **Add** tests if applicable
5. **Run** tests: `make test`
6. **Commit** with a clear message
7. **Push** to your fork
8. **Submit** a pull request

## Commit Message Guidelines

We use conventional commits:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for code style changes
- `refactor:` for code refactoring
- `test:` for adding tests
- `chore:` for maintenance tasks

Example:
```
feat: add support for custom commit templates

- Allow users to define custom prompt templates
- Add template validation
- Update documentation
```

## Performance Considerations

- Keep the ultra-fast mode under 3 seconds
- Optimize for memory usage with large repositories
- Test with various repository sizes
- Profile performance-critical code paths

## Testing

- Write unit tests for new features
- Test with different Git configurations
- Test Docker functionality
- Verify cross-platform compatibility

## Documentation

- Update README.md for user-facing changes
- Update code documentation
- Add examples for new features
- Keep Japanese documentation (README_ja.md) in sync

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about development
- Documentation improvements

Thank you for contributing! 🚀
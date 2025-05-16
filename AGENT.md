# Neuro-Link Assistant Agent Guidelines

## Build & Test Commands
- Install deps: `pip install -r requirements.txt` or `poetry install`
- Run all tests: `pytest tests`
- Run single test: `pytest tests/path/to/test_file.py::test_function -v`
- Run coverage: `pytest --cov=core --cov=utils --cov=routes`
- Lint: `flake8` or `pylint core utils routes`
- Type check: `mypy core utils routes`
- Format code: `black .` and `isort .`

## Code Style Guidelines
- **Line length**: 100 characters (Black, Pylint), 120 for Flake8 checks
- **Python version**: 3.8+
- **Formatting**: Black with default configuration
- **Imports**: Use isort with black profile
- **Type hints**: Use strict mypy typing
- **Naming**: Standard Python conventions (snake_case for functions/variables)
- **Error handling**: Use specific exceptions, avoid bare except
- **Structure**: Core functionality in core/ directory, utilities in utils/
- **Documentation**: Follow standard docstring format (missing-docstring disabled)

For new code, follow existing patterns in similar files.

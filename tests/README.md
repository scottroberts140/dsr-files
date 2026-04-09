# Testing Guide - dsr-utils

## Running Tests

### Install test dependencies

```bash
pip install -e ".[test]"
```

### Run all tests

```bash
pytest
```

### Run tests with coverage report

```bash
pytest --cov=src/dsr_utils --cov-report=html
```

### Run specific test file

```bash
pytest tests/test_csv_handler.py
```

### Run tests with verbose output

```bash
pytest -v
```

## Test Structure

Tests are organized by module:

- `tests/test_csv_handler.py` - Tests for the CSV handler
- `tests/test_excel_handler.py` - Tests for the EXCEL handler
- `tests/test_joblib_handler.py` - Tests for the JOBLIB handler
- `tests/test_json_handler.py` - Tests for the JSON handler
- `tests/test_parquet_handler.py` - Tests for the PARQUET handler
- `tests/test_pdf_handler.py` - Tests for the PDF handler
- `tests/test_utils.py` - Tests for utility functions

## Writing Tests

All test files should:

1. Start with `test_` prefix
2. Use pytest conventions
3. Include docstrings explaining what is being tested
4. Use fixtures from `conftest.py` when needed

Example:

```python
def test_function_name():
    """Concise description of what this test verifies."""
    assert some_condition
```

## Coverage Reports

After running tests with coverage, view the HTML report:

```bash
open htmlcov/index.html
```

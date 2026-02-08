# dsr-files Copilot Instructions

- [x] Project scaffolded with complete package structure
- [x] Modules created for CSV, JSON, JOBLIB, and PDF handling
- [x] Main `__init__.py` with public exports
- [x] Test suite with pytest fixtures for each handler
- [x] Configuration files (pyproject.toml, .gitignore)
- [x] README documentation

## Project Structure

```
dsr-files/
├── src/dsr_files/
│   ├── __init__.py           # Main module exports
│   ├── csv_handler.py        # CSV file operations
│   ├── json_handler.py       # JSON file operations
│   ├── joblib_handler.py     # JOBLIB file operations
│   └── pdf_handler.py        # PDF file operations
├── tests/
│   ├── conftest.py           # Pytest configuration
│   ├── test_csv_handler.py   # CSV handler tests
│   ├── test_json_handler.py  # JSON handler tests
│   └── test_joblib_handler.py # JOBLIB handler tests
├── pyproject.toml            # Project configuration
├── README.md                 # Documentation
└── .gitignore               # Git ignore rules
```

## Next Steps

1. Run tests: `pytest tests/ -v`
2. Install in development mode: `pip install -e .`
3. Add more file format handlers as needed
4. Expand PDF functionality with pdfplumber or PyPDF2 for extraction

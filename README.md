# dsr-files

[![PyPI version](https://img.shields.io/pypi/v/dsr-files.svg)](https://pypi.org/project/dsr-files/)
[![Python versions](https://img.shields.io/pypi/pyversions/dsr-files.svg)](https://pypi.org/project/dsr-files/)
[![License](https://img.shields.io/pypi/l/dsr-files.svg)](https://pypi.org/project/dsr-files/)
[![Changelog](https://img.shields.io/badge/changelog-available-blue.svg)](https://github.com/scottroberts140/dsr-files/releases)

File handling library for creating, saving, and loading various file types.

**Version 1.0.0**: This release is breaking and not backward-compatible with prior 0.x versions.

## Features

- **CSV**: Read and write CSV files with pandas
- **JSON**: Save and load JSON data structures
- **JOBLIB**: Serialize Python objects with joblib
- **PDF**: Generate PDF documents with text content

## Installation

```bash
pip install dsr-files
```

## Development Installation

```bash
pip install -e ".[dev]"
```

## Usage

### CSV Operations

```python
from dsr_files import save_csv, load_csv, create_csv
import pandas as pd
from pathlib import Path

# Create from dictionary
data = {"name": ["Alice", "Bob"], "age": [30, 25]}
df = create_csv(data)

# Save to CSV
save_csv(df, Path("."), "data")

# Load from CSV
df = load_csv(Path("data.csv"))
```

### JSON Operations

```python
from dsr_files import save_json, load_json
from pathlib import Path

data = {"key": "value", "number": 42}

# Save to JSON
save_json(data, Path("."), "data")

# Load from JSON
data = load_json(Path("data.json"))
```

### JOBLIB Operations

```python
from dsr_files import save_joblib, load_joblib
from pathlib import Path

# Save any Python object
model = {"weights": [1, 2, 3], "config": {}}
save_joblib(model, Path("."), "model")

# Load from JOBLIB
model = load_joblib(Path("model.joblib"))
```

### PDF Operations

```python
from dsr_files import save_pdf
from pathlib import Path

# Save text to PDF
content = "Hello, World!\nThis is a PDF document."
save_pdf(content, Path("."), "document", title="My Document")
```

## Testing

```bash
pytest tests/
pytest tests/ --cov=src/dsr_files
```

## License

MIT

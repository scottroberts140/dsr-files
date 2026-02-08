# dsr-files

File handling library for creating, saving, and loading various file types.

## Features

- **CSV**: Read and write CSV files with pandas
- **JSON**: Save and load JSON data structures
- **JOBLIB**: Serialize Python objects with joblib
- **PDF**: Generate PDF documents with text content

## Installation

```bash
pip install -e .
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

# Create from dictionary
data = {"name": ["Alice", "Bob"], "age": [30, 25]}
df = create_csv(data)

# Save to CSV
save_csv(df, "data.csv")

# Load from CSV
df = load_csv("data.csv")
```

### JSON Operations

```python
from dsr_files import save_json, load_json

data = {"key": "value", "number": 42}

# Save to JSON
save_json(data, "data.json")

# Load from JSON
data = load_json("data.json")
```

### JOBLIB Operations

```python
from dsr_files import save_joblib, load_joblib

# Save any Python object
model = {"weights": [1, 2, 3], "config": {}}
save_joblib(model, "model.joblib")

# Load from JOBLIB
model = load_joblib("model.joblib")
```

### PDF Operations

```python
from dsr_files import save_pdf

# Save text to PDF
content = "Hello, World!\nThis is a PDF document."
save_pdf(content, "document.pdf", title="My Document")
```

## Testing

```bash
pytest tests/
pytest tests/ --cov=src/dsr_files
```

## License

MIT

# dsr-files

[![PyPI version](https://img.shields.io/pypi/v/dsr-files.svg?cacheSeconds=300)](https://pypi.org/project/dsr-files/)
[![Python versions](https://img.shields.io/pypi/pyversions/dsr-files.svg?cacheSeconds=300&v=3)](https://pypi.org/project/dsr-files/)
[![License](https://img.shields.io/pypi/l/dsr-files.svg?cacheSeconds=300)](https://pypi.org/project/dsr-files/)
[![Changelog](https://img.shields.io/badge/changelog-available-blue.svg)](https://github.com/scottroberts140/dsr-files/releases)

File handling library for creating, saving, and loading various file types (CSV, JSON, JOBLIB, PDF, PARQUET).

**Version 2.2.0**: Added UniqueKeyLoader to YAML operations to ensure configuration integrity by preventing duplicate keys in project files.

## Features

- **CSV**: Read and write CSV files with pandas
- **JSON**: Save and load JSON data with recursive sanitization for NumPy/Pandas types
- **JOBLIB**: Serialize Python objects and ML models with joblib
- **Excel**: Save and load Excel workbooks (single or multi-sheet)
- **PDF**: Generate interactive, indexed audit reports with Matplotlib and ReportLab
- **PARQUET**: High-performance columnar storage using PyArrow or FastParquet
- **YAML**: Save and load YAML files with recursive logic and **strict key validation** to prevent duplicate entries in configuration files.

## Installation

```bash
pip install dsr-files
```

## Requirements

- **Python**: >= 3.10
- **PyYAML**: >= 6.0.2
- **Pandas**: Required for CSV and Excel operations
- **Joblib**: Required for object serialization

### Optional Dependencies

For Excel support:

```bash
pip install dsr-files[excel]
```

For PDF support:

```bash
pip install dsr-files[pdf]
```

## Development Installation

```bash
pip install -e ".[dev,excel,pdf]"
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

### Excel Operations

```python
from dsr_files import save_excel, load_excel, ExcelSheetConfig
from pathlib import Path
import pandas as pd

sales = pd.DataFrame({"region": ["NA", "EU"], "revenue": [120, 95]})
costs = pd.DataFrame({"region": ["NA", "EU"], "cost": [80, 70]})

# Save multi-sheet workbook
save_excel(
 [
  ExcelSheetConfig(data=sales, sheet_name="Sales"),
  ExcelSheetConfig(data=costs, sheet_name="Costs"),
 ],
 Path("."),
 "report",
)

# Load first sheet
df = load_excel(Path("report.xlsx"))
```

### PDF Operations (Interactive Reports)

```python
from dsr_files import PDFDocument, PageConfiguration, PageSize, PageOrientation, PageColors
from pathlib import Path

# Configure document style
config = PageConfiguration(
    page_size=PageSize.LETTER,
    orientation=PageOrientation.PORTRAIT,
    colors=PageColors(page_num="#000000", title="#444444"),
    margins=(0.07, 0.93, 0.90, 0.10)
)

doc = PDFDocument("Audit Report", config)
page = doc.create_new_page("Summary")
# ... Add Matplotlib content to page.fig ...

doc.render_table_of_contents()
doc.save(Path("."), "audit_report")
```

### PARQUET Operations

```python
from dsr_files import save_parquet, load_parquet
import pandas as pd
from pathlib import Path

df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})

# Save to Parquet
save_parquet(df, Path("."), "data", engine="pyarrow")

# Load from Parquet
df = load_parquet(Path("data.parquet"))
```

### YAML Operations

```python
from dsr_files import save_yaml, load_yaml
from pathlib import Path

data = {"project": "dsr-orchestrator", "steps": ["ingest", "analyze"]}

# Save to YAML
save_yaml(data, Path("config.yaml"))

# Load from YAML using the new UniqueKeyLoader
# This will raise a ConstructorError if duplicate keys are detected,
# protecting your project settings from conflicting edits.
data = load_yaml(Path("config.yaml"))
```

## Testing

```bash
pytest tests/
pytest tests/ --cov=src/dsr_files
```

## License

MIT

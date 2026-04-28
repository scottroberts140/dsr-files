# dsr-files

[![PyPI version](https://img.shields.io/pypi/v/dsr-files.svg?cacheSeconds=300)](https://pypi.org/project/dsr-files/)
[![Python versions](https://img.shields.io/pypi/pyversions/dsr-files.svg?cacheSeconds=300&v=3)](https://pypi.org/project/dsr-files/)
[![License](https://img.shields.io/pypi/l/dsr-files.svg?cacheSeconds=300)](https://pypi.org/project/dsr-files/)
[![Changelog](https://img.shields.io/badge/changelog-available-blue.svg)](https://github.com/scottroberts140/dsr-files/releases)

File handling library for creating, saving, and loading various file types (CSV, JSON, JOBLIB, PDF, PARQUET).

**Version 3.1.1**: Standardized handler path typing around a shared **PathLike** alias for local, cloud, and string inputs, and updated package version reporting to use installed distribution metadata with a safe fallback.

**Unreleased update**: Save handlers now remove an existing target file before writing a replacement, improving overwrite reliability across repeated exports.

## Features

- **CSV**: Read and write CSV files with pandas.
- **JSON**: Save and load JSON data with recursive sanitization; now supports `.jsonl` (JSON Lines) for large datasets.
- **JOBLIB**: Serialize Python objects and ML models with joblib.
- **Excel**: Save and load Excel workbooks; supports .xlsx, .xls, .xlsm, and .xlsb formats.
- **PDF**: Generate interactive, indexed audit reports with Matplotlib and ReportLab.
- **PARQUET**: High-performance columnar storage; now supports .pq as a valid logical extension.
- **YAML**: Save and load YAML files with recursive logic and **strict key validation** to prevent duplicate entries in configuration files.
- **FileType Utilities**: The FileType enum now includes `is_valid_extension()` for performing logical consistency checks between file names and formats without requiring filesystem access. This is ideal for pre-validating configuration files in ML pipelines.

## Installation

```bash
pip install dsr-files
```

## Requirements

- **Python**: >= 3.10
- **PyYAML**: >= 6.0.2
- **Pandas**: Required for CSV and Excel operations
- **Joblib**: Required for object serialization
- **dsr-utils**: >= 1.6.0
- **cloudpathlib**: Required for `AnyPath` and `CloudPath` support

### Optional Dependencies

For Excel support:

```bash
pip install dsr-files[excel]
```

For PDF support:

```bash
pip install dsr-files[pdf]
```

For full cloud support (S3, GCS, Azure)

```bash
pip install cloudpathlib[all]
```

## Development Installation

```bash
pip install -e ".[dev,excel,pdf]"
```

## Developer Transparency

**Note on Parameter Registry**: The list of valid parameters for each format can be found in `dsr_files/resources/params.yaml`. This file serves as the "ground truth" for all `safe_call` filtering operations.

## Usage

## Universal Parameter Filtering

All handlers now support `safe_call=True`. This leverages `dsr-utils` to filter out incompatible keyword arguments that would otherwise cause `TypeErrors` in underlying engines like `pyarrow` or `fastparquet`.

Any parameters that are not compatible with the specific engine are returned in a `rejected` dictionary for debugging and audit logging.

The library no longer relies solely on reflection, but uses a "ground truth" registry for engine-specific safety.

### CSV Operations

```python
from dsr_files import save_csv, load_csv, create_csv
import pandas as pd
from pathlib import Path

# Create from dictionary
data = {"name": ["Alice", "Bob"], "age": [30, 25]}
df = create_csv(data)

# Save to CSV
full_path, rejected = save_csv(df, Path("."), "data")

# Using safe_call
full_path, rejected = save_csv(df, Path("."), "data", safe_call=True, float_format="%.2f")

# Load from CSV
df, rejected = load_csv(Path("data.csv"))
```

### JSON Operations

```python
from dsr_files import save_json, load_json
from pathlib import Path

data = {"key": "value", "number": 42}

# Save to JSON
full_path, rejected = save_json(data, Path("."), "data")

# Load from JSON
data, rejected = load_json(Path("data.json"))
```

### JOBLIB Operations

```python
from dsr_files import save_joblib, load_joblib
from pathlib import Path

# Save any Python object
model = {"weights": [1, 2, 3], "config": {}}
full_path, rejected = save_joblib(model, Path("."), "model")

# Load from JOBLIB
model, rejected = load_joblib(Path("model.joblib"))
```

### Excel Operations

```python
from dsr_files import save_excel, load_excel, ExcelSheetConfig
from pathlib import Path
import pandas as pd

sales = pd.DataFrame({"region": ["NA", "EU"], "revenue": [120, 95]})
costs = pd.DataFrame({"region": ["NA", "EU"], "cost": [80, 70]})

# Save multi-sheet workbook
full_path, rejected = save_excel(
 [
  ExcelSheetConfig(data=sales, sheet_name="Sales"),
  ExcelSheetConfig(data=costs, sheet_name="Costs"),
 ],
 Path("."),
 "report",
)

# Load first sheet
df, rejected = load_excel(Path("report.xlsx"))
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
full_path, rejected = doc.save(Path("."), "audit_report")
```

### PARQUET Operations

```python
from dsr_files import save_parquet, load_parquet
import pandas as pd
from pathlib import Path

df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})

# Save to Parquet
full_path, rejected = save_parquet(df, Path("."), "data", engine="pyarrow")

# Load from Parquet
df, rejected = load_parquet(Path("data.parquet"))
```

### YAML Operations

```python
from dsr_files import save_yaml, load_yaml
from pathlib import Path

data = {"project": "dsr-orchestrator", "steps": ["ingest", "analyze"]}

# Save to YAML
full_path, rejected = save_yaml(data, Path("config.yaml"))

# Load from YAML using the new UniqueKeyLoader
# This will raise a ConstructorError if duplicate keys are detected,
# protecting your project settings from conflicting edits.
data, rejected = load_yaml(Path("config.yaml"))
```

## Cloud-Native Pathing

`dsr-files` now supports both local and cloud filesystems (S3, GCS, Azure) out of the box using `cloudpathlib`. You can pass raw URI strings, `pathlib.Path` objects, or `CloudPath` objects directly to any handler.

```python
from dsr_files import save_csv

# Local path
full_path, rejected = save_csv(df, "./data", "local_audit") 

# Cloud path (requires cloudpathlib[s3])
full_path, rejected = save_csv(df, "s3://my-bucket/audits", "remote_audit")
```

## Testing

```bash
pytest tests/
pytest tests/ --cov=src/dsr_files
```

## License

MIT

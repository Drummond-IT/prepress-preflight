# prepress-preflight

# Prepress Preflight

> Scan PDFs for print-readiness issues â€” RGB images, low resolution, missing bleeds, wrong black buildup. Auto-fix common issues.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Ghostscript](https://img.shields.io/badge/Ghostscript-Optional-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

## The Problem

95% of files received from designers aren't print-ready. Prepress operators manually fix: wrong color space, missing bleeds, low-res images, wrong black buildup. Every. Single. Time.

## The Solution

```bash
# Check a PDF
prepress-preflight check design.pdf

# Auto-fix common issues
prepress-preflight fix design.pdf -o design_printready.pdf

# Get a print checklist
prepress-preflight checklist design.pdf
```

## Quick Start

```bash
git clone https://github.com/darshd9941/prepress-preflight.git
cd prepress-preflight
pip install -e .
```

Optional: install Ghostscript and pikepdf for full analysis:
```bash
pip install pikepdf
```

## Features

- Detect RGB images (should be CMYK)
- Flag low-resolution images (below 300 DPI)
- Verify bleeds (0.125in / 3mm)
- Check black buildup (rich black vs default)
- Auto-fix: RGBâ†’CMYK conversion via Ghostscript
- Generate print-readiness checklists

## License

MIT License â€” see [LICENSE](LICENSE) for details.


## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Clone the Repository

```bash
git clone https://github.com/darshd9941/prepress-preflight.git
cd prepress-preflight
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit .env and add your API keys:
   ```bash
   # Required for Claude vision features
   ANTHROPIC_API_KEY=your-api-key-here
   ```

## Usage

### Web App (if applicable)

```bash
streamlit run app.py
```

### CLI Usage

```bash
python main.py --help
```

### Python API

```python
from module import MainClass

# Initialize the tool
tool = MainClass()

# Use the tool
result = tool.process("input")
print(result)
```

## Configuration

- .env - Environment variables (API keys, settings)
- config.yaml - Configuration file (if applicable)

## Examples

See the examples/ directory for detailed usage examples.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

See LICENSE file for details.

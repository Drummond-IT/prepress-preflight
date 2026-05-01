# Prepress Preflight

> Scan PDFs for print-readiness issues — RGB images, low resolution, missing bleeds, wrong black buildup. Auto-fix common issues.

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
- Auto-fix: RGB→CMYK conversion via Ghostscript
- Generate print-readiness checklists

## License

MIT License — see [LICENSE](LICENSE) for details.

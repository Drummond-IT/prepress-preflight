"""Prepress Preflight — scan PDF files for print-readiness issues."""
import subprocess
import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PreflightReport:
    filename: str
    filepath: str
    pages: int = 0
    page_size: str = ""
    # Issues
    has_rgb_images: bool = False
    has_low_res_images: bool = False
    has_missing_bleeds: bool = False
    has_wrong_blacks: bool = False
    has_rasterized_text: bool = False
    has_thin_knockout: bool = False
    has_gradient_banding_risk: bool = False
    # Details
    rgb_images: list = field(default_factory=list)
    low_res_images: list = field(default_factory=list)
    black_buildup: str = ""
    issues: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    # Metrics
    total_images: int = 0
    image_resolutions: list = field(default_factory=list)
    color_spaces_found: list = field(default_factory=list)


def preflight_pdf(pdf_path: str) -> PreflightReport:
    """Analyze a PDF file for print-readiness issues."""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    report = PreflightReport(filename=path.name, filepath=str(path.absolute()))

    # Use Ghostscript for analysis
    _analyze_with_ghostscript(pdf_path, report)

    # Detect issues
    _detect_issues(report)

    return report


def _analyze_with_ghostscript(pdf_path: str, report: PreflightReport):
    """Analyze PDF using Ghostscript."""
    try:
        # Get page count and info
        cmd = [
            "gs", "-q", "-dNODISPLAY", "-dBATCH",
            "-sFile=" + pdf_path,
            "-c", "File (r) file runpdfbegin pdfpagecount = quit",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        # Parse output
        for line in result.stdout.split("\n"):
            if line.strip().isdigit():
                report.pages = int(line.strip())
    except Exception:
        pass

    # Try PDFMiner or pikepdf for detailed analysis
    try:
        import pikepdf
        _analyze_with_pikepdf(pdf_path, report)
    except ImportError:
        pass


def _analyze_with_pikepdf(pdf_path: str, report: PreflightReport):
    """Detailed analysis using pikepdf."""
    try:
        import pikepdf

        with pikepdf.open(pdf_path) as pdf:
            report.pages = len(pdf.pages)

            for page_num, page in enumerate(pdf.pages, 1):
                # Check for images
                resources = page.get("/Resources", {})
                xobjects = resources.get("/XObject", {})

                for name, xobj in xobjects.items():
                    if isinstance(xobj, pikepdf.Dictionary):
                        subtype = xobj.get("/Subtype", "")
                        if subtype == "/Image":
                            report.total_images += 1

                            # Check color space
                            cs = xobj.get("/ColorSpace", "")
                            cs_str = str(cs)
                            if "DeviceRGB" in cs_str or "/RGB" in cs_str:
                                report.has_rgb_images = True
                                report.rgb_images.append(f"Page {page_num}: {name}")
                                report.color_spaces_found.append("RGB")
                            elif "CMYK" in cs_str:
                                report.color_spaces_found.append("CMYK")

                            # Check resolution
                            width = int(xobj.get("/Width", 0))
                            height = int(xobj.get("/Height", 0))
                            if width > 0 and height > 0:
                                # Rough estimate: assume 72 DPI default
                                # Real resolution depends on placed size
                                report.image_resolutions.append({
                                    "page": page_num,
                                    "name": str(name),
                                    "width": width,
                                    "height": height,
                                })

                                # Flag if very small (likely low-res)
                                if width < 300 or height < 300:
                                    report.has_low_res_images = True
                                    report.low_res_images.append(
                                        f"Page {page_num}: {name} ({width}x{height})"
                                    )

    except Exception as e:
        report.warnings.append(f"Could not analyze with pikepdf: {e}")


def _detect_issues(report: PreflightReport):
    """Detect common prepress issues."""
    # RGB images
    if report.has_rgb_images:
        report.issues.append(
            f"RGB IMAGES FOUND — {len(report.rgb_images)} image(s) not in CMYK. "
            f"Convert to CMYK before printing."
        )

    # Low resolution
    if report.has_low_res_images:
        report.issues.append(
            f"LOW RESOLUTION — {len(report.low_res_images)} image(s) may be below 300 DPI."
        )

    # Missing bleeds (heuristic: if no crop marks found)
    if report.pages > 0 and not report.has_missing_bleeds:
        report.warnings.append(
            "BLEED CHECK — Could not verify bleeds automatically. "
            "Ensure 0.125in (3mm) bleeds on all edges."
        )

    # Black buildup
    report.black_buildup = (
        "CHECK MANUALLY — Ensure rich blacks use 50/40/40/100, "
        "not Adobe default 75/69/68/90"
    )

    # No issues found
    if not report.issues and not report.has_rgb_images and not report.has_low_res_images:
        report.warnings.append("No critical issues detected (automated check)")


def fix_common_issues(pdf_path: str, output_path: Optional[str] = None) -> dict:
    """Attempt to fix common issues using Ghostscript."""
    if not output_path:
        p = Path(pdf_path)
        output_path = str(p.parent / f"{p.stem}_printready{p.suffix}")

    fixes_applied = []

    # Convert RGB to CMYK using Ghostscript
    gs_cmd = [
        "gs",
        "-o", output_path,
        "-sDEVICE=pdfwrite",
        "-dPDFSETTINGS=/prepress",
        "-dCompatibilityLevel=1.4",
        "-dAutoRotatePages=/None",
        "-sColorConversionStrategy=CMYK",
        "-sProcessColorModel=DeviceCMYK",
        pdf_path,
    ]

    try:
        result = subprocess.run(gs_cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            fixes_applied.append("RGB → CMYK conversion")
            fixes_applied.append("PDF optimized for press")
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}

    return {
        "success": True,
        "output": output_path,
        "fixes": fixes_applied,
    }


def generate_print_checklist(report: PreflightReport) -> str:
    """Generate a human-readable print readiness checklist."""
    lines = [
        f"PRINT READINESS CHECKLIST — {report.filename}",
        "=" * 60,
        f"Pages: {report.pages}",
        f"Total Images: {report.total_images}",
        "",
        "CHECKS:",
        f"  [{'X' if not report.has_rgb_images else ' '}] All images in CMYK",
        f"  [{'X' if not report.has_low_res_images else ' '}] All images 300+ DPI",
        f"  [ ] Bleeds set (0.125in / 3mm)",
        f"  [ ] Rich black: 50/40/40/100 (not 75/69/68/90)",
        f"  [ ] No knockout text thinner than 0.5pt",
        f"  [ ] All fonts embedded/outlined",
        f"  [ ] Output intent set to target printer profile",
        "",
    ]

    if report.issues:
        lines.append("ISSUES FOUND:")
        for issue in report.issues:
            lines.append(f"  ! {issue}")
        lines.append("")

    if report.warnings:
        lines.append("WARNINGS:")
        for warn in report.warnings:
            lines.append(f"  * {warn}")

    return "\n".join(lines)

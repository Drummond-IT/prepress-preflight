"""CLI for prepress preflight checks."""
import sys
import click

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from rich.console import Console
from rich.table import Table
from .analyzer import preflight_pdf, fix_common_issues, generate_print_checklist

console = Console(force_terminal=True)


@click.group()
@click.version_option(package_name="prepress-preflight")
def cli():
    """Prepress Preflight — check if your PDFs are print-ready."""
    pass


@cli.command()
@click.argument("pdf_path")
def check(pdf_path):
    """Analyze a PDF for print-readiness issues."""
    console.print(f"\nAnalyzing [cyan]{pdf_path}[/]...")
    report = preflight_pdf(pdf_path)

    table = Table(title=f"Preflight Report — {report.filename}", show_lines=True)
    table.add_column("Check", style="bold")
    table.add_column("Status")
    table.add_column("Details")

    table.add_row("Pages", str(report.pages), "")
    table.add_row("Images", str(report.total_images), "")
    table.add_row("RGB Images", "FAIL" if report.has_rgb_images else "OK",
                   f"{len(report.rgb_images)} found" if report.rgb_images else "")
    table.add_row("Low Res Images", "FAIL" if report.has_low_res_images else "OK",
                   f"{len(report.low_res_images)} found" if report.low_res_images else "")

    console.print(table)

    # Print checklist
    console.print("\n" + generate_print_checklist(report))


@cli.command()
@click.argument("pdf_path")
@click.option("-o", "--output", default=None, help="Output path for fixed PDF")
def fix(pdf_path, output):
    """Attempt to fix common prepress issues."""
    console.print(f"\nFixing [cyan]{pdf_path}[/]...")
    result = fix_common_issues(pdf_path, output)

    if result["success"]:
        console.print(f"[green]OK[/] Fixed PDF saved to: {result['output']}")
        for fix in result["fixes"]:
            console.print(f"  - {fix}")
    else:
        console.print(f"[red]ERROR:[/] {result['error']}")


@cli.command()
@click.argument("pdf_path")
def checklist(pdf_path):
    """Print a print-readiness checklist."""
    report = preflight_pdf(pdf_path)
    console.print(generate_print_checklist(report))


if __name__ == "__main__":
    cli()

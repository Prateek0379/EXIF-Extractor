import click
from pathlib import Path
from exif_extractor.extractor import EXIFExtractor
from exif_extractor.reporter import save_json, save_csv, print_rich_table
from exif_extractor.gps import generate_map
from rich.console import Console

console = Console()

SUPPORTED = {".jpg", ".jpeg", ".tiff", ".tif", ".png", ".heic"}


@click.group()
def cli():
    """EXIF Metadata Extractor — Forensics & Analysis Tool"""
    pass


@cli.command()
@click.argument("image_path")
@click.option("--json", "json_out", default=None, help="Save JSON to file")
@click.option("--quiet", is_flag=True, help="Suppress table output")
def analyze(image_path, json_out, quiet):
    """Analyze a single image file."""
    extractor = EXIFExtractor(image_path)
    metadata = extractor.extract()

    if not quiet:
        print_rich_table(metadata)

    if json_out:
        save_json(metadata, json_out)


@cli.command()
@click.argument("directory")
@click.option("--csv", "csv_out", default="report.csv", help="CSV output path")
@click.option("--map", "map_out", default="map.html", help="HTML map output path")
@click.option("--json-dir", default=None, help="Directory to save per-image JSON")
def batch(directory, csv_out, map_out, json_dir):
    """Batch-process all images in a directory."""
    dir_path = Path(directory)
    images = [f for f in dir_path.rglob("*") if f.suffix.lower() in SUPPORTED]

    if not images:
        console.print("[red]No supported images found.[/]")
        return

    console.print(f"[blue]Found {len(images)} images.[/]")
    results = []

    for img in images:
        try:
            extractor = EXIFExtractor(str(img))
            meta = extractor.extract()
            results.append(meta)
            console.print(f"  [green]✓[/] {img.name}")

            if json_dir:
                Path(json_dir).mkdir(parents=True, exist_ok=True)
                save_json(meta, f"{json_dir}/{img.stem}.json")
        except Exception as e:
            console.print(f"  [red]✗[/] {img.name}: {e}")

    save_csv(results, csv_out)
    generate_map(results, map_out)
    console.print(f"\n[bold green]Done:[/] {len(results)} images processed.")


if __name__ == "__main__":
    cli()
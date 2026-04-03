import json
import csv
import pandas as pd
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box


console = Console()


def save_json(metadata: dict, output_path: str):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, default=str)
    console.print(f"[green]JSON saved:[/] {output_path}")


def save_csv(metadata_list: list, output_path: str):
    rows = []
    for m in metadata_list:
        rows.append({
            "filename": m["file"]["filename"],
            "sha256": m["file"]["sha256"],
            "camera_make": m["camera"]["make"],
            "camera_model": m["camera"]["model"],
            "iso": m["exposure"]["iso"],
            "aperture": m["exposure"]["aperture"],
            "shutter": m["exposure"]["shutter_speed"],
            "datetime_original": m["timestamps"]["datetime_original"],
            "latitude": m["gps"].get("latitude"),
            "longitude": m["gps"].get("longitude"),
            "editing_detected": m["forensics"]["editing_detected"],
            "flags": "; ".join(m["forensics"]["flags"]),
        })
    pd.DataFrame(rows).to_csv(output_path, index=False)
    console.print(f"[green]CSV saved:[/] {output_path}")


def print_rich_table(metadata: dict):
    table = Table(title=metadata["file"]["filename"], box=box.ROUNDED, highlight=True)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    for section, values in metadata.items():
        if isinstance(values, dict):
            for k, v in values.items():
                table.add_row(f"{section}.{k}", str(v))

    console.print(table)

    flags = metadata["forensics"]["flags"]
    if flags:
        console.print("\n[bold red]Forensic Flags:[/]")
        for flag in flags:
            console.print(f"  [yellow]⚠[/] {flag}")
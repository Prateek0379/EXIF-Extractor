# EXIF Metadata Extractor

A Python-based forensic tool for extracting and analyzing EXIF metadata from images. Designed for digital forensics, OSINT investigations, and photojournalism verification.

## Features

- Extracts camera make/model, lens, GPS coordinates, timestamps, and exposure settings
- Detects forensic anomalies — editing software traces, timestamp mismatches
- Generates SHA-256 hash of every image for chain of custody
- Exports results as JSON, CSV, or an interactive HTML map
- Batch processes entire directories
- Automatically opens Google Maps to the exact photo location
- Clean terminal output with colour-coded forensic flags

## Installation
```bash
git clone https://github.com/Prateek0379/exif-extractor.git
cd exif-extractor
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Usage

**Analyze a single image:**
```bash
exif-extract analyze photo.jpg
```

**Save output as JSON:**
```bash
exif-extract analyze photo.jpg --json output.json
```

**Batch process a folder:**
```bash
exif-extract batch ./photos/ --csv report.csv --map locations.html
```

## Technologies Used

| Library | Purpose |
|---|---|
| `Pillow` | Image reading and EXIF decoding |
| `piexif` | Deep EXIF tag parsing |
| `exifread` | Raw tag extraction |
| `folium` | Interactive GPS map generation |
| `pandas` | CSV batch export |
| `rich` | Formatted terminal output |
| `click` | CLI framework |

## Use Cases

- Digital forensics and evidence analysis
- OSINT and geolocation investigations
- Photojournalism authenticity verification
- Wildlife camera trap data processing
- Personal photo metadata auditing

## Forensics Capabilities

- SHA-256 hashing for chain of custody
- Editing software detection (Photoshop, GIMP, Lightroom etc.)
- Timestamp mismatch detection between original and modified dates
- GPS coordinate extraction with direct Google Maps link
- Missing metadata flagging

## Running Tests
```bash
pytest tests/ -v
```

## Author

Prateek Kumar — [github.com/Prateek0379](https://github.com/Prateek0379)

## License

MIT License
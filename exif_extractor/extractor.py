from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif
import exifread
import hashlib
import os
from pathlib import Path
from datetime import datetime


class EXIFExtractor:
    """Extract and parse EXIF metadata from images for forensic analysis."""

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".tiff", ".tif", ".png", ".heic", ".webp"}

    def __init__(self, image_path: str):
        self.path = Path(image_path)
        self._validate()
        self.raw_data = {}
        self.metadata = {}

    def _validate(self):
        if not self.path.exists():
            raise FileNotFoundError(f"Image not found: {self.path}")
        if self.path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {self.path.suffix}")

    def extract(self) -> dict:
        """Run full extraction pipeline and return structured metadata."""
        self.metadata = {
            "file": self._file_info(),
            "camera": self._camera_info(),
            "exposure": self._exposure_info(),
            "gps": self._gps_info(),
            "timestamps": self._timestamp_info(),
            "forensics": self._forensics_info(),
        }
        return self.metadata

    def _file_info(self) -> dict:
        stat = self.path.stat()
        with open(self.path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return {
            "filename": self.path.name,
            "path": str(self.path.resolve()),
            "size_bytes": stat.st_size,
            "size_human": f"{stat.st_size / 1024:.1f} KB",
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "sha256": file_hash,
        }

    def _get_exif_data(self) -> dict:
        """Extract raw EXIF via Pillow."""
        if self.raw_data:
            return self.raw_data
        try:
            img = Image.open(self.path)
            exif_raw = img._getexif()
            if exif_raw:
                self.raw_data = {
                    TAGS.get(tag, tag): value
                    for tag, value in exif_raw.items()
                }
        except Exception:
            self.raw_data = {}
        return self.raw_data

    def _camera_info(self) -> dict:
        data = self._get_exif_data()
        return {
            "make": data.get("Make", "Unknown"),
            "model": data.get("Model", "Unknown"),
            "software": data.get("Software", "Unknown"),
            "lens_model": data.get("LensModel", "Unknown"),
            "orientation": data.get("Orientation", "Unknown"),
        }

    def _exposure_info(self) -> dict:
        data = self._get_exif_data()

        def to_float(val):
            try:
                return float(val.numerator) / float(val.denominator)
            except Exception:
                return val

        iso = data.get("ISOSpeedRatings")
        aperture = to_float(data.get("FNumber", 0))
        shutter = to_float(data.get("ExposureTime", 0))
        focal = to_float(data.get("FocalLength", 0))

        return {
            "iso": iso,
            "aperture": f"f/{aperture:.1f}" if aperture else "Unknown",
            "shutter_speed": f"1/{int(1/shutter)}s" if shutter else "Unknown",
            "focal_length": f"{focal:.0f}mm" if focal else "Unknown",
            "flash": data.get("Flash"),
            "white_balance": data.get("WhiteBalance"),
            "exposure_mode": data.get("ExposureMode"),
        }

    def _gps_info(self) -> dict:
        data = self._get_exif_data()
        gps_raw = data.get("GPSInfo")
        if not gps_raw:
            return {"available": False}

        gps_tags = {GPSTAGS.get(k, k): v for k, v in gps_raw.items()}

        def convert_dms(dms, ref):
            d, m, s = [float(x.numerator) / float(x.denominator) for x in dms]
            decimal = d + m / 60 + s / 3600
            return -decimal if ref in ("S", "W") else decimal

        try:
            lat = convert_dms(gps_tags["GPSLatitude"], gps_tags["GPSLatitudeRef"])
            lon = convert_dms(gps_tags["GPSLongitude"], gps_tags["GPSLongitudeRef"])
            alt = gps_tags.get("GPSAltitude")
            alt_val = float(alt.numerator) / float(alt.denominator) if alt else None

            return {
                "available": True,
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "altitude_m": round(alt_val, 1) if alt_val else None,
                "maps_url": f"https://maps.google.com/?q={lat},{lon}",
            }
        except (KeyError, TypeError, ZeroDivisionError):
            return {"available": False, "error": "Malformed GPS data"}

    def _timestamp_info(self) -> dict:
        data = self._get_exif_data()
        return {
            "datetime_original": data.get("DateTimeOriginal"),
            "datetime_digitized": data.get("DateTimeDigitized"),
            "datetime_modified": data.get("DateTime"),
            "gps_timestamp": data.get("GPSInfo", {}).get(7),  # GPS time UTC
        }

    def _forensics_info(self) -> dict:
        """Flag forensically relevant anomalies."""
        data = self._get_exif_data()
        flags = []

        # Check for software editing traces
        software = str(data.get("Software", "")).lower()
        editing_tools = ["photoshop", "gimp", "lightroom", "affinity", "snapseed"]
        for tool in editing_tools:
            if tool in software:
                flags.append(f"Edited with {software}")

        # Timestamp mismatch detection
        orig = data.get("DateTimeOriginal")
        modified = data.get("DateTime")
        if orig and modified and orig != modified:
            flags.append(f"Timestamp mismatch: original={orig}, modified={modified}")

        # Missing GPS when expected
        if not data.get("GPSInfo"):
            flags.append("No GPS data embedded")

        return {
            "flags": flags,
            "has_thumbnail": "thumbnail" in str(data).lower(),
            "software": data.get("Software", "None"),
            "editing_detected": any(
                t in str(data.get("Software", "")).lower()
                for t in editing_tools
            ),
        }
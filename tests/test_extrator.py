import pytest
from pathlib import Path
from exif_extractor.extractor import EXIFExtractor

SAMPLE = "tests/sample_images/sample_jpeg.jpeg"  # Add a real EXIF-tagged image here


def test_file_info():
    ext = EXIFExtractor(SAMPLE)
    meta = ext.extract()
    assert "filename" in meta["file"]
    assert "sha256" in meta["file"]
    assert len(meta["file"]["sha256"]) == 64  # SHA-256 is 64 hex chars


def test_camera_info():
    ext = EXIFExtractor(SAMPLE)
    meta = ext.extract()
    assert "make" in meta["camera"]
    assert "model" in meta["camera"]


def test_gps_structure():
    ext = EXIFExtractor(SAMPLE)
    meta = ext.extract()
    gps = meta["gps"]
    assert "available" in gps
    if gps["available"]:
        assert -90 <= gps["latitude"] <= 90
        assert -180 <= gps["longitude"] <= 180


def test_forensics_flags():
    ext = EXIFExtractor(SAMPLE)
    meta = ext.extract()
    assert isinstance(meta["forensics"]["flags"], list)


def test_invalid_path():
    with pytest.raises(FileNotFoundError):
        EXIFExtractor("nonexistent.jpg")
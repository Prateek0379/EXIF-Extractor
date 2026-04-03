from setuptools import setup, find_packages

setup(
    name="exif-extractor",
    version="1.0.0",
    author="Your Name",
    description="Forensic EXIF metadata extractor for images",
    packages=find_packages(),
    install_requires=[
        "Pillow>=10.0.0",
        "piexif>=1.1.3",
        "exifread>=3.0.0",
        "folium>=0.14.0",
        "pandas>=2.0.0",
        "rich>=13.0.0",
        "click>=8.1.0",
    ],
    entry_points={
        "console_scripts": ["exif-extract=exif_extractor.cli:cli"]
    },
    python_requires=">=3.9",
)
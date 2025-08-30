"""Resize JPEG images to 60x80 pixels.

The script processes all ``.jpg`` and ``.jpeg`` files in an input
folder and writes the resized versions to an output folder. The output
folder defaults to the input folder if not specified.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

WIDTH = 60
HEIGHT = 80


def resize_image(path: Path, output_dir: Path) -> None:
    """Resize a single image and save it to ``output_dir``."""
    with Image.open(path) as img:
        resized = img.resize((WIDTH, HEIGHT))
        output_path = output_dir / path.name
        resized.save(output_path, format="JPEG")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resize JPEG images to 60x80 pixels."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Directory containing JPEG images to resize.",
    )
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        help="Directory to write resized images. Defaults to the input directory.",
    )
    args = parser.parse_args()

    input_dir = args.input
    output_dir = args.output or input_dir

    if not input_dir.is_dir():
        raise SystemExit(f"Input path {input_dir} is not a directory")
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in input_dir.iterdir():
        if path.suffix.lower() in {".jpg", ".jpeg"} and path.is_file():
            resize_image(path, output_dir)


if __name__ == "__main__":
    main()

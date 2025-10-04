"""Process source monster training images: convert to PNG, resize, and replace generated images.

This script:
1. Scans assets/line_art_cropped/monsters for source training images
2. Converts all to PNG format
3. Resizes to 80x60 (thumbnail) and 320x240 (full) to match generated images
4. Matches filenames with generated images in data/images/monsters/golden_age/
5. Replaces generated images with processed originals where names match
"""
import os
from pathlib import Path
from PIL import Image
import re


def sanitize_filename(name: str) -> str:
    """Convert image filename to match monster naming convention."""
    safe = name.lower().replace(' ', '_').replace("'", '').replace('"', '')
    safe = ''.join(c for c in safe if c.isalnum() or c == '_')
    return safe


def process_source_images(
    source_dir: str = "assets/line_art_cropped/monsters",
    output_dir: str = "data/images/monsters/golden_age",
    thumb_size: tuple = (80, 60),
    full_size: tuple = (320, 240)
):
    """Process all source images and replace generated ones."""
    source_path = Path(source_dir)
    output_path = Path(output_dir)

    if not source_path.exists():
        print(f"Source directory not found: {source_dir}")
        return

    if not output_path.exists():
        print(f"Output directory not found: {output_dir}")
        return

    source_files = list(source_path.glob("*.*"))
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}

    processed = 0
    replaced = 0
    skipped = 0

    for source_file in source_files:
        if source_file.suffix.lower() not in image_extensions:
            continue

        stem = source_file.stem
        sanitized = sanitize_filename(stem)

        thumb_target = output_path / f"{sanitized}.png"
        full_target = output_path / f"{sanitized}_full.png"

        if not thumb_target.exists():
            skipped += 1
            print(f"[SKIP] No generated match for: {source_file.name}")
            continue

        try:
            img = Image.open(source_file)

            if img.mode != 'RGB':
                img = img.convert('RGB')

            full_img = img.resize(full_size, Image.Resampling.LANCZOS)
            thumb_img = img.resize(thumb_size, Image.Resampling.LANCZOS)

            full_img.save(full_target, 'PNG')
            thumb_img.save(thumb_target, 'PNG')

            processed += 1
            replaced += 1
            print(f"[REPLACE] {source_file.name} -> {sanitized}.png")

        except Exception as e:
            print(f"[ERROR] Failed to process {source_file.name}: {e}")

    print(f"\n\nSummary:")
    print(f"  Processed: {processed}")
    print(f"  Replaced: {replaced}")
    print(f"  Skipped (no match): {skipped}")
    print(f"  Total source files: {len([f for f in source_files if f.suffix.lower() in image_extensions])}")


if __name__ == "__main__":
    process_source_images()
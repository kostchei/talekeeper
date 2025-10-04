# Manual Monster Image Replacement Guide

When you find new source images or need to manually replace AI-generated monster images with original training images, use this guide.

## Quick Reference: One-Line Python Command

```bash
python -c "from PIL import Image; img = Image.open('SOURCE_IMAGE_PATH').convert('RGB'); img.resize((320, 240), Image.Resampling.LANCZOS).save('data/images/monsters/golden_age/MONSTER_NAME_full.png'); img.resize((80, 60), Image.Resampling.LANCZOS).save('data/images/monsters/golden_age/MONSTER_NAME.png'); print('Replaced MONSTER_NAME')"
```

Replace:
- `SOURCE_IMAGE_PATH` - Path to your source image (e.g., `assets/line_art_cropped/monsters/duegar.jpg`)
- `MONSTER_NAME` - Sanitized monster name (lowercase, underscores, no spaces - e.g., `duergar`, `winged_kobold`)

## Image Specifications

- **Thumbnail**: 80x60 pixels (for monster cards)
- **Full Resolution**: 320x240 pixels (detail view)
- **Format**: PNG (converted from any source format)
- **Color Mode**: RGB (even for black & white line art)
- **Resampling**: LANCZOS (high quality downscaling)

## Common Scenarios

### Scenario 1: Source Image Has Different Spelling

**Example**: Database has `Duergar` but source file is `duegar.jpg`

```bash
python -c "from PIL import Image; img = Image.open('assets/line_art_cropped/monsters/duegar.jpg').convert('RGB'); img.resize((320, 240), Image.Resampling.LANCZOS).save('data/images/monsters/golden_age/duergar_full.png'); img.resize((80, 60), Image.Resampling.LANCZOS).save('data/images/monsters/golden_age/duergar.png'); print('Replaced duergar with duegar.jpg')"
```

### Scenario 2: Generic Source for Specific Monster

**Example**: Source file is `kobold.jpg` but monster is `Winged Kobold`

```bash
python -c "from PIL import Image; img = Image.open('assets/line_art_cropped/monsters/kobold.jpg').convert('RGB'); img.resize((320, 240), Image.Resampling.LANCZOS).save('data/images/monsters/golden_age/winged_kobold_full.png'); img.resize((80, 60), Image.Resampling.LANCZOS).save('data/images/monsters/golden_age/winged_kobold.png'); print('Replaced winged_kobold with kobold.jpg')"
```

### Scenario 3: New Image Downloaded

**Example**: Downloaded `guard.png` for Guard monster

```bash
python -c "from PIL import Image; img = Image.open('assets/line_art_cropped/monsters/guard.png').convert('RGB'); img.resize((320, 240), Image.Resampling.LANCZOS).save('data/images/monsters/golden_age/guard_full.png'); img.resize((80, 60), Image.Resampling.LANCZOS).save('data/images/monsters/golden_age/guard.png'); print('Replaced guard')"
```

## Finding the Correct Monster Name

Monster names in the output directory are sanitized:
- Lowercase
- Spaces replaced with underscores
- No apostrophes or special characters

**Examples:**
- `Ancient Red Dragon` → `ancient_red_dragon`
- `Kuo-toa Whip` → `kuotoa_whip`
- `Mind Flayer` → `mind_flayer`

### Check What Name is Used:

```bash
# Find generated image for a monster
ls data/images/monsters/golden_age/ | grep -i PARTIAL_NAME

# Example: Find duergar
ls data/images/monsters/golden_age/ | grep -i duergar
# Output: duergar.png, duergar_full.png
```

## Updating Documentation

After replacing images, update the tracking document:

1. Open `docs/humanoid_monster_image_status.md`
2. Change ❌ to ✅ for the replaced monster
3. Update the summary counts
4. Move the monster from "Missing" to "Replaced" list

## Automated Batch Processing

For bulk replacements with matching names, use the automated script:

```bash
python scripts/process_source_monster_images.py
```

This script:
- Scans `assets/line_art_cropped/monsters/`
- Sanitizes filenames
- Matches with generated images
- Replaces where names match
- Skips where no match found

## Troubleshooting

### Image Won't Load
- Check file path is correct
- Ensure file extension matches actual format
- Verify file isn't corrupted

### Name Mismatch
- Use `ls` or `grep` to find the exact output filename
- Check database for exact monster name:
  ```bash
  sqlite3 talekeeper.db "SELECT name FROM monsters WHERE name LIKE '%PARTIAL%'"
  ```

### Wrong Size Output
- Double-check the resize parameters: `(320, 240)` for full, `(80, 60)` for thumbnail
- Verify you're using `Image.Resampling.LANCZOS` for quality

## File Locations

- **Source Images**: `assets/line_art_cropped/monsters/`
- **Output Directory**: `data/images/monsters/golden_age/`
- **Processing Script**: `scripts/process_source_monster_images.py`
- **Tracking Doc**: `docs/humanoid_monster_image_status.md`

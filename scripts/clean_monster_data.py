import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable

# Keys to retain in the cleaned monster data
ALLOWED_KEYS = {
    "name",
    "size",
    "type",
    "alignment",
    "ac",
    "hp",
    "speed",
    "str",
    "dex",
    "con",
    "int",
    "wis",
    "cha",
    "save",
    "skill",
    "senses",
    "passive",
    "languages",
    "cr",
    "trait",
    "action",
    "legendary",
    "environment",
    "traitTags",
    "senseTags",
    "actionTags",
    "damageTagsLegendary",
    "conditionInflictLegendary",
    "savingThrowForced",
    "savingThrowForcedLegendary",
}


def _clean_monster(monster: Dict[str, Any]) -> Dict[str, Any]:
    """Return a new dictionary containing only allowed keys."""
    return {k: v for k, v in monster.items() if k in ALLOWED_KEYS}


def _extract_monsters(data: Any) -> Iterable[Dict[str, Any]]:
    """Extract monster list from various expected JSON structures."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("monster", "monsters"):
            if key in data and isinstance(data[key], list):
                return data[key]
    raise ValueError("Unsupported monster data format")


def clean_file(input_path: Path, output_path: Path) -> None:
    """Load monsters from ``input_path`` and write cleaned data to
    ``output_path``."""
    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    monsters = _extract_monsters(data)
    cleaned = [_clean_monster(m) for m in monsters]

    # Preserve top-level structure if input used an object wrapper
    if isinstance(data, dict):
        if "monster" in data:
            output = {"monster": cleaned}
        elif "monsters" in data:
            output = {"monsters": cleaned}
        else:
            output = cleaned
    else:
        output = cleaned

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean monster JSON data")
    parser.add_argument(
        "input",
        type=Path,
        help="Path to original monster JSON file",
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Path to write cleaned JSON data",
    )
    args = parser.parse_args()

    clean_file(args.input, args.output)

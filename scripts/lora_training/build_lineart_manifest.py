"""Utility to build a JSON manifest for line-art LoRA training."""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


@dataclass
class ManifestEntry:
    """Description of a single training image."""

    image_path: str
    prompt: str
    negative_prompt: str | None = None

    def to_dict(self) -> dict:
        payload = {"image_path": self.image_path, "prompt": self.prompt}
        if self.negative_prompt:
            payload["negative_prompt"] = self.negative_prompt
        return payload


def iter_image_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def default_prompt_for(path: Path, base_prompt: str, subject_template: str | None) -> str:
    if "{subject}" in base_prompt:
        subject = infer_subject_from_path(path, subject_template)
        return base_prompt.format(subject=subject)
    return base_prompt


def infer_subject_from_path(path: Path, template: str | None) -> str:
    candidate_parts: List[str] = []
    if template:
        candidate_parts.append(template.format(
            stem=path.stem.replace("_", " "),
            parent=path.parent.name.replace("_", " ")
        ))
    else:
        candidate_parts.append(path.stem)
        parent = path.parent.name
        if parent and parent.lower() not in {"", "line_art", "cropped"}:
            candidate_parts.append(parent)
    subject = " ".join(candidate_parts)
    subject = subject.replace("_", " ").strip()
    subject = " ".join(filter(None, subject.split()))
    return subject if subject else "line art"


def build_manifest(
    image_root: Path,
    output_path: Path,
    base_prompt: str,
    negative_prompt: str | None,
    subject_template: str | None,
    strip_prefix: Path | None,
) -> Sequence[ManifestEntry]:
    entries: List[ManifestEntry] = []
    for image_path in iter_image_files(image_root):
        manifest_path = image_path
        if strip_prefix and image_path.is_relative_to(strip_prefix):
            manifest_path = image_path.relative_to(strip_prefix)
        prompt = default_prompt_for(image_path, base_prompt, subject_template)
        entries.append(
            ManifestEntry(
                image_path=str(manifest_path).replace(os.sep, "/"),
                prompt=prompt,
                negative_prompt=negative_prompt,
            )
        )
    if not entries:
        raise ValueError(f"No images discovered in {image_root}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        json.dump([entry.to_dict() for entry in entries], f, indent=2)
        f.write("\n")
    return entries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "image_root",
        type=Path,
        help="Directory containing cropped line art images.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/lora/lineart_manifest.json"),
        help="Where to store the generated manifest (JSON).",
    )
    parser.add_argument(
        "--base-prompt",
        default="Clean black-and-white line art of {subject}, thick ink, comic style",
        help="Prompt template used for each entry. Accepts optional '{subject}' placeholder.",
    )
    parser.add_argument(
        "--negative-prompt",
        default="blurry, low contrast, photo, grayscale shading, background noise",
        help="Optional negative prompt stored with each entry.",
    )
    parser.add_argument(
        "--subject-template",
        default="{stem}",
        help="Template for inferring the {subject} placeholder from a filename. Available fields: {stem}, {parent}.",
    )
    parser.add_argument(
        "--strip-prefix",
        type=Path,
        default=None,
        help="If provided, convert image paths to be relative to this directory (useful for portable manifests).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    entries = build_manifest(
        image_root=args.image_root,
        output_path=args.output,
        base_prompt=args.base_prompt,
        negative_prompt=args.negative_prompt,
        subject_template=args.subject_template,
        strip_prefix=args.strip_prefix,
    )
    print(f"Wrote {len(entries)} entries to {args.output}")


if __name__ == "__main__":
    main()

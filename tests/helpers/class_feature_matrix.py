"""
Utilities for loading the SRD -> TaleKeeper class feature matrix.

The matrix is stored in YAML at tests/fixtures/class_feature_matrix.yaml and
captures, for each class, the SRD citation, template path, TaleKeeper services,
and feature verification metadata.  Test suites can import this helper to drive
parameterized progression + UI tests without duplicating configuration.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import yaml


MATRIX_PATH = (
    Path(__file__).resolve().parents[1] / "fixtures" / "class_feature_matrix.yaml"
)


@dataclass(frozen=True)
class FeatureEntry:
    """Single feature row describing level, SRD ref, and verification status."""

    id: str
    name: str
    level: int
    sr_ref: str
    tk_service: str
    db_tables: List[str]
    ui_targets: List[str]
    backend_status: str
    ui_status: str
    backend_tests: List[str]
    ui_tests: List[str]


@dataclass(frozen=True)
class ClassEntry:
    """Class level metadata for progression automation."""

    name: str
    sr_section: str
    default_subclass: str
    template_path: str
    template_notes: str
    services: List[str]
    backend_suite: str
    ui_suite: str
    feature_groups: List[FeatureEntry]

    def to_json(self) -> str:
        """Return a JSON dump used by progress reports."""
        payload = {
            "name": self.name,
            "sr_section": self.sr_section,
            "default_subclass": self.default_subclass,
            "template_path": self.template_path,
            "template_notes": self.template_notes,
            "services": self.services,
            "backend_suite": self.backend_suite,
            "ui_suite": self.ui_suite,
            "feature_groups": [feature.__dict__ for feature in self.feature_groups],
        }
        return json.dumps(payload, indent=2)


def _coerce_feature(name: str, raw: Dict) -> FeatureEntry:
    """Create a FeatureEntry ensuring required keys exist."""
    return FeatureEntry(
        id=raw["id"],
        name=raw["name"],
        level=int(raw["level"]),
        sr_ref=raw["sr_ref"],
        tk_service=raw.get("tk_service", ""),
        db_tables=list(raw.get("db_tables", [])),
        ui_targets=list(raw.get("ui_targets", [])),
        backend_status=raw.get("verification", {})
        .get("backend", {})
        .get("status", "unknown"),
        ui_status=raw.get("verification", {}).get("ui", {}).get("status", "unknown"),
        backend_tests=list(
            raw.get("verification", {}).get("backend", {}).get("tests", [])
        ),
        ui_tests=list(raw.get("verification", {}).get("ui", {}).get("tests", [])),
    )


def load_matrix(path: Optional[Path] = None) -> Dict[str, ClassEntry]:
    """
    Load the matrix into ClassEntry objects keyed by lowercase class id.

    Raises:
        FileNotFoundError: if the YAML does not exist.
        KeyError: if required keys are missing from the document.
    """
    matrix_file = Path(path) if path else MATRIX_PATH
    if not matrix_file.exists():
        raise FileNotFoundError(f"Class feature matrix missing: {matrix_file}")

    with matrix_file.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    classes = data.get("classes")
    if not isinstance(classes, dict):
        raise KeyError("Matrix missing 'classes' section")

    result: Dict[str, ClassEntry] = {}
    for class_id, payload in classes.items():
        feature_rows = payload.get("feature_groups", [])
        entry = ClassEntry(
            name=class_id,
            sr_section=payload["sr_section"],
            default_subclass=payload["default_subclass"],
            template_path=payload["template"]["path"],
            template_notes=payload["template"].get("notes", ""),
            services=list(payload.get("services", [])),
            backend_suite=payload.get("automation", {}).get("backend_suite", ""),
            ui_suite=payload.get("automation", {}).get("ui_suite", ""),
            feature_groups=[_coerce_feature(class_id, row) for row in feature_rows],
        )
        result[class_id] = entry
    return result


def get_class_entry(class_id: str, path: Optional[Path] = None) -> ClassEntry:
    """Helper to fetch a single class entry by name."""
    class_id = class_id.lower()
    matrix = load_matrix(path)
    if class_id not in matrix:
        raise KeyError(f"Class '{class_id}' not defined in class_feature_matrix")
    return matrix[class_id]

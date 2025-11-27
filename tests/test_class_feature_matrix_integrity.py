"""
Smoke tests for the SRD -> TaleKeeper class feature matrix.

Ensures every class entry references an existing template file and captures at
least one feature row so downstream progression tests can parameterize on top.
"""

from pathlib import Path

from tests.helpers.class_feature_matrix import load_matrix


SUPPORTED_CLASSES = {
    "barbarian",
    "cleric",
    "fighter",
    "paladin",
    "rogue",
    "warlock",
    "wizard",
}


def test_class_feature_matrix_templates_exist():
    matrix = load_matrix()
    assert set(matrix.keys()) == SUPPORTED_CLASSES, "Matrix contains unsupported classes"

    repo_root = Path(__file__).resolve().parents[1]
    for class_id, entry in matrix.items():
        template_path = repo_root / entry.template_path
        assert template_path.exists(), f"Template missing for {class_id}: {template_path}"
        assert entry.feature_groups, f"No features defined for {class_id}"
        for feature in entry.feature_groups:
            assert feature.level >= 1, f"Invalid level for {class_id}:{feature.id}"
            assert feature.sr_ref.startswith("docs/"), f"Missing SRD ref for {class_id}:{feature.id}"

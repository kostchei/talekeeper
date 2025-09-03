from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import json
import sqlite3

@dataclass
class ClassFeature:
    """Representation of a single class feature."""
    class_name: str
    level: int
    name: str
    feature_type: str = "passive"
    usage: str = "permanent"
    description: str = ""
    mechanics: Optional[Dict[str, Any]] = None
    resource: Optional[Dict[str, Any]] = None


class ClassFeatureRegistry:
    """Loads and provides access to class feature definitions stored in SQLite."""

    def __init__(self, db_path: str = "talekeeper.db") -> None:
        self.db_path = db_path

    def get_features(self, class_name: str, level: int) -> List[ClassFeature]:
        """Return all features for class at the given level."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT feature_name, feature_type, usage, description, mechanics, resource_name, resource_max_uses
            FROM class_feature_definitions
            WHERE class_name = ? AND level_required = ?
            """,
            (class_name, level),
        )
        rows = cursor.fetchall()
        conn.close()

        features: List[ClassFeature] = []
        for name, feature_type, usage, description, mechanics_json, resource_name, resource_max in rows:
            mechanics = json.loads(mechanics_json) if mechanics_json else None
            resource = None
            if resource_name:
                resource = {"name": resource_name, "max_uses": resource_max}
            features.append(
                ClassFeature(
                    class_name=class_name,
                    level=level,
                    name=name,
                    feature_type=feature_type,
                    usage=usage,
                    description=description,
                    mechanics=mechanics,
                    resource=resource,
                )
            )
        return features


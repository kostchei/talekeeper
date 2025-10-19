# core
# category: core
"""Weapon Mastery persistence and lookup utilities for TaleKeeper."""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, Iterable, List, Optional


class WeaponMasteryService:
    """Persist and retrieve weapon mastery selections for characters."""

    def __init__(self, db_path: str = "talekeeper.db") -> None:
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ------------------------------------------------------------------
    # Character selections
    # ------------------------------------------------------------------
    def get_character_masteries(self, character_id: str) -> List[Dict[str, str]]:
        """Return the weapon mastery assignments for a character."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT weapon_name, mastery_type
                FROM character_weapon_masteries
                WHERE character_id = ?
                ORDER BY weapon_name COLLATE NOCASE
                """,
                (character_id,),
            )
            rows = cursor.fetchall()

        selections: List[Dict[str, str]] = []
        for row in rows:
            weapon_name = (row["weapon_name"] or "").strip()
            mastery_type = (row["mastery_type"] or "").strip()
            if not weapon_name or not mastery_type:
                continue
            selections.append(
                {
                    "weapon_name": weapon_name,
                    "mastery_type": mastery_type.title(),
                }
            )
        return selections

    def set_character_masteries(self, character_id: str, selections: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
        """Persist the provided mastery assignments and return normalized payload."""
        normalized: List[Dict[str, str]] = []
        for entry in selections:
            weapon_name = (entry.get("weapon_name") or "").strip()
            mastery_type = (entry.get("mastery_type") or "").strip()
            if not weapon_name:
                continue
            if not mastery_type:
                mastery_type = self.get_weapon_mastery_for_weapon(weapon_name) or ""
            if not mastery_type:
                continue
            normalized.append(
                {
                    "weapon_name": weapon_name,
                    "mastery_type": mastery_type.title(),
                }
            )

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM character_weapon_masteries WHERE character_id = ?",
                (character_id,),
            )
            for entry in normalized:
                cursor.execute(
                    """
                    INSERT INTO character_weapon_masteries (character_id, weapon_name, mastery_type)
                    VALUES (?, ?, ?)
                    """,
                    (character_id, entry["weapon_name"], entry["mastery_type"].lower()),
                )
            conn.commit()

        # Mirror selections into JSON column for quick reference
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE characters SET weapon_mastery_selections = ? WHERE id = ?",
                (json.dumps(normalized), character_id),
            )
            conn.commit()

        return normalized

    # ------------------------------------------------------------------
    # Available options
    # ------------------------------------------------------------------
    def get_mastery_options(self) -> List[Dict[str, str]]:
        """Return all weapons that carry a mastery property."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT e.name, e.weapon_mastery, wm.description
                FROM equipment e
                LEFT JOIN weapon_masteries wm ON LOWER(e.weapon_mastery) = LOWER(wm.name)
                WHERE e.item_type = 'weapon'
                  AND e.weapon_mastery IS NOT NULL
                  AND e.weapon_mastery != ''
                ORDER BY e.name COLLATE NOCASE
                """
            )
            rows = cursor.fetchall()

        result: List[Dict[str, str]] = []
        for row in rows:
            mastery = (row["weapon_mastery"] or "").strip()
            if not mastery:
                continue
            result.append(
                {
                    "weapon_name": row["name"],
                    "mastery_type": mastery.title(),
                    "description": (row["description"] or "").strip(),
                }
            )
        return result

    def get_character_weapon_options(self, character_id: str) -> List[Dict[str, str]]:
        """Return mastery-bearing weapons the character currently owns or has equipped."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Inventory weapons
            cursor.execute(
                """
                SELECT ci.item_name,
                       MAX(ci.equipped) AS equipped,
                       MIN(ci.quantity) AS quantity,
                       e.weapon_mastery,
                       wm.description
                FROM character_inventory ci
                LEFT JOIN equipment e ON LOWER(e.name) = LOWER(ci.item_name)
                LEFT JOIN weapon_masteries wm ON LOWER(e.weapon_mastery) = LOWER(wm.name)
                WHERE ci.character_id = ? AND ci.item_type = 'weapon'
                GROUP BY ci.item_name COLLATE NOCASE
                ORDER BY ci.item_name COLLATE NOCASE
                """,
                (character_id,),
            )
            inventory_rows = cursor.fetchall()

            # Equipped weapons stored directly on characters table (covers cases not in inventory)
            cursor.execute(
                """
                SELECT equipment_main_hand AS slot_weapon FROM characters WHERE id = ?
                UNION ALL
                SELECT equipment_off_hand FROM characters WHERE id = ?
                """,
                (character_id, character_id),
            )
            equipped_rows = [row["slot_weapon"] for row in cursor.fetchall() if row["slot_weapon"]]

        options: Dict[str, Dict[str, str]] = {}

        def _add_option(weapon_name: str, mastery_type: Optional[str], description: str = "", equipped: bool = False) -> None:
            weapon_key = weapon_name.strip()
            if not weapon_key:
                return
            mastery = (mastery_type or "").strip()
            if mastery:
                mastery = mastery.title()
            else:
                mastery = (self.get_weapon_mastery_for_weapon(weapon_key) or "").title()
            if not mastery:
                return
            existing = options.get(weapon_key)
            if existing:
                # Preserve equipped flag if either source marks it equipped
                existing["equipped"] = existing.get("equipped", False) or equipped
                return
            options[weapon_key] = {
                "weapon_name": weapon_key,
                "mastery_type": mastery,
                "description": description.strip(),
                "equipped": equipped,
            }

        for row in inventory_rows:
            weapon_name = row["item_name"] or ""
            equipped_flag = bool(row["equipped"])
            mastery_type = row["weapon_mastery"]
            description = row["description"] or ""
            _add_option(weapon_name, mastery_type, description, equipped_flag)

        for weapon_name in equipped_rows:
            if weapon_name:
                _add_option(weapon_name, None, "", True)

        return list(options.values())

    # ------------------------------------------------------------------
    # Reference data
    # ------------------------------------------------------------------
    def get_weapon_mastery_for_weapon(self, weapon_name: str) -> Optional[str]:
        """Return the default mastery for the requested weapon."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT weapon_mastery FROM equipment WHERE LOWER(name) = LOWER(?)",
                (weapon_name,),
            )
            row = cursor.fetchone()
        return (row["weapon_mastery"] or "").title() if row and row["weapon_mastery"] else None

    # ------------------------------------------------------------------
    # Mastery definitions
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_mastery_key(mastery_name: str) -> str:
        """Return a lowercase cache key for mastery lookups."""
        return (mastery_name or "").strip().lower()

    @staticmethod
    def _coerce_bool(value: Any) -> bool:
        """Coerce SQLite truthy values into a bool."""
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "t", "yes", "y"}
        return bool(value)

    def get_mastery_definition(self, mastery_name: str) -> Optional[Dict[str, Any]]:
        """Return the database-backed definition for a weapon mastery."""
        cache = getattr(self, "_mastery_definition_cache", None)
        if cache is None:
            cache = {}
            self._mastery_definition_cache = cache

        cache_key = self._normalize_mastery_key(mastery_name)
        if not cache_key:
            return None

        if cache_key in cache:
            return cache[cache_key]

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT name,
                       trigger_condition,
                       description,
                       requires_save,
                       save_ability,
                       save_dc_formula,
                       damage_formula,
                       special_effects
                FROM weapon_masteries
                WHERE LOWER(name) = ?
                """,
                (cache_key,),
            )
            row = cursor.fetchone()

        if not row:
            cache[cache_key] = None
            return None

        definition = {
            "name": (row["name"] or "").strip() or mastery_name.title(),
            "trigger_condition": (row["trigger_condition"] or "").strip() or "on_hit",
            "description": (row["description"] or "").strip(),
            "requires_save": self._coerce_bool(row["requires_save"]),
            "save_ability": (row["save_ability"] or "").strip() or None,
            "save_dc_formula": (row["save_dc_formula"] or "").strip() or None,
            "damage_formula": (row["damage_formula"] or "").strip() or None,
            "special_effects": (row["special_effects"] or "").strip(),
        }

        cache[cache_key] = definition
        return definition


__all__ = ["WeaponMasteryService"]


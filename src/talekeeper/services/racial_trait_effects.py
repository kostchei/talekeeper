# core
# category: core
import sqlite3
import json
import random
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class RacialTraitEffect:
    trait_name: str
    race_id: str
    effect_type: str
    value: Any
    description: str


class RacialTraitEffectsProcessor:

    def __init__(self, db_path: str = "talekeeper.db"):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_race_traits(self, race_id: str) -> List[RacialTraitEffect]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT traits FROM races WHERE id = ?", (race_id,))
        result = cursor.fetchone()
        conn.close()

        if not result or not result['traits']:
            return []

        traits_json = json.loads(result['traits'])
        effects = []

        for trait_name, description in traits_json.items():
            effect = self._parse_trait_to_effect(trait_name, race_id, description)
            if effect:
                effects.append(effect)

        return effects

    def _parse_trait_to_effect(self, trait_name: str, race_id: str, description: str) -> Optional[RacialTraitEffect]:

        if trait_name == "giant_ancestry_fires_burn":
            return RacialTraitEffect(
                trait_name="Fires Burn",
                race_id=race_id,
                effect_type="damage_bonus",
                value={"dice": "1d10", "damage_type": "fire", "uses": "proficiency_bonus", "rest_type": "long_rest"},
                description=description
            )

        elif trait_name == "large_form":
            return RacialTraitEffect(
                trait_name="Large Form",
                race_id=race_id,
                effect_type="transformation",
                value={"level_required": 5, "duration_minutes": 10, "uses": 1, "rest_type": "long_rest"},
                description=description
            )

        elif trait_name == "powerful_build":
            return RacialTraitEffect(
                trait_name="Powerful Build",
                race_id=race_id,
                effect_type="passive",
                value={"grapple_advantage": True, "carry_capacity_multiplier": 2},
                description=description
            )

        elif trait_name == "dwarven_resilience":
            return RacialTraitEffect(
                trait_name="Dwarven Resilience",
                race_id=race_id,
                effect_type="resistance",
                value={"damage_type": "poison", "condition_advantage": "poisoned"},
                description=description
            )

        elif trait_name == "dwarven_toughness":
            return RacialTraitEffect(
                trait_name="Dwarven Toughness",
                race_id=race_id,
                effect_type="hp_bonus",
                value={"hp_per_level": 1},
                description=description
            )

        elif trait_name == "darkvision":
            return RacialTraitEffect(
                trait_name="Darkvision",
                race_id=race_id,
                effect_type="sense",
                value={"range_feet": 120},
                description=description
            )

        return RacialTraitEffect(
            trait_name=trait_name,
            race_id=race_id,
            effect_type="passive",
            value={},
            description=description
        )

    def initialize_racial_resources(self, character_id: str, race_id: str, level: int):
        conn = self._get_connection()
        cursor = conn.cursor()

        traits = self.get_race_traits(race_id)
        prof_bonus = 2 + ((level - 1) // 4)

        for trait in traits:
            if trait.effect_type == "damage_bonus" and trait.trait_name == "Fires Burn":
                cursor.execute("""
                    INSERT OR IGNORE INTO character_resources
                    (character_id, resource_name, current_uses, max_uses, rest_type, source_class)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (character_id, "Fires Burn", prof_bonus, prof_bonus, "long_rest", "racial"))

            elif trait.effect_type == "transformation" and trait.trait_name == "Large Form":
                if level >= trait.value["level_required"]:
                    cursor.execute("""
                        INSERT OR IGNORE INTO character_resources
                        (character_id, resource_name, current_uses, max_uses, rest_type, source_class)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (character_id, "Large Form", 1, 1, "long_rest", "racial"))

        conn.commit()
        conn.close()

    def get_racial_damage_bonus(self, character_id: str, character_race: str = None, target_hp_after_hit: int = None) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()

        if not character_race:
            cursor.execute("SELECT race_id FROM characters WHERE id = ?", (character_id,))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return None
            character_race = result['race_id']

        if character_race != "goliath_fire":
            conn.close()
            return None

        cursor.execute("""
            SELECT current_uses, max_uses FROM character_resources
            WHERE character_id = ? AND resource_name = 'Fires Burn'
        """, (character_id,))

        result = cursor.fetchone()

        if not result or result['current_uses'] <= 0:
            conn.close()
            return None

        cursor.execute("""
            SELECT fires_burn_used_this_round FROM character_combat_state
            WHERE character_id = ?
        """, (character_id,))

        combat_state = cursor.fetchone()

        if combat_state and combat_state['fires_burn_used_this_round']:
            conn.close()
            return None

        if target_hp_after_hit is not None and target_hp_after_hit <= 0:
            conn.close()
            return None

        fire_damage = random.randint(1, 10)

        cursor.execute("""
            UPDATE character_resources
            SET current_uses = current_uses - 1
            WHERE character_id = ? AND resource_name = 'Fires Burn'
        """, (character_id,))

        cursor.execute("""
            INSERT OR REPLACE INTO character_combat_state
            (character_id, fires_burn_used_this_round)
            VALUES (?, 1)
        """, (character_id,))

        conn.commit()
        conn.close()

        return {
            'damage': fire_damage,
            'damage_type': 'fire',
            'trait_name': 'Fires Burn',
            'uses_remaining': result['current_uses'] - 1
        }

    def check_racial_ability_available(self, character_id: str, ability_name: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT current_uses FROM character_resources
            WHERE character_id = ? AND resource_name = ?
        """, (character_id, ability_name))

        result = cursor.fetchone()
        conn.close()

        return result and result['current_uses'] > 0

    def apply_racial_hp_bonus(self, race_id: str, level: int) -> int:
        if race_id == "dwarf":
            return level
        return 0

    def reset_fires_burn_tracking(self, character_id: str):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE character_combat_state
            SET fires_burn_used_this_round = 0
            WHERE character_id = ?
        """, (character_id,))

        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO character_combat_state
                (character_id, fires_burn_used_this_round)
                VALUES (?, 0)
            """, (character_id,))

        conn.commit()
        conn.close()

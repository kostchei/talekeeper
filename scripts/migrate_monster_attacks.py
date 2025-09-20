"""
Monster Attack Migration Script

Converts monsters from complex text-based attack descriptions to
standardized structured JSON format for reliable parsing.
"""

import sqlite3
import json
import re
from typing import Dict, List, Any, Optional

# Standardized attack definitions for key monsters
STANDARDIZED_MONSTERS = {
    "Giant Spider": [
        {
            "name": "Bite",
            "attack_type": "melee",
            "attack_bonus": 5,
            "reach": 5,
            "damage": {
                "primary": {
                    "dice": "1d8+3",
                    "type": "piercing"
                }
            },
            "effects": [
                {
                    "type": "save_or_damage",
                    "save_dc": 11,
                    "save_ability": "constitution",
                    "damage_fail": {
                        "dice": "2d8",
                        "type": "poison"
                    },
                    "damage_success": {
                        "dice": "1d4",
                        "type": "poison"
                    }
                },
                {
                    "type": "conditional_condition",
                    "trigger": "reduced_to_0_hp_by_poison",
                    "condition": "poisoned",
                    "duration": "1 hour"
                },
                {
                    "type": "linked_condition",
                    "while_condition": "poisoned",
                    "also_condition": "paralyzed"
                }
            ],
            "description": "Venomous bite that can poison and paralyze victims."
        },
        {
            "name": "Web",
            "attack_type": "ranged",
            "attack_bonus": 5,
            "range_normal": 30,
            "range_long": 60,
            "recharge": "5-6",
            "damage": {
                "primary": {
                    "dice": "0",
                    "type": "none"
                }
            },
            "effects": [
                {
                    "type": "automatic_condition",
                    "condition": "restrained",
                    "escape_type": "strength_check",
                    "escape_dc": 12,
                    "destroy_ac": 10,
                    "destroy_hp": 5,
                    "vulnerability": "fire"
                }
            ],
            "description": "Restraining web that can be escaped or destroyed."
        }
    ],

    "Ankheg": [
        {
            "name": "Bite",
            "attack_type": "melee",
            "attack_bonus": 5,
            "reach": 5,
            "damage": {
                "primary": {
                    "dice": "2d6+3",
                    "type": "slashing"
                },
                "additional": [
                    {
                        "dice": "1d6",
                        "type": "acid"
                    }
                ]
            },
            "effects": [
                {
                    "type": "size_condition",
                    "max_size": "large",
                    "condition": "grappled",
                    "escape_dc": 13
                }
            ],
            "description": "Powerful bite that grapples smaller creatures."
        },
        {
            "name": "Acid Spray",
            "attack_type": "area",
            "recharge": "5-6",
            "shape": "line",
            "length": 30,
            "width": 5,
            "requires": "no_grappled_creature",
            "effects": [
                {
                    "type": "area_save",
                    "save_dc": 13,
                    "save_ability": "dexterity",
                    "damage_fail": {
                        "dice": "3d6",
                        "type": "acid"
                    },
                    "damage_success": {
                        "dice": "1d6+1",
                        "type": "acid"
                    }
                }
            ],
            "description": "Line of acid that dissolves armor and flesh."
        }
    ],

    "Ghast": [
        {
            "name": "Bite",
            "attack_type": "melee",
            "attack_bonus": 3,
            "reach": 5,
            "damage": {
                "primary": {
                    "dice": "2d8+3",
                    "type": "piercing"
                }
            },
            "effects": [],
            "description": "Simple bite attack."
        },
        {
            "name": "Claws",
            "attack_type": "melee",
            "attack_bonus": 5,
            "reach": 5,
            "damage": {
                "primary": {
                    "dice": "2d6+3",
                    "type": "slashing"
                }
            },
            "effects": [
                {
                    "type": "save_or_condition",
                    "target_restriction": "not_undead",
                    "save_dc": 10,
                    "save_ability": "constitution",
                    "condition": "paralyzed",
                    "duration": "1 minute",
                    "save_frequency": "end_of_turn"
                }
            ],
            "description": "Claws that can paralyze living creatures."
        }
    ],

    "Air Elemental": [
        {
            "name": "Slam",
            "attack_type": "melee",
            "attack_bonus": 8,
            "reach": 5,
            "damage": {
                "primary": {
                    "dice": "2d8+5",
                    "type": "bludgeoning"
                }
            },
            "effects": [],
            "description": "Powerful elemental slam."
        },
        {
            "name": "Whirlwind",
            "attack_type": "special",
            "recharge": "4-6",
            "target": "creatures_in_space",
            "effects": [
                {
                    "type": "save_or_multiple",
                    "save_dc": 13,
                    "save_ability": "strength",
                    "effects_on_fail": [
                        {
                            "type": "damage",
                            "damage": {
                                "dice": "3d8+2",
                                "type": "bludgeoning"
                            }
                        },
                        {
                            "type": "forced_movement",
                            "distance": 20,
                            "direction": "away_random",
                            "height": 20
                        },
                        {
                            "type": "condition",
                            "condition": "prone"
                        },
                        {
                            "type": "impact_damage",
                            "damage_per_10ft": "1d6",
                            "damage_type": "bludgeoning"
                        }
                    ],
                    "effects_on_success": [
                        {
                            "type": "damage",
                            "damage": {
                                "dice": "1d8+1",
                                "type": "bludgeoning"
                            }
                        }
                    ]
                }
            ],
            "description": "Violent whirlwind that flings creatures around."
        }
    ],

    "Basilisk": [
        {
            "name": "Bite",
            "attack_type": "melee",
            "attack_bonus": 5,
            "reach": 5,
            "damage": {
                "primary": {
                    "dice": "2d6+3",
                    "type": "piercing"
                },
                "additional": [
                    {
                        "dice": "2d6",
                        "type": "poison"
                    }
                ]
            },
            "effects": [],
            "description": "Venomous bite."
        }
        # Note: Petrifying Gaze is a special ability, not an attack
    ],

    "Adult Black Dragon": [
        {
            "name": "Bite",
            "attack_type": "melee",
            "attack_bonus": 11,
            "reach": 10,
            "damage": {
                "primary": {
                    "dice": "2d10+6",
                    "type": "piercing"
                },
                "additional": [
                    {
                        "dice": "1d8",
                        "type": "acid"
                    }
                ]
            },
            "effects": [],
            "description": "Massive acidic bite."
        },
        {
            "name": "Claw",
            "attack_type": "melee",
            "attack_bonus": 11,
            "reach": 5,
            "damage": {
                "primary": {
                    "dice": "2d6+6",
                    "type": "slashing"
                }
            },
            "effects": [],
            "description": "Razor-sharp claws."
        },
        {
            "name": "Tail",
            "attack_type": "melee",
            "attack_bonus": 11,
            "reach": 15,
            "damage": {
                "primary": {
                    "dice": "2d8+6",
                    "type": "bludgeoning"
                }
            },
            "effects": [],
            "description": "Sweeping tail attack."
        },
        {
            "name": "Frightful Presence",
            "attack_type": "aura",
            "range": 120,
            "target": "creatures_of_choice",
            "effects": [
                {
                    "type": "save_or_condition",
                    "save_dc": 16,
                    "save_ability": "wisdom",
                    "condition": "frightened",
                    "duration": "1 minute",
                    "save_frequency": "end_of_turn",
                    "immunity_on_success": "24 hours"
                }
            ],
            "description": "Overwhelming draconic presence."
        },
        {
            "name": "Acid Breath",
            "attack_type": "breath_weapon",
            "recharge": "5-6",
            "shape": "line",
            "length": 60,
            "width": 5,
            "effects": [
                {
                    "type": "area_save",
                    "save_dc": 18,
                    "save_ability": "dexterity",
                    "damage_fail": {
                        "dice": "12d8",
                        "type": "acid"
                    },
                    "damage_success": {
                        "dice": "6d8",
                        "type": "acid"
                    }
                }
            ],
            "description": "Devastating line of corrosive acid."
        }
    ]
}


def migrate_monster_attacks(db_path: str = "talekeeper.db", dry_run: bool = True):
    """
    Migrate monster attacks to standardized format.

    Args:
        db_path: Path to the database
        dry_run: If True, only print what would be changed
    """

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        for monster_name, standardized_attacks in STANDARDIZED_MONSTERS.items():
            print(f"\n=== Migrating {monster_name} ===")

            # Get current monster data
            cursor.execute("SELECT id, actions FROM monsters WHERE name = ?", (monster_name,))
            row = cursor.fetchone()

            if not row:
                print(f"X Monster '{monster_name}' not found in database")
                continue

            monster_id, current_actions = row

            print(f"Current actions: {len(json.loads(current_actions) if current_actions else [])} actions")
            print(f"New actions: {len(standardized_attacks)} actions")

            # Show the difference
            if current_actions:
                try:
                    old_actions = json.loads(current_actions)
                    print("\nCurrent attack names:")
                    for action in old_actions:
                        print(f"  - {action.get('name', 'Unnamed')}")
                except json.JSONDecodeError:
                    print("  Warning: Current actions are not valid JSON")

            print("\nNew attack names:")
            for attack in standardized_attacks:
                print(f"  - {attack['name']} ({attack['attack_type']})")
                if attack.get('effects'):
                    for effect in attack['effects']:
                        print(f"    * {effect['type']}")

            if not dry_run:
                # Update the database
                new_actions_json = json.dumps(standardized_attacks, indent=2)
                cursor.execute(
                    "UPDATE monsters SET actions = ? WHERE id = ?",
                    (new_actions_json, monster_id)
                )
                print(f"Updated {monster_name} in database")
            else:
                print(f"Dry run - {monster_name} would be updated")

        if not dry_run:
            conn.commit()
            print(f"\nMigration complete! Updated {len(STANDARDIZED_MONSTERS)} monsters")
        else:
            print(f"\nDry run complete. Would update {len(STANDARDIZED_MONSTERS)} monsters")
            print("Run with dry_run=False to apply changes")


def validate_standardized_format(attack_data: Dict[str, Any]) -> List[str]:
    """Validate that an attack follows the standardized format."""
    errors = []

    # Required fields
    required_fields = ["name", "attack_type"]
    for field in required_fields:
        if field not in attack_data:
            errors.append(f"Missing required field: {field}")

    # Attack type validation
    valid_attack_types = ["melee", "ranged", "area", "breath_weapon", "aura", "special"]
    if attack_data.get("attack_type") not in valid_attack_types:
        errors.append(f"Invalid attack_type: {attack_data.get('attack_type')}")

    # Damage validation
    damage = attack_data.get("damage")
    if damage and "primary" in damage:
        primary = damage["primary"]
        if "dice" not in primary or "type" not in primary:
            errors.append("Primary damage missing dice or type")

    # Effects validation
    effects = attack_data.get("effects", [])
    for i, effect in enumerate(effects):
        if "type" not in effect:
            errors.append(f"Effect {i} missing type")

    return errors


def create_standardized_parser():
    """Create a simple parser for standardized attack format."""

    class StandardizedAttackParser:
        def parse_attack(self, attack_data: Dict[str, Any]) -> Dict[str, Any]:
            """Parse a standardized attack into execution data."""

            # Validate format
            errors = validate_standardized_format(attack_data)
            if errors:
                raise ValueError(f"Invalid attack format: {errors}")

            # Extract basic attack info
            result = {
                "name": attack_data["name"],
                "attack_type": attack_data["attack_type"],
                "attack_bonus": attack_data.get("attack_bonus", 0),
                "reach": attack_data.get("reach", 5),
                "range_normal": attack_data.get("range_normal"),
                "range_long": attack_data.get("range_long"),
                "damage": attack_data.get("damage", {}),
                "effects": [],
                "description": attack_data.get("description", "")
            }

            # Parse effects
            for effect in attack_data.get("effects", []):
                parsed_effect = self.parse_effect(effect)
                result["effects"].append(parsed_effect)

            return result

        def parse_effect(self, effect_data: Dict[str, Any]) -> Dict[str, Any]:
            """Parse a standardized effect."""
            effect_type = effect_data["type"]

            if effect_type == "save_or_condition":
                return {
                    "type": "save_condition",
                    "save_dc": effect_data["save_dc"],
                    "save_ability": effect_data["save_ability"],
                    "condition": effect_data["condition"],
                    "duration": effect_data.get("duration"),
                    "save_frequency": effect_data.get("save_frequency", "end_of_turn")
                }

            elif effect_type == "automatic_condition":
                return {
                    "type": "automatic_condition",
                    "condition": effect_data["condition"],
                    "escape_dc": effect_data.get("escape_dc"),
                    "escape_type": effect_data.get("escape_type")
                }

            elif effect_type == "save_or_damage":
                return {
                    "type": "save_damage",
                    "save_dc": effect_data["save_dc"],
                    "save_ability": effect_data["save_ability"],
                    "damage_fail": effect_data.get("damage_fail"),
                    "damage_success": effect_data.get("damage_success")
                }

            elif effect_type == "size_condition":
                return {
                    "type": "conditional_automatic",
                    "trigger": f"target_size_{effect_data['max_size']}_or_smaller",
                    "condition": effect_data["condition"],
                    "escape_dc": effect_data.get("escape_dc")
                }

            # Pass through unknown effect types
            return effect_data

    return StandardizedAttackParser()


if __name__ == "__main__":
    print("Monster Attack Migration Script")
    print("=" * 50)

    # Run dry run first
    print("Running dry run to preview changes...")
    migrate_monster_attacks(dry_run=True)

    # Apply migration automatically for testing
    print("\n" + "=" * 50)
    print("Applying migration...")
    migrate_monster_attacks(dry_run=False)

    # Test the new parser
    print("\nTesting standardized parser...")
    parser = create_standardized_parser()

    test_attack = STANDARDIZED_MONSTERS["Giant Spider"][0]  # Bite attack
    try:
        parsed = parser.parse_attack(test_attack)
        print("Parser test successful!")
        print(f"   Parsed {parsed['name']} with {len(parsed['effects'])} effects")
    except Exception as e:
        print(f"Parser test failed: {e}")
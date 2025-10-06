import random
import json
import os
import re
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from talekeeper.services.campaign_description_service import CampaignDescriptionService

# XP budgets per encounter level/difficulty
XP_BUDGETS = [
{"Level": 1, "Low": 50, "Moderate": 75, "High": 100},
{"Level": 2, "Low": 100, "Moderate": 150, "High": 200},
{"Level": 3, "Low": 150, "Moderate": 225, "High": 400},
{"Level": 4, "Low": 250, "Moderate": 375, "High": 500},
{"Level": 5, "Low": 500, "Moderate": 750, "High": 1100},
{"Level": 6, "Low": 600, "Moderate": 1000, "High": 1400},
{"Level": 7, "Low": 750, "Moderate": 1300, "High": 1700},
{"Level": 8, "Low": 900, "Moderate": 1600, "High": 2100},
{"Level": 9, "Low": 1100, "Moderate": 1900, "High": 2600},
{"Level": 10, "Low": 1300, "Moderate": 2300, "High": 3100},
{"Level": 11, "Low": 1600, "Moderate": 2700, "High": 3700},
{"Level": 12, "Low": 1900, "Moderate": 3200, "High": 4300},
{"Level": 13, "Low": 2200, "Moderate": 3700, "High": 5000},
{"Level": 14, "Low": 2600, "Moderate": 4300, "High": 5800},
{"Level": 15, "Low": 3000, "Moderate": 5000, "High": 6700},
{"Level": 16, "Low": 3500, "Moderate": 5800, "High": 7800},
{"Level": 17, "Low": 4000, "Moderate": 6700, "High": 9000},
{"Level": 18, "Low": 4700, "Moderate": 7800, "High": 10500},
{"Level": 19, "Low": 5400, "Moderate": 9000, "High": 12100},
{"Level": 20, "Low": 6300, "Moderate": 10500, "High": 14100}
]

# CR to XP conversion table
CR_TO_XP = {
    "0": 10, "1/8": 25, "1/4": 50, "1/2": 100,
    "1": 200, "2": 450, "3": 700, "4": 1100, "5": 1800,
    "6": 2300, "7": 2900, "8": 3900, "9": 5000, "10": 5900,
    "11": 7200, "12": 8400, "13": 10000, "14": 11500, "15": 13000,
    "16": 15000, "17": 18000, "18": 20000, "19": 22000, "20": 25000,
    "21": 33000, "22": 41000, "23": 50000, "24": 62000, "30": 155000
}

def load_monsters():
    """Load monsters from database"""
    import sqlite3
    conn = sqlite3.connect("talekeeper.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM monsters")
    monster_rows = cursor.fetchall()

    monsters = []
    for monster_row in monster_rows:
        # Reconstruct monster dict from database
        monster = {
            'id': monster_row[0],
            'name': monster_row[1],
            'type': monster_row[2],
            'cr': monster_row[15],
            'alignment': monster_row[5],
            'intelligence': monster_row[12] if len(monster_row) > 12 else 3,
            'aquatic_only': monster_row[30] if len(monster_row) > 30 else 0
        }
        # Extract type - handle both string and object formats
        monster_type = monster['type']
        if isinstance(monster_type, dict):
            monster_type = monster_type['type']
        
        # Convert CR to string and numeric value for comparison
        cr = monster['cr']
        cr_str = str(cr)
        
        # Handle complex CR data that might be stringified JSON or Python dict
        if cr_str.startswith('{') and 'cr' in cr_str:
            try:
                import json
                # First try standard JSON parsing
                cr_data = json.loads(cr_str)
                cr_str = cr_data.get('cr', '0')
            except json.JSONDecodeError:
                try:
                    # If JSON fails, try eval for Python dict syntax (safe for simple dicts)
                    cr_data = eval(cr_str)
                    if isinstance(cr_data, dict):
                        cr_str = cr_data.get('cr', '0')
                    else:
                        cr_str = '0'
                except:
                    cr_str = '0'
            except:
                cr_str = '0'
        elif isinstance(cr, dict):
            cr_str = cr.get('cr', '0')
        
        # Parse fractional CRs
        try:
            if '/' in cr_str:
                numerator, denominator = cr_str.split('/')
                cr_numeric = float(numerator) / float(denominator)
            else:
                cr_numeric = float(cr_str)
        except (ValueError, TypeError):
            cr_numeric = 0
        
        # HP is stored directly as a number from the migration - use database value
        average_hp = monster_row[7] if monster_row[7] else 8  # hit_points column
        # Use the database HP value directly instead of rolling dice
        hp_formula = str(average_hp)  # Use fixed HP from database
        
        monsters.append({
            "name": monster['name'],
            "cr": cr_numeric,
            "cr_str": cr_str,
            "xp": CR_TO_XP.get(cr_str, 0),
            "type": monster_type,
            "alignment": monster.get('alignment', 'N'),
            "intelligence": monster.get('intelligence', 3),
            "average_hp": average_hp,
            "hp_formula": hp_formula,
            "aquatic_only": monster.get('aquatic_only', 0)
        })
    
    conn.close()
    return monsters

# Load monster database from JSON
MONSTER_DB = load_monsters()


def roll_monster_hp(hp_formula: str) -> int:
    """Roll HP using dice formula like '3d8' or '18d10 + 36'."""
    try:
        # Parse dice formula (e.g., "3d8", "18d10 + 36")
        formula = hp_formula.strip().lower()
        
        # Handle formulas with modifiers (+ or -)
        if '+' in formula:
            dice_part, modifier_part = formula.split('+')
            modifier = int(modifier_part.strip())
        elif '-' in formula and formula.count('-') == 1:
            dice_part, modifier_part = formula.split('-')
            modifier = -int(modifier_part.strip())
        else:
            dice_part = formula
            modifier = 0
        
        dice_part = dice_part.strip()
        
        # Parse dice notation (e.g., "3d8")
        if 'd' not in dice_part:
            # Just a number, return it
            return int(dice_part) + modifier
        
        num_dice, die_size = dice_part.split('d')
        num_dice = int(num_dice) if num_dice else 1
        die_size = int(die_size)
        
        # Roll the dice
        total = sum(random.randint(1, die_size) for _ in range(num_dice))
        return max(1, total + modifier)  # Minimum 1 HP
        
    except (ValueError, AttributeError) as e:
        print(f"Error rolling HP formula '{hp_formula}': {e}")
        return 8  # Default HP on error


class CampaignFrame:
    """Simple data class to hold campaign frame data"""
    def __init__(self, data: Dict[str, Any]):
        self.monster_type_weights = data.get('monster_type_weights', {})
        self.difficulty_distribution = data.get('difficulty_distribution', {})
        self.rest_rules = data.get('rest_rules', {})
        self.style = data.get('style', '')
        self.available_classes = data.get('available_classes', [])
        self.monster_alignment_rules = data.get('monster_alignment_rules', {})
        self.tags = data.get('tags', [])


class RandomBag:
    def __init__(self, items: List[Any]):
        self.original = items[:]
        self.pool = items[:]

    def draw(self):
        if not self.pool:
            self.pool = self.original[:]
        item = random.choice(self.pool)
        self.pool.remove(item)
        return item


class EncounterGenerator:
    def __init__(self, frame: CampaignFrame, description_service: Optional["CampaignDescriptionService"] = None):
        self.frame = frame
        self.bags: Dict[int, RandomBag] = {}
        self.description_service = description_service

    def _attach_monster_narrative(self, monsters: List[Dict[str, Any]], level: int, difficulty: str) -> List[Dict[str, Any]]:
        """Return copies of ``monsters`` with a unified encounter description."""

        decorated: List[Dict[str, Any]] = []
        for monster in monsters:
            decorated.append(monster.copy())

        from talekeeper.core.config import get_config
        config = get_config()

        if self.description_service and decorated and config.narrative.enable_combat_narratives:
            encounter_data = self.description_service.generate_encounter_description(
                decorated,
                self.frame,
                level,
                difficulty
            )

            if encounter_data:
                for monster in decorated:
                    monster["encounter_description"] = encounter_data.get("description")
                    monster["tarot_card"] = encounter_data.get("tarot_card")
                    monster["tarot_orientation"] = encounter_data.get("tarot_orientation")
                    monster["tarot_aspect"] = encounter_data.get("tarot_aspect")
                    monster["tarot_detail"] = encounter_data.get("tarot_detail")

        return decorated

    def get_budget(self, level: int, difficulty: str) -> int:
        for entry in XP_BUDGETS:
            if entry["Level"] == level:
                return entry[difficulty.capitalize()]
        raise ValueError("Unknown level")

    def _get_available_monsters(self, level: int) -> List[Dict[str, Any]]:
        """Get monsters available for this level based on CR and campaign rules"""
        cr_cap = 0.25 * level if level < 5 else 0.5 * level
        allowed = []
        is_aquatic_campaign = 'aquatic' in self.frame.tags

        for m in MONSTER_DB:
            if m["cr"] > cr_cap:
                continue

            if m.get("aquatic_only", 0) == 1 and not is_aquatic_campaign:
                continue

            alignment = m.get("alignment", "N").upper()

            if self.frame.monster_alignment_rules.get("allow_evil", False):
                if "E" in alignment:
                    allowed.append(m)
                    continue

            if self.frame.monster_alignment_rules.get("allow_humanoid_not_good", False):
                if m["type"] == "humanoid" and "G" not in alignment:
                    allowed.append(m)
                    continue

        return allowed if allowed else [m for m in MONSTER_DB if m["cr"] <= cr_cap]

    def _can_pair_with_beast(self, monster: Dict[str, Any]) -> bool:
        """Check if a monster can be paired with a beast (both must have Int 6+)"""
        return monster["type"] == "beast" or monster["intelligence"] >= 6

    def _generate_solo_encounter(self, available: List[Dict[str, Any]], budget: int) -> List[Dict[str, Any]]:
        """High difficulty: Single strongest monster"""
        available_sorted = sorted(available, key=lambda m: m["xp"], reverse=True)
        for monster in available_sorted:
            if monster["xp"] <= budget:
                return [monster]
        return [available_sorted[0]] if available_sorted else []

    def _generate_pair_encounter(self, available: List[Dict[str, Any]], budget: int) -> List[Dict[str, Any]]:
        """Pair of 2 random types (if one is beast, other must be beast or Int 6+)"""
        encounter = []

        first = random.choice(available)
        if first["xp"] > budget * 0.7:
            return []

        encounter.append(first)
        remaining_budget = budget - first["xp"]

        valid_pairs = []
        for m in available:
            if m["xp"] > remaining_budget:
                continue

            if first["type"] == "beast":
                if m["type"] == "beast" or m["intelligence"] >= 6:
                    valid_pairs.append(m)
            elif m["type"] == "beast":
                if first["intelligence"] >= 6:
                    valid_pairs.append(m)
            else:
                valid_pairs.append(m)

        if valid_pairs:
            second = max(valid_pairs, key=lambda m: m["xp"])
            encounter.append(second)

        return encounter

    def _generate_leader_minions_encounter(self, available: List[Dict[str, Any]], budget: int) -> List[Dict[str, Any]]:
        """1 leader + 1-4 minions of same type (aberration, fiend, humanoid, undead, etc)"""
        valid_types = ["aberration", "fiend", "humanoid", "undead", "beast", "dragon", "elemental", "fey", "giant", "monstrosity", "ooze", "plant"]

        type_groups = {}
        for m in available:
            mtype = m["type"]
            if mtype in valid_types:
                if mtype not in type_groups:
                    type_groups[mtype] = []
                type_groups[mtype].append(m)

        for mtype, monsters in type_groups.items():
            if len(monsters) < 2:
                continue

            monsters_sorted = sorted(monsters, key=lambda m: m["xp"], reverse=True)

            for leader in monsters_sorted:
                if leader["xp"] > budget * 0.6:
                    continue

                encounter = [leader]
                remaining_budget = budget - leader["xp"]

                minions = [m for m in monsters_sorted if m["name"] != leader["name"] and m["xp"] <= remaining_budget * 0.4]

                if not minions:
                    continue

                minion_type = max(minions, key=lambda m: m["xp"])

                count = 0
                while count < 4 and remaining_budget >= minion_type["xp"]:
                    encounter.append(minion_type)
                    remaining_budget -= minion_type["xp"]
                    count += 1

                if len(encounter) >= 2:
                    return encounter

        return []

    def generate_encounter(self, level: int) -> Dict[str, Any]:
        difficulty = random.choices(
            population=["low", "moderate", "high"],
            weights=[self.frame.difficulty_distribution.get(k, 0) for k in ["low", "moderate", "high"]]
        )[0]

        budget = self.get_budget(level, difficulty)
        available = self._get_available_monsters(level)

        if not available:
            return {
                "level": level,
                "difficulty": difficulty,
                "monsters": [],
                "total_xp": 0
            }

        encounter = []

        if difficulty == "high":
            pattern = random.choice(["solo", "pair", "leader_minions"])

            if pattern == "solo":
                encounter = self._generate_solo_encounter(available, budget)
            elif pattern == "pair":
                encounter = self._generate_pair_encounter(available, budget)
                if not encounter:
                    encounter = self._generate_leader_minions_encounter(available, budget)
            else:
                encounter = self._generate_leader_minions_encounter(available, budget)
                if not encounter:
                    encounter = self._generate_pair_encounter(available, budget)

        else:
            cr_cap = 0.25 * level if level < 5 else 0.5 * level
            available_capped = [m for m in available if m["cr"] <= cr_cap]

            if not available_capped:
                available_capped = available

            pattern = random.choice(["pair", "leader_minions"])

            if pattern == "pair":
                encounter = self._generate_pair_encounter(available_capped, budget)
                if not encounter:
                    encounter = self._generate_leader_minions_encounter(available_capped, budget)
            else:
                encounter = self._generate_leader_minions_encounter(available_capped, budget)
                if not encounter:
                    encounter = self._generate_pair_encounter(available_capped, budget)

        if not encounter:
            encounter = self._generate_solo_encounter(available, budget)

        total_xp = sum(m["xp"] for m in encounter)
        monsters = self._attach_monster_narrative(encounter, level, difficulty)

        return {
            "level": level,
            "difficulty": difficulty,
            "monsters": monsters,
            "total_xp": total_xp
        }
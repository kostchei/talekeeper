import random
import json
import os
import re
from typing import List, Dict, Any

# XP budgets per encounter level/difficulty
XP_BUDGETS = [
{"Level": 1, "Low": 50, "Moderate": 75, "High": 100},
{"Level": 2, "Low": 100, "Moderate": 150, "High": 200},
{"Level": 3, "Low": 150, "Moderate": 225, "High": 400},
{"Level": 4, "Low": 250, "Moderate": 375, "High": 500},
{"Level": 5, "Low": 500, "Moderate": 750, "High": 1100},
{"Level": 6, "Low": 600, "Moderate": 1000, "High": 1400},
{"Level": 7, "Low": 750, "Moderate": 1300, "High": 1700},
# ... more levels as needed
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
            'alignment': monster_row[5]  # Add alignment from database
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
            "average_hp": average_hp,
            "hp_formula": hp_formula
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
    def __init__(self, frame: CampaignFrame):
        self.frame = frame
        self.bags: Dict[int, RandomBag] = {}

    def get_budget(self, level: int, difficulty: str) -> int:
        for entry in XP_BUDGETS:
            if entry["Level"] == level:
                return entry[difficulty.capitalize()]
        raise ValueError("Unknown level")

    def generate_encounter(self, level: int) -> Dict[str, Any]:
        if level not in self.bags:
            # Filter monsters based on CR limits and alignment rules
            cr_cap = 0.25 * level if level < 5 else 0.5 * level
            allowed = []
            
            for m in MONSTER_DB:
                if m["cr"] > cr_cap:
                    continue
                    
                # Check alignment rules
                alignment = m.get("alignment", "N").upper()
                
                # Allow evil monsters if configured
                if self.frame.monster_alignment_rules.get("allow_evil", False):
                    if "E" in alignment:  # Check for evil alignment
                        allowed.append(m)
                        continue
                
                # Allow humanoid non-good monsters if configured
                if self.frame.monster_alignment_rules.get("allow_humanoid_not_good", False):
                    if m["type"] == "humanoid" and "G" not in alignment:
                        allowed.append(m)
                        continue
            
            # Create equally weighted pool from allowed monsters
            self.bags[level] = RandomBag(allowed if allowed else [m for m in MONSTER_DB if m["cr"] <= cr_cap])

        difficulty = random.choices(
            population=["low", "moderate", "high"],
            weights=[self.frame.difficulty_distribution.get(k, 0) for k in ["low", "moderate", "high"]]
        )[0]

        budget = self.get_budget(level, difficulty)

        if difficulty == "high":
            # High encounter = 1 strong monster
            attempts = 0
            max_attempts = 100  # Prevent infinite loop
            while attempts < max_attempts:
                monster = self.bags[level].draw()
                if monster["xp"] >= budget * 0.8:
                    return {
                        "level": level,
                        "difficulty": difficulty,
                        "monsters": [monster],
                        "total_xp": monster["xp"]
                    }
                attempts += 1
            
            # Fallback: return any monster if we can't find one that meets criteria
            monster = self.bags[level].draw()
            return {
                "level": level,
                "difficulty": "moderate",  # Downgrade difficulty
                "monsters": [monster],
                "total_xp": monster["xp"]
            }
        else:
            # Low/Moderate: build up encounter
            encounter = []
            total = 0
            while total < budget and len(encounter) < 4:
                m = self.bags[level].draw()
                if total + m["xp"] <= budget:
                    encounter.append(m)
                    total += m["xp"]
                else:
                    break
            return {
                "level": level,
                "difficulty": difficulty,
                "monsters": encounter,
                "total_xp": total
            }
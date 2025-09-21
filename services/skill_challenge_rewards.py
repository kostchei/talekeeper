import sqlite3
import random
import re
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta


class SkillChallengeRewards:
    """Handle application of skill challenge rewards and penalties."""

    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path

    def apply_reward(self, character_data: Dict, reward: str) -> Tuple[Dict, List[str]]:
        """Apply a success reward to the character. Returns updated character data and log messages."""
        log_messages = []
        updated_character = character_data.copy()

        reward_lower = reward.lower().strip()

        if reward_lower == 'rest':
            updated_character, messages = self._apply_rest(updated_character)
            log_messages.extend(messages)

        elif reward_lower == 'rations':
            updated_character, messages = self._apply_rations_gain(updated_character)
            log_messages.extend(messages)

        elif 'view' in reward_lower and 'hex' in reward_lower:
            updated_character, messages = self._apply_exploration_view(updated_character, reward)
            log_messages.extend(messages)

        elif reward_lower == 'coin':
            updated_character, messages = self._apply_coin_reward(updated_character)
            log_messages.extend(messages)

        elif reward_lower == 'item':
            updated_character, messages = self._apply_item_reward(updated_character)
            log_messages.extend(messages)

        elif reward_lower == 'inspiration':
            updated_character, messages = self._apply_inspiration(updated_character)
            log_messages.extend(messages)

        elif reward_lower == 'consumable':
            updated_character, messages = self._apply_consumable_reward(updated_character)
            log_messages.extend(messages)

        elif 'quest' in reward_lower:
            updated_character, messages = self._apply_quest_modifier(updated_character, reward)
            log_messages.extend(messages)

        elif 'reputation' in reward_lower:
            updated_character, messages = self._apply_reputation_gain(updated_character, reward)
            log_messages.extend(messages)

        elif 'vendor' in reward_lower:
            updated_character, messages = self._apply_vendor_modifier(updated_character, reward)
            log_messages.extend(messages)

        elif 'healing potion' in reward_lower:
            updated_character, messages = self._apply_healing_potion(updated_character)
            log_messages.extend(messages)

        elif "healer's kit" in reward_lower:
            updated_character, messages = self._apply_healers_kit(updated_character)
            log_messages.extend(messages)

        else:
            log_messages.append(f"Applied reward: {reward}")

        return updated_character, log_messages

    def apply_penalty(self, character_data: Dict, penalty: str) -> Tuple[Dict, List[str]]:
        """Apply a failure penalty to the character. Returns updated character data and log messages."""
        log_messages = []
        updated_character = character_data.copy()

        penalty_lower = penalty.lower().strip()

        if penalty_lower == 'exhaustion':
            updated_character, messages = self._apply_exhaustion(updated_character)
            log_messages.extend(messages)

        elif 'dangerous trap' in penalty_lower:
            updated_character, messages = self._apply_damage(updated_character, penalty)
            log_messages.extend(messages)

        elif 'damage' in penalty_lower:
            updated_character, messages = self._apply_damage(updated_character, penalty)
            log_messages.extend(messages)

        elif 'poison' in penalty_lower:
            updated_character, messages = self._apply_poison_condition(updated_character)
            log_messages.extend(messages)

        elif penalty_lower == 'rations':
            updated_character, messages = self._apply_rations_loss(updated_character)
            log_messages.extend(messages)

        elif 'lose coin' in penalty_lower or penalty_lower == 'coin':
            updated_character, messages = self._apply_coin_loss(updated_character)
            log_messages.extend(messages)

        elif 'reputation' in penalty_lower:
            updated_character, messages = self._apply_reputation_loss(updated_character)
            log_messages.extend(messages)

        elif 'encounter' in penalty_lower:
            updated_character, messages = self._apply_forced_encounter(updated_character, penalty)
            log_messages.extend(messages)

        elif 'quest' in penalty_lower:
            updated_character, messages = self._apply_quest_modifier(updated_character, penalty)
            log_messages.extend(messages)

        else:
            log_messages.append(f"Applied penalty: {penalty}")

        return updated_character, log_messages

    def apply_refuse_cost(self, character_data: Dict, cost: str) -> Tuple[Dict, List[str]]:
        """Apply the cost of refusing a challenge. Returns updated character data and log messages."""
        if cost.lower().strip() == 'none':
            return character_data, ["No cost for refusing this challenge."]

        # Refuse costs are typically milder versions of penalties
        return self.apply_penalty(character_data, cost)

    def _apply_rest(self, character_data: Dict) -> Tuple[Dict, List[str]]:
        """Apply long rest benefits."""
        messages = []

        # Long rest: full healing and resource restoration
        max_hp = character_data.get('hit_points_max', 0)
        current_hp = character_data.get('hit_points_current', 0)
        character_data['hit_points_current'] = max_hp

        # Restore hit dice (half, minimum 1)
        max_hit_dice = character_data.get('hit_dice_max', 1)
        restored_dice = max(1, max_hit_dice // 2)
        character_data['hit_dice_current'] = min(max_hit_dice,
            character_data.get('hit_dice_current', 0) + restored_dice)

        # Reset death saves
        character_data['death_saves_successes'] = 0
        character_data['death_saves_failures'] = 0

        # Calculate healing done
        healing_done = max_hp - current_hp

        if healing_done > 0:
            messages.append(f"Long rest: Healed {healing_done} HP to full health and restored {restored_dice} hit dice")
        else:
            messages.append(f"Long rest: Already at full HP, restored {restored_dice} hit dice")

        return character_data, messages

    def _apply_rations_gain(self, character_data: Dict) -> Tuple[Dict, List[str]]:
        """Apply ration gain (food/water supplies)."""
        amount = random.randint(2, 6)  # 2-6 days worth
        # For now, just log it since we don't track rations in character data
        return character_data, [f"Gained {amount} days worth of rations"]

    def _apply_rations_loss(self, character_data: Dict) -> Tuple[Dict, List[str]]:
        """Apply ration loss."""
        amount = random.randint(1, 3)
        return character_data, [f"Lost {amount} days worth of rations"]

    def _apply_exploration_view(self, character_data: Dict, reward: str) -> Tuple[Dict, List[str]]:
        """Apply exploration view benefit."""
        # Extract number of hexes from reward text
        hex_match = re.search(r'(\d+)\s*hex', reward.lower())
        hex_count = int(hex_match.group(1)) if hex_match else 2

        return character_data, [f"Gained view of {hex_count} surrounding hexes for exploration"]

    def _apply_coin_reward(self, character_data: Dict) -> Tuple[Dict, List[str]]:
        """Apply coin reward based on character level."""
        level = character_data.get('level', 1)

        if level <= 4:
            coin_amount = random.randint(50, 200)
            coin_type = "silver pieces"
        elif level <= 10:
            coin_amount = random.randint(20, 100)
            coin_type = "gold pieces"
        elif level <= 16:
            coin_amount = random.randint(50, 200)
            coin_type = "gold pieces"
        else:
            coin_amount = random.randint(100, 500)
            coin_type = "gold pieces"

        return character_data, [f"Earned {coin_amount} {coin_type}"]

    def _apply_coin_loss(self, character_data: Dict) -> Tuple[Dict, List[str]]:
        """Apply coin loss."""
        level = character_data.get('level', 1)

        if level <= 4:
            loss_amount = random.randint(25, 100)
            coin_type = "silver pieces"
        else:
            loss_amount = random.randint(10, 50)
            coin_type = "gold pieces"

        return character_data, [f"Lost {loss_amount} {coin_type}"]

    def _apply_item_reward(self, character_data: Dict) -> Tuple[Dict, List[str]]:
        """Apply random item reward."""
        level = character_data.get('level', 1)

        if level <= 4:
            items = ["Common magic item", "Superior equipment", "Useful tool"]
        elif level <= 10:
            items = ["Uncommon magic item", "Rare equipment", "Magical consumable"]
        else:
            items = ["Rare magic item", "Legendary equipment", "Powerful consumable"]

        item = random.choice(items)
        return character_data, [f"Received: {item}"]

    def _apply_inspiration(self, character_data: Dict) -> Tuple[Dict, List[str]]:
        """Apply inspiration reward."""
        # Inspiration is typically tracked separately, for now just log
        return character_data, ["Gained Inspiration (advantage on next ability check, attack roll, or saving throw)"]

    def _apply_consumable_reward(self, character_data: Dict) -> Tuple[Dict, List[str]]:
        """Apply consumable item reward."""
        consumables = [
            "Potion of Healing",
            "Potion of Climbing",
            "Oil of Slipperiness",
            "Scroll of Utility Spell",
            "Antitoxin",
            "Holy Water"
        ]
        item = random.choice(consumables)
        return character_data, [f"Received: {item}"]

    def _apply_healing_potion(self, character_data: Dict) -> Tuple[Dict, List[str]]:
        """Apply healing potion to inventory."""
        return character_data, ["Received: Potion of Healing (2d4+2 HP)"]

    def _apply_healers_kit(self, character_data: Dict) -> Tuple[Dict, List[str]]:
        """Apply healer's kit to inventory."""
        return character_data, ["Received: Healer's Kit (10 uses)"]

    def _apply_exhaustion(self, character_data: Dict) -> Tuple[Dict, List[str]]:
        """Apply exhaustion condition."""
        # Exhaustion would need to be tracked in conditions system
        return character_data, ["Gained one level of exhaustion"]

    def _get_dangerous_trap_damage(self, level: int) -> Tuple[str, int]:
        """Get dangerous trap damage based on character level using existing trap system."""
        # Import the trap system
        from encounter_pane.alt_encounters import TRAP_DETAILS

        # Determine level range
        if level <= 4:
            level_range = '1-4'
        elif level <= 10:
            level_range = '5-10'
        elif level <= 16:
            level_range = '11-16'
        else:
            level_range = '17-20'

        # Get dangerous trap damage for this level
        trap_info = TRAP_DETAILS[level_range]['Dangerous']
        damage_formula = trap_info['damage']

        # Roll the damage
        damage_amount = self._roll_damage_dice(damage_formula)

        return damage_formula, damage_amount

    def _roll_damage_dice(self, dice_formula: str) -> int:
        """Roll damage dice from a formula like '2d10' or '4d10'."""
        try:
            # Parse dice formula (e.g., "2d10", "4d10")
            if 'd' not in dice_formula:
                return int(dice_formula)

            num_dice, die_size = dice_formula.split('d')
            num_dice = int(num_dice)
            die_size = int(die_size)

            # Roll the dice
            total = sum(random.randint(1, die_size) for _ in range(num_dice))
            return max(1, total)  # Minimum 1 damage

        except (ValueError, AttributeError) as e:
            print(f"Error rolling damage formula '{dice_formula}': {e}")
            return random.randint(1, 6)  # Default to 1d6

    def _apply_damage(self, character_data: Dict, damage_desc: str) -> Tuple[Dict, List[str]]:
        """Apply damage to character."""
        damage_amount = 0
        damage_type = "bludgeoning"
        level = character_data.get('level', 1)

        # Check for specific damage types and use appropriate systems
        if 'dangerous trap' in damage_desc.lower():
            # Use the dangerous trap system for level-appropriate damage
            damage_formula, damage_amount = self._get_dangerous_trap_damage(level)
            damage_type = "piercing/slashing"  # Dangerous traps are typically blades/spikes
        elif 'falling' in damage_desc.lower():
            damage_amount = random.randint(1, 6) * 2  # 2d6 falling damage
            damage_type = "bludgeoning"
        elif 'bludgeoning' in damage_desc.lower():
            # Look for dice notation
            dice_match = re.search(r'(\d+)d(\d+)', damage_desc)
            if dice_match:
                num_dice, die_size = int(dice_match.group(1)), int(dice_match.group(2))
                damage_amount = sum(random.randint(1, die_size) for _ in range(num_dice))
            else:
                damage_amount = random.randint(1, 8)
            damage_type = "bludgeoning"
        elif 'force' in damage_desc.lower():
            dice_match = re.search(r'(\d+)d(\d+)', damage_desc)
            if dice_match:
                num_dice, die_size = int(dice_match.group(1)), int(dice_match.group(2))
                damage_amount = sum(random.randint(1, die_size) for _ in range(num_dice))
            else:
                damage_amount = random.randint(2, 12)
            damage_type = "force"
        else:
            # Default: use dangerous trap damage for unspecified damage
            damage_formula, damage_amount = self._get_dangerous_trap_damage(level)
            damage_type = "physical"

        # Apply damage
        current_hp = character_data.get('hit_points_current', 0)
        new_hp = max(0, current_hp - damage_amount)
        character_data['hit_points_current'] = new_hp

        return character_data, [f"Took {damage_amount} {damage_type} damage (HP: {current_hp} -> {new_hp})"]

    def _apply_poison_condition(self, character_data: Dict) -> Tuple[Dict, List[str]]:
        """Apply poisoned condition."""
        # Poison condition would need to be tracked in conditions system
        return character_data, ["Poisoned condition applied (disadvantage on attack rolls and ability checks)"]

    def _apply_quest_modifier(self, character_data: Dict, modifier: str) -> Tuple[Dict, List[str]]:
        """Apply quest difficulty modifier."""
        if 'easy' in modifier.lower():
            return character_data, ["Next quest will be easier (advantage on relevant checks)"]
        elif 'hard' in modifier.lower():
            return character_data, ["Next quest will be harder (disadvantage on relevant checks)"]
        elif 'medium' in modifier.lower():
            return character_data, ["Received a medium difficulty quest opportunity"]
        else:
            return character_data, [f"Quest modifier: {modifier}"]

    def _apply_reputation_gain(self, character_data: Dict, reward: str) -> Tuple[Dict, List[str]]:
        """Apply reputation gain."""
        # Parse reputation amount
        rep_match = re.search(r'\+(\d+)', reward)
        amount = int(rep_match.group(1)) if rep_match else 1

        return character_data, [f"Gained {amount} reputation with local faction"]

    def _apply_reputation_loss(self, character_data: Dict) -> Tuple[Dict, List[str]]:
        """Apply reputation loss."""
        return character_data, ["Lost reputation with local faction"]

    def _apply_vendor_modifier(self, character_data: Dict, modifier: str) -> Tuple[Dict, List[str]]:
        """Apply vendor price modifier."""
        if '0.8' in modifier:
            return character_data, ["Next vendor offers 20% discount on all items"]
        elif '1.2' in modifier:
            return character_data, ["Next vendor charges 20% markup on all items"]
        else:
            return character_data, [f"Vendor modifier: {modifier}"]

    def _apply_forced_encounter(self, character_data: Dict, encounter_desc: str) -> Tuple[Dict, List[str]]:
        """Apply forced encounter effect."""
        return character_data, [f"Triggered encounter: {encounter_desc}"]

    def save_character_data(self, character_data: Dict):
        """Save updated character data to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Update basic character stats
            cursor.execute('''
                UPDATE characters SET
                hit_points_current = ?,
                hit_dice_current = ?,
                death_saves_successes = ?,
                death_saves_failures = ?
                WHERE id = ?
            ''', (
                character_data.get('hit_points_current'),
                character_data.get('hit_dice_current'),
                character_data.get('death_saves_successes', 0),
                character_data.get('death_saves_failures', 0),
                character_data.get('id')
            ))

            conn.commit()

        except Exception as e:
            print(f"Error saving character data: {e}")
        finally:
            if conn:
                conn.close()

    def log_reward_application(self, character_id: str, reward_type: str,
                             description: str, details: str = ""):
        """Log reward/penalty application to database for tracking."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create a log table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS skill_challenge_rewards_log (
                    id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    reward_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    details TEXT,
                    applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (character_id) REFERENCES characters(id)
                )
            ''')

            from uuid import uuid4
            cursor.execute('''
                INSERT INTO skill_challenge_rewards_log
                (id, character_id, reward_type, description, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (str(uuid4()), character_id, reward_type, description, details))

            conn.commit()

        except Exception as e:
            print(f"Error logging reward application: {e}")
        finally:
            if conn:
                conn.close()
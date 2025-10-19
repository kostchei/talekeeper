# core
# category: core
import sqlite3
import random
from typing import Dict, List, Optional, Tuple
from uuid import uuid4


class ParlaySystem:
    """
    System for diplomatic resolution of encounters with non-evil monsters.

    - Intelligence and alignment-based skill selection
    - 4 parlay types: Diplomatic, Dangerous, Animal Handling, Desperate
    - Disadvantage for evil creatures
    - Reward: 50% of TOTAL encounter XP, no combat
    - Pickpocket: 75% XP + treasure (requires Deception + Sleight of Hand)
    """

    def __init__(self, db_path: str = 'talekeeper.db'):
        self.db_path = db_path

    def _determine_if_evil(self, alignment: str) -> bool:
        """
        Determine if creature is evil based on alignment.

        Rules:
        - "any" alignment = 1/3 chance of being evil
        - "unaligned" = not evil
        - "neutral" (alone) = not evil
        - Otherwise check if "evil" in alignment string

        Args:
            alignment: Monster alignment string

        Returns:
            True if evil, False if not evil
        """
        if not alignment:
            return False

        alignment_lower = alignment.strip().lower()

        if alignment_lower == "any":
            return random.random() < 0.33

        if alignment_lower in ("unaligned", "neutral"):
            return False

        return 'evil' in alignment_lower

    def _get_most_powerful_monster(self, monsters: List[Dict]) -> Optional[Dict]:
        """
        Get most powerful monster by XP.

        Args:
            monsters: List of monster dicts with 'xp' field

        Returns:
            Monster with highest XP, or None if empty
        """
        if not monsters:
            return None

        return max(monsters, key=lambda m: m.get('xp', 0))

    def can_parlay_with_monster(self, monster: Dict) -> bool:
        """
        Determine if a monster can be parlayed with.

        Rules:
        - Evil alignment monsters cannot be parlayed with
        - 75% of non-evil monsters can be parlayed with
        """
        alignment = monster.get('alignment', '').lower()

        if not alignment:
            return False

        if 'evil' in alignment:
            return False

        return random.random() < 0.75

    def can_parlay_with_encounter(self, monsters: List[Dict]) -> Tuple[bool, str]:
        """
        Check if an encounter can be parlayed with.
        Returns (can_parlay, reason)
        """
        if not monsters:
            return False, "No monsters in encounter"

        all_evil = all('evil' in m.get('alignment', '').lower() for m in monsters)
        if all_evil:
            return False, "These creatures are too evil to negotiate with"

        any_non_evil = any('evil' not in m.get('alignment', '').lower() for m in monsters)
        if not any_non_evil:
            return False, "These creatures cannot be reasoned with"

        if random.random() < 0.75:
            return True, "These creatures might be willing to talk"
        else:
            return False, "These creatures seem hostile and unwilling to parlay"

    def get_parlay_skills(self) -> List[str]:
        """
        Get the skills available for parlay (legacy method).

        Returns list of 4 skills:
        - 3 CHA skills
        - 1 random INT or WIS skill
        """
        cha_skills = ['Deception', 'Intimidation', 'Performance', 'Persuasion']
        int_skills = ['Arcana', 'History', 'Investigation', 'Nature', 'Religion']
        wis_skills = ['Animal Handling', 'Insight', 'Medicine', 'Perception', 'Survival']

        selected_cha = random.sample(cha_skills, 3)

        int_or_wis = random.choice([*int_skills, *wis_skills])

        return selected_cha + [int_or_wis]

    def get_parlay_skills_for_encounter(self, monsters: List[Dict]) -> Tuple[List[str], str]:
        """
        Get parlay skills based on monster intelligence and alignment.

        Uses most powerful monster to determine parlay type.

        Returns:
            Tuple of (skills_list, disadvantage_mode)
            disadvantage_mode: 'none', 'first', 'all'

        Parlay Types:
        - INT 4+, non-evil: Diplomatic (2 CHA + 1 INT/WIS, no disadvantage)
        - INT 4+, evil: Dangerous (Deception + Intimidation + random, first disadvantage)
        - INT 3-, non-evil: Animal Handling (Nature + Survival + limited, no disadvantage)
        - INT 3-, evil: Desperate (Nature + Survival + limited, all disadvantage)
        """
        if not monsters:
            return [], 'none'

        primary_monster = self._get_most_powerful_monster(monsters)
        if not primary_monster:
            return [], 'none'

        intelligence = primary_monster.get('intelligence', 10)
        alignment = primary_monster.get('alignment', '')

        is_evil = self._determine_if_evil(alignment)

        if intelligence >= 4:
            if not is_evil:
                return self._get_intelligent_non_evil_skills(), 'none'
            else:
                return self._get_intelligent_evil_skills(), 'first'
        else:
            if not is_evil:
                return self._get_simple_non_evil_skills(), 'none'
            else:
                return self._get_simple_evil_skills(), 'all'

    def _get_intelligent_non_evil_skills(self) -> List[str]:
        """2 random CHA skills + 1 random INT/WIS skill (diplomatic negotiation)."""
        cha_skills = ['Deception', 'Intimidation', 'Performance', 'Persuasion']
        int_wis_skills = [
            'Arcana', 'History', 'Investigation', 'Nature', 'Religion',
            'Animal Handling', 'Insight', 'Medicine', 'Perception', 'Survival'
        ]

        selected_cha = random.sample(cha_skills, 2)
        selected_int_wis = random.choice(int_wis_skills)

        return selected_cha + [selected_int_wis]

    def _get_intelligent_evil_skills(self) -> List[str]:
        """Deception + Intimidation + 1 random skill/tool (dangerous negotiation)."""
        all_skills = [
            'Athletics', 'Acrobatics', 'Sleight of Hand', 'Stealth',
            'Arcana', 'History', 'Investigation', 'Nature', 'Religion',
            'Animal Handling', 'Insight', 'Medicine', 'Perception', 'Survival',
            'Performance', 'Persuasion'
        ]

        tool_proficiencies = [
            "Thieves' Tools", "Smith's Tools", "Brewer's Supplies",
            "Alchemist's Supplies", "Carpenter's Tools",
            "Gaming Set (Dice)", "Gaming Set (Cards)"
        ]

        all_options = all_skills + tool_proficiencies
        random_selection = random.choice(all_options)

        return ['Deception', 'Intimidation', random_selection]

    def _get_simple_non_evil_skills(self) -> List[str]:
        """Nature + Survival + 1 from limited pool (animal handling)."""
        limited_pool = ['Medicine', 'Insight', 'Persuasion', 'Intimidation']
        random_skill = random.choice(limited_pool)

        return ['Nature', 'Survival', random_skill]

    def _get_simple_evil_skills(self) -> List[str]:
        """Nature + Survival + 1 from very limited pool (desperate parlay)."""
        very_limited_pool = ['Insight', 'Persuasion', 'Intimidation']
        random_skill = random.choice(very_limited_pool)

        return ['Nature', 'Survival', random_skill]

    def calculate_parlay_xp_reward(self, monsters: List[Dict]) -> int:
        """
        Calculate XP reward for successful parlay.

        Award 50% of TOTAL encounter XP (sum of all monsters).
        """
        if not monsters:
            return 0

        total_xp = sum(m.get('xp', 0) for m in monsters)
        return total_xp // 2

    def create_parlay_challenge(self, character_id: str, monsters: List[Dict]) -> Optional[str]:
        """
        Create a skill challenge for parlay attempt.

        Returns the session_id of the created challenge, or None if failed.
        """
        from talekeeper.services.skill_challenge_manager import SkillChallengeManager

        parlay_skills, disadvantage_mode = self.get_parlay_skills_for_encounter(monsters)
        xp_reward = self.calculate_parlay_xp_reward(monsters)

        if not parlay_skills:
            return None

        primary_monster = self._get_most_powerful_monster(monsters)
        monster_names = ', '.join(m.get('name', 'creature') for m in monsters[:3])

        level = self._get_character_level(character_id)
        base_dc = 10 + level // 2

        template_id = str(uuid4())

        intelligence = primary_monster.get('intelligence', 10) if primary_monster else 10
        alignment = primary_monster.get('alignment', 'unknown') if primary_monster else 'unknown'
        is_evil = self._determine_if_evil(alignment)

        if intelligence >= 4:
            base_name = "Dangerous Negotiation" if is_evil else "Diplomatic Parlay"
        else:
            base_name = "Desperate Parlay" if is_evil else "Animal Handling"

        template_name = f"{base_name} ({template_id[:8]})"

        template_description = f"Attempt to negotiate peaceful passage with {monster_names}."

        success_reward = f"Peaceful resolution - gain {xp_reward} XP without combat"
        failure_penalty = "Negotiations break down - combat begins"
        refuse_cost = "Walk away cautiously - no XP, no combat"

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO skill_challenge_templates
                (id, name, description, base_dc)
                VALUES (?, ?, ?, ?)
            ''', (template_id, template_name, template_description, base_dc))

            for idx, skill in enumerate(parlay_skills):
                cursor.execute('''
                    INSERT INTO skill_challenge_template_skills
                    (template_id, skill_name, skill_order)
                    VALUES (?, ?, ?)
                ''', (template_id, skill, idx))

            cursor.execute('''
                INSERT INTO skill_challenge_template_success
                (template_id, success_option)
                VALUES (?, ?)
            ''', (template_id, success_reward))

            cursor.execute('''
                INSERT INTO skill_challenge_template_failure
                (template_id, failure_option)
                VALUES (?, ?)
            ''', (template_id, failure_penalty))

            cursor.execute('''
                INSERT INTO skill_challenge_template_refuse
                (template_id, refuse_option)
                VALUES (?, ?)
            ''', (template_id, refuse_cost))

            cursor.execute('''
                INSERT INTO skill_challenge_metadata
                (template_id, metadata_key, metadata_value)
                VALUES (?, ?, ?)
            ''', (template_id, 'disadvantage_mode', disadvantage_mode))

            conn.commit()

            manager = SkillChallengeManager(self.db_path)
            template = manager.get_template_by_id(template_id)
            if template:
                session = manager.create_session(character_id, template)
                return session.id

            return None

        except Exception as e:
            print(f"Error creating parlay challenge: {e}")
            import traceback
            traceback.print_exc()
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    def _get_character_level(self, character_id: str) -> int:
        """Get character level from talekeeper.database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT level FROM characters WHERE id = ?', (character_id,))
            result = cursor.fetchone()

            return result[0] if result else 1

        except Exception as e:
            print(f"Error getting character level: {e}")
            return 1
        finally:
            if conn:
                conn.close()

    def apply_parlay_success(self, character_id: str, xp_reward: int) -> Dict[str, any]:
        """
        Apply the rewards for successful parlay.

        Returns dict with:
        - xp_gained: amount of XP awarded
        - message: success message
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE characters
                SET experience_points = experience_points + ?
                WHERE id = ?
            ''', (xp_reward, character_id))

            conn.commit()

            return {
                'xp_gained': xp_reward,
                'message': f"Diplomatic success! Gained {xp_reward} XP through peaceful negotiation."
            }

        except Exception as e:
            print(f"Error applying parlay success: {e}")
            return {'xp_gained': 0, 'message': 'Error applying parlay rewards'}
        finally:
            if conn:
                conn.close()

    def _get_monster_insight(self, monster: Dict) -> int:
        """
        Get monster Insight DC.

        If monster has Insight skill listed, use 10 + skill bonus.
        Otherwise, use raw Wisdom score (not modifier).
        """
        skills = monster.get('skills', {})
        if isinstance(skills, dict) and 'insight' in skills:
            return 10 + skills['insight']

        wisdom = monster.get('wisdom', 10)
        return wisdom

    def _get_monster_perception(self, monster: Dict) -> int:
        """
        Get monster Perception DC.

        If monster has Perception skill listed, use 10 + skill bonus.
        Otherwise, use raw Wisdom score (not modifier).
        """
        skills = monster.get('skills', {})
        if isinstance(skills, dict) and 'perception' in skills:
            return 10 + skills['perception']

        wisdom = monster.get('wisdom', 10)
        return wisdom

    def execute_pickpocket_attempt(self, character_id: str, monsters: List[Dict]) -> Dict[str, any]:
        """
        Execute pickpocket attempt with dual skill checks.

        Both Deception vs Insight AND Sleight of Hand vs Perception must succeed.

        Returns dict with:
        - success: bool
        - deception_result: dict with roll, dc, success
        - sleight_result: dict with roll, dc, success
        - xp_gained: int (75% of parlay XP if successful)
        - treasure: dict (generated item if successful)
        - message: str
        """
        from talekeeper.services.dice import dice

        if not monsters:
            return {
                'success': False,
                'message': 'No monsters to pickpocket'
            }

        primary_monster = self._get_most_powerful_monster(monsters)
        if not primary_monster:
            return {
                'success': False,
                'message': 'Could not determine target'
            }

        insight_dc = self._get_monster_insight(primary_monster)
        perception_dc = self._get_monster_perception(primary_monster)

        deception_bonus = self._get_character_skill_bonus(character_id, 'Deception')
        sleight_bonus = self._get_character_skill_bonus(character_id, 'Sleight of Hand')

        deception_roll = dice.roll('1d20') + deception_bonus
        deception_success = deception_roll >= insight_dc

        result = {
            'deception_result': {
                'roll': deception_roll,
                'dc': insight_dc,
                'success': deception_success
            }
        }

        if not deception_success:
            result['success'] = False
            result['message'] = 'Deception failed - creature noticed you'
            return result

        sleight_roll = dice.roll('1d20') + sleight_bonus
        sleight_success = sleight_roll >= perception_dc

        result['sleight_result'] = {
            'roll': sleight_roll,
            'dc': perception_dc,
            'success': sleight_success
        }

        if not sleight_success:
            result['success'] = False
            result['message'] = 'Sleight of Hand failed - creature noticed you'
            return result

        total_xp = sum(m.get('xp', 0) for m in monsters)
        pickpocket_xp = int(total_xp * 0.75)

        treasure = self._generate_individual_treasure(primary_monster)

        self._award_pickpocket_xp(character_id, pickpocket_xp)
        if treasure:
            self._add_treasure_to_inventory(character_id, treasure)

        result['success'] = True
        result['xp_gained'] = pickpocket_xp
        result['treasure'] = treasure
        result['message'] = f"Successfully pickpocketed {primary_monster.get('name', 'creature')}!"

        return result

    def _get_character_skill_bonus(self, character_id: str, skill_name: str) -> int:
        """Get character skill bonus (ability modifier + proficiency if applicable)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            ability_map = {
                'Deception': 'charisma',
                'Sleight of Hand': 'dexterity'
            }

            ability = ability_map.get(skill_name, 'charisma')

            cursor.execute(f'SELECT {ability}, proficiency_bonus FROM characters WHERE id = ?', (character_id,))
            result = cursor.fetchone()

            if not result:
                return 0

            ability_score, proficiency_bonus = result
            ability_modifier = (ability_score - 10) // 2

            cursor.execute('''
                SELECT proficient FROM character_skills
                WHERE character_id = ? AND skill_name = ?
            ''', (character_id, skill_name))
            skill_result = cursor.fetchone()

            is_proficient = skill_result and skill_result[0] == 1

            total_bonus = ability_modifier
            if is_proficient:
                total_bonus += proficiency_bonus

            return total_bonus

        except Exception as e:
            print(f"Error getting skill bonus: {e}")
            return 0
        finally:
            if conn:
                conn.close()

    def _generate_individual_treasure(self, monster: Dict) -> Optional[Dict]:
        """
        Generate individual treasure based on monster CR.

        Uses LootDropService to generate CR-appropriate item.
        """
        from talekeeper.services.loot_drop_service import LootDropService

        cr = monster.get('challenge_rating', 0)

        try:
            if isinstance(cr, str):
                if '/' in cr:
                    cr = eval(cr)
                else:
                    cr = float(cr)
            else:
                cr = float(cr)
        except:
            cr = 0

        if cr < 1:
            rarity = 'Common'
        elif cr < 5:
            rarity = 'Uncommon'
        elif cr < 11:
            rarity = 'Rare'
        elif cr < 17:
            rarity = 'Very Rare'
        else:
            rarity = 'Legendary'

        loot_service = LootDropService(self.db_path)
        items = loot_service.generate_loot_by_rarity(rarity, 1)

        if items:
            return items[0]
        return None

    def _award_pickpocket_xp(self, character_id: str, xp_amount: int) -> None:
        """Award XP for successful pickpocket."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE characters
                SET experience_points = experience_points + ?
                WHERE id = ?
            ''', (xp_amount, character_id))

            conn.commit()

        except Exception as e:
            print(f"Error awarding pickpocket XP: {e}")
        finally:
            if conn:
                conn.close()

    def _add_treasure_to_inventory(self, character_id: str, treasure: Dict) -> None:
        """Add treasure item to character inventory."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO character_inventory (character_id, item_id, quantity, equipped)
                VALUES (?, ?, 1, 0)
            ''', (character_id, treasure.get('id')))

            conn.commit()

        except Exception as e:
            print(f"Error adding treasure to inventory: {e}")
        finally:
            if conn:
                conn.close()
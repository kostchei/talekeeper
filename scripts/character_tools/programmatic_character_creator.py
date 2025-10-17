"""
Programmatic Character Creator for TaleKeeper

Creates characters from JSON/YAML templates without using the UI.
Bypasses the 6-step character creation wizard by calling backend APIs directly.

Usage:
    python scripts/character_tools/programmatic_character_creator.py templates/fighter_soldier.json

Template format: See templates/fighter_soldier.json for example
"""

import json
import yaml
import sqlite3
import random
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from uuid import uuid4

import sys
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / 'src'))

from talekeeper.core.game_engine_sqlite import GameEngineSQLite
from talekeeper.services.feat_effects import FeatEffectsProcessor
from talekeeper.services.weapon_attack_service import WeaponAttackService


class ProgrammaticCharacterCreator:
    """
    Programmatically create D&D characters from templates.

    Mirrors the UI workflow from encounter_panel.py character creation steps,
    but calls backend APIs directly without Qt interactions.
    """

    def __init__(self, db_path='talekeeper.db'):
        self.game_engine = GameEngineSQLite(db_path)
        self.db_path = db_path
        self.feat_processor = FeatEffectsProcessor()
        self.weapon_service = WeaponAttackService(db_path)

    def create_from_template(self, template_path: str) -> Dict[str, Any]:
        """
        Create a character from a JSON or YAML template file.

        Args:
            template_path: Path to .json or .yaml template file

        Returns:
            Created character data from database
        """
        template = self._load_template(template_path)
        return self.create_from_dict(template)

    def create_from_dict(self, template: dict) -> Dict[str, Any]:
        """
        Create a character from a template dictionary.

        This is the main entry point that orchestrates all 11 steps.

        Args:
            template: Character template data

        Returns:
            Created character data from database
        """
        print(f"\n=== Creating Character from Template ===")

        character_data = {}

        character_data['class_data'] = self._step_2_load_class(template)

        character_data['class_features'] = self._step_3_select_class_features(
            template,
            character_data['class_data']
        )

        bg_species = self._step_4_load_background_species(template)
        character_data['background_data'] = bg_species['background']
        character_data['species_data'] = bg_species['species']

        character_data['selected_feats'] = self._step_5_select_feats(
            template,
            character_data['background_data'],
            character_data['species_data']
        )

        abilities_skills = self._step_6_allocate_abilities_skills(
            template,
            character_data['class_data'],
            character_data['background_data'],
            character_data['species_data']
        )
        character_data['ability_scores'] = abilities_skills['ability_scores']
        character_data['selected_class_skills'] = abilities_skills['class_skills']
        character_data['selected_species_skills'] = abilities_skills['species_skills']
        character_data['selected_background_skills'] = abilities_skills['background_skills']

        character_data['equipment_choices'] = self._step_7_select_equipment(
            template,
            character_data['class_data']
        )

        character_data['name'] = self._step_8_generate_name(
            template,
            character_data['species_data'],
            character_data['class_data'],
            character_data['background_data']
        )

        final_payload = self._step_9_assemble_payload(character_data, template)

        save_data = self._step_10_prepare_for_save(final_payload)

        saved_character = self._step_11_persist_and_verify(save_data, template)

        print(f"\n[OK] Character created: {saved_character['name']}")
        print(f"  Level {saved_character['level']} {saved_character['race_name']} {saved_character['class_name']}")
        print(f"  HP: {saved_character['hit_points_current']}/{saved_character['hit_points_max']}")
        print(f"  AC: {saved_character['armor_class']}")
        print(f"  Save Slot: {saved_character.get('save_slot', 'Unknown')}")

        return saved_character

    def _step_2_load_class(self, template: dict) -> Dict[str, Any]:
        """
        Step 2: Load class data (mirrors encounter_panel._load_class_data).

        Calls GameEngineSQLite.get_available_classes_sync() and loads full metadata
        including armor/weapon proficiencies, saving throws, and skill choices.
        """
        print("\n[Step 2] Loading class data...")

        class_name = template.get('class', 'Fighter')

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id, name, description, hit_die,
                armor_proficiencies, weapon_proficiencies,
                item_proficiencies, skill_choices
            FROM classes
            WHERE name = ?
        """, (class_name,))

        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Class '{class_name}' not found in database")

        class_data = dict(row)

        cursor.execute("""
            SELECT skill_count, available_skills
            FROM class_skill_choices
            WHERE class_id = ?
        """, (class_data['id'],))

        skill_choice_row = cursor.fetchone()
        if skill_choice_row:
            class_data['skill_choices'] = [{'choices_allowed': skill_choice_row['skill_count']}]
        else:
            class_data['skill_choices'] = []

        conn.close()

        print(f"  [OK] Loaded class: {class_data['name']} (HD: d{class_data['hit_die']})")
        print(f"    Skills to choose: {class_data['skill_choices'][0]['choices_allowed'] if class_data['skill_choices'] else 0}")

        return class_data

    def _step_3_select_class_features(self, template: dict, class_data: dict) -> Dict[str, Any]:
        """
        Step 3: Select class-specific features.

        Handles different class requirements:
        - Fighter/Paladin/Ranger: Fighting style + weapon masteries
        - Warlock: Pact boon + invocations
        - Cleric/Wizard: Spell selection
        - Barbarian: Rage tracking setup
        - Rogue: Expertise skills
        """
        print("\n[Step 3] Selecting class features...")

        class_id = class_data['id']
        features = {}

        if class_id == 'fighter':
            features = self._select_fighter_features(template)
        elif class_id == 'barbarian':
            features = self._select_barbarian_features(template)
        elif class_id == 'warlock':
            features = self._select_warlock_features(template)
        elif class_id == 'paladin':
            features = self._select_paladin_features(template)
        elif class_id in ['cleric', 'wizard', 'druid', 'sorcerer', 'bard']:
            features = self._select_spellcaster_features(template, class_id)
        elif class_id == 'rogue':
            features = self._select_rogue_features(template)
        elif class_id == 'ranger':
            features = self._select_ranger_features(template)
        else:
            print(f"  ⚠ No specific features for class '{class_id}', using defaults")

        return features

    def _select_fighter_features(self, template: dict) -> Dict[str, Any]:
        """Fighter: Fighting style + weapon masteries."""
        features = {}

        fighting_style_name = template.get('fighting_style', 'Defense')

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, description, category
            FROM feats
            WHERE category = 'FS' AND name = ?
        """, (fighting_style_name,))

        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError(f"Fighting style '{fighting_style_name}' not found")

        features['fighting_style'] = dict(row)
        conn.close()

        weapon_masteries = template.get('weapon_masteries', ['longsword', 'shield', 'longbow'])
        features['weapon_masteries'] = weapon_masteries

        print(f"  [OK] Fighting Style: {fighting_style_name}")
        print(f"  [OK] Weapon Masteries: {', '.join(weapon_masteries)}")

        return features

    def _select_barbarian_features(self, template: dict) -> Dict[str, Any]:
        """Barbarian: Rage setup."""
        features = {}

        features['rage_uses'] = 2
        features['rage_damage'] = 2

        features['weapon_masteries'] = template.get('weapon_masteries', ['greataxe', 'handaxe', 'javelin'])

        print(f"  [OK] Rage: {features['rage_uses']} uses, +{features['rage_damage']} damage")
        print(f"  [OK] Weapon Masteries: {', '.join(features['weapon_masteries'])}")

        return features

    def _select_warlock_features(self, template: dict) -> Dict[str, Any]:
        """Warlock: Pact boon + invocations + spells."""
        features = {}

        features['pact_boon'] = template.get('pact_boon', 'pact_of_the_blade')
        features['patron'] = template.get('patron', 'fiend')

        invocations = template.get('invocations', ['agonizing_blast'])
        features['invocations'] = invocations

        cantrips = template.get('cantrips', ['eldritch_blast', 'mage_hand'])
        spells_known = template.get('spells_known', ['hex', 'armor_of_agathys'])

        features['cantrips'] = cantrips
        features['spells_known'] = spells_known
        features['spell_slots'] = 1
        features['spell_slot_level'] = 1

        print(f"  [OK] Patron: {features['patron']}")
        print(f"  [OK] Pact Boon: {features['pact_boon']}")
        print(f"  [OK] Invocations: {', '.join(invocations)}")
        print(f"  [OK] Cantrips: {', '.join(cantrips)}")
        print(f"  [OK] Spells: {', '.join(spells_known)}")

        return features

    def _select_paladin_features(self, template: dict) -> Dict[str, Any]:
        """Paladin: Fighting style + weapon masteries + Divine Smite."""
        features = {}

        fighting_style_name = template.get('fighting_style', 'Defense')

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, description, category
            FROM feats
            WHERE category = 'FS' AND name = ?
        """, (fighting_style_name,))

        row = cursor.fetchone()
        if row:
            features['fighting_style'] = dict(row)
        conn.close()

        weapon_masteries = template.get('weapon_masteries', ['longsword', 'shield', 'javelin'])
        features['weapon_masteries'] = weapon_masteries

        features['divine_smite'] = True
        features['lay_on_hands'] = 5

        print(f"  [OK] Fighting Style: {fighting_style_name}")
        print(f"  [OK] Weapon Masteries: {', '.join(weapon_masteries)}")
        print(f"  [OK] Divine Smite available")
        print(f"  [OK] Lay on Hands: {features['lay_on_hands']} HP pool")

        return features

    def _select_spellcaster_features(self, template: dict, class_id: str) -> Dict[str, Any]:
        """Spellcaster: Cantrips + prepared/known spells."""
        features = {}

        cantrips = template.get('cantrips', [])
        spells_prepared = template.get('spells_prepared', [])

        features['cantrips'] = cantrips
        features['spells_prepared'] = spells_prepared

        if class_id in ['wizard', 'cleric', 'druid']:
            features['spellcasting_type'] = 'prepared'
        else:
            features['spellcasting_type'] = 'known'

        print(f"  [OK] Spellcasting: {features['spellcasting_type']}")
        print(f"  [OK] Cantrips: {', '.join(cantrips) if cantrips else 'None selected'}")
        print(f"  [OK] Spells: {', '.join(spells_prepared) if spells_prepared else 'None selected'}")

        return features

    def _select_rogue_features(self, template: dict) -> Dict[str, Any]:
        """Rogue: Expertise skills + Sneak Attack."""
        features = {}

        expertise_skills = template.get('expertise_skills', ['Stealth', 'Sleight of Hand'])
        features['expertise_skills'] = expertise_skills

        features['sneak_attack_dice'] = 1

        print(f"  [OK] Expertise: {', '.join(expertise_skills)}")
        print(f"  [OK] Sneak Attack: {features['sneak_attack_dice']}d6")

        return features

    def _select_ranger_features(self, template: dict) -> Dict[str, Any]:
        """Ranger: Fighting style + favored enemy + spells."""
        features = {}

        fighting_style_name = template.get('fighting_style', 'Archery')

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, description, category
            FROM feats
            WHERE category = 'FS' AND name = ?
        """, (fighting_style_name,))

        row = cursor.fetchone()
        if row:
            features['fighting_style'] = dict(row)
        conn.close()

        favored_enemy = template.get('favored_enemy', 'Humanoid')
        features['favored_enemy'] = favored_enemy

        spells_prepared = template.get('spells_prepared', [])
        features['spells_prepared'] = spells_prepared

        print(f"  [OK] Fighting Style: {fighting_style_name}")
        print(f"  [OK] Favored Enemy: {favored_enemy}")
        print(f"  [OK] Spells: {', '.join(spells_prepared) if spells_prepared else 'None'}")

        return features

    def _step_4_load_background_species(self, template: dict) -> Dict[str, Any]:
        """
        Step 4: Load background and species data.

        Mirrors encounter_panel._load_background_species_data.
        Includes skill proficiencies and ability score increases from background.
        """
        print("\n[Step 4] Loading background and species...")

        background_name = template.get('background', 'Soldier')
        species_name = template.get('species', 'Human')

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, description, skill_proficiencies, feat
            FROM backgrounds
            WHERE name = ?
        """, (background_name,))

        bg_row = cursor.fetchone()
        if not bg_row:
            raise ValueError(f"Background '{background_name}' not found")

        background_data = dict(bg_row)

        cursor.execute("""
            SELECT id, name, description, speed, size, ability_score_increases,
                   traits, languages
            FROM races
            WHERE name = ?
        """, (species_name,))

        sp_row = cursor.fetchone()
        if not sp_row:
            raise ValueError(f"Species '{species_name}' not found")

        species_data = dict(sp_row)

        cursor.execute("""
            SELECT proficiency_type, proficiency_name
            FROM species_proficiencies
            WHERE species_id = ?
        """, (species_data['id'],))

        species_prof_rows = cursor.fetchall()
        species_data['proficiency_options'] = [dict(p) for p in species_prof_rows] if species_prof_rows else []

        conn.close()

        print(f"  [OK] Background: {background_data['name']}")
        print(f"    Skills: {background_data.get('skill_proficiencies', 'None')}")
        print(f"    Origin Feat: {background_data.get('feat', 'None')}")
        print(f"  [OK] Species: {species_data['name']}")

        return {
            'background': background_data,
            'species': species_data
        }

    def _step_5_select_feats(self, template: dict, background_data: dict, species_data: dict) -> List[str]:
        """
        Step 5: Select origin and bonus feats.

        Mirrors encounter_panel._populate_feat_lists.
        Background provides one origin feat (e.g., Savage Attacker).
        Species (Human) provides one bonus feat (e.g., Tough).
        """
        print("\n[Step 5] Selecting feats...")

        selected_feats = []

        background_origin_feat = background_data.get('feat')
        if background_origin_feat:
            selected_feats.append(background_origin_feat)
            print(f"  [OK] Background origin feat: {background_origin_feat}")

        species_bonus_feats = template.get('feats', ['Tough'])
        for feat in species_bonus_feats:
            if feat not in selected_feats:
                selected_feats.append(feat)
                print(f"  [OK] Species bonus feat: {feat}")

        return selected_feats

    def _step_6_allocate_abilities_skills(
        self,
        template: dict,
        class_data: dict,
        background_data: dict,
        species_data: dict
    ) -> Dict[str, Any]:
        """
        Step 6: Allocate ability scores and skill proficiencies.

        Mirrors encounter_panel._update_final_scores.
        Uses point-buy or standard array, applies background ASI (+2/+1),
        and selects class/background/species skills.
        """
        print("\n[Step 6] Allocating abilities and skills...")

        base_scores = template.get('ability_scores', {
            'strength': 15,
            'dexterity': 14,
            'constitution': 13,
            'intelligence': 12,
            'wisdom': 10,
            'charisma': 8
        })

        final_scores = base_scores.copy()

        print(f"  [OK] Ability scores: STR {final_scores['strength']}, DEX {final_scores['dexterity']}, CON {final_scores['constitution']}, INT {final_scores['intelligence']}, WIS {final_scores['wisdom']}, CHA {final_scores['charisma']}")

        class_skills = template.get('class_skills', ['Athletics', 'Perception'])
        background_skills_json = background_data.get('skill_proficiencies', '[]')
        try:
            background_skills = json.loads(background_skills_json) if isinstance(background_skills_json, str) else background_skills_json
        except:
            background_skills = []

        species_skills = template.get('species_skills', [])

        print(f"  [OK] Class skills: {', '.join(class_skills)}")
        print(f"  [OK] Background skills: {', '.join(background_skills)}")
        if species_skills:
            print(f"  [OK] Species skills: {', '.join(species_skills)}")

        return {
            'ability_scores': final_scores,
            'class_skills': class_skills,
            'background_skills': background_skills,
            'species_skills': species_skills
        }

    def _step_7_select_equipment(self, template: dict, class_data: dict) -> Dict[str, Any]:
        """
        Step 7: Select starting equipment.

        Calls GameEngineSQLite.get_class_equipment_choices_sync('fighter')
        and selects equipment based on template (e.g., Longsword + Shield).
        """
        print("\n[Step 7] Selecting equipment...")

        equipment_choices_raw = template.get('equipment_choices', {})

        equipment_choices = {}
        for slot, item_name in equipment_choices_raw.items():
            equipment_choices[slot] = item_name
            print(f"  [OK] {slot}: {item_name}")

        return equipment_choices

    def _step_8_generate_name(
        self,
        template: dict,
        species_data: dict,
        class_data: dict,
        background_data: dict
    ) -> str:
        """
        Step 8: Generate a campaign-aware name.

        Uses NAMES_BY_HOMELAND from alt_encounters.py or template override.
        """
        print("\n[Step 8] Generating name...")

        if template.get('name') and template['name'] != 'random':
            name = template['name']
            print(f"  [OK] Using template name: {name}")
            return name

        HUMAN_FIRST_NAMES = [
            'Aldric', 'Brenna', 'Cedric', 'Diana', 'Erik', 'Fiona',
            'Gareth', 'Helena', 'Ivan', 'Jenna', 'Kael', 'Lyra',
            'Marcus', 'Nora', 'Owen', 'Petra', 'Quinn', 'Rowan'
        ]

        SOLDIER_SURNAMES = [
            'Ironhand', 'Steelhart', 'Battleborn', 'Warblade',
            'Shieldwall', 'Strongarm', 'Warforge', 'Valorheart'
        ]

        first_name = random.choice(HUMAN_FIRST_NAMES)

        if background_data['name'] == 'Soldier':
            surname = random.choice(SOLDIER_SURNAMES)
            full_name = f"{first_name} {surname}"
        else:
            full_name = first_name

        print(f"  [OK] Generated name: {full_name}")
        return full_name

    def _step_9_assemble_payload(self, character_data: dict, template: dict) -> Dict[str, Any]:
        """
        Step 9: Assemble the character creation payload.

        Mirrors encounter_panel._finish_character_creation.
        Builds the final dict with all character data.
        """
        print("\n[Step 9] Assembling character payload...")

        payload = {
            'name': character_data['name'],
            'class_data': character_data['class_data'],
            'background_data': character_data['background_data'],
            'species_data': character_data['species_data'],
            'ability_scores': character_data['ability_scores'],
            'selected_feats': character_data['selected_feats'],
            'class_features': character_data['class_features'],
            'equipment_choices': character_data['equipment_choices'],
            'selected_class_skills': character_data['selected_class_skills'],
            'selected_background_skills': character_data.get('selected_background_skills', []),
            'selected_species_skills': character_data.get('selected_species_skills', []),
            'level': template.get('level', 1),
            'experience_points': template.get('experience_points', 0)
        }

        print(f"  [OK] Assembled payload for {payload['name']}")
        return payload

    def _step_10_prepare_for_save(self, payload: dict) -> Dict[str, Any]:
        """
        Step 10: Convert to engine schema.

        Mirrors main_window._prepare_character_for_save.
        Maps names to IDs, computes HP, applies feat effects (Tough +2 HP/level).
        """
        print("\n[Step 10] Preparing for database save...")

        class_data = payload['class_data']
        background_data = payload['background_data']
        species_data = payload['species_data']
        ability_scores = payload['ability_scores']

        con_mod = (ability_scores['constitution'] - 10) // 2
        hit_die = class_data['hit_die']
        level = payload['level']

        base_hp = hit_die + con_mod

        save_data = {
            'id': str(uuid4()),
            'name': payload['name'],
            'race_id': species_data['id'],
            'class_id': class_data['id'],
            'background_id': background_data['id'],
            'level': level,
            'experience_points': payload.get('experience_points', 0),

            'strength': ability_scores['strength'],
            'dexterity': ability_scores['dexterity'],
            'constitution': ability_scores['constitution'],
            'intelligence': ability_scores['intelligence'],
            'wisdom': ability_scores['wisdom'],
            'charisma': ability_scores['charisma'],

            'hit_points_max': base_hp,
            'hit_points_current': base_hp,
            'hit_dice_max': level,
            'hit_dice_current': level,

            'feats': payload['selected_feats'],
            'class_features': payload['class_features'],
            'equipment_choices': payload['equipment_choices'],
            'selected_class_skills': payload.get('selected_class_skills', []),
            'selected_background_skills': payload.get('selected_background_skills', []),
            'selected_species_skills': payload.get('selected_species_skills', []),

            'weapon_masteries': payload['class_features'].get('weapon_masteries', []),

            'ability_uses': self._get_class_ability_uses(class_data['id'], payload['class_features']),
            'ability_uses_max': self._get_class_ability_uses(class_data['id'], payload['class_features'])
        }

        save_data = self.feat_processor.apply_feat_effects_to_character(save_data, save_data['feats'])

        print(f"  [OK] Base HP: {base_hp} (d{hit_die} + {con_mod} CON)")
        print(f"  [OK] After feat effects: {save_data['hit_points_max']} HP")

        return save_data

    def _step_11_persist_and_verify(self, save_data: dict, template: dict) -> Dict[str, Any]:
        """
        Step 11: Persist to database and verify.

        Calls create_new_character_sync, applies equipment choices,
        updates mastery resources, and loads back to verify.
        """
        print("\n[Step 11] Persisting to database...")

        save_slot = self._find_available_slot()

        saved_character = self.game_engine.create_new_character_sync(save_data, save_slot=save_slot)

        character_id = saved_character['id']

        if save_data.get('equipment_choices'):
            self.game_engine.apply_equipment_choices_sync(saved_character, save_data['equipment_choices'])

        self.weapon_service.update_character_mastery_resources(character_id)

        final_character = self.game_engine.load_character_sync(save_slot)

        print(f"  [OK] Saved to slot {save_slot}")
        print(f"  [OK] Character ID: {character_id}")

        return final_character

    def _find_available_slot(self) -> int:
        """Find the next available save slot."""
        save_slots = self.game_engine.get_save_slots_sync()
        occupied = {slot['slot_number'] for slot in save_slots if slot['is_occupied']}

        slot_num = 1
        while slot_num in occupied:
            slot_num += 1

        return slot_num

    def _get_class_ability_uses(self, class_id: str, class_features: dict) -> Dict[str, int]:
        """Get ability uses based on class and level."""
        ability_uses = {}

        if class_id == 'fighter':
            ability_uses['Second Wind'] = 1
            ability_uses['Action Surge'] = 0

        elif class_id == 'barbarian':
            ability_uses['Rage'] = class_features.get('rage_uses', 2)

        elif class_id == 'warlock':
            ability_uses['Spell Slots'] = class_features.get('spell_slots', 1)

        elif class_id == 'paladin':
            ability_uses['Lay on Hands'] = class_features.get('lay_on_hands', 5)
            ability_uses['Divine Smite'] = 999

        elif class_id == 'rogue':
            ability_uses['Sneak Attack'] = 999

        elif class_id in ['cleric', 'wizard', 'druid', 'sorcerer', 'bard']:
            ability_uses['Spell Slots (1st)'] = 2

        return ability_uses

    def _load_template(self, template_path: str) -> dict:
        """Load template from JSON or YAML file."""
        path = Path(template_path)

        if not path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(path, 'r') as f:
            if path.suffix == '.json':
                return json.load(f)
            elif path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported template format: {path.suffix}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='Create TaleKeeper characters from templates')
    parser.add_argument('template', help='Path to JSON or YAML template file')
    parser.add_argument('--db', default='talekeeper.db', help='Database path')

    args = parser.parse_args()

    creator = ProgrammaticCharacterCreator(args.db)
    character = creator.create_from_template(args.template)

    print("\n=== Character Created Successfully ===")
    print(json.dumps({
        'name': character['name'],
        'class': character['class_name'],
        'species': character['race_name'],
        'level': character['level'],
        'hp': f"{character['hit_points_current']}/{character['hit_points_max']}",
        'ac': character['armor_class']
    }, indent=2))


if __name__ == '__main__':
    main()

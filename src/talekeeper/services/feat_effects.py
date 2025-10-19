# core
# category: core
"""
Feat Effects Processor for TaleKeeper

Handles the mechanical effects of feats on character statistics and abilities.
Processes feat data from feats_srd.json and applies bonuses to character models.

Supported Effects:
- Hit Point bonuses (Tough feat)
- Ability score improvements (Linguist, etc.)
- Skill/tool/language proficiencies
- Additional spells (Magic Initiate, etc.)
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class FeatEffect:
    """Represents a single mechanical effect from a feat."""
    feat_name: str
    effect_type: str  # 'hit_points', 'ability_score', 'proficiency', 'spells'
    value: Any
    description: str


class FeatEffectsProcessor:
    """Processes feat mechanical effects and applies them to characters."""
    
    def __init__(self, feats_file_path: str = None):
        """Initialize with feat data."""
        self.feats_data = {}
        self._load_feats_data(feats_file_path)
    
    def _load_feats_data(self, feats_file_path: str = None):
        """Load feat data from talekeeper.database."""
        try:
            import sqlite3
            conn = sqlite3.connect("talekeeper.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM feats")
            feats_rows = cursor.fetchall()
            
            # Index feats by name for quick lookup
            for feat_row in feats_rows:
                feat_data = {
                    'name': feat_row[1],
                    'description': feat_row[2],
                    'prerequisites': json.loads(feat_row[3]),
                    'ability_score_increases': json.loads(feat_row[4]),
                    'benefits': json.loads(feat_row[5])
                }
                self.feats_data[feat_data['name']] = feat_data
            
            conn.close()
                    
        except Exception as e:
            print(f"Error loading feats data: {e}")
            self.feats_data = {}
    
    def get_feat_effects(self, feat_name: str) -> List[FeatEffect]:
        """Get all mechanical effects for a given feat."""
        effects = []
        
        # Handle Tough feat directly (common case)
        if feat_name == 'Tough':
            effects.append(FeatEffect(
                feat_name='Tough',
                effect_type='hit_points',
                value={'per_level': 2, 'initial_bonus': True},
                description='Hit Point maximum increases by 2 per character level'
            ))
            return effects
        
        feat_data = self.feats_data.get(feat_name)
        if not feat_data:
            return []
        
        # Hit point bonuses (like Tough)
        hp_effect = self._get_hit_point_effect(feat_data)
        if hp_effect:
            effects.append(hp_effect)
        
        # Ability score improvements
        ability_effects = self._get_ability_score_effects(feat_data)
        effects.extend(ability_effects)
        
        # Proficiency effects
        prof_effects = self._get_proficiency_effects(feat_data)
        effects.extend(prof_effects)
        
        # Spell effects
        spell_effects = self._get_spell_effects(feat_data)
        effects.extend(spell_effects)
        
        # Combat effects (initiative, damage, etc.)
        combat_effects = self._get_combat_effects(feat_data)
        effects.extend(combat_effects)
        
        return effects
    
    def _get_hit_point_effect(self, feat_data: Dict) -> Optional[FeatEffect]:
        """Check if feat provides hit point bonuses."""
        feat_name = feat_data.get('name', '')
        
        # Special case for Tough feat
        if feat_name == 'Tough':
            entries = feat_data.get('entries', [])
            for entry in entries:
                if isinstance(entry, str) and 'Hit Point' in entry:
                    return FeatEffect(
                        feat_name=feat_name,
                        effect_type='hit_points',
                        value={'per_level': 2, 'initial_bonus': True},
                        description='Hit Point maximum increases by 2 per character level'
                    )
        
        return None
    
    def _get_ability_score_effects(self, feat_data: Dict) -> List[FeatEffect]:
        """Check if feat provides ability score improvements."""
        feat_name = feat_data.get('name', '')
        effects = []
        
        ability_bonuses = feat_data.get('ability', [])
        for bonus in ability_bonuses:
            if isinstance(bonus, dict):
                for ability, value in bonus.items():
                    if ability in ['str', 'dex', 'con', 'int', 'wis', 'cha']:
                        # Convert short names to full names
                        ability_full = {
                            'str': 'strength', 'dex': 'dexterity', 'con': 'constitution',
                            'int': 'intelligence', 'wis': 'wisdom', 'cha': 'charisma'
                        }.get(ability, ability)
                        
                        effects.append(FeatEffect(
                            feat_name=feat_name,
                            effect_type='ability_score',
                            value={'ability': ability_full, 'bonus': value},
                            description=f'+{value} {ability_full.title()}'
                        ))
        
        return effects
    
    def _get_proficiency_effects(self, feat_data: Dict) -> List[FeatEffect]:
        """Check if feat provides proficiency bonuses."""
        feat_name = feat_data.get('name', '')
        effects = []
        
        # Tool proficiencies
        tool_profs = feat_data.get('toolProficiencies', [])
        if tool_profs:
            effects.append(FeatEffect(
                feat_name=feat_name,
                effect_type='proficiency',
                value={'type': 'tools', 'data': tool_profs},
                description='Tool proficiencies'
            ))
        
        # Skill proficiencies
        skill_profs = feat_data.get('skillProficiencies', [])
        if skill_profs:
            effects.append(FeatEffect(
                feat_name=feat_name,
                effect_type='proficiency',
                value={'type': 'skills', 'data': skill_profs},
                description='Skill proficiencies'
            ))
        
        # Language proficiencies
        lang_profs = feat_data.get('languageProficiencies', [])
        if lang_profs:
            effects.append(FeatEffect(
                feat_name=feat_name,
                effect_type='proficiency',
                value={'type': 'languages', 'data': lang_profs},
                description='Language proficiencies'
            ))
        
        return effects
    
    def _get_spell_effects(self, feat_data: Dict) -> List[FeatEffect]:
        """Check if feat provides additional spells."""
        feat_name = feat_data.get('name', '')
        effects = []
        
        additional_spells = feat_data.get('additionalSpells', [])
        if additional_spells:
            effects.append(FeatEffect(
                feat_name=feat_name,
                effect_type='spells',
                value={'spells': additional_spells},
                description='Additional spells'
            ))
        
        return effects
    
    def _get_combat_effects(self, feat_data: Dict) -> List[FeatEffect]:
        """Check if feat provides combat-related effects."""
        feat_name = feat_data.get('name', '')
        effects = []
        
        # Alert feat - Initiative Proficiency and Advantage
        if feat_name == 'Alert':
            effects.append(FeatEffect(
                feat_name=feat_name,
                effect_type='combat',
                value={'type': 'initiative_proficiency'},
                description='Add proficiency bonus to Initiative rolls'
            ))
            effects.append(FeatEffect(
                feat_name=feat_name,
                effect_type='combat',
                value={'type': 'initiative_advantage'},
                description='Advantage on Initiative rolls (solo play adaptation)'
            ))
        
        # Savage Attacker - Damage reroll
        elif feat_name == 'Savage Attacker':
            effects.append(FeatEffect(
                feat_name=feat_name,
                effect_type='combat',
                value={'type': 'damage_reroll', 'frequency': 'once_per_turn'},
                description='Reroll weapon damage dice once per turn'
            ))
        
        # Tavern Brawler - Enhanced Unarmed Strike
        elif feat_name == 'Tavern Brawler':
            effects.append(FeatEffect(
                feat_name=feat_name,
                effect_type='combat',
                value={'type': 'enhanced_unarmed_strike', 'damage': '1d4', 'reroll_ones': True},
                description='Enhanced Unarmed Strike (1d4 + STR) with damage rerolls'
            ))
        
        # Lucky feat - Luck points
        elif feat_name == 'Lucky':
            effects.append(FeatEffect(
                feat_name=feat_name,
                effect_type='resource',
                value={'type': 'luck_points', 'amount': 'proficiency_bonus', 'recharge': 'long_rest'},
                description='Luck Points equal to proficiency bonus'
            ))
        
        return effects
    
    def apply_feat_effects_to_character(self, character_data: Dict, feat_names: List[str]) -> Dict:
        """Apply all feat effects to a character's data."""
        modified_data = character_data.copy()
        
        for feat_name in feat_names:
            effects = self.get_feat_effects(feat_name)
            
            for effect in effects:
                if effect.effect_type == 'hit_points':
                    modified_data = self._apply_hit_point_effect(modified_data, effect)
                elif effect.effect_type == 'ability_score':
                    modified_data = self._apply_ability_score_effect(modified_data, effect)
                elif effect.effect_type == 'proficiency':
                    modified_data = self._apply_proficiency_effect(modified_data, effect)
                elif effect.effect_type == 'combat':
                    modified_data = self._apply_combat_effect(modified_data, effect)
                elif effect.effect_type == 'resource':
                    modified_data = self._apply_resource_effect(modified_data, effect)
                # Spells would be handled separately in spell system
        
        return modified_data
    
    def _apply_hit_point_effect(self, character_data: Dict, effect: FeatEffect) -> Dict:
        """Apply hit point bonuses from feats."""
        if effect.feat_name == 'Tough':
            character_level = character_data.get('level', 1)
            
            # Tough gives +2 HP per level
            hp_bonus = 2 * character_level
            
            # Apply to max HP
            current_max = character_data.get('hit_points_max', 8)
            character_data['hit_points_max'] = current_max + hp_bonus
            
            # Also update alternative field names for combat system
            character_data['max_hit_points'] = character_data['hit_points_max']
            
            # If at full health, increase current HP too
            current_hp = character_data.get('hit_points_current', 8)
            original_max = character_data.get('hit_points_max', 8) - hp_bonus
            if current_hp >= original_max:  # Was at full health
                character_data['hit_points_current'] = character_data['hit_points_max']
                character_data['current_hit_points'] = character_data['hit_points_max']
        
        return character_data
    
    def _apply_ability_score_effect(self, character_data: Dict, effect: FeatEffect) -> Dict:
        """Apply ability score bonuses from feats."""
        value = effect.value
        ability = value.get('ability')
        bonus = value.get('bonus', 0)
        
        if ability and bonus:
            current_score = character_data.get(ability, 10)
            character_data[ability] = min(20, current_score + bonus)  # Cap at 20
        
        return character_data
    
    def _apply_proficiency_effect(self, character_data: Dict, effect: FeatEffect) -> Dict:
        """Apply proficiency bonuses from feats."""
        # For now, just add to the proficiencies list
        # More complex implementation would handle specific tool/skill/language tracking
        if 'proficiencies' not in character_data:
            character_data['proficiencies'] = []
        
        prof_description = f"{effect.feat_name}: {effect.description}"
        if prof_description not in character_data['proficiencies']:
            character_data['proficiencies'].append(prof_description)
        
        return character_data
    
    def _apply_combat_effect(self, character_data: Dict, effect: FeatEffect) -> Dict:
        """Apply combat-related effects from feats."""
        if 'feat_combat_effects' not in character_data:
            character_data['feat_combat_effects'] = []
        
        combat_effect = {
            'feat_name': effect.feat_name,
            'effect_type': effect.value.get('type'),
            'effect_data': effect.value,
            'description': effect.description
        }
        
        # Don't duplicate effects
        existing_effects = [e for e in character_data['feat_combat_effects'] 
                          if e.get('feat_name') == effect.feat_name]
        if not existing_effects:
            character_data['feat_combat_effects'].append(combat_effect)
        
        return character_data
    
    def _apply_resource_effect(self, character_data: Dict, effect: FeatEffect) -> Dict:
        """Apply resource-based effects from feats."""
        if 'feat_resources' not in character_data:
            character_data['feat_resources'] = {}
        
        resource_name = f"{effect.feat_name}_{effect.value.get('type')}"
        
        # Calculate resource amount
        if effect.value.get('amount') == 'proficiency_bonus':
            proficiency_bonus = max(2, 2 + (character_data.get('level', 1) - 1) // 4)
            amount = proficiency_bonus
        else:
            amount = effect.value.get('amount', 1)
        
        character_data['feat_resources'][resource_name] = {
            'current': amount,
            'maximum': amount,
            'recharge': effect.value.get('recharge', 'long_rest'),
            'description': effect.description
        }
        
        return character_data


# Test the processor
if __name__ == "__main__":
    processor = FeatEffectsProcessor()
    
    # Test Tough feat
    tough_effects = processor.get_feat_effects("Tough")
    print(f"Tough feat effects: {[e.description for e in tough_effects]}")
    
    # Test applying to a character
    test_char = {'level': 3, 'hit_points_max': 12, 'hit_points_current': 12}
    modified_char = processor.apply_feat_effects_to_character(test_char, ["Tough"])
    print(f"Level 3 character with Tough: {modified_char['hit_points_max']} max HP")
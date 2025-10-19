# core
# category: core
from typing import Dict, List, Any
from .base_handler import SpellHandler, roll_dice


class ShieldOfFaithHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else caster_id

        self.concentration.start_concentration(
            caster_id, 'shield_of_faith', slot_level, duration_rounds=100
        )

        buff_data = {
            'source': 'shield_of_faith',
            'spell_name': 'Shield of Faith',
            'spell_level': slot_level,
            'type': 'ac_bonus',
            'value': 2
        }

        result = self.effects.apply_buff(target_id, buff_data, duration_rounds=100,
                                         caster_id=caster_id, concentration=True)

        return {
            **result,
            'spell_name': 'Shield of Faith',
            'ac_bonus': 2,
            'duration': '10 minutes',
            'concentration': True,
            'target': target_id
        }


class DivineFavorHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        self.concentration.start_concentration(
            caster_id, 'divine_favor', slot_level, duration_rounds=10
        )

        buff_data = {
            'source': 'divine_favor',
            'spell_name': 'Divine Favor',
            'spell_level': slot_level,
            'type': 'damage_bonus_per_hit',
            'damage_dice': '1d4',
            'damage_type': 'radiant'
        }

        result = self.effects.apply_buff(caster_id, buff_data, duration_rounds=10,
                                         caster_id=caster_id, concentration=True)

        return {
            **result,
            'spell_name': 'Divine Favor',
            'damage_bonus': '1d4 radiant',
            'duration': '1 minute',
            'concentration': True
        }


class AidHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else caster_id

        hp_increase = 5 * slot_level

        buff_data = {
            'source': 'aid',
            'spell_name': 'Aid',
            'spell_level': slot_level,
            'type': 'hp_maximum_increase',
            'value': hp_increase
        }

        result = self.effects.apply_buff(target_id, buff_data, duration_rounds=4800,
                                         caster_id=caster_id, concentration=False)

        healing_result = self.effects.apply_healing(target_id, hp_increase, 'aid')

        return {
            **result,
            'spell_name': 'Aid',
            'hp_increase': hp_increase,
            'duration': '8 hours',
            'concentration': False,
            'healing': healing_result.get('healing', 0),
            'new_hp': healing_result.get('new_hp', 0)
        }


class BlessHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        self.concentration.start_concentration(
            caster_id, 'bless', slot_level, duration_rounds=10
        )

        target_id = targets[0] if targets else caster_id

        buff_data = {
            'source': 'bless',
            'spell_name': 'Bless',
            'spell_level': slot_level,
            'type': 'attack_and_save_bonus',
            'bonus_dice': '1d4',
            'applies_to': ['attack_rolls', 'saving_throws']
        }

        result = self.effects.apply_buff(target_id, buff_data, duration_rounds=10,
                                         caster_id=caster_id, concentration=True)

        return {
            **result,
            'spell_name': 'Bless',
            'bonus': '1d4 to attacks and saves',
            'duration': '1 minute',
            'concentration': True,
            'target': target_id
        }


class HeroismHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else caster_id

        self.concentration.start_concentration(
            caster_id, 'heroism', slot_level, duration_rounds=10
        )

        caster_data = context.get('caster', {})
        spellcasting_mod = caster_data.get('spellcasting_ability_mod', 0)

        buff_data = {
            'source': 'heroism',
            'spell_name': 'Heroism',
            'spell_level': slot_level,
            'type': 'temp_hp_per_turn',
            'temp_hp_per_turn': spellcasting_mod,
            'condition_immunity': 'frightened'
        }

        result = self.effects.apply_buff(target_id, buff_data, duration_rounds=10,
                                         caster_id=caster_id, concentration=True)

        condition_buff_data = {
            'source': 'heroism',
            'spell_name': 'Heroism',
            'spell_level': slot_level,
            'type': 'condition_immunity',
            'condition': 'frightened'
        }

        self.effects.apply_buff(target_id, condition_buff_data, duration_rounds=10,
                               caster_id=caster_id, concentration=True)

        return {
            **result,
            'spell_name': 'Heroism',
            'temp_hp_per_turn': spellcasting_mod,
            'immunity': 'frightened',
            'duration': '1 minute',
            'concentration': True,
            'target': target_id
        }


class MagicWeaponHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else caster_id

        self.concentration.start_concentration(
            caster_id, 'magic_weapon', slot_level, duration_rounds=60
        )

        bonus = 1 if slot_level < 4 else (2 if slot_level < 6 else 3)

        buff_data = {
            'source': 'magic_weapon',
            'spell_name': 'Magic Weapon',
            'spell_level': slot_level,
            'type': 'weapon_enchantment',
            'attack_bonus': bonus,
            'damage_bonus': bonus,
            'makes_magical': True
        }

        result = self.effects.apply_buff(target_id, buff_data, duration_rounds=60,
                                         caster_id=caster_id, concentration=True)

        return {
            **result,
            'spell_name': 'Magic Weapon',
            'bonus': f'+{bonus}',
            'duration': '1 hour',
            'concentration': True,
            'target': target_id
        }


class WardingBondHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else caster_id

        buff_data = {
            'source': 'warding_bond',
            'spell_name': 'Warding Bond',
            'spell_level': slot_level,
            'type': 'warding_bond',
            'ac_bonus': 1,
            'saving_throw_bonus': 1,
            'resistance': 'all',
            'caster_id': caster_id,
            'shares_damage': True
        }

        result = self.effects.apply_buff(target_id, buff_data, duration_rounds=60,
                                         caster_id=caster_id, concentration=False)

        return {
            **result,
            'spell_name': 'Warding Bond',
            'ac_bonus': 1,
            'save_bonus': 1,
            'resistance': 'all damage',
            'damage_sharing': 'caster takes half',
            'duration': '1 hour',
            'concentration': False,
            'target': target_id
        }


class DeathWardHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else caster_id

        buff_data = {
            'source': 'death_ward',
            'spell_name': 'Death Ward',
            'spell_level': slot_level,
            'type': 'death_ward',
            'prevents_death': True,
            'restore_to_1_hp': True
        }

        result = self.effects.apply_buff(target_id, buff_data, duration_rounds=4800,
                                         caster_id=caster_id, concentration=False)

        return {
            **result,
            'spell_name': 'Death Ward',
            'effect': 'Prevents death once',
            'restores_to': '1 HP',
            'duration': '8 hours',
            'concentration': False,
            'target': target_id
        }


class AuraOfLifeHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        self.concentration.start_concentration(
            caster_id, 'aura_of_life', slot_level, duration_rounds=100
        )

        buff_data = {
            'source': 'aura_of_life',
            'spell_name': 'Aura of Life',
            'spell_level': slot_level,
            'type': 'aura_of_life',
            'resistance': 'necrotic',
            'aura_radius': 30,
            'heals_unconscious': True,
            'unconscious_heal_amount': 1
        }

        result = self.effects.apply_buff(caster_id, buff_data, duration_rounds=100,
                                         caster_id=caster_id, concentration=True)

        return {
            **result,
            'spell_name': 'Aura of Life',
            'resistance': 'necrotic',
            'aura_radius': '30 feet',
            'unconscious_heal': '1 HP per turn',
            'duration': '10 minutes',
            'concentration': True
        }


class ProtectionFromEvilAndGoodHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else caster_id

        self.concentration.start_concentration(
            caster_id, 'protection_from_evil_and_good', slot_level, duration_rounds=100
        )

        buff_data = {
            'source': 'protection_from_evil_and_good',
            'spell_name': 'Protection from Evil and Good',
            'spell_level': slot_level,
            'type': 'protection_from_evil_and_good',
            'protected_types': ['aberrations', 'celestials', 'elementals',
                               'fey', 'fiends', 'undead'],
            'disadvantage_on_attacks': True,
            'cant_be_charmed_frightened_possessed': True
        }

        result = self.effects.apply_buff(target_id, buff_data, duration_rounds=100,
                                         caster_id=caster_id, concentration=True)

        return {
            **result,
            'spell_name': 'Protection from Evil and Good',
            'protected_from': '6 creature types',
            'effects': 'Disadvantage on attacks, immunity to charm/fear/possession',
            'duration': '10 minutes',
            'concentration': True,
            'target': target_id
        }


class ShiningSMiteHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        self.concentration.start_concentration(
            caster_id, 'shining_smite', slot_level, duration_rounds=10
        )

        damage_dice = 2 + (slot_level - 2)

        buff_data = {
            'source': 'shining_smite',
            'spell_name': 'Shining Smite',
            'spell_level': slot_level,
            'type': 'next_hit_bonus_damage',
            'damage_dice': damage_dice,
            'damage_die_type': 'd6',
            'damage_type': 'radiant',
            'on_hit_apply_condition': 'illuminated',
            'grants_advantage': True
        }

        result = self.effects.apply_buff(caster_id, buff_data, duration_rounds=10,
                                         caster_id=caster_id, concentration=True)

        return {
            **result,
            'spell_name': 'Shining Smite',
            'damage': f'{damage_dice}d6 radiant',
            'effect': 'Target sheds light, attacks have advantage',
            'duration': '1 minute',
            'concentration': True
        }


class ZoneOfTruthHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        buff_data = {
            'source': 'zone_of_truth',
            'spell_name': 'Zone of Truth',
            'spell_level': slot_level,
            'type': 'zone_of_truth',
            'radius': 15,
            'prevents_lies': True,
            'save_dc': context.get('spell_save_dc', 8)
        }

        result = self.effects.apply_buff(caster_id, buff_data, duration_rounds=100,
                                         caster_id=caster_id, concentration=False)

        return {
            **result,
            'spell_name': 'Zone of Truth',
            'radius': '15 feet',
            'effect': 'Creatures cannot lie (Cha save)',
            'duration': '10 minutes',
            'concentration': False
        }

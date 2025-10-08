from typing import Dict, List, Any
from .base_handler import SpellHandler, roll_dice


class CommandHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else None

        if not target_id:
            return {
                'success': False,
                'reason': 'Command requires a target'
            }

        dc = self._get_spell_save_dc(caster_id)
        saved = self._make_save(target_id, 'wisdom', dc)

        if saved:
            return {
                'success': True,
                'spell_name': 'Command',
                'target': target_id,
                'saved': True,
                'effect': 'Target resisted the command'
            }

        command_word = context.get('command_word', 'flee')

        buff_data = {
            'source': 'command',
            'spell_name': 'Command',
            'spell_level': slot_level,
            'type': 'command_effect',
            'command_word': command_word,
            'save_dc': dc
        }

        result = self.effects.apply_buff(target_id, buff_data, duration_rounds=1,
                                        caster_id=caster_id, concentration=False)

        return {
            **result,
            'spell_name': 'Command',
            'target': target_id,
            'saved': False,
            'command': command_word,
            'duration': '1 round'
        }


class PurifyFoodAndDrinkHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:

        return {
            'success': True,
            'spell_name': 'Purify Food and Drink',
            'effect': 'All nonmagical food and drink within 5-foot radius is purified',
            'removes': 'Poison and disease',
            'instant': True
        }


class GentleReposeHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else None

        if not target_id:
            return {
                'success': False,
                'reason': 'Gentle Repose requires a corpse target'
            }

        buff_data = {
            'source': 'gentle_repose',
            'spell_name': 'Gentle Repose',
            'spell_level': slot_level,
            'type': 'gentle_repose',
            'prevents_decay': True,
            'prevents_undead': True
        }

        result = self.effects.apply_buff(target_id, buff_data, duration_rounds=14400,
                                        caster_id=caster_id, concentration=False)

        return {
            **result,
            'spell_name': 'Gentle Repose',
            'target': target_id,
            'effect': 'Corpse protected from decay and becoming undead',
            'duration': '10 days'
        }


class LesserRestorationHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else caster_id

        condition_to_remove = context.get('condition', None)

        removable_conditions = ['blinded', 'deafened', 'paralyzed', 'poisoned']

        if not condition_to_remove:
            return {
                'success': False,
                'reason': 'Must specify condition to remove',
                'removable': removable_conditions
            }

        if condition_to_remove not in removable_conditions:
            return {
                'success': False,
                'reason': f'Cannot remove {condition_to_remove}',
                'removable': removable_conditions
            }

        result = self.effects.remove_condition(target_id, condition_to_remove)

        return {
            **result,
            'spell_name': 'Lesser Restoration',
            'target': target_id,
            'condition_removed': condition_to_remove,
            'instant': True
        }


class ProtectionFromPoisonHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else caster_id

        remove_result = self.effects.remove_condition(target_id, 'poisoned')

        buff_data = {
            'source': 'protection_from_poison',
            'spell_name': 'Protection from Poison',
            'spell_level': slot_level,
            'type': 'protection_from_poison',
            'resistance': 'poison',
            'advantage_on_saves': 'poison'
        }

        result = self.effects.apply_buff(target_id, buff_data, duration_rounds=60,
                                        caster_id=caster_id, concentration=False)

        return {
            **result,
            'spell_name': 'Protection from Poison',
            'target': target_id,
            'poisoned_removed': remove_result.get('success', False),
            'resistance': 'poison damage',
            'advantage': 'poison saves',
            'duration': '1 hour'
        }


class RemoveCurseHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else caster_id

        curse_type = context.get('curse_type', 'curse')

        result = self.effects.remove_condition(target_id, 'cursed')

        return {
            **result,
            'spell_name': 'Remove Curse',
            'target': target_id,
            'effect': 'All curses on target or cursed item are broken',
            'attunement': 'Cursed items can be removed',
            'instant': True
        }


class RevivifyHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else None

        if not target_id:
            return {
                'success': False,
                'reason': 'Revivify requires a dead creature target'
            }

        death_time = context.get('death_time_minutes', 0)

        if death_time > 1:
            return {
                'success': False,
                'reason': 'Target has been dead too long (max 1 minute)',
                'time_limit': '1 minute'
            }

        result = self.effects.apply_healing(target_id, 1, 'revivify')

        buff_data = {
            'source': 'revivify',
            'spell_name': 'Revivify',
            'spell_level': slot_level,
            'type': 'resurrection',
            'restored_to_life': True,
            'penalty': 'returns at 1 HP'
        }

        self.effects.apply_buff(target_id, buff_data, duration_rounds=1,
                               caster_id=caster_id, concentration=False)

        return {
            **result,
            'spell_name': 'Revivify',
            'target': target_id,
            'restored': True,
            'hp_restored': 1,
            'material_cost': '300 gp diamonds (consumed)',
            'instant': True
        }


class RaiseDeadHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else None

        if not target_id:
            return {
                'success': False,
                'reason': 'Raise Dead requires a dead creature target'
            }

        death_time_days = context.get('death_time_days', 0)

        if death_time_days > 10:
            return {
                'success': False,
                'reason': 'Target has been dead too long (max 10 days)',
                'time_limit': '10 days'
            }

        result = self.effects.apply_healing(target_id, 1, 'raise_dead')

        buff_data = {
            'source': 'raise_dead',
            'spell_name': 'Raise Dead',
            'spell_level': slot_level,
            'type': 'resurrection',
            'restored_to_life': True,
            'penalty': 'death penalty until long rest',
            'hp_max_reduction': -4,
            'attack_penalty': -4,
            'save_penalty': -4,
            'ability_check_penalty': -4
        }

        self.effects.apply_buff(target_id, buff_data, duration_rounds=1,
                               caster_id=caster_id, concentration=False)

        return {
            **result,
            'spell_name': 'Raise Dead',
            'target': target_id,
            'restored': True,
            'hp_restored': 1,
            'penalty': '-4 to all d20 rolls until long rest',
            'material_cost': '500 gp diamond (consumed)',
            'cast_time': '1 hour'
        }

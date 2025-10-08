from typing import Dict, List, Any
from .base_handler import SpellHandler, roll_dice


class CureWoundsHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        cha_mod = self._get_ability_mod(caster_id, 'charisma')

        base_dice = 1
        extra_dice = slot_level - 1
        total_dice = base_dice + extra_dice

        healing = roll_dice(total_dice, 8) + cha_mod

        target_id = targets[0] if targets else caster_id

        result = self.effects.apply_healing(target_id, healing, 'cure_wounds')

        return {
            **result,
            'spell_name': 'Cure Wounds',
            'healing_roll': healing,
            'dice': f"{total_dice}d8",
            'modifier': cha_mod,
            'slot_level': slot_level
        }

    def can_cast(self, caster_id: str, context: Dict[str, Any]):
        return True, ""


class PrayerOfHealingHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        cha_mod = self._get_ability_mod(caster_id, 'charisma')

        base_dice = 2
        extra_dice = slot_level - 2
        total_dice = base_dice + extra_dice

        healing = roll_dice(total_dice, 8) + cha_mod

        target_id = targets[0] if targets else caster_id

        result = self.effects.apply_healing(target_id, healing, 'prayer_of_healing')

        return {
            **result,
            'spell_name': 'Prayer of Healing',
            'healing_roll': healing,
            'dice': f"{total_dice}d8",
            'modifier': cha_mod,
            'slot_level': slot_level,
            'cast_time': '10 minutes'
        }

    def can_cast(self, caster_id: str, context: Dict[str, Any]):
        return True, ""

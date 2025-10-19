# core
# category: core
from typing import Dict, List, Any
from .base_handler import SpellHandler, roll_dice
import json


class FindSteedHandler(SpellHandler):
    AVAILABLE_FORMS = ['warhorse', 'pony', 'camel', 'elk', 'mastiff']

    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        form = context.get('steed_form', 'warhorse')

        if form not in self.AVAILABLE_FORMS:
            return {
                'success': False,
                'reason': f'Invalid steed form. Choose from: {", ".join(self.AVAILABLE_FORMS)}'
            }

        existing_steed = self._get_active_summon(caster_id)
        if existing_steed:
            self._dismiss_summon(caster_id, existing_steed)

        stat_block = self._get_steed_stats(form)

        summon_id = self._create_summon(caster_id, form, stat_block)

        return {
            'success': True,
            'spell_name': 'Find Steed',
            'steed_form': form,
            'summon_id': summon_id,
            'stats': stat_block,
            'telepathic_link': True,
            'can_dismiss': True,
            'duration': 'Until dismissed or killed'
        }

    def _get_active_summon(self, caster_id: str) -> Dict[str, Any]:
        try:
            import sqlite3
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, summon_name, stat_block
                    FROM spell_summons
                    WHERE character_id = ? AND spell_id = 'find_steed' AND is_active = 1
                """, (caster_id,))
                result = cursor.fetchone()
                if result:
                    return {
                        'id': result[0],
                        'name': result[1],
                        'stats': json.loads(result[2]) if result[2] else {}
                    }
        except Exception as e:
            print(f"Error getting active summon: {e}")
        return None

    def _dismiss_summon(self, caster_id: str, summon: Dict[str, Any]):
        try:
            import sqlite3
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE spell_summons
                    SET is_active = 0, dismissed_at = datetime('now')
                    WHERE id = ?
                """, (summon['id'],))
                conn.commit()
        except Exception as e:
            print(f"Error dismissing summon: {e}")

    def _create_summon(self, caster_id: str, form: str, stat_block: Dict) -> str:
        try:
            import sqlite3
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO spell_summons
                    (character_id, spell_id, summon_name, summon_type, stat_block,
                     current_hp, max_hp, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """, (caster_id, 'find_steed', form, 'mount',
                      json.dumps(stat_block), stat_block['hp'], stat_block['hp']))
                conn.commit()
                return str(cursor.lastrowid)
        except Exception as e:
            print(f"Error creating summon: {e}")
            return "unknown"

    def _get_steed_stats(self, form: str) -> Dict[str, Any]:
        stats = {
            'warhorse': {
                'hp': 19, 'ac': 11, 'speed': 60,
                'str': 18, 'dex': 12, 'con': 13, 'int': 2, 'wis': 12, 'cha': 7,
                'attacks': [{'name': 'Hooves', 'bonus': 6, 'damage': '2d6+4', 'type': 'bludgeoning'}]
            },
            'pony': {
                'hp': 11, 'ac': 10, 'speed': 40,
                'str': 15, 'dex': 10, 'con': 13, 'int': 2, 'wis': 11, 'cha': 7,
                'attacks': [{'name': 'Hooves', 'bonus': 4, 'damage': '2d4+2', 'type': 'bludgeoning'}]
            },
            'camel': {
                'hp': 15, 'ac': 9, 'speed': 50,
                'str': 16, 'dex': 8, 'con': 14, 'int': 2, 'wis': 8, 'cha': 5,
                'attacks': [{'name': 'Bite', 'bonus': 5, 'damage': '1d4+3', 'type': 'bludgeoning'}]
            },
            'elk': {
                'hp': 13, 'ac': 10, 'speed': 50,
                'str': 16, 'dex': 10, 'con': 12, 'int': 2, 'wis': 10, 'cha': 6,
                'attacks': [{'name': 'Ram', 'bonus': 5, 'damage': '1d6+3', 'type': 'bludgeoning'}]
            },
            'mastiff': {
                'hp': 5, 'ac': 12, 'speed': 40,
                'str': 13, 'dex': 14, 'con': 12, 'int': 3, 'wis': 12, 'cha': 7,
                'attacks': [{'name': 'Bite', 'bonus': 3, 'damage': '1d6+1', 'type': 'piercing'}]
            }
        }
        return stats.get(form, stats['warhorse'])


class DispelMagicHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else None

        if not target_id:
            return {
                'success': False,
                'reason': 'Dispel Magic requires a target'
            }

        active_effects = self.effects.get_active_buffs(target_id)

        dispelled = []
        failed = []

        for effect in active_effects:
            effect_level = effect.get('spell_level_cast', 0)

            if effect_level <= 3:
                self.effects.remove_buff(target_id, effect['spell_id'])
                dispelled.append(effect['spell_name'])

            elif effect_level <= slot_level:
                self.effects.remove_buff(target_id, effect['spell_id'])
                dispelled.append(effect['spell_name'])

            else:
                cha_mod = self._get_ability_mod(caster_id, 'charisma')
                dc = 10 + effect_level
                check_roll = roll_dice(1, 20) + cha_mod

                if check_roll >= dc:
                    self.effects.remove_buff(target_id, effect['spell_id'])
                    dispelled.append(effect['spell_name'])
                else:
                    failed.append({
                        'spell': effect['spell_name'],
                        'level': effect_level,
                        'dc': dc,
                        'roll': check_roll
                    })

        if self.concentration.is_concentrating(target_id):
            conc_spell = self.concentration.get_concentration_spell(target_id)
            if conc_spell:
                conc_level = conc_spell.get('spell_level', 0)
                if conc_level <= slot_level:
                    self.concentration.end_concentration(target_id)
                    dispelled.append(conc_spell.get('spell_id', 'concentration'))

        return {
            'success': True,
            'spell_name': 'Dispel Magic',
            'target': target_id,
            'dispelled_spells': dispelled,
            'failed_dispels': failed,
            'total_dispelled': len(dispelled)
        }


class MagicCircleHandler(SpellHandler):
    CREATURE_TYPES = ['aberrations', 'celestials', 'elementals', 'fey', 'fiends', 'undead']

    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        creature_type = context.get('creature_type', 'fiends')

        if creature_type not in self.CREATURE_TYPES:
            return {
                'success': False,
                'reason': f'Invalid creature type. Choose from: {", ".join(self.CREATURE_TYPES)}'
            }

        buff_data = {
            'source': 'magic_circle',
            'spell_name': 'Magic Circle',
            'spell_level': slot_level,
            'type': 'magic_circle',
            'radius': 10,
            'creature_type': creature_type,
            'cannot_enter': True,
            'disadvantage_on_attacks': True,
            'cannot_charm_frighten_possess': True
        }

        result = self.effects.apply_buff(caster_id, buff_data, duration_rounds=60,
                                        caster_id=caster_id, concentration=False)

        return {
            **result,
            'spell_name': 'Magic Circle',
            'radius': '10 feet',
            'creature_type': creature_type,
            'effects': 'Cannot enter, attacks at disadvantage, immune to charm/fear/possession',
            'duration': '1 hour',
            'cast_time': '1 minute'
        }


class DaylightHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        buff_data = {
            'source': 'daylight',
            'spell_name': 'Daylight',
            'spell_level': slot_level,
            'type': 'daylight',
            'radius': 60,
            'bright_light': 60,
            'dim_light': 60,
            'dispels_darkness': True,
            'counters_darkness_spells': True
        }

        result = self.effects.apply_buff(caster_id, buff_data, duration_rounds=60,
                                        caster_id=caster_id, concentration=False)

        return {
            **result,
            'spell_name': 'Daylight',
            'radius': '60 feet bright, 60 feet dim',
            'effect': 'Creates sunlight, dispels magical darkness of 3rd level or lower',
            'duration': '1 hour'
        }


class CreateFoodAndWaterHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        food_created = 45
        water_created = 30

        return {
            'success': True,
            'spell_name': 'Create Food and Water',
            'food_pounds': food_created,
            'water_gallons': water_created,
            'feeds': '15 humanoids or 5 horses for 24 hours',
            'duration': '24 hours (food spoils after)',
            'instant': True
        }


class GreaterRestorationHandler(SpellHandler):
    RESTORABLE_EFFECTS = ['exhaustion', 'charmed', 'petrified', 'ability_reduction', 'max_hp_reduction']

    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else caster_id
        effect_type = context.get('effect_type', None)

        if not effect_type:
            return {
                'success': False,
                'reason': 'Must specify effect to remove',
                'restorable': self.RESTORABLE_EFFECTS
            }

        if effect_type not in self.RESTORABLE_EFFECTS:
            return {
                'success': False,
                'reason': f'Cannot restore {effect_type}',
                'restorable': self.RESTORABLE_EFFECTS
            }

        result_data = {'success': True, 'spell_name': 'Greater Restoration', 'target': target_id}

        if effect_type == 'exhaustion':
            exhaustion_removed = self._reduce_exhaustion(target_id)
            result_data['effect'] = f'Reduced exhaustion by 1 level'
            result_data['exhaustion_removed'] = exhaustion_removed

        elif effect_type == 'charmed':
            self.effects.remove_condition(target_id, 'charmed')
            result_data['effect'] = 'Removed charmed condition'

        elif effect_type == 'petrified':
            self.effects.remove_condition(target_id, 'petrified')
            result_data['effect'] = 'Removed petrified condition'

        elif effect_type == 'ability_reduction':
            self._restore_ability_scores(target_id)
            result_data['effect'] = 'Restored ability score reduction'

        elif effect_type == 'max_hp_reduction':
            self._restore_max_hp(target_id)
            result_data['effect'] = 'Restored maximum HP'

        result_data['instant'] = True
        result_data['material_cost'] = '100 gp diamond dust (consumed)'

        return result_data

    def _reduce_exhaustion(self, character_id: str) -> bool:
        try:
            import sqlite3
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT exhaustion_level FROM characters WHERE id = ?
                """, (character_id,))
                result = cursor.fetchone()
                if result and result[0] > 0:
                    new_level = result[0] - 1
                    cursor.execute("""
                        UPDATE characters SET exhaustion_level = ? WHERE id = ?
                    """, (new_level, character_id))
                    conn.commit()
                    return True
        except Exception as e:
            print(f"Error reducing exhaustion: {e}")
        return False

    def _restore_ability_scores(self, character_id: str):
        pass

    def _restore_max_hp(self, character_id: str):
        try:
            import sqlite3
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE characters
                    SET max_hit_points = CASE
                        WHEN max_hit_points < base_max_hp THEN base_max_hp
                        ELSE max_hit_points
                    END
                    WHERE id = ?
                """, (character_id,))
                conn.commit()
        except Exception as e:
            print(f"Error restoring max HP: {e}")


class DispelEvilAndGoodHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        self.concentration.start_concentration(
            caster_id, 'dispel_evil_and_good', slot_level, duration_rounds=10
        )

        buff_data = {
            'source': 'dispel_evil_and_good',
            'spell_name': 'Dispel Evil and Good',
            'spell_level': slot_level,
            'type': 'dispel_evil_and_good',
            'creature_types': ['aberrations', 'celestials', 'elementals', 'fey', 'fiends', 'undead'],
            'disadvantage_on_attacks': True,
            'cannot_be_charmed_frightened_possessed': True,
            'can_break_enchantment': True,
            'can_dismiss_creature': True
        }

        result = self.effects.apply_buff(caster_id, buff_data, duration_rounds=10,
                                        caster_id=caster_id, concentration=True)

        return {
            **result,
            'spell_name': 'Dispel Evil and Good',
            'effects': [
                'Creatures have disadvantage on attacks',
                'Immune to charm/fear/possession',
                'Action: Break enchantment (touch)',
                'Action: Dismiss creature (touch, Charisma save)'
            ],
            'duration': '1 minute',
            'concentration': True
        }


class GeasHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else None

        if not target_id:
            return {
                'success': False,
                'reason': 'Geas requires a target'
            }

        command = context.get('command', '')

        if not command:
            return {
                'success': False,
                'reason': 'Must provide a command or instruction'
            }

        dc = self._get_spell_save_dc(caster_id)
        saved = self._make_save(target_id, 'wisdom', dc)

        if saved:
            return {
                'success': True,
                'spell_name': 'Geas',
                'target': target_id,
                'saved': True,
                'effect': 'Target resisted the geas'
            }

        buff_data = {
            'source': 'geas',
            'spell_name': 'Geas',
            'spell_level': slot_level,
            'type': 'geas',
            'command': command,
            'damage_per_day_disobeyed': '5d10',
            'damage_type': 'psychic',
            'save_dc': dc
        }

        result = self.effects.apply_buff(target_id, buff_data, duration_rounds=86400,
                                        caster_id=caster_id, concentration=False)

        return {
            **result,
            'spell_name': 'Geas',
            'target': target_id,
            'saved': False,
            'command': command,
            'damage_on_disobey': '5d10 psychic per day',
            'duration': '30 days',
            'cast_time': '1 minute',
            'removable_by': 'Remove Curse, Greater Restoration, Wish'
        }

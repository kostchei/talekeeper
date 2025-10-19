# core
# category: core
from typing import Dict, List, Any
from .base_handler import SpellHandler, roll_dice


class SearingSmiteHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        self.concentration.start_concentration(
            caster_id, 'searing_smite', slot_level, duration_rounds=10
        )

        damage_dice = slot_level

        buff_data = {
            'source': 'searing_smite',
            'spell_name': 'Searing Smite',
            'spell_level': slot_level,
            'type': 'next_hit_bonus_damage',
            'damage_dice': damage_dice,
            'damage_die_type': 'd6',
            'damage_type': 'fire',
            'on_hit_apply_condition': 'ignited',
            'ignite_save_dc': self._get_spell_save_dc(caster_id),
            'ignite_damage_per_turn': '1d6'
        }

        result = self.effects.apply_buff(caster_id, buff_data, duration_rounds=10,
                                        caster_id=caster_id, concentration=True)

        return {
            **result,
            'spell_name': 'Searing Smite',
            'damage_on_hit': f'{damage_dice}d6 fire',
            'ignite_effect': '1d6 fire/turn (Dex save ends)',
            'duration': '1 minute',
            'concentration': True
        }


class DetectMagicHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        self.concentration.start_concentration(
            caster_id, 'detect_magic', slot_level, duration_rounds=100
        )

        buff_data = {
            'source': 'detect_magic',
            'spell_name': 'Detect Magic',
            'spell_level': slot_level,
            'type': 'detection_active',
            'detects': 'magic',
            'range': 30,
            'can_sense_school': True
        }

        result = self.effects.apply_buff(caster_id, buff_data, duration_rounds=100,
                                        caster_id=caster_id, concentration=True)

        nearby_magic = self._scan_for_magic(caster_id, context)

        return {
            **result,
            'spell_name': 'Detect Magic',
            'range': '30 feet',
            'detected_magic': nearby_magic,
            'duration': '10 minutes',
            'concentration': True
        }

    def _scan_for_magic(self, caster_id: str, context: Dict[str, Any]) -> List[Dict]:
        detected = []

        encounter_monsters = context.get('monsters', [])
        for monster in encounter_monsters:
            if monster.get('is_magical') or monster.get('has_magic_items'):
                detected.append({
                    'type': 'creature',
                    'name': monster.get('name', 'Unknown'),
                    'school': monster.get('magic_school', 'unknown')
                })

        magical_items = context.get('magical_items', [])
        for item in magical_items:
            detected.append({
                'type': 'item',
                'name': item.get('name', 'Unknown'),
                'school': item.get('magic_school', 'unknown')
            })

        return detected


class DetectEvilAndGoodHandler(SpellHandler):
    DETECTABLE_TYPES = ['aberration', 'celestial', 'elemental', 'fey', 'fiend', 'undead']

    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        self.concentration.start_concentration(
            caster_id, 'detect_evil_and_good', slot_level, duration_rounds=100
        )

        buff_data = {
            'source': 'detect_evil_and_good',
            'spell_name': 'Detect Evil and Good',
            'spell_level': slot_level,
            'type': 'detection_active',
            'detects': 'creature_types',
            'range': 30,
            'creature_types': self.DETECTABLE_TYPES
        }

        result = self.effects.apply_buff(caster_id, buff_data, duration_rounds=100,
                                        caster_id=caster_id, concentration=True)

        nearby_creatures = self._scan_for_creatures(caster_id, context)

        return {
            **result,
            'spell_name': 'Detect Evil and Good',
            'range': '30 feet',
            'detected_creatures': nearby_creatures,
            'types_detected': self.DETECTABLE_TYPES,
            'duration': '10 minutes',
            'concentration': True
        }

    def _scan_for_creatures(self, caster_id: str, context: Dict[str, Any]) -> List[Dict]:
        detected = []

        encounter_monsters = context.get('monsters', [])
        for monster in encounter_monsters:
            creature_type = monster.get('type', '').lower()
            if creature_type in self.DETECTABLE_TYPES:
                detected.append({
                    'name': monster.get('name', 'Unknown'),
                    'type': creature_type,
                    'direction': 'present'
                })

        return detected


class DetectPoisonAndDiseaseHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        self.concentration.start_concentration(
            caster_id, 'detect_poison_and_disease', slot_level, duration_rounds=100
        )

        buff_data = {
            'source': 'detect_poison_and_disease',
            'spell_name': 'Detect Poison and Disease',
            'spell_level': slot_level,
            'type': 'detection_active',
            'detects': 'poison_disease',
            'range': 30,
            'can_identify_type': True
        }

        result = self.effects.apply_buff(caster_id, buff_data, duration_rounds=100,
                                        caster_id=caster_id, concentration=True)

        nearby_threats = self._scan_for_poison_disease(caster_id, context)

        return {
            **result,
            'spell_name': 'Detect Poison and Disease',
            'range': '30 feet',
            'detected_threats': nearby_threats,
            'duration': '10 minutes',
            'concentration': True
        }

    def _scan_for_poison_disease(self, caster_id: str, context: Dict[str, Any]) -> List[Dict]:
        detected = []

        encounter_monsters = context.get('monsters', [])
        for monster in encounter_monsters:
            if monster.get('has_poison') or monster.get('has_disease'):
                detected.append({
                    'name': monster.get('name', 'Unknown'),
                    'threat_type': 'poison' if monster.get('has_poison') else 'disease',
                    'kind': monster.get('poison_type', 'unknown')
                })

        environment = context.get('environment', {})
        if environment.get('has_poison'):
            detected.append({
                'name': 'Environmental Poison',
                'threat_type': 'poison',
                'kind': environment.get('poison_type', 'unknown')
            })

        return detected


class LocateObjectHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        self.concentration.start_concentration(
            caster_id, 'locate_object', slot_level, duration_rounds=100
        )

        object_description = context.get('object_description', '')

        if not object_description:
            return {
                'success': False,
                'reason': 'Must describe object to locate'
            }

        buff_data = {
            'source': 'locate_object',
            'spell_name': 'Locate Object',
            'spell_level': slot_level,
            'type': 'detection_active',
            'detects': 'object',
            'range': 1000,
            'object_description': object_description
        }

        result = self.effects.apply_buff(caster_id, buff_data, duration_rounds=100,
                                        caster_id=caster_id, concentration=True)

        location = self._locate_object(object_description, context)

        return {
            **result,
            'spell_name': 'Locate Object',
            'range': '1000 feet',
            'object_sought': object_description,
            'location': location,
            'duration': '10 minutes',
            'concentration': True
        }

    def _locate_object(self, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        objects = context.get('available_objects', [])
        for obj in objects:
            if description.lower() in obj.get('name', '').lower():
                return {
                    'found': True,
                    'direction': obj.get('direction', 'unknown'),
                    'distance': obj.get('distance', 'unknown')
                }

        return {'found': False}


class LocateCreatureHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        self.concentration.start_concentration(
            caster_id, 'locate_creature', slot_level, duration_rounds=60
        )

        creature_description = context.get('creature_description', '')

        if not creature_description:
            return {
                'success': False,
                'reason': 'Must describe creature to locate'
            }

        buff_data = {
            'source': 'locate_creature',
            'spell_name': 'Locate Creature',
            'spell_level': slot_level,
            'type': 'detection_active',
            'detects': 'creature',
            'range': 1000,
            'creature_description': creature_description
        }

        result = self.effects.apply_buff(caster_id, buff_data, duration_rounds=60,
                                        caster_id=caster_id, concentration=True)

        location = self._locate_creature(creature_description, context)

        return {
            **result,
            'spell_name': 'Locate Creature',
            'range': '1000 feet',
            'creature_sought': creature_description,
            'location': location,
            'duration': '1 hour',
            'concentration': True
        }

    def _locate_creature(self, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        creatures = context.get('available_creatures', [])
        for creature in creatures:
            if description.lower() in creature.get('name', '').lower() or \
               description.lower() in creature.get('type', '').lower():
                return {
                    'found': True,
                    'direction': creature.get('direction', 'unknown'),
                    'distance': creature.get('distance', 'unknown')
                }

        return {'found': False}


class BanishmentHandler(SpellHandler):
    def execute(self, caster_id: str, targets: List[str], slot_level: int,
                context: Dict[str, Any]) -> Dict[str, Any]:
        target_id = targets[0] if targets else None

        if not target_id:
            return {
                'success': False,
                'reason': 'Banishment requires a target'
            }

        dc = self._get_spell_save_dc(caster_id)
        saved = self._make_save(target_id, 'charisma', dc)

        if saved:
            return {
                'success': True,
                'spell_name': 'Banishment',
                'target': target_id,
                'saved': True,
                'effect': 'Target resisted banishment'
            }

        self.concentration.start_concentration(
            caster_id, 'banishment', slot_level, duration_rounds=10
        )

        buff_data = {
            'source': 'banishment',
            'spell_name': 'Banishment',
            'spell_level': slot_level,
            'type': 'banishment',
            'banished': True,
            'returns_on_concentration_end': True
        }

        result = self.effects.apply_buff(target_id, buff_data, duration_rounds=10,
                                        caster_id=caster_id, concentration=True)

        return {
            **result,
            'spell_name': 'Banishment',
            'target': target_id,
            'saved': False,
            'effect': 'Target banished to harmless demiplane',
            'duration': '1 minute',
            'concentration': True,
            'permanent_if_native': 'Permanent if maintained full duration on extraplanar creature'
        }

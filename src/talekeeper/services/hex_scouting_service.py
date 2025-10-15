from typing import Dict, List, Optional, Tuple
import random
import sqlite3

class HexScoutingService:

    TERRAIN_SCOUT_SKILLS: Dict[str, List[str]] = {
        'plains': ['nature', 'survival'],
        'forest': ['nature', 'survival'],
        'mountain': ['nature', 'survival'],
        'hills': ['nature', 'survival'],
        'swamp': ['nature', 'survival'],
        'desert': ['nature', 'survival']
    }

    ENCOUNTER_SCOUT_SKILLS: Dict[str, List[str]] = {
        'aberration': ['arcana'],
        'beast': ['nature', 'survival'],
        'celestial': ['religion'],
        'construct': ['arcana', 'investigation'],
        'dragon': ['arcana', 'history'],
        'elemental': ['arcana', 'nature'],
        'fey': ['arcana', 'nature'],
        'fiend': ['religion'],
        'giant': ['history', 'insight'],
        'humanoid': ['history', 'insight'],
        'monstrosity': ['nature'],
        'ooze': ['arcana', 'nature'],
        'plant': ['nature', 'survival'],
        'undead': ['religion']
    }

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def scout_hex(self, character_id: str, hex_q: int, hex_r: int, hex_data: Dict) -> Dict:
        character = self._get_character(character_id)
        if not character:
            return self._basic_hex_info(hex_data)

        scouting_info = {
            'terrain': hex_data['terrain_type'],
            'biome': hex_data['biome'],
            'terrain_details': [],
            'encounter_hints': [],
            'danger_level': 'unknown',
            'skill_checks': []
        }

        nature_bonus = self._get_skill_bonus(character, 'nature')
        survival_bonus = self._get_skill_bonus(character, 'survival')
        perception_bonus = self._get_skill_bonus(character, 'perception')

        terrain_dc = self._get_terrain_dc(hex_data['biome'])
        nature_roll = self._roll_check(nature_bonus)
        survival_roll = self._roll_check(survival_bonus)

        scouting_info['skill_checks'].append({
            'skill': 'Nature',
            'roll': nature_roll,
            'dc': terrain_dc,
            'success': nature_roll >= terrain_dc
        })

        scouting_info['skill_checks'].append({
            'skill': 'Survival',
            'roll': survival_roll,
            'dc': terrain_dc,
            'success': survival_roll >= terrain_dc
        })

        if nature_roll >= terrain_dc:
            scouting_info['terrain_details'].extend(self._get_nature_details(hex_data, nature_roll - terrain_dc))

        if survival_roll >= terrain_dc:
            scouting_info['terrain_details'].extend(self._get_survival_details(hex_data, survival_roll - terrain_dc))

        encounter_data = self._check_for_encounter(hex_data)
        if encounter_data:
            perception_dc = self._get_encounter_dc(encounter_data)
            perception_roll = self._roll_check(perception_bonus)

            scouting_info['skill_checks'].append({
                'skill': 'Perception',
                'roll': perception_roll,
                'dc': perception_dc,
                'success': perception_roll >= perception_dc
            })

            if perception_roll >= perception_dc:
                scouting_info['encounter_hints'].extend(
                    self._get_encounter_hints(character, encounter_data, perception_roll - perception_dc)
                )
                scouting_info['danger_level'] = self._assess_danger(encounter_data)
            else:
                scouting_info['encounter_hints'].append("You sense nothing unusual...")

        return scouting_info

    def _basic_hex_info(self, hex_data: Dict) -> Dict:
        return {
            'terrain': hex_data['terrain_type'],
            'biome': hex_data['biome'],
            'terrain_details': [f"{hex_data['biome'].title()} terrain"],
            'encounter_hints': [],
            'danger_level': 'unknown',
            'skill_checks': []
        }

    def _get_character(self, character_id: str) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def _get_skill_bonus(self, character: Dict, skill: str) -> int:
        skill_abilities = {
            'arcana': 'intelligence',
            'nature': 'intelligence',
            'religion': 'intelligence',
            'history': 'intelligence',
            'insight': 'wisdom',
            'investigation': 'intelligence',
            'survival': 'wisdom',
            'perception': 'wisdom'
        }

        ability = skill_abilities.get(skill.lower(), 'intelligence')
        ability_score = character.get(ability, 10)
        modifier = (ability_score - 10) // 2

        level = character.get('level', 1)
        prof_bonus = 2 + ((level - 1) // 4)

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 1 FROM character_proficiencies
            WHERE character_id = ? AND proficiency_type = 'skill' AND proficiency_name = ?
        ''', (character['id'], skill.lower()))

        is_proficient = cursor.fetchone() is not None
        conn.close()

        if is_proficient:
            modifier += prof_bonus

        return modifier

    def _roll_check(self, bonus: int) -> int:
        return random.randint(1, 20) + bonus

    def _get_terrain_dc(self, biome: str) -> int:
        terrain_dcs = {
            'plains': 10,
            'forest': 12,
            'mountain': 15,
            'hills': 12,
            'swamp': 14,
            'desert': 13
        }
        return terrain_dcs.get(biome, 12)

    def _get_nature_details(self, hex_data: Dict, margin: int) -> List[str]:
        details = []
        biome = hex_data['biome']

        if margin >= 0:
            nature_info = {
                'plains': "Open grasslands with good visibility",
                'forest': "Dense woodland with limited sightlines",
                'mountain': "Rocky terrain with steep inclines",
                'hills': "Rolling terrain with moderate elevation changes",
                'swamp': "Waterlogged ground with thick vegetation",
                'desert': "Arid terrain with sparse vegetation"
            }
            details.append(nature_info.get(biome, "Natural terrain"))

        if margin >= 3:
            flora_info = {
                'plains': "Edible grasses and herbs grow here",
                'forest': "Ancient trees provide shelter and resources",
                'mountain': "Hardy mountain plants cling to the rocks",
                'hills': "Wildflowers and shrubs dot the landscape",
                'swamp': "Poisonous plants mix with edible roots",
                'desert': "Cacti and drought-resistant plants survive here"
            }
            details.append(flora_info.get(biome, "Various plants grow here"))

        if margin >= 6:
            details.append(f"The {biome} shows signs of recent activity")

        return details

    def _get_survival_details(self, hex_data: Dict, margin: int) -> List[str]:
        details = []
        biome = hex_data['biome']

        if margin >= 0:
            move_costs = {
                'plains': "Easy travel - normal movement speed",
                'forest': "Difficult terrain - slower movement",
                'mountain': "Very difficult - climbing may be required",
                'hills': "Moderate difficulty - watch your footing",
                'swamp': "Treacherous - slow and dangerous",
                'desert': "Exhausting - water is critical"
            }
            details.append(move_costs.get(biome, "Travel difficulty uncertain"))

        if margin >= 3:
            details.append("You notice tracks and trails through the area")

        if margin >= 5:
            shelter_info = {
                'plains': "Few natural shelters - exposed to elements",
                'forest': "Good places to make camp under the canopy",
                'mountain': "Caves and overhangs provide shelter",
                'hills': "Valleys offer protection from wind",
                'swamp': "Finding dry ground for camp will be challenging",
                'desert': "Shelter from sun is essential for survival"
            }
            details.append(shelter_info.get(biome, "Camping conditions uncertain"))

        return details

    def _check_for_encounter(self, hex_data: Dict) -> Optional[Dict]:
        seed = hex_data.get('encounter_seed', 0)
        random.seed(seed)

        encounter_rates = {
            'plains': 0.3,
            'forest': 0.5,
            'mountain': 0.4,
            'hills': 0.35,
            'swamp': 0.6,
            'desert': 0.2
        }

        rate = encounter_rates.get(hex_data['biome'], 0.3)
        if random.random() < rate:
            cr = self._calculate_encounter_cr(hex_data)
            monster_type = self._get_monster_type(hex_data['biome'])
            return {
                'type': monster_type,
                'cr': cr,
                'biome': hex_data['biome']
            }

        return None

    def _calculate_encounter_cr(self, hex_data: Dict) -> int:
        from .hex_coordinate_system import HexCoordinateSystem
        coord_system = HexCoordinateSystem()
        distance = coord_system.get_distance(0, 0, hex_data['q'], hex_data['r'])

        base_cr = distance // 3

        if hex_data['biome'] in ['mountain', 'swamp']:
            base_cr += 1

        return max(0, min(base_cr, 10))

    def _get_monster_type(self, biome: str) -> str:
        biome_types = {
            'plains': 'beast',
            'forest': 'beast',
            'mountain': 'giant',
            'hills': 'humanoid',
            'swamp': 'monstrosity',
            'desert': 'monstrosity'
        }
        return biome_types.get(biome, 'beast')

    def _get_encounter_dc(self, encounter_data: Dict) -> int:
        base_dc = 10 + encounter_data['cr']

        if encounter_data['type'] in ['aberration', 'fey']:
            base_dc += 2

        return base_dc

    def _get_encounter_hints(self, character: Dict, encounter_data: Dict, margin: int) -> List[str]:
        hints = []
        monster_type = encounter_data['type']
        cr = encounter_data['cr']

        location_type = encounter_data.get('location_type', 'combat')

        if location_type == 'vendor':
            if margin >= 0:
                hints.append("Vendor: signs of a traveling merchant")
            return hints
        elif location_type == 'hazard':
            if margin >= 0:
                hints.append("Possible hazard detected")
            if margin >= 5:
                hints.append(f"Natural hazard: {encounter_data.get('hazard_type', 'unknown danger')}")
            return hints
        elif location_type == 'landmark':
            if margin >= 0:
                hints.append(f"Landmark: {encounter_data.get('landmark_name', 'Point of Interest')}")
            return hints

        if margin >= 0:
            type_names = {
                'beast': "Beast",
                'giant': "Giant",
                'humanoid': "Humanoid",
                'monstrosity': "Monstrosity",
                'dragon': "Dragon",
                'undead': "Undead",
                'aberration': "Aberration",
                'fey': "Fey",
                'fiend': "Fiend",
                'elemental': "Elemental",
                'construct': "Construct",
                'ooze': "Ooze",
                'plant': "Plant"
            }
            type_name = type_names.get(monster_type, "Creature")

            monster_name = encounter_data.get('name', type_name)
            hints.append(f"{monster_name} (CR {cr})")

        return hints

    def _assess_danger(self, encounter_data: Dict) -> str:
        cr = encounter_data['cr']
        if cr <= 2:
            return 'low'
        elif cr <= 5:
            return 'moderate'
        elif cr <= 8:
            return 'high'
        else:
            return 'extreme'

    def format_scouting_html(self, scouting_info: Dict) -> str:
        html = []

        html.append('<div style="padding: 8px; background-color: #2b2b2b; border-radius: 4px;">')

        html.append(f'<div style="font-size: 14px; font-weight: bold; color: #fff; margin-bottom: 8px;">')
        html.append(f"{scouting_info['biome'].title()} Terrain")
        html.append('</div>')

        if scouting_info['skill_checks']:
            html.append('<div style="margin-bottom: 8px; color: #aaa; font-size: 12px;">')
            for check in scouting_info['skill_checks']:
                color = '#4CAF50' if check['success'] else '#f44336'
                symbol = '✓' if check['success'] else '✗'
                html.append(f"<span style='color: {color};'>{check['skill']}: {check['roll']} vs DC {check['dc']} {symbol}</span><br/>")
            html.append('</div>')

        if scouting_info['terrain_details']:
            html.append('<div style="margin-top: 8px;">')
            html.append('<span style="color: #64B5F6; font-weight: bold;">Terrain:</span>')
            html.append('<ul style="margin: 4px 0; padding-left: 20px;">')
            for detail in scouting_info['terrain_details']:
                html.append(f'<li style="color: #ddd;">{detail}</li>')
            html.append('</ul>')
            html.append('</div>')

        if scouting_info['encounter_hints']:
            html.append('<div style="margin-top: 8px;">')
            danger_colors = {
                'low': '#4CAF50',
                'moderate': '#FFC107',
                'high': '#FF9800',
                'extreme': '#f44336',
                'unknown': '#888'
            }
            danger_color = danger_colors.get(scouting_info['danger_level'], '#888')

            html.append(f'<span style="color: {danger_color}; font-weight: bold;">Danger Detected:</span>')
            html.append('<ul style="margin: 4px 0; padding-left: 20px;">')
            for hint in scouting_info['encounter_hints']:
                html.append(f'<li style="color: #ddd;">{hint}</li>')
            html.append('</ul>')
            html.append('</div>')

        html.append('</div>')

        return ''.join(html)

from typing import Dict, List, Any, Optional
from services.feature_registry import FeatureRegistry


class DynamicActionService:
    def __init__(self, db_path: str):
        self.feature_registry = FeatureRegistry(db_path)

    def get_action_cards(self, character_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get all action cards for a character organized by action type"""
        action_cards = {
            'actions': [],
            'bonus_actions': [],
            'reactions': [],
            'free_actions': []
        }

        action_features = self.feature_registry.get_features_by_type(character_id, 'action')
        bonus_action_features = self.feature_registry.get_features_by_type(character_id, 'bonus_action')
        reaction_features = self.feature_registry.get_features_by_type(character_id, 'reaction')
        free_action_features = self.feature_registry.get_features_by_type(character_id, 'free_action')

        action_cards['actions'] = self._create_action_cards(action_features, 'action')
        action_cards['bonus_actions'] = self._create_action_cards(bonus_action_features, 'bonus_action')
        action_cards['reactions'] = self._create_action_cards(reaction_features, 'reaction')
        action_cards['free_actions'] = self._create_action_cards(free_action_features, 'free_action')

        self._add_basic_actions(action_cards)

        return action_cards

    def _create_action_cards(self, features: List[Dict[str, Any]], action_type: str) -> List[Dict[str, Any]]:
        """Create action cards from feature data"""
        cards = []

        for feature in features:
            card = {
                'name': feature['feature_name'],
                'type': action_type,
                'description': feature.get('description', ''),
                'source': feature['feature_source'],
                'mechanics': feature.get('mechanics', {}),
                'current_uses': feature.get('current_uses', 0),
                'max_uses': feature.get('max_uses', 0),
                'recharge_type': feature.get('recharge_type', 'permanent'),
                'available': self._is_feature_available(feature),
                'tooltip': self._generate_tooltip(feature)
            }

            if feature['feature_name'] == 'Rage':
                card.update(self._customize_rage_card(feature))
            elif feature['feature_name'] == 'Action Surge':
                card.update(self._customize_action_surge_card(feature))
            elif feature['feature_name'] == 'Second Wind':
                card.update(self._customize_second_wind_card(feature))
            elif feature['feature_name'] == 'Cunning Action':
                card.update(self._customize_cunning_action_card(feature))

            cards.append(card)

        return cards

    def _add_basic_actions(self, action_cards: Dict[str, List[Dict[str, Any]]]):
        """Add basic combat actions that all characters have"""
        basic_actions = [
            {
                'name': 'Attack',
                'type': 'action',
                'description': 'Make a weapon or unarmed attack',
                'source': 'basic',
                'available': True,
                'tooltip': 'Make an attack with a weapon or unarmed strike'
            },
            {
                'name': 'Cast a Spell',
                'type': 'action',
                'description': 'Cast a spell with casting time of 1 action',
                'source': 'basic',
                'available': True,
                'tooltip': 'Cast a spell that requires an action'
            },
            {
                'name': 'Dash',
                'type': 'action',
                'description': 'Double your speed for this turn',
                'source': 'basic',
                'available': True,
                'tooltip': 'Your movement speed doubles until the end of your turn'
            },
            {
                'name': 'Dodge',
                'type': 'action',
                'description': 'Gain advantage on Dex saves, attacks against you have disadvantage',
                'source': 'basic',
                'available': True,
                'tooltip': 'Focus on avoiding attacks until your next turn'
            },
            {
                'name': 'Help',
                'type': 'action',
                'description': 'Give an ally advantage on their next ability check or attack',
                'source': 'basic',
                'available': True,
                'tooltip': 'Assist an ally with their next action'
            },
            {
                'name': 'Hide',
                'type': 'action',
                'description': 'Make a Stealth check to become hidden',
                'source': 'basic',
                'available': True,
                'tooltip': 'Attempt to hide from enemies'
            },
            {
                'name': 'Ready',
                'type': 'action',
                'description': 'Prepare an action to trigger on a specific condition',
                'source': 'basic',
                'available': True,
                'tooltip': 'Ready an action to use when a trigger occurs'
            },
            {
                'name': 'Search',
                'type': 'action',
                'description': 'Make a Perception or Investigation check',
                'source': 'basic',
                'available': True,
                'tooltip': 'Look for hidden objects, creatures, or clues'
            },
            {
                'name': 'Use an Object',
                'type': 'action',
                'description': 'Interact with an object or use an item',
                'source': 'basic',
                'available': True,
                'tooltip': 'Use an item or interact with the environment'
            }
        ]

        for action in basic_actions:
            action_cards['actions'].append(action)

    def _is_feature_available(self, feature: Dict[str, Any]) -> bool:
        """Check if a feature is currently available for use"""
        if feature.get('max_uses', 0) > 0:
            return feature.get('current_uses', 0) > 0
        return True

    def _generate_tooltip(self, feature: Dict[str, Any]) -> str:
        """Generate a tooltip for the feature"""
        tooltip = feature.get('description', '')

        mechanics = feature.get('mechanics', {})
        if 'damage_bonus' in mechanics:
            tooltip += f"\nDamage Bonus: +{mechanics['damage_bonus']}"

        if feature.get('max_uses', 0) > 0:
            current = feature.get('current_uses', 0)
            max_uses = feature.get('max_uses', 0)
            recharge = feature.get('recharge_type', 'permanent')
            tooltip += f"\nUses: {current}/{max_uses} (Recharges on {recharge.replace('_', ' ')})"

        return tooltip

    def _customize_rage_card(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Customize the rage action card with specific mechanics"""
        mechanics = feature.get('mechanics', {})
        return {
            'damage_bonus': mechanics.get('damage_bonus', 2),
            'resistances': mechanics.get('resistance', []),
            'duration_rounds': mechanics.get('duration_rounds', 10),
            'special_effects': ['Advantage on Strength checks and saves', 'Extra damage on Strength-based attacks']
        }

    def _customize_action_surge_card(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Customize the Action Surge card"""
        mechanics = feature.get('mechanics', {})
        return {
            'extra_actions': mechanics.get('extra_actions', 1),
            'special_effects': ['Gain an additional action on your turn']
        }

    def _customize_second_wind_card(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Customize the Second Wind card"""
        mechanics = feature.get('mechanics', {})
        return {
            'healing': mechanics.get('healing', '1d10+level'),
            'special_effects': ['Regain hit points as a bonus action']
        }

    def _customize_cunning_action_card(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Customize the Cunning Action card"""
        mechanics = feature.get('mechanics', {})
        return {
            'bonus_actions': mechanics.get('bonus_actions', ['dash', 'disengage', 'hide']),
            'special_effects': ['Use Dash, Disengage, or Hide as a bonus action']
        }

    def get_spellcasting_actions(self, character_id: str, class_id: str) -> List[Dict[str, Any]]:
        """Get spellcasting-related action cards"""
        spellcasting_classes = ['wizard', 'cleric', 'sorcerer', 'warlock', 'bard', 'druid', 'paladin', 'ranger']

        if class_id not in spellcasting_classes:
            return []

        spellcasting_features = self.feature_registry.get_character_features(character_id)
        spell_actions = []

        for feature in spellcasting_features:
            if 'spellcasting' in feature['feature_name'].lower():
                mechanics = feature.get('mechanics', {})

                if 'cantrips_known' in mechanics:
                    spell_actions.append({
                        'name': 'Cast Cantrip',
                        'type': 'action',
                        'description': 'Cast a cantrip spell',
                        'source': 'spellcasting',
                        'available': True,
                        'tooltip': f"Known cantrips: {mechanics['cantrips_known']}"
                    })

                if 'spell_slots' in mechanics:
                    spell_actions.append({
                        'name': 'Cast Spell',
                        'type': 'action',
                        'description': 'Cast a leveled spell',
                        'source': 'spellcasting',
                        'available': True,
                        'tooltip': f"Available spell slots based on level"
                    })

        return spell_actions
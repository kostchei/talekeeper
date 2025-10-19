import random
from typing import Dict, List, Tuple

class TreasureGenerator:

    GEM_VALUES = [10, 50, 100, 500, 1000, 5000]

    ART_OBJECT_TEMPLATES = [
        ('Silver ewer', 25, 1.0),
        ('Carved bone statuette', 25, 0.5),
        ('Small gold bracelet', 25, 0.5),
        ('Cloth-of-gold vestments', 25, 2.0),
        ('Black velvet mask stitched with silver thread', 25, 0.5),
        ('Copper chalice with silver filigree', 25, 1.0),
        ('Pair of engraved bone dice', 25, 0.5),
        ('Small mirror set in a painted wooden frame', 25, 1.0),
        ('Embroidered silk handkerchief', 25, 0.5),
        ('Gold locket with a painted portrait inside', 25, 0.5),

        ('Gold ring set with bloodstones', 250, 0.5),
        ('Carved ivory statuette', 250, 1.5),
        ('Large gold bracelet', 250, 1.0),
        ('Silver necklace with a gemstone pendant', 250, 0.5),
        ('Bronze crown', 250, 2.0),
        ('Silk robe with gold embroidery', 250, 1.5),
        ('Large well-made tapestry', 250, 2.0),
        ('Brass mug with jade inlay', 250, 1.0),
        ('Box of turquoise animal figurines', 250, 1.0),
        ('Gold bird cage with electrum filigree', 250, 1.5),

        ('Silver chalice set with moonstones', 750, 1.5),
        ('Silver-plated steel longsword with jet set in hilt', 750, 1.5),
        ('Carved harp of exotic wood with ivory inlay', 750, 2.0),
        ('Small gold idol', 750, 1.0),
        ('Gold dragon comb set with red garnets', 750, 0.5),
        ('Bottle stopper cork embossed with gold leaf', 750, 0.5),
        ('Ceremonial electrum dagger with black pearl', 750, 1.0),
        ('Silver and gold brooch', 750, 0.5),
        ('Obsidian statuette with gold fittings', 750, 1.5),
        ('Painted gold war mask', 750, 1.0),

        ('Fine gold chain set with a fire opal', 2500, 0.5),
        ('Old masterpiece painting', 2500, 2.0),
        ('Embroidered silk and velvet mantle with gemstones', 2500, 1.5),
        ('Platinum bracelet set with sapphires', 2500, 1.0),
        ('Embroidered glove set with jewel chips', 2500, 0.5),
        ('Jeweled anklet', 2500, 0.5),
        ('Gold music box', 2500, 1.5),
        ('Gold circlet set with four aquamarines', 2500, 1.0),
        ('Eye patch with mock eye set in blue sapphire', 2500, 0.5),
        ('Ceremonial silver and gold armor', 2500, 2.0),
    ]

    @staticmethod
    def generate_gem(min_value: int = 10, max_value: int = 5000) -> Dict:
        available_values = [v for v in TreasureGenerator.GEM_VALUES if min_value <= v <= max_value]
        if not available_values:
            available_values = [TreasureGenerator.GEM_VALUES[0]]

        value_gp = random.choice(available_values)

        gem_types = {
            10: ['Azurite', 'Banded agate', 'Blue quartz', 'Eye agate', 'Hematite', 'Lapis lazuli', 'Malachite', 'Moss agate', 'Obsidian', 'Rhodochrosite', 'Tiger eye', 'Turquoise'],
            50: ['Bloodstone', 'Carnelian', 'Chalcedony', 'Chrysoprase', 'Citrine', 'Jasper', 'Moonstone', 'Onyx', 'Quartz', 'Sardonyx', 'Star rose quartz', 'Zircon'],
            100: ['Amber', 'Amethyst', 'Chrysoberyl', 'Coral', 'Garnet', 'Jade', 'Jet', 'Pearl', 'Spinel', 'Tourmaline'],
            500: ['Alexandrite', 'Aquamarine', 'Black pearl', 'Blue spinel', 'Peridot', 'Topaz'],
            1000: ['Black opal', 'Blue sapphire', 'Emerald', 'Fire opal', 'Opal', 'Star ruby', 'Star sapphire', 'Yellow sapphire'],
            5000: ['Black sapphire', 'Diamond', 'Jacinth', 'Ruby']
        }

        gem_name = random.choice(gem_types.get(value_gp, ['Unknown Gem']))

        weight_lb = value_gp / 10000.0

        return {
            'name': gem_name,
            'item_type': 'treasure',
            'treasure_type': 'gem',
            'value_gp': value_gp,
            'unit_value_gp': value_gp,
            'quantity': 1,
            'weight_lb': weight_lb,
            'description': f'A precious {gem_name.lower()} gem worth {value_gp} GP.'
        }

    @staticmethod
    def generate_art_object(min_value: int = 25, max_value: int = 2500) -> Dict:
        available_art = [art for art in TreasureGenerator.ART_OBJECT_TEMPLATES
                        if min_value <= art[1] <= max_value]
        if not available_art:
            available_art = [TreasureGenerator.ART_OBJECT_TEMPLATES[0]]

        name, value_gp, weight_lb = random.choice(available_art)

        return {
            'name': name,
            'item_type': 'treasure',
            'treasure_type': 'art',
            'value_gp': value_gp,
            'unit_value_gp': value_gp,
            'quantity': 1,
            'weight_lb': weight_lb,
            'description': f'A fine art object worth {value_gp} GP.'
        }

    @staticmethod
    def convert_gold_to_treasure(gold_amount: int, cr: float = 1.0) -> Tuple[List[Dict], int]:
        treasures = []
        remaining_gold = gold_amount

        gem_value_limits = {
            0: (10, 100),
            5: (50, 500),
            11: (100, 1000),
            17: (500, 5000),
        }
        art_value_limits = {
            0: (25, 250),
            5: (250, 750),
            11: (750, 2500),
            17: (750, 2500),
        }

        cr_tier = 0
        if cr >= 17:
            cr_tier = 17
        elif cr >= 11:
            cr_tier = 11
        elif cr >= 5:
            cr_tier = 5

        gem_min, gem_max = gem_value_limits[cr_tier]
        art_min, art_max = art_value_limits[cr_tier]

        while remaining_gold > 0:
            roll = random.random()

            if roll < 0.25:
                gem = TreasureGenerator.generate_gem(gem_min, gem_max)
                if gem['value_gp'] <= remaining_gold:
                    treasures.append(gem)
                    remaining_gold -= gem['value_gp']
                else:
                    break

            elif roll < 0.75:
                art = TreasureGenerator.generate_art_object(art_min, art_max)
                if art['value_gp'] <= remaining_gold:
                    treasures.append(art)
                    remaining_gold -= art['value_gp']
                else:
                    break
            else:
                break

        return treasures, remaining_gold

    @staticmethod
    def should_use_treasure_conversion(gold_amount: int, threshold: int = 1000) -> bool:
        return gold_amount > threshold

    @staticmethod
    def generate_beast_rations(individual_treasure_gp: float) -> Dict:
        """
        Generate rations from beast individual treasure value.

        Args:
            individual_treasure_gp: GP value of individual treasure

        Returns:
            Dict with ration loot item
        """
        ration_cost_gp = 0.5
        ration_weight_lb = 2.0
        quantity = max(1, int(individual_treasure_gp / ration_cost_gp))

        return {
            'name': 'Beast Rations',
            'item_type': 'consumable',
            'treasure_type': 'rations',
            'quantity': quantity,
            'unit_value_gp': ration_cost_gp,
            'value_gp': quantity * ration_cost_gp,
            'weight_lb': quantity * ration_weight_lb,
            'description': f'Edible meat from a slain beast ({quantity} days of food)'
        }

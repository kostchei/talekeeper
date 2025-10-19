import random
import sqlite3
from typing import Dict, Optional, Tuple


HISTORIC_INN_NAMES = [
    "The Crimson Rat", "The Dancing Wench", "The Dog & Lantern", "The Rusty Eel",
    "The Demon's Goblet", "The Singing Trident", "The Boar & Candle", "The Silver Dagger",
    "The Filthy Wheel", "The Captain's Pig", "The Jolly Snake", "The Wise Camel",
    "Cloak & Dragon", "The Royal Axe", "The Gilded Bell", "The Blade & Tankard",
    "The Drunken Shield", "Cup & Blade", "The Jeweled Anvil", "The Frog & Bard",
    "The Red Lion", "The White Hart", "The Royal Oak", "The King's Head",
    "The Queen's Arms", "The Crown & Anchor", "The George & Dragon", "The Rose & Crown",
    "The Golden Eagle", "The Black Bull", "The Green Man", "The Swan & Cygnet",
    "The Old Bell", "The Angel & Crown", "The Lamb & Flag", "The Ship & Anchor",
    "The Plough & Stars", "The Three Barrels", "The Copper Kettle", "The Blue Door",
    "The Hop Pole", "The Barley Mow", "The White Horse", "The Saracen's Head",
    "The Turk's Head", "The Holly Bush", "The Bull & Bush", "The Crossed Keys",
    "The Bell & Dragon", "The Harp & Crown", "The Fox & Hounds", "The Stag & Hounds",
    "The Coach & Horses", "The Wheatsheaf", "The Miller's Arms", "The Smith's Forge",
    "The Traveler's Rest", "The Sailor's Return", "The Merchant's Hall", "The Cooper's Arms"
]

ADJECTIVES = [
    "Red", "White", "Black", "Golden", "Silver", "Blue", "Green",
    "Royal", "King's", "Queen's", "Crown",
    "Old", "Ancient", "New",
    "Jolly", "Merry", "Dancing", "Singing",
    "Wise", "Drunken"
]

NOUNS_ANIMALS = [
    "Lion", "Hart", "Stag", "Boar", "Bear", "Bull", "Eagle", "Swan", "Horse",
    "Dragon", "Wyvern", "Griffin", "Unicorn",
    "Rat", "Eel", "Pig", "Snake", "Camel", "Frog", "Crow",
    "Hound", "Fox", "Hare", "Badger", "Otter", "Wolf", "Raven", "Hawk", "Owl", "Deer"
]

NOUNS_OBJECTS = [
    "Crown", "Bell", "Anvil", "Wheel", "Axe", "Hammer", "Anchor",
    "Rose", "Oak", "Bush", "Tree", "Vine",
    "Tankard", "Goblet", "Barrel", "Keg", "Flagon",
    "Shield", "Sword", "Dagger", "Blade", "Lance",
    "Key", "Lock", "Gate", "Door", "Lantern",
    "Plough", "Sickle", "Mill", "Star", "Moon"
]

OCCUPATIONS = [
    "Smith", "Miller", "Cooper", "Fletcher", "Merchant",
    "Sailor", "Traveler", "Captain", "Bishop", "Friar",
    "Knight", "Abbot", "Shepherd", "Carpenter", "Mason",
    "Brewer", "Baker", "Butcher", "Tailor", "Weaver"
]

MALE_WORTHY_NAMES = [
    "Aelric", "Aldric", "Alwin", "Athelstan", "Beorn",
    "Brand", "Cedric", "Cynric", "Dunstan", "Eadric",
    "Edgar", "Edmund", "Edwin", "Godwin", "Harold",
    "Leofric", "Osric", "Oswald", "Randulf", "Roderic",
    "Siward", "Thorfinn", "Thurstan", "Ulfric", "Wulfric",
    "Geoffrey", "Gilbert", "Hugh", "Ralph", "Roger",
    "Walter", "William", "Robert", "Richard", "Henry",
    "Thomas", "John", "Peter", "Simon", "Matthew",
    "Baldwin", "Bertram", "Conrad", "Godfrey", "Humphrey",
    "Reynard", "Theobald", "Warin", "Warner", "Wymond"
]

FEMALE_WORTHY_NAMES = [
    "Aelgifu", "Aldith", "Edith", "Elfleda", "Godgifu",
    "Gunnhild", "Matilda", "Maud", "Sybil", "Eadgyth",
    "Eleanor", "Isabella", "Joanna", "Katherine", "Margaret",
    "Alice", "Beatrice", "Cecily", "Emma", "Hawise",
    "Joan", "Juliana", "Lucy", "Mary", "Philippa",
    "Agnes", "Avice", "Constance", "Dionisia", "Ela"
]

HAMLET_FEATURES = [
    "Crossing", "Ford", "Bridge", "Mill", "Farm", "Stead",
    "Hollow", "Glen", "Vale", "Dell",
    "Croft", "Garth", "Thorp", "Wick", "End",
    "Green", "Heath", "Moor", "Common", "Rest"
]

VILLAGE_PREFIXES = [
    "High", "Low", "Deep", "Broad", "Long", "Wide",
    "North", "South", "East", "West",
    "Wood", "Stone", "Iron", "Silver", "Gold",
    "River", "Brook", "Lake", "Mere", "Marsh",
    "Hill", "Ridge", "Down", "Peak", "Tor",
    "Oak", "Ash", "Elm", "Willow", "Thorn",
    "White", "Black", "Grey", "Green", "Red",
    "Old", "New", "Fair", "Bright", "Dark"
]

VILLAGE_SUFFIXES = [
    "ton", "ham", "bury", "ford", "bridge",
    "ley", "leigh", "field", "mere", "marsh",
    "wood", "ridge", "hill", "vale", "dale"
]

TOWN_FEATURES = [
    "Castle", "Fort", "Keep", "Tower", "Wall",
    "Market", "Gate", "Port", "Haven", "Cross",
    "King", "Queen", "Prince", "Duke", "Earl"
]

TOWN_SUFFIXES = [
    "ton", "bury", "gate", "port", "haven",
    "field", "shire", "borough", "castle", "keep"
]

HISTORIC_TOWN_NAMES = [
    "Irongate", "Silverkeep", "Kingsport", "Queensbury", "Castleton",
    "Marketshire", "Portfield", "Wallham", "Fortbridge", "Towerhaven",
    "Goldengate", "Redcastle", "Whitehaven", "Blackport", "Greybury",
    "Stonemarket", "Highcastle", "Deepport", "Brightkeep", "Fairhaven"
]


class SettlementNameService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def generate_inn_name(self, seed: int) -> str:
        """Generate inn/tavern name using seed-based randomization."""
        rng = random.Random(seed)

        if rng.random() < 0.6:
            return rng.choice(HISTORIC_INN_NAMES)
        else:
            pattern = rng.choice(["adjective_noun", "noun_and_noun", "possessive"])

            if pattern == "adjective_noun":
                adj = rng.choice(ADJECTIVES)
                noun = rng.choice(NOUNS_ANIMALS + NOUNS_OBJECTS)
                return f"The {adj} {noun}"

            elif pattern == "noun_and_noun":
                nouns = NOUNS_ANIMALS + NOUNS_OBJECTS
                noun1 = rng.choice(nouns)
                noun2 = rng.choice(nouns)
                while noun2 == noun1:
                    noun2 = rng.choice(nouns)
                return f"{noun1} & {noun2}"

            else:
                owner = rng.choice(OCCUPATIONS)
                place = rng.choice(["Arms", "Rest", "Lodge", "Hall", "Table", "Forge"])
                return f"The {owner}'s {place}"

    def generate_worthy_name(self, settlement_type: str, seed: int) -> str:
        """Generate noble/leader name with title based on settlement type."""
        rng = random.Random(seed)

        is_male = rng.random() < 0.7

        if rng.random() < 0.6:
            name = rng.choice(MALE_WORTHY_NAMES if is_male else FEMALE_WORTHY_NAMES)
        else:
            name = self._generate_syllable_name(is_male, rng)

        if settlement_type == 'hamlet':
            if is_male:
                title = rng.choice(["Headman", "Goodman", "Yeoman", "Elder"])
            else:
                title = rng.choice(["Goodwife", "Wise Woman", "Elder"])

        elif settlement_type == 'village':
            if is_male:
                title = rng.choice(["Reeve", "Bailiff", "Alderman", "Squire"])
            else:
                title = rng.choice(["Dame", "Goodwife", "Mistress"])

        else:
            if is_male:
                title = rng.choice(["Lord", "Baron", "Chief", "Thane", "Master"])
            else:
                title = rng.choice(["Lady", "Baroness", "Mistress", "Dame"])

        return f"{title} {name}"

    def _generate_syllable_name(self, is_male: bool, rng: random.Random) -> str:
        """Generate name from syllables (fallback when not using curated lists)."""
        if is_male:
            start = rng.choice(["Ael", "Al", "Ed", "God", "Os", "Wulf", "Thur", "Ran", "Leof"])
            mid = rng.choice(["ric", "win", "stan", "mund", "wald", "bert", "fred"])
            end = rng.choice(["", "son", "ton"])
        else:
            start = rng.choice(["Ae", "Ed", "El", "Gunn", "Gwen", "Mor", "Ceri", "Bran"])
            mid = rng.choice(["gi", "flae", "hild", "wen", "wyn", "dwen"])
            end = rng.choice(["da", "lyn", "wen", "eth", "ith", "lian"])

        syllable_count = rng.choice([2, 3])
        if syllable_count == 2:
            return f"{start}{mid}"
        else:
            return f"{start}{mid}{end}"

    def generate_settlement_name(self, settlement_type: str, biome: str, seed: int) -> str:
        """Generate settlement name based on type and biome."""
        rng = random.Random(seed)

        if settlement_type == 'hamlet':
            owner = rng.choice(MALE_WORTHY_NAMES + FEMALE_WORTHY_NAMES)
            feature = rng.choice(HAMLET_FEATURES)
            return f"{owner}'s {feature}"

        elif settlement_type == 'village':
            prefix = rng.choice(VILLAGE_PREFIXES)
            suffix = rng.choice(VILLAGE_SUFFIXES)
            return f"{prefix}{suffix}"

        else:
            if rng.random() < 0.5:
                return rng.choice(HISTORIC_TOWN_NAMES)
            else:
                feature = rng.choice(TOWN_FEATURES)
                suffix = rng.choice(TOWN_SUFFIXES)
                return f"{feature}{suffix}"

    def get_or_create_settlement_names(self, character_id: str, q: int, r: int) -> Dict:
        """Get existing names or generate new ones for hex settlement."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT settlement_type, settlement_name, accommodation_name, encounter_seed
            FROM character_hex_map
            WHERE character_id = ? AND q = ? AND r = ?
        ''', (character_id, q, r))

        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        settlement_type, existing_settlement_name, existing_accommodation_name, seed = row

        if settlement_type in [None, 'empty']:
            conn.close()
            return {
                'settlement_type': 'empty',
                'settlement_name': None,
                'accommodation_name': None,
                'worthy_name': None,
                'population': 0
            }

        if existing_settlement_name and existing_accommodation_name:
            conn.close()
            return {
                'settlement_type': settlement_type,
                'settlement_name': existing_settlement_name,
                'accommodation_name': existing_accommodation_name,
                'worthy_name': None,
                'population': self._estimate_population(settlement_type)
            }

        population = self._estimate_population(settlement_type)
        settlement_name = None
        accommodation_name = None
        worthy_name = None

        if population >= 500:
            settlement_name = self.generate_settlement_name(settlement_type, 'plains', seed)

        highest_lifestyle = self._determine_highest_lifestyle(settlement_type)
        if highest_lifestyle in ['modest', 'comfortable', 'wealthy']:
            accommodation_name = self.generate_inn_name(seed + 1)

        if settlement_type in ['village', 'town_small', 'town_medium', 'town_large']:
            worthy_name = self.generate_worthy_name(settlement_type, seed + 2)

        cursor.execute('''
            UPDATE character_hex_map
            SET settlement_name = ?, accommodation_name = ?
            WHERE character_id = ? AND q = ? AND r = ?
        ''', (settlement_name, accommodation_name, character_id, q, r))

        conn.commit()
        conn.close()

        return {
            'settlement_type': settlement_type,
            'settlement_name': settlement_name,
            'accommodation_name': accommodation_name,
            'worthy_name': worthy_name,
            'population': population
        }

    def _estimate_population(self, settlement_type: str) -> int:
        """Estimate population midpoint for settlement type."""
        population_map = {
            'hamlet': 100,
            'village': 750,
            'town_small': 2500,
            'town_medium': 5000,
            'town_large': 10000
        }
        return population_map.get(settlement_type, 0)

    def _determine_highest_lifestyle(self, settlement_type: str) -> str:
        """Determine highest available lifestyle for settlement type."""
        lifestyle_map = {
            'hamlet': 'modest',
            'village': 'comfortable',
            'town_small': 'wealthy',
            'town_medium': 'wealthy',
            'town_large': 'wealthy'
        }
        return lifestyle_map.get(settlement_type, 'wretched')

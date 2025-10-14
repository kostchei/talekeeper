import sqlite3
from typing import List, Dict, Tuple

MONSTERS_BY_CR = {
    "0": ["Commoner"],
    "1/8": ["Bandit", "Guard", "Cultist", "Tribal Warrior", "Warrior Infantry", "Noble"],
    "1/4": ["Skeleton", "Preist Acolyte", "Grimlock", "Axe Beak", "Zombie"],
    "1/2": ["Scout", "Tough", "Ape", "Shadow"],
    "1": ["Animated Armor", "Giant Spider", "Giant Vulture", "Lion", "Pirate", "Spy",
          "Spectre", "Manes Vapourswarm", "Orgrillon Ogre", "Yuan-ti Infiltrator"],
    "2": ["Bandit Captain", "Berserker", "Cult Fanatic", "Mage Apprentice",
          "Giant Constrictor Snake", "Gibbering Mouther", "Priest", "Shadow Mastif",
          "Ogre", "Ettercap", "Quaggoth"],
    "3": ["Knight", "Warrior Veteran", "Scout Captain", "Wight", "Phase Spider",
          "Bandit Captain", "Manticore", "Quaggoth Thonot", "Yeti", "Mummy"],
    "4": ["Shadow Demon", "Guard Captain", "Tough Boss", "Succubus", "Helmed Horror",
          "Black Pudding", "Ghost"],
    "5": ["Gladiator", "Champion", "Gibbering Mouther", "Giant Crocodile", "Barlgura",
          "Hill Giant", "Giant Axe Beak", "Wraith", "Skum"],
    "6": ["Mage", "Pirate Capatain", "Vrock", "Wyvern", "Giant Squid"],
    "7": ["Giant Ape", "Bandit Deceiver", "Stone Giant", "Yuan-ti Abomination"],
    "8": ["Assassin", "Aberrant Cultist", "Frost Giant", "Berserker Commander",
          "Death Cultist", "Fiend Cultist", "Tyrannosaurus Rex", "Hezrou",
          "Vampire Nightbringer"],
    "9": ["Champion", "Glabrezu", "Gray Slaad", "Fire Giant", "Abominable Yeti"],
    "10": ["Cultist Heirophant", "Noble Prodigy", "Spy Master", "Warrior Commander",
           "Stone Golem", "Aboleth"]
}

def check_monster_exists(cursor: sqlite3.Cursor, monster_name: str) -> Tuple[bool, str, str]:
    query = "SELECT name, challenge_rating FROM monsters WHERE LOWER(name) = LOWER(?)"
    cursor.execute(query, (monster_name,))
    result = cursor.fetchone()

    if result:
        return True, result[0], result[1]

    query_partial = "SELECT name, challenge_rating FROM monsters WHERE LOWER(name) LIKE LOWER(?)"
    cursor.execute(query_partial, (f"%{monster_name}%",))
    result = cursor.fetchone()

    if result:
        return True, result[0], result[1]

    return False, "", ""

def main():
    db_path = "talekeeper.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    total_monsters = 0
    found_monsters = 0
    missing_monsters = []
    found_list = []

    print("=" * 80)
    print("TALEKEEPER MONSTER DATABASE CHECK")
    print("=" * 80)
    print()

    for cr, monsters in MONSTERS_BY_CR.items():
        print(f"\n### CR {cr}")
        print("-" * 40)

        for monster in monsters:
            total_monsters += 1
            exists, db_name, db_cr = check_monster_exists(cursor, monster)

            if exists:
                found_monsters += 1
                status = "FOUND"
                if db_name.lower() != monster.lower():
                    print(f"  [{status}] {monster} -> DB: '{db_name}' (CR {db_cr})")
                else:
                    print(f"  [{status}] {monster} (CR {db_cr})")
                found_list.append((cr, monster, db_name, db_cr))
            else:
                status = "MISSING"
                print(f"  [{status}] {monster}")
                missing_monsters.append((cr, monster))

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Monsters Checked: {total_monsters}")
    print(f"Found in Database: {found_monsters} ({found_monsters/total_monsters*100:.1f}%)")
    print(f"Missing from Database: {len(missing_monsters)} ({len(missing_monsters)/total_monsters*100:.1f}%)")

    if missing_monsters:
        print(f"\n### MISSING MONSTERS ({len(missing_monsters)})")
        print("-" * 40)
        current_cr = None
        for cr, monster in missing_monsters:
            if cr != current_cr:
                print(f"\nCR {cr}:")
                current_cr = cr
            print(f"  - {monster}")

    print("\n" + "=" * 80)

    cursor.execute("SELECT COUNT(*) FROM monsters")
    total_in_db = cursor.fetchone()[0]
    print(f"\nTotal monsters in database: {total_in_db}")

    conn.close()

if __name__ == "__main__":
    main()

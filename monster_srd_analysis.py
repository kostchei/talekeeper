import re

MISSING_MONSTERS = [
    'Preist Acolyte',
    'Spectre',
    'Manes Vapourswarm',
    'Orgrillon Ogre',
    'Yuan-ti Infiltrator',
    'Mage Apprentice',
    'Shadow Mastif',
    'Scout Captain',
    'Shadow Demon',
    'Champion',
    'Giant Axe Beak',
    'Skum',
    'Pirate Capatain',
    'Giant Squid',
    'Bandit Deceiver',
    'Aberrant Cultist',
    'Berserker Commander',
    'Death Cultist',
    'Fiend Cultist',
    'Vampire Nightbringer',
    'Cultist Heirophant',
    'Noble Prodigy',
    'Spy Master',
    'Warrior Commander'
]

SRD_VARIATIONS = {
    'Spectre': ['Specter'],
    'Shadow Mastif': ['Shadow Mastiff'],
    'Pirate Capatain': ['Pirate Captain'],
    'Cultist Heirophant': ['Cultist Hierophant']
}

def search_srd(monster_name, srd_content):
    variations = [monster_name] + SRD_VARIATIONS.get(monster_name, [])

    for variant in variations:
        pattern = r'\b' + re.escape(variant) + r'\b'
        matches = re.findall(pattern, srd_content, re.IGNORECASE)
        if matches:
            return True, variant, len(matches)

    base_words = monster_name.split()
    if len(base_words) > 1:
        base = base_words[-1]
        pattern = r'\b' + re.escape(base) + r'\b'
        matches = re.findall(pattern, srd_content, re.IGNORECASE)
        if matches and len(matches) < 100:
            return True, f"{base} (base form)", len(matches)

    return False, None, 0

def main():
    srd_path = 'docs/SRD_CC_v5.2.1.md'

    with open(srd_path, 'r', encoding='utf-8') as f:
        srd_content = f.read()

    print('=' * 80)
    print('MISSING MONSTERS - SRD ANALYSIS')
    print('=' * 80)
    print()

    in_srd = []
    not_in_srd = []
    probable_homebrew = []

    for monster in MISSING_MONSTERS:
        found, variant, count = search_srd(monster, srd_content)

        if found and variant and 'base form' not in variant:
            in_srd.append((monster, variant, count))
            print(f'[IN SRD] {monster}')
            if variant != monster:
                print(f'         -> Found as: "{variant}" ({count} mentions)')
        elif found and 'base form' in variant:
            print(f'[VARIANT] {monster}')
            print(f'          -> Base form in SRD: {variant}')
            probable_homebrew.append((monster, variant))
        else:
            not_in_srd.append(monster)
            print(f'[NOT IN SRD] {monster}')

    print()
    print('=' * 80)
    print('SUMMARY')
    print('=' * 80)
    print(f'Total Missing Monsters: {len(MISSING_MONSTERS)}')
    print(f'Found in SRD: {len(in_srd)}')
    print(f'Variants (base in SRD): {len(probable_homebrew)}')
    print(f'Not in SRD (homebrew): {len(not_in_srd)}')

    if in_srd:
        print()
        print('IN SRD (Should be added):')
        for monster, variant, count in in_srd:
            if variant != monster:
                print(f'  - {monster} (as "{variant}")')
            else:
                print(f'  - {monster}')

    if probable_homebrew:
        print()
        print('PROBABLE VARIANTS (base creature in SRD):')
        for monster, base in probable_homebrew:
            print(f'  - {monster} (base: {base})')

    if not_in_srd:
        print()
        print('NOT IN SRD (likely homebrew/3rd party):')
        for monster in not_in_srd:
            print(f'  - {monster}')

if __name__ == '__main__':
    main()

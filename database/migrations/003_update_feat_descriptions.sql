-- Update feat descriptions with D&D 2024 rules
-- Adds stat increases, categories (O=Origin, FS=Fighting Style), and full descriptions

-- General Feats (Alphabetical)
UPDATE feats SET description = 'Increase one ability score by 2, or increase two ability scores by 1 each. You cannot increase an ability score above 20.' WHERE id = 'ability_score_improvement';

UPDATE feats SET description = 'Talented at mimicry and dramatics. Advantage on Charisma (Deception) and Charisma (Performance) checks when trying to pass yourself off as a different person. You can mimic the speech of another person or creature sounds. +1 Charisma.' WHERE id = 'actor';

UPDATE feats SET description = 'Talented at mimicry and dramatics. Advantage on Charisma (Deception) and Charisma (Performance) checks when trying to pass yourself off as a different person. You can mimic the speech of another person or creature sounds. +1 Charisma.' WHERE id = 'actor';

UPDATE feats SET description = 'You have undergone extensive physical training. Climbing does not cost extra movement. You can make a running long jump or running high jump after moving only 5 feet. +1 Strength or Dexterity.' WHERE id = 'athlete';

UPDATE feats SET description = 'You learn two cantrips of your choice from the Cleric spell list. This is a Fighting Style option for Paladins.' WHERE id = 'blessed_warrior';

UPDATE feats SET description = 'You have blindsight with a range of 10 feet. Within that range, you can effectively see anything that is not behind total cover, even if you are blinded or in darkness.' WHERE id = 'blind_fighting';

UPDATE feats SET description = 'Epic Boon (Level 19+). You gain proficiency in all skills. If you are already proficient in a skill, you add double your proficiency bonus to checks using it.' WHERE id = 'boon_of_combat_prowess';

UPDATE feats SET description = 'Epic Boon (Level 19+). As a bonus action, you can teleport up to 30 feet to an unoccupied space you can see.' WHERE id = 'boon_of_dimensional_travel';

UPDATE feats SET description = 'Epic Boon (Level 19+). You gain resistance to two damage types of your choice (except bludgeoning, piercing, or slashing).' WHERE id = 'boon_of_energy_resistance';

UPDATE feats SET description = 'Epic Boon (Level 19+). When you miss with an attack roll or fail an ability check or saving throw, you can roll 1d10 and add it to the total, potentially turning it into a success. Once used, cannot be used again until you finish a short or long rest.' WHERE id = 'boon_of_fate';

UPDATE feats SET description = 'Epic Boon (Level 19+). Your hit point maximum increases by 40.' WHERE id = 'boon_of_fortitude';

UPDATE feats SET description = 'Epic Boon (Level 19+). You can bypass the resistances and immunities to damage of any creature.' WHERE id = 'boon_of_irresistible_offense';

UPDATE feats SET description = 'Epic Boon (Level 19+). You can use a bonus action to regain hit points equal to half your hit point maximum. Once used, cannot be used again until you finish a long rest.' WHERE id = 'boon_of_recovery';

UPDATE feats SET description = 'Epic Boon (Level 19+). You gain proficiency in all skills. If you are already proficient, you add double your proficiency bonus to checks with that skill.' WHERE id = 'boon_of_skill';

UPDATE feats SET description = 'Epic Boon (Level 19+). Your walking speed increases by 30 feet.' WHERE id = 'boon_of_speed';

UPDATE feats SET description = 'Epic Boon (Level 19+). You can cast any spell you have previously cast today without expending a spell slot. Once used, cannot be used again until you finish a long rest.' WHERE id = 'boon_of_spell_recall';

UPDATE feats SET description = 'Epic Boon (Level 19+). You have truesight out to a range of 60 feet.' WHERE id = 'boon_of_truesight';

UPDATE feats SET description = 'Epic Boon (Level 19+). You gain darkvision out to 120 feet, and you have advantage on Dexterity (Stealth) checks made to hide in darkness or dim light.' WHERE id = 'boon_of_the_night_spirit';

UPDATE feats SET description = 'When you use your action to Dash, you can use a bonus action to make one melee weapon attack or to shove a creature. If you move at least 10 feet in a straight line before the attack or shove, you either gain +5 to damage or push the target 10 feet.' WHERE id = 'charger';

UPDATE feats SET description = 'Time and effort spent mastering the culinary arts. You gain proficiency with cook''s utensils. You can cook special food during a long rest providing temporary hit points. +1 Constitution or Wisdom.' WHERE id = 'chef';

UPDATE feats SET description = 'Thanks to extensive practice with crossbows, you ignore the loading property, being within 5 feet of a hostile creature does not impose disadvantage on ranged attack rolls, and when you use the Attack action with a one-handed weapon, you can use a bonus action to attack with a loaded hand crossbow.' WHERE id = 'crossbow_expert';

UPDATE feats SET description = 'You are practiced in the art of crushing your enemies. Once per turn when you hit with an attack that deals bludgeoning damage, you can move the target 5 feet to an unoccupied space. When you score a critical hit, attack rolls against the target have advantage until the start of your next turn. +1 Strength or Constitution.' WHERE id = 'crusher';

UPDATE feats SET description = 'When you are hit by an attack while wielding a finesse weapon, you can use your reaction to add your proficiency bonus to your AC for that attack, potentially causing it to miss. Requires 13+ Dexterity.' WHERE id = 'defensive_duelist';

UPDATE feats SET description = 'You learn two cantrips from the Druid spell list. This is a Fighting Style option for Rangers.' WHERE id = 'druidic_warrior';

UPDATE feats SET description = 'You master two-weapon fighting. You gain +1 AC while wielding a separate melee weapon in each hand. You can draw or stow two one-handed weapons when you would normally draw or stow one. +1 Strength or Dexterity.' WHERE id = 'dual_wielder';

UPDATE feats SET description = 'Alert to hidden traps and secret doors. You have advantage on Perception checks to detect secret doors and traps. You have advantage on saving throws to avoid or resist traps. You have resistance to damage dealt by traps. +1 Intelligence or Wisdom.' WHERE id = 'dungeon_delver';

UPDATE feats SET description = 'Hardy and resilient. When you roll Hit Dice to regain hit points, the minimum number you can roll is equal to twice your Constitution modifier (minimum of 2). +1 Constitution.' WHERE id = 'durable';

UPDATE feats SET description = 'When you gain this feat, choose a damage type: acid, cold, fire, lightning, or thunder. Spells you cast ignore resistance to that damage type. When you roll damage for a spell you cast that deals damage of that type, you can treat any 1 on a damage die as a 2. You can select this feat multiple times, choosing a different damage type each time.' WHERE id = 'elemental_adept';

UPDATE feats SET description = 'Your exposure to the Feywild has changed you. You learn Misty Step and one 1st-level spell of your choice from the Divination or Enchantment school. You can cast each spell once without a spell slot, regaining the ability on a long rest. You can also cast these spells using spell slots. +1 Intelligence, Wisdom, or Charisma.' WHERE id = 'fey-touched';

UPDATE feats SET description = 'You have advantage on attack rolls against a creature you are grappling. You can use your action to try to pin a creature grappled by you (escape DC = 8 + proficiency + Strength modifier). Until the grapple ends, the creature is restrained and you cannot grapple another creature. +1 Strength or Dexterity.' WHERE id = 'grappler';

UPDATE feats SET description = 'Before you make a melee attack with a heavy weapon, you can choose to take a -5 penalty to the attack roll. If the attack hits, you add +10 to the damage.' WHERE id = 'great_weapon_master';

UPDATE feats SET description = 'You have trained to master the use of heavy armor. You gain proficiency with heavy armor. +1 Strength.' WHERE id = 'heavily_armored';

UPDATE feats SET description = 'You can use your armor to deflect strikes. While wearing heavy armor, bludgeoning, piercing, and slashing damage you take from nonmagical attacks is reduced by 3. +1 Strength.' WHERE id = 'heavy_armor_master';

UPDATE feats SET description = 'When a creature you can see hits a target other than you within 5 feet with an attack, you can use your reaction to reduce the damage by 1d10 + your proficiency bonus. You must be wielding a shield or a simple or martial weapon. This is a Fighting Style option.' WHERE id = 'interception';

UPDATE feats SET description = 'You have a mind that can track time, direction, and detail with uncanny precision. You always know which way is north and hours until sunrise/sunset. You can accurately recall anything you have seen or heard in the past month. +1 Intelligence.' WHERE id = 'keen_mind';

UPDATE feats SET description = 'You have trained to master the use of light armor. You gain proficiency with light armor. +1 Strength or Dexterity.' WHERE id = 'lightly_armored';

UPDATE feats SET description = 'You have studied languages and codes. You learn three languages. You can create written ciphers that others cannot decipher without magic or your help. +1 Intelligence.' WHERE id = 'linguist';

UPDATE feats SET description = 'You have experience slaying spellcasters. When a creature within 5 feet casts a spell, you can make a melee weapon attack against them as a reaction. When you damage a creature concentrating on a spell, it has disadvantage on the saving throw. You have advantage on saves against spells cast by creatures within 5 feet.' WHERE id = 'mage_slayer';

UPDATE feats SET description = 'You learn two maneuvers from the Battle Master archetype and gain one superiority die (d6). You can use this die to fuel your maneuvers. It is expended when you use it and is regained when you finish a short or long rest.' WHERE id = 'martial_adept';

UPDATE feats SET description = 'You have trained extensively with martial weapons. You gain proficiency with four martial weapons of your choice. +1 Strength or Dexterity.' WHERE id = 'martial_weapon_training';

UPDATE feats SET description = 'You have practiced moving in medium armor. Wearing medium armor does not impose disadvantage on Dexterity (Stealth) checks. When wearing medium armor, you can add 3, rather than 2, to your AC if you have a Dexterity of 16 or higher.' WHERE id = 'medium_armor_master';

UPDATE feats SET description = 'You are exceptionally speedy and agile. Your speed increases by 10 feet. When you use the Dash action, difficult terrain does not cost extra movement. When you make a melee attack, you do not provoke opportunity attacks from that target for the rest of the turn.' WHERE id = 'mobile';

UPDATE feats SET description = 'You have trained to master the use of medium armor and shields. You gain proficiency with medium armor and shields. +1 Strength or Dexterity.' WHERE id = 'moderately_armored';

UPDATE feats SET description = 'You are a dangerous foe to face while mounted. You have advantage on melee attack rolls against unmounted creatures smaller than your mount. You can force an attack targeting your mount to target you instead. If your mount is subjected to an effect allowing a Dexterity save for half damage, it takes no damage on success and half on failure.' WHERE id = 'mounted_combatant';

UPDATE feats SET description = 'You are adept at using your sharp mind to notice details. You gain a +5 bonus to passive Perception and passive Investigation. You can read lips. +1 Intelligence or Wisdom.' WHERE id = 'observant';

UPDATE feats SET description = 'You have achieved mastery over piercing weapons. Once per turn when you hit with an attack that deals piercing damage, you can reroll one damage die and use either result. When you score a critical hit with piercing damage, you can roll one additional damage die. +1 Strength or Dexterity.' WHERE id = 'piercer';

UPDATE feats SET description = 'You gain proficiency with the poisoner''s kit. You can apply poison to a weapon as a bonus action. When you make a damage roll that deals poison damage, it ignores resistance. You can coat a weapon in poison as a bonus action. +1 Intelligence.' WHERE id = 'poisoner';

UPDATE feats SET description = 'You can keep your enemies at bay with reach weapons. While wielding a glaive, halberd, quarterstaff, pike, or spear, other creatures provoke an opportunity attack when they enter your reach. You can use a bonus action to make a melee attack with the opposite end of the weapon (1d4 bludgeoning).' WHERE id = 'polearm_master';

UPDATE feats SET description = 'Choose a saving throw. You gain proficiency in that save. +1 to the ability score for the chosen save.' WHERE id = 'resilient';

UPDATE feats SET description = 'You learn two cantrips and can cast them as rituals. Choose a class: Cleric, Druid, or Wizard. You learn two 1st-level spells with the ritual tag from that class. You can cast these spells as rituals. +1 Intelligence or Wisdom.' WHERE id = 'ritual_caster';

UPDATE feats SET description = 'You have mastered techniques to take advantage of openings. Creatures provoke opportunity attacks even if they Disengage. When you hit with an opportunity attack, the target''s speed becomes 0 for the rest of the turn. When a creature within 5 feet makes an attack against a target other than you, you can use your reaction to make a melee weapon attack against the attacking creature.' WHERE id = 'sentinel';

UPDATE feats SET description = 'Your exposure to the Shadowfell has changed you. You learn Invisibility and one 1st-level spell of your choice from the Illusion or Necromancy school. You can cast each once without a spell slot, regaining the ability on a long rest. You can also cast these spells using spell slots. +1 Intelligence, Wisdom, or Charisma.' WHERE id = 'shadow-touched';

UPDATE feats SET description = 'You have mastered ranged weapons and can make shots others find difficult. Attacking at long range does not impose disadvantage. Your ranged weapon attacks ignore half cover and three-quarters cover. Before you make a ranged attack with a weapon, you can take a -5 penalty to the attack roll. If the attack hits, you add +10 to damage.' WHERE id = 'sharpshooter';

UPDATE feats SET description = 'You use shields for offense and defense. If you take the Attack action, you can use a bonus action to shove with your shield. If you are not incapacitated, you can add your shield''s AC bonus to Dexterity saves against spells and harmful effects targeting only you. If you succeed on a Dexterity save for half damage while using a shield, you take no damage instead.' WHERE id = 'shield_master';

UPDATE feats SET description = 'You have honed your skills. You gain proficiency in one skill. You gain expertise in one skill you are proficient in (double proficiency bonus). +1 to any ability score.' WHERE id = 'skill_expert';

UPDATE feats SET description = 'You are expert at slinking through shadows. You can hide when lightly obscured. When hidden and you miss with a ranged attack, making the attack does not reveal your position. Dim light does not impose disadvantage on Perception checks. +1 Dexterity.' WHERE id = 'skulker';

UPDATE feats SET description = 'You have learned where to cut to have the greatest effect. Once per turn when you hit with slashing damage, you can reduce the target''s speed by 10 feet until the start of your next turn. When you score a critical hit with slashing damage, you grievously wound the target; it has disadvantage on attack rolls until the start of your next turn. +1 Strength or Dexterity.' WHERE id = 'slasher';

UPDATE feats SET description = 'You are uncommonly swift. Your walking speed increases by 10 feet. +1 Strength, Dexterity, or Constitution.' WHERE id = 'speedy';

UPDATE feats SET description = 'You have learned techniques for enhancing your attacks with spells. When you cast a spell that requires you to make an attack roll, the spell''s range is doubled. Your ranged spell attacks ignore half cover and three-quarters cover. You learn one cantrip requiring an attack roll from a class spell list. +1 Intelligence, Wisdom, or Charisma.' WHERE id = 'spell_sniper';

UPDATE feats SET description = 'You learn the prestidigitation and mage hand cantrips. You can cast mage hand without verbal or somatic components, and you can make the hand invisible. You can use the bonus action granted by mage hand to try to shove a creature or make a Dexterity (Sleight of Hand) check. +1 Intelligence, Wisdom, or Charisma.' WHERE id = 'telekinetic';

UPDATE feats SET description = 'You learn the detect thoughts spell and can cast it once without a spell slot, regaining the ability on a long rest. You can communicate telepathically with any willing creature within 60 feet. You do not need to share a language but the creature must understand at least one language. +1 Intelligence, Wisdom, or Charisma.' WHERE id = 'telepathic';

UPDATE feats SET description = 'You master unarmed strikes and grappling. Your unarmed strikes deal 1d6 + Strength modifier bludgeoning damage. When you hit with an unarmed strike as part of the Attack action, you can grapple or shove as a bonus action. This is a Fighting Style option.' WHERE id = 'unarmed_fighting';

UPDATE feats SET description = 'You have practiced casting spells in combat. You have advantage on Constitution saves to maintain concentration when damaged. You can perform somatic components even when wielding weapons or a shield. You can use your reaction to cast a spell at a creature that provokes an opportunity attack.' WHERE id = 'war_caster';

UPDATE feats SET description = 'You have practiced extensively with weapons. You gain proficiency with four weapons of your choice. +1 Strength or Dexterity.' WHERE id = 'weapon_master';

UPDATE feats SET description = 'You have been touched by the Outer Planes. You gain proficiency in Intimidation or Persuasion. You can manifest spectral wings as a bonus action, gaining a flying speed equal to your walking speed for 1 minute. Once used, cannot be used again until you finish a long rest. +1 Strength, Dexterity, or Charisma.' WHERE id = 'inspiring_leader';

-- Update categories for proper sorting
UPDATE feats SET category = 'O' WHERE id IN (
    'alert', 'crafter', 'healer', 'lucky', 'magic_initiate_cleric', 'magic_initiate_wizard',
    'musician', 'savage_attacker', 'skilled', 'tavern_brawler', 'tough'
);

UPDATE feats SET category = 'FS' WHERE id IN (
    'archery', 'blind_fighting', 'blessed_warrior', 'defense', 'druidic_warrior',
    'dueling', 'great_weapon_fighting', 'interception', 'protection',
    'thrown_weapon_fighting', 'two-weapon_fighting', 'unarmed_fighting'
);

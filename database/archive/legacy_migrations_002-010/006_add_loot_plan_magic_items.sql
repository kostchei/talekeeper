-- Migration 006: Add Loot Plan Magic Items
-- Adds magical items from the loot plan to support the hoard treasure system

-- Common Magic Items
INSERT INTO equipment (name, description, item_type, rarity, cost_gp, weight_lb, is_magical) VALUES
('1st Level Spell Scroll', 'A spell scroll containing a 1st-level spell. A spellcaster can use an action to cast the spell without expending a spell slot.', 'consumable', 'common', 25.0, 0.0, 1),
('Silvered Weapon (Rapier)', 'A rapier plated with silver for harming certain creatures.', 'weapon', 'common', 100.0, 2.0, 1),
('Silvered Weapon (Longsword)', 'A longsword plated with silver for harming certain creatures.', 'weapon', 'common', 115.0, 3.0, 1),
('Silvered Weapon (Greatsword)', 'A greatsword plated with silver for harming certain creatures.', 'weapon', 'common', 150.0, 6.0, 1),
('Silvered Weapon (Greataxe)', 'A greataxe plated with silver for harming certain creatures.', 'weapon', 'common', 130.0, 7.0, 1),
('Silvered Weapon (Scimitar)', 'A scimitar plated with silver for harming certain creatures.', 'weapon', 'common', 125.0, 3.0, 1),
('Silvered Weapon (Spear)', 'A spear plated with silver for harming certain creatures.', 'weapon', 'common', 102.0, 3.0, 1),
('Silvered Weapon (Staff)', 'A quarterstaff plated with silver for harming certain creatures.', 'weapon', 'common', 102.0, 4.0, 1);

-- Uncommon Magic Items
INSERT INTO equipment (name, description, item_type, rarity, cost_gp, weight_lb, is_magical) VALUES
('Potion of Greater Healing', 'A magic potion that restores 4d4 + 4 hit points when consumed as a bonus action.', 'consumable', 'uncommon', 200.0, 0.5, 1),
('2nd Level Spell Scroll', 'A spell scroll containing a 2nd-level spell. A spellcaster can use an action to cast the spell without expending a spell slot.', 'consumable', 'uncommon', 50.0, 0.0, 1),
('3rd Level Spell Scroll', 'A spell scroll containing a 3rd-level spell. A spellcaster can use an action to cast the spell without expending a spell slot.', 'consumable', 'uncommon', 100.0, 0.0, 1),
('Luckstone', 'While this polished agate is on your person, you gain a +1 bonus to ability checks and saving throws.', 'wondrous item', 'uncommon', 200.0, 0.0, 1),
('Shield +1', 'A shield that grants a +1 bonus to AC in addition to the shield''s normal bonus to AC.', 'armor', 'uncommon', 200.0, 6.0, 1),
('Rapier +1', 'A magic rapier with a +1 bonus to attack and damage rolls.', 'weapon', 'uncommon', 200.0, 2.0, 1),
('Longsword +1', 'A magic longsword with a +1 bonus to attack and damage rolls.', 'weapon', 'uncommon', 200.0, 3.0, 1),
('Greatsword +1', 'A magic greatsword with a +1 bonus to attack and damage rolls.', 'weapon', 'uncommon', 200.0, 6.0, 1),
('Greataxe +1', 'A magic greataxe with a +1 bonus to attack and damage rolls.', 'weapon', 'uncommon', 200.0, 7.0, 1),
('Scimitar +1', 'A magic scimitar with a +1 bonus to attack and damage rolls.', 'weapon', 'uncommon', 200.0, 3.0, 1),
('Spear +1', 'A magic spear with a +1 bonus to attack and damage rolls.', 'weapon', 'uncommon', 200.0, 3.0, 1),
('Staff +1', 'A magic quarterstaff with a +1 bonus to attack and damage rolls.', 'weapon', 'uncommon', 200.0, 4.0, 1),
('Wand of the War Mage +1', 'While holding this wand, you gain a +1 bonus to spell attack rolls. In addition, you ignore half cover when making a spell attack.', 'wand', 'uncommon', 200.0, 1.0, 1),
('Rod of the Pact Keeper +1', 'While holding this rod, you gain a +1 bonus to spell attack rolls and to the saving throw DCs of your warlock spells. You can regain one warlock spell slot as an action once per long rest.', 'rod', 'uncommon', 200.0, 2.0, 1),
('Cloak of Protection', 'You gain a +1 bonus to AC and saving throws while you wear this cloak.', 'wondrous item', 'uncommon', 200.0, 1.0, 1),
('Adamantine Breastplate', 'This armor is reinforced with adamantine, making any critical hit against you become a normal hit.', 'armor', 'uncommon', 500.0, 20.0, 1),
('Adamantine Half Plate', 'This armor is reinforced with adamantine, making any critical hit against you become a normal hit.', 'armor', 'uncommon', 950.0, 40.0, 1),
('Adamantine Plate', 'This armor is reinforced with adamantine, making any critical hit against you become a normal hit.', 'armor', 'uncommon', 1700.0, 65.0, 1),
('Bag of Holding', 'This bag has an interior space considerably larger than its outside dimensions. The bag can hold up to 500 pounds, not exceeding a volume of 64 cubic feet.', 'wondrous item', 'uncommon', 200.0, 15.0, 1);

-- Rare Magic Items
INSERT INTO equipment (name, description, item_type, rarity, cost_gp, weight_lb, is_magical) VALUES
('Potion of Superior Healing', 'A magic potion that restores 8d4 + 8 hit points when consumed as a bonus action.', 'consumable', 'rare', 2000.0, 0.5, 1),
('4th Level Spell Scroll', 'A spell scroll containing a 4th-level spell. A spellcaster can use an action to cast the spell without expending a spell slot.', 'consumable', 'rare', 200.0, 0.0, 1),
('5th Level Spell Scroll', 'A spell scroll containing a 5th-level spell. A spellcaster can use an action to cast the spell without expending a spell slot.', 'consumable', 'rare', 500.0, 0.0, 1),
('Plate Armor +1', 'Magical plate armor that grants a +1 bonus to AC.', 'armor', 'rare', 2000.0, 65.0, 1),
('Studded Leather +1', 'Magical studded leather armor that grants a +1 bonus to AC.', 'armor', 'rare', 2000.0, 13.0, 1),
('Elven Chain', 'You gain a +1 bonus to AC while wearing this armor. You are considered proficient with this armor even if you lack proficiency with medium armor.', 'armor', 'rare', 2000.0, 20.0, 1),
('Rapier +2', 'A magic rapier with a +2 bonus to attack and damage rolls.', 'weapon', 'rare', 2000.0, 2.0, 1),
('Longsword +2', 'A magic longsword with a +2 bonus to attack and damage rolls.', 'weapon', 'rare', 2000.0, 3.0, 1),
('Greatsword +2', 'A magic greatsword with a +2 bonus to attack and damage rolls.', 'weapon', 'rare', 2000.0, 6.0, 1),
('Greataxe +2', 'A magic greataxe with a +2 bonus to attack and damage rolls.', 'weapon', 'rare', 2000.0, 7.0, 1),
('Scimitar +2', 'A magic scimitar with a +2 bonus to attack and damage rolls.', 'weapon', 'rare', 2000.0, 3.0, 1),
('Executioner''s Axe', 'When you roll a 20 on your attack roll with this magic weapon, the target takes an extra 10 slashing damage.', 'weapon', 'rare', 2000.0, 7.0, 1),
('Vicious Weapon', 'When you roll a 20 on your attack roll with this magic weapon, your critical hit deals an extra 7 damage of the weapon''s type.', 'weapon', 'rare', 2000.0, 0.0, 1),
('Shield +2', 'A shield that grants a +2 bonus to AC in addition to the shield''s normal bonus to AC.', 'armor', 'rare', 2000.0, 6.0, 1),
('Bracers of Defense', 'While wearing these bracers, you gain a +2 bonus to AC if you are wearing no armor and using no shield.', 'wondrous item', 'rare', 2000.0, 2.0, 1),
('Ring of Protection', 'You gain a +1 bonus to AC and saving throws while wearing this ring.', 'ring', 'rare', 2000.0, 0.0, 1),
('Ring of Spell Storing', 'This ring stores spells cast into it, holding them until the attuned wearer uses them. The ring can store up to 5 levels worth of spells at a time.', 'ring', 'rare', 2000.0, 0.0, 1),
('Belt of Hill Giant Strength', 'Your Strength score is 21 while you wear this belt. It has no effect on you if your Strength is already 21 or higher.', 'wondrous item', 'rare', 2000.0, 2.0, 1),
('Cloak of Displacement', 'While you wear this cloak, it projects an illusion that makes you appear to be standing in a place near your actual location, causing any creature to have disadvantage on attack rolls against you.', 'wondrous item', 'rare', 2000.0, 1.0, 1),
('Ring of Resistance', 'You have resistance to one damage type while wearing this ring.', 'ring', 'rare', 2000.0, 0.0, 1),
('Ioun Stone (Protection)', 'An ioun stone is named after Ioun, a god of knowledge and prophecy. This stone orbits your head and grants a +1 bonus to AC.', 'wondrous item', 'rare', 2000.0, 0.0, 1);

-- Very Rare Magic Items
INSERT INTO equipment (name, description, item_type, rarity, cost_gp, weight_lb, is_magical) VALUES
('Potion of Supreme Healing', 'A magic potion that restores 10d4 + 20 hit points when consumed as a bonus action.', 'consumable', 'very rare', 20000.0, 0.5, 1),
('6th Level Spell Scroll', 'A spell scroll containing a 6th-level spell. A spellcaster can use an action to cast the spell without expending a spell slot.', 'consumable', 'very rare', 1000.0, 0.0, 1),
('7th Level Spell Scroll', 'A spell scroll containing a 7th-level spell. A spellcaster can use an action to cast the spell without expending a spell slot.', 'consumable', 'very rare', 2000.0, 0.0, 1),
('Plate Armor +2', 'Magical plate armor that grants a +2 bonus to AC.', 'armor', 'very rare', 20000.0, 65.0, 1),
('Studded Leather +2', 'Magical studded leather armor that grants a +2 bonus to AC.', 'armor', 'very rare', 20000.0, 13.0, 1),
('Rapier +3', 'A magic rapier with a +3 bonus to attack and damage rolls.', 'weapon', 'very rare', 20000.0, 2.0, 1),
('Longsword +3', 'A magic longsword with a +3 bonus to attack and damage rolls.', 'weapon', 'very rare', 20000.0, 3.0, 1),
('Greatsword +3', 'A magic greatsword with a +3 bonus to attack and damage rolls.', 'weapon', 'very rare', 20000.0, 6.0, 1),
('Greataxe +3', 'A magic greataxe with a +3 bonus to attack and damage rolls.', 'weapon', 'very rare', 20000.0, 7.0, 1),
('Scimitar +3', 'A magic scimitar with a +3 bonus to attack and damage rolls.', 'weapon', 'very rare', 20000.0, 3.0, 1),
('Shield +3', 'A shield that grants a +3 bonus to AC in addition to the shield''s normal bonus to AC.', 'armor', 'very rare', 20000.0, 6.0, 1),
('Illusionist''s Bracers', 'While wearing these bracers, you can use a bonus action to cast a cantrip.', 'wondrous item', 'very rare', 20000.0, 2.0, 1),
('Staff of Power', 'This staff can be wielded as a magic quarterstaff that grants a +2 bonus to attack and damage rolls. While holding it, you gain a +2 bonus to Armor Class, saving throws, and spell attack rolls.', 'staff', 'very rare', 20000.0, 4.0, 1),
('Belt of Stone Giant Strength', 'Your Strength score is 23 while you wear this belt. It has no effect on you if your Strength is already 23 or higher.', 'wondrous item', 'very rare', 20000.0, 2.0, 1),
('Manual of Gainful Exercise', 'This book contains exercises for improving dexterity, and its words are charged with magic. If you spend 48 hours over a period of 6 days or fewer studying the book, your Constitution score increases by 2, to a maximum of 22.', 'wondrous item', 'very rare', 20000.0, 5.0, 1),
('Tome of Clear Thought', 'This book contains memory and logic exercises, and its words are charged with magic. If you spend 48 hours over a period of 6 days or fewer studying the book, your Intelligence score increases by 2, to a maximum of 22.', 'wondrous item', 'very rare', 20000.0, 5.0, 1),
('Ioun Stone (Fortitude)', 'This stone orbits your head and grants you a +2 bonus to Constitution saving throws.', 'wondrous item', 'very rare', 20000.0, 0.0, 1);

-- Legendary Magic Items
INSERT INTO equipment (name, description, item_type, rarity, cost_gp, weight_lb, is_magical) VALUES
('Plate Armor +3', 'Magical plate armor that grants a +3 bonus to AC.', 'armor', 'legendary', 100000.0, 65.0, 1),
('Studded Leather +3', 'Magical studded leather armor that grants a +3 bonus to AC.', 'armor', 'legendary', 100000.0, 13.0, 1),
('Robe of the Archmagi', 'This elegant garment is made from exquisite cloth and adorned with runes. You gain these benefits while wearing the robe: AC 15 + Dex modifier, advantage on saving throws against spells, spell save DC and spell attack bonus each increase by 2.', 'armor', 'legendary', 100000.0, 4.0, 1),
('Holy Avenger', 'This magic sword grants a +3 bonus to attack and damage rolls. When you hit a fiend or an undead with it, that creature takes an extra 2d10 radiant damage.', 'weapon', 'legendary', 100000.0, 3.0, 1),
('Vorpal Sword', 'This magic sword grants a +3 bonus to attack and damage rolls. When you attack a creature with this weapon and roll a 20 on the attack roll, that target takes an extra 6d8 slashing damage.', 'weapon', 'legendary', 100000.0, 3.0, 1),
('Sword of Answering', 'This sword grants a +3 bonus to attack and damage rolls. While you hold the sword, you can use your reaction to make one melee attack against any creature within 5 feet of you that damages you.', 'weapon', 'legendary', 100000.0, 3.0, 1),
('Defender', 'This magic sword grants a +3 bonus to attack and damage rolls. The first time you attack with the sword on each of your turns, you can transfer some or all of the sword''s bonus to your Armor Class instead.', 'weapon', 'legendary', 100000.0, 3.0, 1),
('Staff of the Magi', 'This staff can be wielded as a magic quarterstaff that grants a +2 bonus to attack and damage rolls. While you hold it, you gain a +2 bonus to spell attack rolls and your spell save DC increases by 2.', 'staff', 'legendary', 100000.0, 4.0, 1),
('8th Level Spell Scroll', 'A spell scroll containing an 8th-level spell. A spellcaster can use an action to cast the spell without expending a spell slot.', 'consumable', 'legendary', 5000.0, 0.0, 1),
('9th Level Spell Scroll', 'A spell scroll containing a 9th-level spell. A spellcaster can use an action to cast the spell without expending a spell slot.', 'consumable', 'legendary', 10000.0, 0.0, 1),
('Belt of Cloud Giant Strength', 'Your Strength score is 27 while you wear this belt. It has no effect on you if your Strength is already 27 or higher.', 'wondrous item', 'legendary', 100000.0, 2.0, 1),
('Deck of Many Things', 'Usually found in a box or pouch, this deck contains a number of cards made of ivory or vellum. Most have only thirteen cards, but the full deck has twenty-two.', 'wondrous item', 'legendary', 100000.0, 1.0, 1);
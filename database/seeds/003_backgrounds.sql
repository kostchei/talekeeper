-- TaleKeeper Game Data Export
-- Generated: 2025-09-13T13:48:22.561740
-- Tables: backgrounds, background_proficiencies


-- backgrounds (5 rows)
INSERT INTO backgrounds (id, name, description, skill_proficiencies, language_proficiencies, tool_proficiencies, starting_equipment, equipment_option_a, equipment_option_a_gold, feature_name, feature_description, feat, display_order) VALUES ('farmer', 'Farmer', 'You know the hard work of the farm and field. You understand the cycle of seasons and the patience required to nurture crops and livestock.', '["Animal Handling", "Nature"]', '[]', '["Carpenter''s Tools"]', '{"option_a": {"equipment": ["carpenters_tools", "shovel", "common_clothes", "belt_pouch", "backpack", "potion_of_healing", "rations_5"], "gold": 10}, "option_b": {"gold": 50}}', '["carpenters_tools", "shovel", "common_clothes", "belt_pouch", "backpack", "potion_of_healing", "rations_5"]', 10, '', '', 'Tough', 0);
INSERT INTO backgrounds (id, name, description, skill_proficiencies, language_proficiencies, tool_proficiencies, starting_equipment, equipment_option_a, equipment_option_a_gold, feature_name, feature_description, feat, display_order) VALUES ('soldier', 'Soldier', 'You began training for war as soon as you reached adulthood and carry precious few memories of life before you took up arms. Battle is in your blood. The crash of weapons, the stink of blood, the screams of enemies—this is the music that makes your heart race. War has been your life for as long as you care to remember.', '["Athletics", "Intimidation"]', '[]', '["Gaming Set"]', '{"option_a": {"equipment": ["spear", "shortbow", "arrows_20", "gaming_set", "healers_kit", "quiver", "travelers_clothes"], "gold": 14}, "option_b": {"gold": 50}}', '["spear", "shortbow", "arrows_20", "gaming_set", "healers_kit", "quiver", "travelers_clothes"]', 14, '', '', 'Savage Attacker', 1);
INSERT INTO backgrounds (id, name, description, skill_proficiencies, language_proficiencies, tool_proficiencies, starting_equipment, equipment_option_a, equipment_option_a_gold, feature_name, feature_description, feat, display_order) VALUES ('acolyte', 'Acolyte', 'You devoted yourself to service in a temple, either nestled in a town or secluded in a sacred grove. There you performed rites in honor of a god or pantheon. You served under a priest and studied religion. Thanks to your priest''s instruction and your own devotion, you gained mastery over your god''s mysteries.', '["Insight", "Religion"]', '[]', '["Calligrapher''s Supplies"]', '{"option_a": {"equipment": ["calligraphers_supplies", "prayer_book", "holy_symbol", "parchment_10", "robe"], "gold": 8}, "option_b": {"gold": 50}}', '["calligraphers_supplies", "prayer_book", "holy_symbol", "parchment_10", "robe"]', 8, '', '', 'Magic Initiate (Cleric)', 2);
INSERT INTO backgrounds (id, name, description, skill_proficiencies, language_proficiencies, tool_proficiencies, starting_equipment, equipment_option_a, equipment_option_a_gold, feature_name, feature_description, feat, display_order) VALUES ('criminal', 'Criminal', 'You once broke the law and paid for it, learning a hard lesson about the reach of legal authority. You spent time among other criminals and developed connections within the criminal underworld. You''re far closer than most people to the world of murder, theft, and violence that pervades the underbelly of civilization.', '["Sleight of Hand", "Stealth"]', '[]', '["Thieves'' Tools"]', '{"option_a": {"equipment": ["dagger", "dagger", "thieves_tools", "crowbar", "pouch", "pouch", "travelers_clothes"], "gold": 16}, "option_b": {"gold": 50}}', '["dagger", "dagger", "thieves_tools", "crowbar", "pouch", "pouch", "travelers_clothes"]', 16, '', '', 'Alert', 3);
INSERT INTO backgrounds (id, name, description, skill_proficiencies, language_proficiencies, tool_proficiencies, starting_equipment, equipment_option_a, equipment_option_a_gold, feature_name, feature_description, feat, display_order) VALUES ('sage', 'Sage', 'You spent your formative years traveling between libraries, scriptoriums, and universities, learning from scholars, wizards, and other learned persons. You became an apprentice to a master who taught you to value knowledge above all else. You mastered the basics of accessing the most fundamental sources of knowledge.', '["Arcana", "History"]', '[]', '["Calligrapher''s Supplies"]', '{"option_a": {"equipment": ["quarterstaff", "calligraphers_supplies", "history_book", "parchment_8", "robe"], "gold": 8}, "option_b": {"gold": 50}}', '["quarterstaff", "calligraphers_supplies", "history_book", "parchment_8", "robe"]', 8, '', '', 'Magic Initiate (Wizard)', 4);

-- background_proficiencies (33 rows)
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('soldier', 'skill', 'Athletics');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('soldier', 'skill', 'Intimidation');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('soldier', 'tool', 'gaming_set');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('soldier', 'tool', 'vehicles_land');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('criminal', 'skill', 'Deception');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('criminal', 'skill', 'Stealth');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('criminal', 'tool', 'thieves_tools');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('criminal', 'tool', 'gaming_set');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('sage', 'skill', 'Arcana');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('sage', 'skill', 'History');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('sage', 'language', 'choice_2');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('acolyte', 'skill', 'Insight');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('acolyte', 'skill', 'Religion');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('acolyte', 'language', 'choice_2');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('criminal', 'skill', 'Deception');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('criminal', 'skill', 'Stealth');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('criminal', 'tool', 'thieves_tools');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('criminal', 'tool', 'gaming_set');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('folk_hero', 'skill', 'Animal Handling');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('folk_hero', 'skill', 'Survival');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('folk_hero', 'tool', 'artisan_tools');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('folk_hero', 'tool', 'vehicles_land');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('noble', 'skill', 'History');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('noble', 'skill', 'Persuasion');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('noble', 'tool', 'gaming_set');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('noble', 'language', 'choice_1');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('sage', 'skill', 'Arcana');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('sage', 'skill', 'History');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('sage', 'language', 'choice_2');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('soldier', 'skill', 'Athletics');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('soldier', 'skill', 'Intimidation');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('soldier', 'tool', 'gaming_set');
INSERT INTO background_proficiencies (background_id, proficiency_type, proficiency_name) VALUES ('soldier', 'tool', 'vehicles_land');

-- TaleKeeper Game Data Export
-- Generated: 2025-09-13T13:48:22.576256
-- Tables: class_armor_proficiencies, class_equipment_choices, class_saving_throws, class_skill_choices, class_skill_proficiencies, class_weapon_proficiencies, species_proficiencies


-- class_armor_proficiencies (16 rows)
INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES ('fighter', 'light');
INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES ('fighter', 'medium');
INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES ('fighter', 'heavy');
INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES ('fighter', 'shields');
INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES ('barbarian', 'light');
INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES ('barbarian', 'medium');
INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES ('barbarian', 'shields');
INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES ('cleric', 'light');
INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES ('cleric', 'medium');
INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES ('cleric', 'shields');
INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES ('paladin', 'light');
INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES ('paladin', 'medium');
INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES ('paladin', 'heavy');
INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES ('paladin', 'shields');
INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES ('rogue', 'light');
INSERT INTO class_armor_proficiencies (class_id, armor_type) VALUES ('warlock', 'light');

-- class_equipment_choices (10 rows)
INSERT INTO class_equipment_choices (id, class_id, choice_group, choice_name, options, created_at) VALUES (3, 'barbarian', 'weapon_choice', 'Weapon Choice', '["Shield + Spear", "Greataxe", "2x Scimitars"]', '2025-09-02 13:33:05');
INSERT INTO class_equipment_choices (id, class_id, choice_group, choice_name, options, created_at) VALUES (4, 'barbarian', 'armor_choice', 'Armor/Helmet Choice', '["Dread Helm", "Scale Mail", "Chain Mail"]', '2025-09-02 13:33:05');
INSERT INTO class_equipment_choices (id, class_id, choice_group, choice_name, options, created_at) VALUES (5, 'rogue', 'armor_choice', 'Armor', '["Studded Leather"]', '2025-09-02 13:33:05');
INSERT INTO class_equipment_choices (id, class_id, choice_group, choice_name, options, created_at) VALUES (6, 'rogue', 'weapon_choice', 'Weapon Choice', '["Rapier + Dagger", "Scimitar + Shortsword"]', '2025-09-02 13:33:05');
INSERT INTO class_equipment_choices (id, class_id, choice_group, choice_name, options, created_at) VALUES (7, 'cleric', 'equipment_choice', 'Equipment', '["Holy Symbol + Scale Mail + Mace + Shield", "Holy Symbol + Chain Mail + Mace + Shield"]', '2025-09-02 13:33:13');
INSERT INTO class_equipment_choices (id, class_id, choice_group, choice_name, options, created_at) VALUES (8, 'paladin', 'equipment_choice', 'Equipment Choice', '["Holy Symbol + Scale Mail + Longsword + Shield", "Holy Symbol + Chain Mail + Longsword + Shield", "Holy Symbol + Scale Mail + Greatsword", "Holy Symbol + Chain Mail + Greatsword"]', '2025-09-02 13:33:13');
INSERT INTO class_equipment_choices (id, class_id, choice_group, choice_name, options, created_at) VALUES (9, 'wizard', 'equipment_choice', 'Equipment Choice', '["Arcane Focus + Spellbook + Quarterstaff", "Arcane Focus + Spellbook + Dagger"]', '2025-09-02 13:33:13');
INSERT INTO class_equipment_choices (id, class_id, choice_group, choice_name, options, created_at) VALUES (10, 'warlock', 'equipment_auto', 'Starting Equipment', '["Studded Leather + Arcane Focus + Spear"]', '2025-09-02 13:33:20');
INSERT INTO class_equipment_choices (id, class_id, choice_group, choice_name, options, created_at) VALUES (11, 'fighter', 'armor_choice', 'Armor Choice', '["Studded Leather", "Scale Mail", "Chain Mail"]', '2025-09-04 02:45:31');
INSERT INTO class_equipment_choices (id, class_id, choice_group, choice_name, options, created_at) VALUES (12, 'fighter', 'weapon_choice', 'Weapon Choice', '["Greatsword", "Longsword + Shield", "Scimitar + Scimitar"]', '2025-09-04 02:45:31');

-- class_saving_throws (14 rows)
INSERT INTO class_saving_throws (class_id, ability) VALUES ('fighter', 'strength');
INSERT INTO class_saving_throws (class_id, ability) VALUES ('fighter', 'constitution');
INSERT INTO class_saving_throws (class_id, ability) VALUES ('barbarian', 'strength');
INSERT INTO class_saving_throws (class_id, ability) VALUES ('barbarian', 'constitution');
INSERT INTO class_saving_throws (class_id, ability) VALUES ('cleric', 'wisdom');
INSERT INTO class_saving_throws (class_id, ability) VALUES ('cleric', 'charisma');
INSERT INTO class_saving_throws (class_id, ability) VALUES ('paladin', 'wisdom');
INSERT INTO class_saving_throws (class_id, ability) VALUES ('paladin', 'charisma');
INSERT INTO class_saving_throws (class_id, ability) VALUES ('rogue', 'dexterity');
INSERT INTO class_saving_throws (class_id, ability) VALUES ('rogue', 'intelligence');
INSERT INTO class_saving_throws (class_id, ability) VALUES ('warlock', 'wisdom');
INSERT INTO class_saving_throws (class_id, ability) VALUES ('warlock', 'charisma');
INSERT INTO class_saving_throws (class_id, ability) VALUES ('wizard', 'intelligence');
INSERT INTO class_saving_throws (class_id, ability) VALUES ('wizard', 'wisdom');

-- class_skill_choices (12 rows)
INSERT INTO class_skill_choices (class_id, skill_count, available_skills) VALUES ('fighter', 2, '["Acrobatics", "Animal Handling", "Athletics", "History", "Insight", "Intimidation", "Perception", "Survival"]');
INSERT INTO class_skill_choices (class_id, skill_count, available_skills) VALUES ('barbarian', 2, '["Animal Handling", "Athletics", "Intimidation", "Nature", "Perception", "Survival"]');
INSERT INTO class_skill_choices (class_id, skill_count, available_skills) VALUES ('cleric', 2, '["History", "Insight", "Medicine", "Persuasion", "Religion"]');
INSERT INTO class_skill_choices (class_id, skill_count, available_skills) VALUES ('rogue', 4, '["Acrobatics", "Athletics", "Deception", "Insight", "Intimidation", "Investigation", "Perception", "Performance", "Persuasion", "Sleight of Hand", "Stealth"]');
INSERT INTO class_skill_choices (class_id, skill_count, available_skills) VALUES ('wizard', 2, '["Arcana", "History", "Insight", "Investigation", "Medicine", "Religion"]');
INSERT INTO class_skill_choices (class_id, skill_count, available_skills) VALUES ('paladin', 2, '["Athletics", "Insight", "Intimidation", "Medicine", "Persuasion", "Religion"]');
INSERT INTO class_skill_choices (class_id, skill_count, available_skills) VALUES ('fighter', 2, '["Acrobatics", "Animal Handling", "Athletics", "History", "Insight", "Intimidation", "Perception", "Survival"]');
INSERT INTO class_skill_choices (class_id, skill_count, available_skills) VALUES ('barbarian', 2, '["Animal Handling", "Athletics", "Intimidation", "Nature", "Perception", "Survival"]');
INSERT INTO class_skill_choices (class_id, skill_count, available_skills) VALUES ('cleric', 2, '["History", "Insight", "Medicine", "Persuasion", "Religion"]');
INSERT INTO class_skill_choices (class_id, skill_count, available_skills) VALUES ('rogue', 4, '["Acrobatics", "Athletics", "Deception", "Insight", "Intimidation", "Investigation", "Perception", "Performance", "Persuasion", "Sleight of Hand", "Stealth"]');
INSERT INTO class_skill_choices (class_id, skill_count, available_skills) VALUES ('wizard', 2, '["Arcana", "History", "Insight", "Investigation", "Medicine", "Religion"]');
INSERT INTO class_skill_choices (class_id, skill_count, available_skills) VALUES ('paladin', 2, '["Athletics", "Insight", "Intimidation", "Medicine", "Persuasion", "Religion"]');

-- class_skill_proficiencies (50 rows)
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('fighter', 'Acrobatics');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('fighter', 'Animal Handling');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('fighter', 'Athletics');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('fighter', 'History');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('fighter', 'Insight');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('fighter', 'Intimidation');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('fighter', 'Perception');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('fighter', 'Survival');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('barbarian', 'Animal Handling');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('barbarian', 'Athletics');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('barbarian', 'Intimidation');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('barbarian', 'Nature');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('barbarian', 'Perception');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('barbarian', 'Survival');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('cleric', 'History');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('cleric', 'Insight');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('cleric', 'Medicine');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('cleric', 'Persuasion');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('cleric', 'Religion');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('paladin', 'Athletics');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('paladin', 'Insight');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('paladin', 'Intimidation');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('paladin', 'Medicine');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('paladin', 'Persuasion');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('paladin', 'Religion');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('rogue', 'Acrobatics');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('rogue', 'Athletics');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('rogue', 'Deception');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('rogue', 'Insight');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('rogue', 'Intimidation');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('rogue', 'Investigation');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('rogue', 'Perception');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('rogue', 'Performance');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('rogue', 'Persuasion');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('rogue', 'Sleight of Hand');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('rogue', 'Stealth');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('rogue', 'Survival');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('warlock', 'Arcana');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('warlock', 'Deception');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('warlock', 'History');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('warlock', 'Intimidation');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('warlock', 'Investigation');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('warlock', 'Nature');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('warlock', 'Religion');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('wizard', 'Arcana');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('wizard', 'History');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('wizard', 'Insight');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('wizard', 'Investigation');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('wizard', 'Medicine');
INSERT INTO class_skill_proficiencies (class_id, skill) VALUES ('wizard', 'Religion');

-- class_weapon_proficiencies (18 rows)
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('fighter', 'simple');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('fighter', 'martial');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('barbarian', 'simple');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('barbarian', 'martial');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('cleric', 'simple');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('paladin', 'simple');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('paladin', 'martial');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('rogue', 'simple');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('rogue', 'hand_crossbow');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('rogue', 'longsword');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('rogue', 'rapier');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('rogue', 'shortsword');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('warlock', 'simple');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('wizard', 'daggers');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('wizard', 'darts');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('wizard', 'slings');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('wizard', 'quarterstaffs');
INSERT INTO class_weapon_proficiencies (class_id, weapon_type) VALUES ('wizard', 'light crossbows');

-- species_proficiencies (12 rows)
INSERT INTO species_proficiencies (species_id, proficiency_type, proficiency_name, choice_count, available_options) VALUES ('human', 'skill', NULL, 1, '["any"]');
INSERT INTO species_proficiencies (species_id, proficiency_type, proficiency_name, choice_count, available_options) VALUES ('dwarf', 'tool', 'smith_tools', 0, NULL);
INSERT INTO species_proficiencies (species_id, proficiency_type, proficiency_name, choice_count, available_options) VALUES ('elf', 'skill', 'Perception', 0, NULL);
INSERT INTO species_proficiencies (species_id, proficiency_type, proficiency_name, choice_count, available_options) VALUES ('elf', 'weapon', 'longsword', 0, NULL);
INSERT INTO species_proficiencies (species_id, proficiency_type, proficiency_name, choice_count, available_options) VALUES ('elf', 'weapon', 'shortbow', 0, NULL);
INSERT INTO species_proficiencies (species_id, proficiency_type, proficiency_name, choice_count, available_options) VALUES ('halfling', 'skill', 'Stealth', 0, NULL);
INSERT INTO species_proficiencies (species_id, proficiency_type, proficiency_name, choice_count, available_options) VALUES ('human', 'skill', NULL, 1, '["any"]');
INSERT INTO species_proficiencies (species_id, proficiency_type, proficiency_name, choice_count, available_options) VALUES ('dwarf', 'tool', 'smith_tools', 0, NULL);
INSERT INTO species_proficiencies (species_id, proficiency_type, proficiency_name, choice_count, available_options) VALUES ('elf', 'skill', 'Perception', 0, NULL);
INSERT INTO species_proficiencies (species_id, proficiency_type, proficiency_name, choice_count, available_options) VALUES ('elf', 'weapon', 'longsword', 0, NULL);
INSERT INTO species_proficiencies (species_id, proficiency_type, proficiency_name, choice_count, available_options) VALUES ('elf', 'weapon', 'shortbow', 0, NULL);
INSERT INTO species_proficiencies (species_id, proficiency_type, proficiency_name, choice_count, available_options) VALUES ('halfling', 'skill', 'Stealth', 0, NULL);

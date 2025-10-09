-- Migration 015b: Warlock Class Enhancements
-- Adds tracking columns and patron features to complete Warlock implementation

-- Note: warlock_features table already has most columns from previous migration
-- This migration only adds missing pieces

-- Create warlock_patron_features table for patron-specific features
CREATE TABLE IF NOT EXISTS warlock_patron_features (
    id TEXT PRIMARY KEY,
    patron TEXT NOT NULL,
    level INTEGER NOT NULL,
    feature_name TEXT NOT NULL,
    description TEXT,
    effect_type TEXT,
    effect_data TEXT
);

-- Populate Fiend Patron features
INSERT OR IGNORE INTO warlock_patron_features (id, patron, level, feature_name, description, effect_type, effect_data)
VALUES
    ('fiend_dark_ones_blessing', 'Fiend', 3, 'Dark One''s Blessing',
     'When you reduce a hostile creature to 0 hit points, you gain temporary hit points equal to your Charisma modifier + your warlock level (minimum 1). You also gain this benefit if someone else reduces a hostile creature to 0 hit points within 10 feet of you.',
     'passive',
     '{"trigger": "enemy_defeated", "temp_hp_formula": "cha_mod + warlock_level", "range": 10}'),

    ('fiend_patron_spells', 'Fiend', 3, 'Fiend Spells',
     'The magic of your patron ensures you always have certain spells ready.',
     'spell_list',
     '{"3": ["burning_hands", "command", "scorching_ray", "suggestion"], "5": ["fireball", "stinking_cloud"], "7": ["fire_shield", "wall_of_fire"], "9": ["geas", "insect_plague"]}'),

    ('fiend_dark_ones_luck', 'Fiend', 6, 'Dark One''s Own Luck',
     'You can call on your fiendish patron to alter fate in your favor. When you make an ability check or a saving throw, you can use this feature to add 1d10 to your roll. You can do so after seeing the roll but before any of the roll''s effects occur. Once you use this feature, you can''t use it again until you finish a short or long rest.',
     'active',
     '{"bonus_dice": "1d10", "timing": "after_roll", "uses_per_rest": "cha_mod", "rest_type": "long"}'),

    ('fiend_fiendish_resilience', 'Fiend', 10, 'Fiendish Resilience',
     'You can choose one damage type when you finish a short or long rest. You gain resistance to that damage type until you choose a different one with this feature. Damage from magical weapons or silver weapons ignores this resistance.',
     'active',
     '{"resistance_choice": true, "reset_on_rest": true, "exclude": ["force"]}'),

    ('fiend_hurl_through_hell', 'Fiend', 14, 'Hurl Through Hell',
     'When you hit a creature with an attack, you can use this feature to instantly transport the target through the lower planes. The creature disappears and hurtles through a nightmare landscape. At the end of your next turn, the target returns to the space it previously occupied, or the nearest unoccupied space. If the target is not a fiend, it takes 10d10 psychic damage as it reels from its horrific experience. Once you use this feature, you can''t use it again until you finish a long rest.',
     'active',
     '{"trigger": "on_hit", "damage": "10d10", "damage_type": "psychic", "fiend_immune": true, "duration_turns": 1, "uses_per_rest": 1, "rest_type": "long"}');

-- Update invocations with corrected D&D 2024 data
UPDATE invocations SET prerequisites = '{"level": 2, "cantrip": "eldritch_blast"}' WHERE id = 'agonizing_blast';
UPDATE invocations SET prerequisites = '{"level": 2}' WHERE id = 'devils_sight';
UPDATE invocations SET prerequisites = '{"level": 2, "cantrip": "eldritch_blast"}' WHERE id = 'eldritch_spear';
UPDATE invocations SET prerequisites = '{"level": 5}' WHERE id = 'one_with_shadows';
UPDATE invocations SET prerequisites = '{"level": 2, "cantrip": "eldritch_blast"}' WHERE id = 'repelling_blast';
UPDATE invocations SET prerequisites = '{"level": 7}' WHERE id = 'whispers_of_the_grave';

-- Add missing D&D 2024 invocations
INSERT OR IGNORE INTO invocations (id, name, description, prerequisites, effect_type, effect_data)
VALUES
    ('ascendant_step', 'Ascendant Step', 'You can cast levitate on yourself at will, without expending a spell slot or material components', '{"level": 5}', 'active', '{"spell": "levitate", "cost": "none", "target": "self"}'),

    ('eldritch_mind', 'Eldritch Mind', 'You have advantage on Constitution saving throws that you make to maintain your concentration on a spell', '{"level": 2}', 'passive', '{"concentration_advantage": true}'),

    ('eldritch_smite', 'Eldritch Smite', 'Once per turn when you hit a creature with your pact weapon, you can expend a warlock spell slot to deal an extra 1d8 force damage to the target, plus another 1d8 per level of the spell slot, and you can knock the target prone if it is Huge or smaller', '{"level": 5, "pact": "blade"}', 'active', '{"damage_per_slot_level": "1d8", "damage_type": "force", "base_dice": 1, "can_knock_prone": true, "size_limit": "Huge"}'),

    ('gift_of_the_depths', 'Gift of the Depths', 'You can breathe underwater, and you gain a swimming speed equal to your walking speed. You can also cast water breathing once without expending a spell slot. You regain the ability to do so when you finish a long rest', '{"level": 5}', 'passive', '{"breathe_underwater": true, "swim_speed": "walking", "spell": "water_breathing", "spell_uses": 1}'),

    ('gift_of_the_protectors', 'Gift of the Protectors', 'A new page appears in your Book of Shadows. With your permission, a creature can use its action to write its name on that page, which can contain a number of names equal to your proficiency bonus. When any creature whose name is on the page is reduced to 0 hit points but not killed outright, the creature magically drops to 1 hit point instead. Once this magic is triggered, no creature can benefit from it until you finish a long rest', '{"level": 9, "pact": "tome"}', 'passive', '{"prevent_death": true, "max_creatures": "proficiency_bonus", "uses_per_rest": 1}'),

    ('investment_of_chain_master', 'Investment of the Chain Master', 'When you cast find familiar, you infuse the summoned familiar with a measure of your eldritch power, granting the creature additional benefits', '{"level": 5, "pact": "chain"}', 'passive', '{"familiar_fly_swim": 40, "familiar_bonus_action_attack": true, "familiar_damage_conversion": ["necrotic", "radiant"], "familiar_save_dc": "warlock", "familiar_resistance_reaction": true}'),

    ('lessons_of_the_first_ones', 'Lessons of the First Ones', 'You have received knowledge from an elder entity of the multiverse, allowing you to gain one Origin feat of your choice', '{"level": 2}', 'passive', '{"grant_origin_feat": true, "repeatable": true}'),

    ('devouring_blade', 'Devouring Blade', 'The Extra Attack of your Thirsting Blade invocation confers two extra attacks rather than one', '{"level": 12, "invocation": "thirsting_blade"}', 'passive', '{"extra_attacks": 2}'),

    ('visions_of_distant_realms', 'Visions of Distant Realms', 'You can cast arcane eye at will, without expending a spell slot', '{"level": 9}', 'active', '{"spell": "arcane_eye", "cost": "none"}');

-- Update warlock_pact_progression with correct invocations_known values (D&D 2024)
UPDATE warlock_pact_progression SET invocations_known = 1 WHERE level = 1;
UPDATE warlock_pact_progression SET invocations_known = 3 WHERE level = 2;
UPDATE warlock_pact_progression SET invocations_known = 3 WHERE level = 3;
UPDATE warlock_pact_progression SET invocations_known = 3 WHERE level = 4;
UPDATE warlock_pact_progression SET invocations_known = 5 WHERE level = 5;
UPDATE warlock_pact_progression SET invocations_known = 5 WHERE level = 6;
UPDATE warlock_pact_progression SET invocations_known = 6 WHERE level = 7;
UPDATE warlock_pact_progression SET invocations_known = 6 WHERE level = 8;
UPDATE warlock_pact_progression SET invocations_known = 7 WHERE level = 9;
UPDATE warlock_pact_progression SET invocations_known = 7 WHERE level = 10;
UPDATE warlock_pact_progression SET invocations_known = 7 WHERE level = 11;
UPDATE warlock_pact_progression SET invocations_known = 8 WHERE level = 12;
UPDATE warlock_pact_progression SET invocations_known = 8 WHERE level = 13;
UPDATE warlock_pact_progression SET invocations_known = 8 WHERE level = 14;
UPDATE warlock_pact_progression SET invocations_known = 9 WHERE level = 15;
UPDATE warlock_pact_progression SET invocations_known = 9 WHERE level = 16;
UPDATE warlock_pact_progression SET invocations_known = 9 WHERE level = 17;
UPDATE warlock_pact_progression SET invocations_known = 10 WHERE level = 18;
UPDATE warlock_pact_progression SET invocations_known = 10 WHERE level = 19;
UPDATE warlock_pact_progression SET invocations_known = 10 WHERE level = 20;

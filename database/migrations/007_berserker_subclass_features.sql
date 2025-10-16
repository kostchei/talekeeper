-- Barbarian Subclass Features (Path of the Berserker and Path of the Slayer)

-- Path of the Berserker
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics, prerequisites) VALUES
('berserker', 3, 'Frenzy', 'bonus_action', 'Make an extra attack as a bonus action while raging',
 '{"cost_type": "exhaustion", "cost_amount": 1, "attack_bonus_action": true, "requires_rage": true}',
 '{"requires_rage": true}'),

('berserker', 6, 'Mindless Rage', 'passive', 'Cannot be charmed or frightened while raging',
 '{"charm_immunity": true, "fear_immunity": true, "requires_rage": true}',
 '{"requires_rage": true}'),

('berserker', 10, 'Intimidating Presence', 'action', 'Frighten a creature within 30 feet',
 '{"action_type": "action", "range": 30, "save_type": "wisdom", "save_dc": "8+prof+cha", "duration_rounds": 1, "uses_per_short_rest": null}',
 null),

('berserker', 14, 'Retaliation', 'reaction', 'Make a melee attack when you take damage from a creature within 5 feet',
 '{"action_type": "reaction", "trigger": "take_damage", "range": 5, "melee_attack": true}',
 null);

-- Path of the Slayer
INSERT OR REPLACE INTO subclass_features_progression (subclass_id, level, feature_name, feature_type, description, mechanics, prerequisites) VALUES
('slayer', 3, 'Armored Fury', 'passive', 'Gain full benefits of rage while wearing heavy armor and gain heavy armor proficiency',
 '{"rage_in_heavy_armor": true, "armor_proficiency": "heavy"}',
 null),

('slayer', 6, 'Hooped and Hasped', 'passive', 'Add full Dexterity modifier to AC regardless of armor type and no stealth disadvantage',
 '{"full_dex_bonus_ac": true, "no_stealth_penalty": true}',
 null),

('slayer', 10, 'Hammerhand', 'passive', 'Unarmed strikes are martial weapons dealing 1d4 damage and crit on 19-20 while raging. Bonus unarmed attack on miss.',
 '{"unarmed_damage": "1d4", "unarmed_crit_range": 19, "bonus_attack_on_miss": true, "requires_rage": true}',
 null),

('slayer', 14, 'Splintered Spears & Shattered Shields', 'action', 'Auto-crit destroying your weapon or destroy enemy shield',
 '{"uses_per_long_rest": 1, "auto_crit_destroy_weapon": true, "destroy_shield": true}',
 null),

('slayer', 17, 'Improved Splintered Spears', 'passive', 'Use Splintered Spears & Shattered Shields twice per long rest',
 '{"splintered_spears_uses": 2}',
 null);

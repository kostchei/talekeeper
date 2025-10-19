-- Migration 043: Beast Ration Drop System
-- Beasts drop rations instead of gold as individual treasure

-- Add flag to track which monsters drop rations
ALTER TABLE monsters ADD COLUMN drops_rations INTEGER DEFAULT 0;

-- Update all beast-type monsters to drop rations
UPDATE monsters SET drops_rations = 1 WHERE type = 'beast';

-- Add rations as equipment item (ID 417)
INSERT OR IGNORE INTO equipment (
    id,
    name,
    item_type,
    description,
    cost_gp,
    weight_lb,
    rarity
) VALUES (
    417,
    'Beast Rations',
    'consumable',
    'Edible meat harvested from a slain beast. Provides sustenance for 1 day.',
    0.5,
    2.0,
    'Common'
);

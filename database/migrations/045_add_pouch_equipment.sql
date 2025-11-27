-- Add Pouch to equipment table
INSERT INTO equipment (
    name, item_type, cost_gp, weight_lb, description, 
    rarity, is_magical, requires_attunement
) VALUES (
    'Pouch', 'gear', 0.5, 1.0, 'A cloth or leather pouch can hold up to 20 sling bullets or 50 blowgun needles, among other things. A compartmentalized pouch for holding spell components is called a component pouch (described earlier in this section). Capacity: 1/5 cubic ft. or 6 lbs. gear.',
    'common', 0, 0
);

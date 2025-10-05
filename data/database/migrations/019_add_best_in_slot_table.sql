CREATE TABLE IF NOT EXISTS best_in_slot_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_build TEXT NOT NULL,
    rarity TEXT NOT NULL,
    slot_number INTEGER,
    item_name TEXT NOT NULL,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_bis_class_rarity ON best_in_slot_items(class_build, rarity);
CREATE INDEX IF NOT EXISTS idx_bis_item_name ON best_in_slot_items(item_name);
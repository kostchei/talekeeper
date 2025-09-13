# Archived Database Files

## Legacy Migrations (legacy_migrations_002-010/)

These migration files were used in the old migration system (Sept 2025) but are now archived.

### What was migrated:
- **002_add_fighter_features.sql** - Fighter resource tracking (Second Wind, Action Surge, Indomitable)
- **003_add_srd_equipment.sql** - SRD equipment items
- **003_fix_skill_proficiencies.sql** - Skill proficiency system fixes
- **004_add_subclass_system.sql** - Complete subclass system
- **004_add_tools_instruments.sql** - Tools and musical instruments
- **005_add_available_classes_to_campaigns.sql** - Campaign class filtering
- **005_add_rarity_table.sql** - Item rarity table for loot generation
- **006_add_loot_plan_magic_items.sql** - Loot and magic item systems
- **007_add_attunement_requirements.sql** - Magic item attunement
- **008_update_item_types_and_proficiencies.sql** - Item type and proficiency updates
- **009_add_class_proficiencies.sql** - Class proficiency system
- **010_add_campaign_available_classes.sql** - Campaign available classes

### Why archived:
All features from these migrations are now integrated into the main schema (`database/schema/001_initial_schema.sql`).

### New system:
- **Schema versioning** instead of individual migrations
- **Current version: 2** (includes all legacy migration features)
- **Fresh installs** get complete schema immediately
- **Existing databases** are automatically marked as v2 (all migrations already applied)

### For developers:
- **Future changes**: Update schema version and create upgrade logic in `database_init.py`
- **No new migration files** needed - just version the schema
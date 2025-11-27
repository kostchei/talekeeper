    def _add_starting_equipment(self, cursor, character_id: str, character_data: Dict):
        """Add starting equipment based on class and background."""
        import uuid
        from talekeeper.services.equipment import equipment_service

        # Check if character already has equipment
        cursor.execute("SELECT COUNT(*) FROM character_inventory WHERE character_id = ?", (character_id,))
        existing_items = cursor.fetchone()[0]

        if existing_items > 0:
            print(f"[SQLite] Character already has {existing_items} items in inventory, skipping starting equipment")
            return

        class_id = character_data.get('class_id', '').lower()
        background_id = character_data.get('background_id', '').lower()
        equipment_choices = character_data.get('equipment_choices', {})
        skip_automatic = character_data.get('skip_automatic_equipment', False)

        if skip_automatic:
            print(f"[SQLite] Programmatic creation mode - only adding template equipment choices")
        else:
            print(f"[SQLite] Adding starting equipment for class '{class_id}' background '{background_id}'")
        
        # Helper to add item from DB
        def add_item_from_db(item_name, quantity=1, equipped=0, fallback_type='gear', fallback_desc=''):
            # Name mappings for inconsistencies
            name_map = {
                'Rations': 'Rations (1 day)',
                'rations': 'Rations (1 day)',
                'Waterskin': 'Waterskin',
                'Pouch': 'Pouch',
                'Backpack': 'Backpack',
                'Potion of Healing': 'Potion of Healing',
                "Explorer's Pack": "Explorer's Pack",
                'Javelin': 'Javelin',
                'Greataxe': 'Greataxe',
                'Scimitar': 'Scimitar'
            }
            
            db_name = name_map.get(item_name, item_name)
            
            # Normalize plural names if needed (e.g. "daggers" -> "Dagger")
            if db_name not in name_map:  # Don't normalize if we have a direct map
                db_name = self._normalize_item_name(db_name)

            equipment_data = equipment_service.get_item(db_name)
            
            if equipment_data:
                item_type = equipment_data['item_type']
                weight_lb = equipment_data['weight_lb']
                description = equipment_data['description'] or ''
                value_gp = equipment_data['cost_gp']
                
                cursor.execute("""
                    INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp, equipped)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), character_id, equipment_data['name'], item_type, quantity, weight_lb, description, value_gp, equipped))
                print(f"[SQLite] Added {equipment_data['name']} (qty: {quantity})")
                return True
            else:
                print(f"[SQLite] Warning: Item '{item_name}' (mapped: '{db_name}') not found in DB. Using fallback.")
                cursor.execute("""
                    INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp, equipped)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), character_id, item_name, fallback_type, quantity, 1.0, fallback_desc or f'{item_name} (fallback)', 0, equipped))
                return False

        # First, add equipment from character creation choices
        if equipment_choices:
            print(f"[SQLite] Adding equipment from character creation choices: {equipment_choices}")
            
            # Process each equipment choice using compound choice parsing
            for choice_key, item_name in equipment_choices.items():
                print(f"[SQLite] Processing choice '{choice_key}': {item_name}")

                # Parse compound equipment choices (e.g., "Scimitar + Shortsword", "2 Shortswords")
                items_to_add = self._parse_equipment_choice(item_name)

                for item_entry in items_to_add:
                    item_name_clean = item_entry['name']
                    quantity = item_entry.get('quantity', 1)

                    # Determine if equipped based on choice type
                    equipped = 1 if any(key in choice_key.lower() for key in ['weapon', 'armor', 'shield']) else 0
                    
                    add_item_from_db(item_name_clean, quantity, equipped)

        # Skip automatic class and background equipment if flag is set
        if skip_automatic:
            print(f"[SQLite] Skipping automatic class/background equipment additions")
            return

        # Fighter Class Starting Equipment
        if class_id in ['fighter']:
            add_item_from_db('Potion of Healing', 1, 0, 'consumable')
            add_item_from_db('Backpack', 1, 0, 'gear')
        
        # Barbarian Class Starting Equipment
        elif class_id in ['barbarian']:
            add_item_from_db("Explorer's Pack", 1, 0, 'gear')
            add_item_from_db('Javelin', 4, 0, 'weapon')
            
            # Add 2 scimitars separately for dual-wielding (not stacked)
            for i in range(2):
                add_item_from_db('Scimitar', 1, 1 if i == 0 else 0, 'weapon')
            
            # Check equipment choices for greataxe vs scale mail choice
            barbarian_choice = equipment_choices.get('barbarian_choice', '')
            if not barbarian_choice:
                # No choice made, default to greataxe
                add_item_from_db('Greataxe', 1, 0, 'weapon')
                print(f"[SQLite] Barbarian defaulted to Greataxe (no choice made)")
            elif 'scale' in barbarian_choice.lower() or 'mail' in barbarian_choice.lower():
                print(f"[SQLite] Barbarian chose Scale Mail")
            else:
                print(f"[SQLite] Barbarian chose Greataxe")
        
        # Background Equipment (direct database query)
        print(f"[SQLite] Loading background equipment for '{background_id}'")
        
        # Query background directly from database
        cursor.execute("""
            SELECT equipment_option_a, equipment_option_a_gold FROM backgrounds WHERE name = ? COLLATE NOCASE
        """, (background_id,))
        
        background_row = cursor.fetchone()
        if background_row:
            background_equipment = json.loads(background_row['equipment_option_a'])
            background_gold = background_row['equipment_option_a_gold']
            
            print(f"[SQLite] Adding {len(background_equipment)} items from {background_id} background")
            
            for equipment_name in background_equipment:
                quantity = 1
                # Handle special quantity items (like arrows_20, rations_5)
                if '_' in equipment_name and equipment_name.split('_')[-1].isdigit():
                    quantity = int(equipment_name.split('_')[-1])
                    equipment_name = equipment_name.rsplit('_', 1)[0]  # Remove quantity suffix
                
                add_item_from_db(equipment_name, quantity)
            
            # Add starting gold from background
            if background_gold > 0:
                cursor.execute("""
                    INSERT INTO character_inventory (id, character_id, item_name, item_type, quantity, weight_lb, description, value_gp, treasure_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (str(uuid.uuid4()), character_id, 'Gold Pieces', 'currency', background_gold, background_gold / 50.0, 'Starting money from background', background_gold, 'coins'))
                print(f"[SQLite] Added {background_gold} gold pieces from {background_id} background")
        else:
            print(f"[SQLite] Warning: Background '{background_id}' not found in database")
        
        # Universal starting equipment (everyone gets these)
        add_item_from_db('Rations', 10, 0, 'gear')
        add_item_from_db('Waterskin', 1, 0, 'gear')
        
        print(f"[SQLite] Added starting equipment for {class_id} {background_id}")

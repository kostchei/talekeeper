# TaleKeeper Function Catalog

_Generated: 2025-10-19T18:49:04_

Total functions documented: 6842

## Parse Issues
- `src/talekeeper/services/warlock_patrons/sorcerer_king_patron.py` - SyntaxError: unindent does not match any outer indentation level (<unknown>, line 95)

## core - `action_cards/action_panel.py`

- `__init__(self, action_type, icon: str, name: str, description: str, parent: Optional[QWidget]=None)` - Inferred from name: init.
- `_apply_assassin_surprising_strikes(self, context: Dict[str, Any])` - Apply Assassin Surprising Strikes bonus damage if conditions are met.
- `_apply_death_strike(self, context: Dict[str, Any], damage_breakdown: dict)` - Apply Death Strike if conditions are met (Assassin level 17+).
- `_apply_styles(self)` - Apply styling to the action card.
- `_is_assassin(self)` - Check if character is an Assassin.
- `_is_attack_action(self)` - Check if this action card represents an attack that can benefit from advantage.
- `_is_first_round_of_combat(self)` - Check if it's the first round of combat.
- `_on_advantage_resource_used(self, resource_type)` - Handle advantage resource usage.
- `_persist_advantage_counts(self, lucky_current: int, lucky_max: int, inspiration_current: int, inspiration_max: int)` - Persist advantage counts to the characters table.
- `_setup_ui(self)` - Setup the action card UI.
- `_trigger_action(self)` - Trigger the action.
- `_update_advantage_halo(self)` - Update and position the advantage halo.
- `_use_brutal_strike(self, strike_type: str)` - Use a Brutal Strike with the specified effect.
- `_use_fast_hands_sleight_of_hand(self)` - Make a Sleight of Hand check as a bonus action with Fast Hands.
- `_use_fast_hands_thieves_tools(self)` - Use thieves' tools as a bonus action with Fast Hands.
- `_use_fast_hands_utilise(self)` - Use Utilise action as a bonus action with Fast Hands.
- `_use_heroic_warrior(self)` - Trigger Heroic Warrior inspiration gain.
- `_use_instinctive_pounce(self)` - Use Instinctive Pounce movement when entering Rage.
- `_use_intimidating_presence(self)` - Use Intimidating Presence to frighten nearby enemies.
- `_use_masterful_mimicry(self)` - Use Masterful Mimicry to mimic speech or handwriting.
- `_use_retaliation(self)` - Use Retaliation reaction to attack an enemy that damaged you.
- `_use_survivor(self)` - Trigger Survivor healing if conditions are met.
- `clear_cooldown(self)` - Clear the cooldown.
- `enterEvent(self, event)` - Handle mouse enter for hover effect.
- `leaveEvent(self, event)` - Handle mouse leave.
- `set_available(self, available: bool)` - Set whether the action is available.
- `set_cooldown(self, turns: int)` - Set cooldown remaining.
- `set_description(self, description: str)` - Update the description text.
- `set_resource_manager(self, resource_manager)` - Set the advantage resource manager.
- `set_tooltip_suffix(self, suffix: str)` - Add a suffix to the action card tooltip (for action economy status).
- `update_theme_styles(self, theme_name: str)` - Update styling based on theme.
- `__init__(self, parent: Optional[QWidget]=None, layout_profile: Optional[LayoutProfile]=None)` - Inferred from name: init.
- `_action_hovered(self, action_type: ActionType, description: str)` - Handle action hover from card.
- `_advance_combat_turn(self, encounter_panel)` - Advance to the next combatant's turn using the CombatManager.
- `_apply_channel_divinity_effect(self, option_name: str, option_data: Dict[str, Any])` - Apply Channel Divinity effect and update resources.
- `_apply_cunning_strike_effects(self, damage_breakdown: dict, dice_cost: int)` - Apply cunning strike effects and log them.
- `_apply_damage_to_player(self, damage: int, encounter_panel, damage_type: str='physical')` - Apply damage to the player character, with class-specific resistances.
- `_apply_dueling_bonus(self, context: Dict[str, Any])` - Apply Dueling fighting style bonus (+2 damage when wielding one melee weapon in one hand and no other weapons).
- `_apply_fighting_style_effects(self, dice_rolls: list, context: Dict[str, Any])` - Apply fighting style effects to damage dice rolls.
- `_apply_great_weapon_fighting(self, dice_rolls: list, context: Dict[str, Any])` - Apply Great Weapon Fighting: reroll 1s and 2s on melee weapons with two-handed or heavy property.
- `_apply_healing_to_player(self, healing: int)` - Apply healing to the player character.
- `_apply_lay_on_hands_healing(self, healing_points: int, cure_conditions: dict, target_id: str)` - Apply Lay on Hands healing and update resources.
- `_apply_mastery_effect(self, mastery_name: str, hit: bool, context: Dict[str, Any])` - Apply the specific mastery effect using the service definitions.
- `_apply_savage_attacker(self, dice_rolls: list, num_dice: int, die_size: int, context: Dict[str, Any])` - Apply Savage Attacker feat - roll weapon damage dice twice, use higher roll (first attack per round only).
- `_apply_smite_of_protection(self)` - Apply Smite of Protection buff (Devotion level 15).
- `_apply_sneak_attack(self, context: Dict[str, Any], damage_breakdown: dict)` - Apply sneak attack damage if conditions are met.
- `_apply_styles(self)` - Apply initial styling based on the active theme.
- `_apply_styles_for_theme(self, theme_name: str)` - Inferred from name: apply styles for theme.
- `_apply_weapon_mastery_effects(self, weapon_name: str, attack_total: int, target_ac: int, hit: bool, damage_total: int, context: Dict[str, Any])` - Apply weapon mastery effects using simplified database-driven logic.
- `_attach_resource_manager(self, card)` - Ensure a newly created card is wired to the active advantage manager.
- `_build_off_hand_context(self, base_context: Dict[str, Any])` - Build context for off-hand attack.
- `_build_weapon_dict_from_context(self, context: Dict[str, Any])` - Build weapon dictionary from action context for service calls.
- `_calculate_cunning_strike_cost(self)` - Calculate total dice cost for active cunning strike effects.
- `_calculate_hit_bonus(self, weapon: Dict[str, Any], hand: str)` - Calculate attack bonus for a weapon.
- `_calculate_spell_attack_bonus(self)` - Calculate spell attack bonus = proficiency + spellcasting ability modifier.
- `_calculate_spell_damage(self, spell_name: str, spell_level: int, cast_level: int)` - Calculate spell damage based on spell and cast level. Returns (total_damage, log_string).
- `_calculate_spell_save_dc(self)` - Calculate spell save DC = 8 + proficiency + spellcasting ability modifier.
- `_can_dual_wield(self)` - Check if character can dual wield with current equipment.
- `_can_sneak_attack(self, context: Dict[str, Any])` - Check if sneak attack can be applied.
- `_cast_spell(self, action_type: ActionType, context: Dict[str, Any])` - Handle spell casting from slot cards.
- `_cast_spell_from_slot(self, slot_data: Dict[str, Any], character_id: str)` - Cast spell from new slot card system.
- `_cast_spell_legacy(self, action_type: ActionType, spell_data: Dict[str, Any], character_id: str)` - Legacy spell casting for old system compatibility.
- `_character_has_potions(self)` - Check if character has any healing potions.
- `_character_has_weapon_mastery_feature(self)` - Check if character class gets weapon masteries (Fighter, Rogue, Barbarian, Paladin).
- `_check_and_roll_initiative(self, encounter_panel, context: Dict[str, Any])` - Check if initiative needs to be rolled and roll it.
- `_check_concentration_save(self, character_id: str, damage: int)` - Check for concentration saves when character takes damage.
- `_check_divine_smite(self, is_critical: bool, target_monster: Any, context: Dict[str, Any], base_damage: int=0)` - Check if Paladin wants to use Divine Smite after hitting.
- `_clear_feature_cards(self)` - Clear all feature-based action cards (like Second Wind).
- `_consume_healing_potion(self, character_id: str)` - Remove one healing potion from character's inventory.
- `_consume_ration(self, character_id: str)` - Consume one ration from character inventory.
- `_continue_combat_turn_cycle(self, encounter_panel)` - Continue the combat turn cycle with a small delay to prevent infinite recursion.
- `_continue_monster_attacks(self, remaining_monsters, monster_data, encounter_panel)` - Continue executing remaining monster attacks.
- `_create_action_cards(self)` - Create action cards for different action types.
- `_create_feature_cards(self)` - Create action cards for character features like Second Wind.
- `_create_slots_display(self, available: int, maximum: int)` - Create visual display of spell slots like ●●●○○ (3/5).
- `_create_spell_action_cards(self)` - Create swappable spell slot cards grouped by level and action type.
- `_create_spell_description(self, spell: Dict[str, Any])` - Create a concise description for the spell action card.
- `_create_spell_slot_card(self, spell_level: int, action_type: ActionType, default_spell: Dict[str, Any], available_spells: List[Dict[str, Any]], available_slots: int, max_slots: int)` - Create a swappable spell slot card.
- `_create_weapon_cards(self)` - Create weapon attack cards based on equipped weapons.
- `_determine_spell_action_type(self, spell: Dict[str, Any])` - Determine the appropriate action type for a spell.
- `_end_combat(self, encounter_panel)` - End combat when all monsters are defeated.
- `_ensure_combat_session(self)` - Ensure there is an action-economy combat session available.
- `_execute_attack_without_initiative(self, action_type: ActionType, context: Dict[str, Any], encounter_panel)` - Execute the attack without rolling initiative (used for immediate attacks and pending attacks).
- `_execute_channel_divinity_effect(self, option_name: str, option_data: Dict[str, Any])` - Execute the specific Channel Divinity effect.
- `_execute_mastery_effect(self, mastery_name: str, special_effects: str, context: Dict[str, Any], requires_save: bool, save_ability: Optional[str], save_dc_formula: Optional[str], damage_formula: Optional[str])` - Execute the specific mastery effect.
- `_execute_monster_attack(self, monster_instance, monster_stats: dict, encounter_panel)` - Execute a single monster's attack against the player.
- `_execute_monster_attacks_with_delay(self, living_monsters, monster_data, encounter_panel)` - Execute monster attacks with a small delay between each attack.
- `_execute_monster_turns_before_player(self, encounter_panel, initiative_order: list, monster_data: dict)` - Execute monster attacks for all monsters that go before the player.
- `_execute_multiple_attacks(self, action_type: ActionType, context: Dict[str, Any], encounter_panel, num_attacks: int)` - Execute multiple attacks, allowing target switching if enemies are killed.
- `_execute_pending_attack(self)` - Execute the player's attack that was held due to losing initiative.
- `_execute_remaining_initiative_turns(self, encounter_panel, current_encounter)` - Execute remaining monster turns in initiative order after player's turn.
- `_execute_single_attack(self, action_type: ActionType, context: Dict[str, Any], encounter_panel)` - Execute a single attack (used by two-weapon fighting system).
- `_execute_single_monster_attack(self, monster_instance, action, monster_stats: dict, encounter_panel, attack_num: int=1, total_attacks: int=1)` - Execute a single attack from a monster action.
- `_execute_two_weapon_attack(self, context: Dict[str, Any], encounter_panel)` - Execute both main-hand and off-hand attacks if dual wielding.
- `_extract_weapon_properties(weapon: Dict[str, Any])` - Safely extract weapon property tags as a list.
- `_feature_name_to_action_type(self, feature_name: str)` - Convert a feature name to its corresponding ActionType.
- `_format_damage(self, weapon: Dict[str, Any], is_off_hand: bool=False)` - Format weapon damage string.
- `_get_ability_uses_remaining(self, ability_name: str)` - Get remaining uses for an ability from character resources.
- `_get_action_cooldown(self, action_type: ActionType)` - Get the cooldown turns for an action.
- `_get_all_damage_bonuses(self, context: Dict[str, Any])` - Get all feature-based damage bonuses and their values.
- `_get_attack_count(self, context: Dict[str, Any])` - Get number of attacks based on class features and levels.
- `_get_barbarian_level_from_database(self)` - Get the character's barbarian class level from database (for multiclass support).
- `_get_cantrip_dice_by_level(self, char_level: int)` - Get number of damage dice for cantrips based on character level.
- `_get_channel_divinity_uses_text(self)` - Get Channel Divinity uses as text (e.g., '2/2', '1/2', '0/2').
- `_get_character_castable_spells(self, character_id: str)` - Get list of spells the character can currently cast.
- `_get_character_hit_die(self)` - Get the character's hit die size based on their class.
- `_get_character_spell_slots(self, character_id: str)` - Get character's spell slots using the spellcasting service.
- `_get_combat_manager(self)` - Lazily construct the combat manager with the active DB path.
- `_get_constitution_modifier(self)` - Get character's Constitution modifier.
- `_get_context_damage_profile(self, context: Dict[str, Any])` - Return damage dice/type, falling back to weapon metadata when absent.
- `_get_context_weapon_properties(self, context: Dict[str, Any])` - Extract weapon properties from attack context dictionaries.
- `_get_dueling_bonus(self, context: Dict[str, Any])` - Check if character gets Dueling fighting style bonus (+2 damage).
- `_get_economy_unavailability_reason(self, action_type: ActionType)` - Get reason why an action is unavailable due to action economy.
- `_get_encounter_panel(self)` - Get the encounter panel from the main window.
- `_get_equipment_database(self)` - Lazily construct the equipment database helper with the active DB path.
- `_get_feat_resource_remaining(self, feat_name: str, resource_type: str)` - Get remaining uses for a feat resource.
- `_get_feature_data(self, feature_name: str)` - Retrieve feature metadata by display name.
- `_get_fighting_style_ac_bonus(self)` - Get AC bonus from fighting styles.
- `_get_fighting_style_attack_bonus(self, context: Dict[str, Any])` - Get attack bonus from fighting styles.
- `_get_fighting_style_damage_bonus(self, context: Dict[str, Any])` - Get damage bonus from fighting styles.
- `_get_mastery_definition(self, mastery_name: str)` - Retrieve and cache mastery metadata from the service.
- `_get_monster_data_for_combat_manager(self, monster_instance)` - Get monster data in the format expected by combat manager.
- `_get_radiant_strikes_bonus(self, context: Dict[str, Any])` - Get Radiant Strikes bonus for Paladins at level 11+.
- `_get_rage_damage_bonus(self, context: Dict[str, Any])` - Check if Barbarian gets rage damage bonus for melee weapon attacks using Strength.
- `_get_rage_damage_from_database(self, barbarian_level: int)` - Get rage damage bonus from database by looking up barbarian features.
- `_get_resource_service(self)` - Lazily construct the character resource service.
- `_get_sneak_attack_damage(self)` - Get sneak attack damage based on rogue level.
- `_get_spell_icon(self, spell: Dict[str, Any])` - Get an appropriate icon for the spell based on school and properties.
- `_get_spell_mechanics(self, spell_name: str)` - Determine spell mechanics: 'attack', 'save', or 'auto'.
- `_get_spell_save_type(self, spell_name: str)` - Get the type of saving throw required for a spell.
- `_get_spell_slots(self, level: int)` - Get available spell slots of given level.
- `_get_spellcasting_service(self)` - Lazily construct the spellcasting service with the active DB path.
- `_get_two_weapon_fighting_damage_bonus(self, context: Dict[str, Any])` - Get damage bonus from Two-Weapon Fighting style for off-hand attacks.
- `_get_unavailability_reasons(self, action_type: ActionType)` - Get reasons why an action is unavailable.
- `_get_weapon_attack_service(self)` - Lazily construct the weapon attack service with the active DB path.
- `_get_weapon_mastery(self, weapon_name: str)` - Get mastery for a weapon from cached assignments or equipment data.
- `_get_weapon_mastery_service(self)` - Lazily construct the weapon mastery service with the active DB path.
- `_handle_cleave_followup(self, action_type: ActionType, context: Dict[str, Any], encounter_panel, original_target_id: str, weapon_name: str)` - Resolve Cleave mastery follow-up attack against a random nearby foe.
- `_handle_combat_manager_result(self, result, monster_instance, encounter_panel)` - Handle the results from combat manager monster attack.
- `_handle_rest_action(self, context: Dict[str, Any])` - Handle rest action - prompt for short or long rest.
- `_handle_spell_attack(self, spell_data: Dict[str, Any], context: Dict[str, Any])` - Handle attack spell effects.
- `_handle_spell_effects(self, action_type: ActionType, spell_data: Dict[str, Any], cast_level: int)` - Handle spell effects based on action type.
- `_handle_spell_reaction(self, spell_data: Dict[str, Any], context: Dict[str, Any])` - Handle reaction spell effects.
- `_handle_spell_utility(self, spell_data: Dict[str, Any], context: Dict[str, Any])` - Handle utility/buff spell effects.
- `_has_channel_divinity_uses(self)` - Check if paladin has Channel Divinity uses remaining.
- `_has_class_feature(self, feature_name: str)` - Check if character has a specific class feature.
- `_has_healing_potion(self, character_id: str)` - Check if character has healing potions in inventory.
- `_has_lay_on_hands_uses(self)` - Check if paladin has Lay on Hands uses remaining.
- `_has_rage_uses(self)` - Check if character has rage uses remaining.
- `_has_rations(self, character_id: str)` - Check if character has at least one ration in inventory.
- `_has_stroke_of_luck_uses(self)` - Check if character has Stroke of Luck uses remaining.
- `_hazards_present(self)` - Check if any hazards are currently active.
- `_hydrate_equipped_weapon(self, weapon: Dict[str, Any])` - Ensure equipped weapon entries include mastery-critical metadata.
- `_infer_base_weapon_name(weapon_name: str)` - Best-effort extraction of the non-magical base weapon name.
- `_is_action_available(self, action_type: ActionType)` - Check if an action is currently available.
- `_is_action_available_by_economy(self, action_type: ActionType)` - Check if an action is available based on action economy rules.
- `_is_combat_action(self, action_type: ActionType)` - Check if an action should trigger turn advancement (end player turn).
- `_is_critical_hit(self, attack_breakdown: dict, context: Dict[str, Any])` - Check if an attack is a critical hit based on character class/subclass.
- `_is_monster_alive_in_encounter(self, encounter_panel, monster_id: str)` - Check if a monster is still alive in the encounter panel.
- `_is_player_turn_d20(self)` - Check if it's the player's turn using D&D 2024 rules.
- `_load_monster_data(self)` - Load monster data from database for stats lookups.
- `_log_action_economy_usage(self, action_type: ActionType, economy_type)` - Log action economy usage to combat log.
- `_log_attack_result(self, hit: bool, weapon: str, target: str, attack_breakdown: dict, target_ac: int, damage_breakdown: dict=None)` - Log the result of an attack with detailed dice breakdown.
- `_log_fighting_style(self, style_name: str, bonus_type: str, description: str)` - Log fighting style bonuses to combat log.
- `_log_initiative_results(self, player_initiative: int, initiative_order: list, player_dex_mod: int)` - Log the initiative results to show turn order.
- `_log_mastery_effect(self, mastery_name: str, description: str)` - Log mastery effect to combat log.
- `_log_monster_attack_result(self, hit: bool, monster_name: str, action_name: str, attack_roll: int, player_ac: int, damage: int, attack_info: dict, roll_breakdown: dict=None, attack_num: int=1, total_attacks: int=1)` - Log monster attack results with advantage/disadvantage information.
- `_log_player_turn_start(self)` - Log that it's the player's turn again.
- `_log_to_combat_panel(self, message: str)` - Log message to combat panel.
- `_log_to_parent(self, message: str)` - Log message to parent's log panel.
- `_log_weapon_mastery_effects(self, mastery_effects: Dict[str, Any])` - Log weapon mastery effects to combat log.
- `_log_weapon_mastery_effects_old(self, mastery_effects: Dict[str, Any])` - OLD VERSION - Log weapon mastery effects to combat log.
- `_long_rest_healing(self)` - Full healing during long rest.
- `_map_action_to_economy_type(self, action_type: ActionType)` - Map ActionType to ActionEconomyType.
- `_monsters_present(self)` - Check if any monsters are currently present/alive.
- `_new_execute_attack(self, action_type: ActionType, context: Dict[str, Any])` - NEW ATTACK SYSTEM - Built from scratch with Fighter Extra Attacks support.
- `_normalize_feature_name(name: str)` - Normalize feature names for internal lookups.
- `_normalize_weapon_properties(properties: Any)` - Normalize weapon property payloads into a lowercase list.
- `_parse_monster_attack(self, action: dict, monster_stats: dict)` - Parse monster attack info from action entry.
- `_prepare_equipped_item(self, item: Any)` - Deep-copy equipped items and hydrate weapons with database metadata.
- `_refresh_action_availability(self)` - Refresh the availability state of all action cards and tabs.
- `_refresh_advantage_resources(self)` - Sync Lucky/Inspiration counts from the database after rests.
- `_refresh_spell_action_cards(self)` - Refresh spell action cards to reflect current spell slot availability.
- `_resolve_character_id(self)` - Resolve the active character ID from context or parent widgets.
- `_resolve_db_path(self)` - Resolve the database path for resource operations.
- `_restore_all_abilities(self)` - Restore all abilities (long rest).
- `_restore_short_rest_abilities(self)` - Restore abilities that recharge on short rest.
- `_roll_attack(self, context: Dict[str, Any])` - Roll an attack roll (d20 + modifiers) with advantage/disadvantage. Returns (total, breakdown).
- `_roll_damage(self, context: Dict[str, Any])` - Roll damage dice with ability modifier. Returns (total, breakdown).
- `_roll_monster_damage(self, damage_dice: str, damage_bonus: int)` - Roll damage for monster attack.
- `_roll_monster_save(self, target_monster, save_type: str)` - Roll a saving throw for a monster.
- `_roll_spell_attack(self)` - Roll a spell attack (1d20 + spell attack bonus).
- `_save_character_xp(self)` - Save character XP to database.
- `_set_category(self, category: ActionCategory)` - Set the active action category.
- `_setup_combat_manager(self, encounter_panel, initiative_order)` - Set up the combat manager with player and monster combatants.
- `_setup_ui(self)` - Initialize the action panel UI components.
- `_short_rest_healing(self)` - Allow hit die healing during short rest.
- `_show_action_unavailable_feedback(self, action_type: ActionType, reason: str)` - Show feedback when an action cannot be taken.
- `_show_cunning_strike_dialog(self)` - Show Cunning Strike selection dialog
- `_show_spell_level_selection_dialog(self, spell: Dict[str, Any], character_id: str)` - Show dialog to select which spell level to cast at.
- `_show_spell_selection_dialog(self, available_spells: List[Dict[str, Any]])` - Show dialog to select which spell to cast from available options.
- `_store_cunning_strike_selection(self, character_id: str, effects: List)` - Store Cunning Strike selection in character_combat_state
- `_take_long_rest(self, dialog)` - Execute long rest.
- `_take_short_rest(self, dialog)` - Execute short rest.
- `_toggle_reckless_attack(self)` - Toggle Reckless Attack state for barbarian.
- `_trigger_action(self, action_type: ActionType, context: Dict[str, Any])` - Handle action trigger from card.
- `_trigger_action_with_economy(self, action_type: ActionType, context: Dict[str, Any])` - Trigger an action with action economy enforcement.
- `_trigger_feature_action(self, action_type)` - Handle feature-based action triggers.
- `_trigger_monster_counter_attacks(self, encounter_panel)` - Trigger counter-attacks from all living monsters after player's action.
- `_trigger_rogue_action(self, action_type)` - Handle rogue feature actions.
- `_trigger_subclass_action(self, action_type)` - Handle subclass feature actions.
- `_update_action_availability(self)` - Update action card availability based on action economy.
- `_update_action_economy(self, used_action: ActionType)` - Update action economy after using an action.
- `_update_action_economy_display(self)` - Update action economy display including tabs and cards.
- `_update_card_availability(self)` - Update the availability state of all action cards.
- `_update_cooldowns(self)` - Update action cooldowns (called by timer).
- `_update_economy_status_display(self)` - Update the action economy status display in the header.
- `_update_potion_card(self)` - Update the potion card to show current potion count.
- `_update_rage_state(self)` - Update rage state at the start of each turn.
- `_update_reckless_attack_state(self)` - Update Reckless Attack state at the start of each turn.
- `_update_tab_availability(self, status: Dict[str, Any])` - Update the visual state of category tabs based on action economy.
- `_update_visible_cards(self)` - Update which action cards are visible based on current category.
- `_use_ability(self, ability_name: str)` - Use an ability - decrement uses remaining via resource service.
- `_use_channel_divinity(self)` - Use Channel Divinity with proper dialog.
- `_use_feat_resource(self, feat_name: str, resource_type: str)` - Use a feat resource - decrement remaining uses.
- `_use_healing_potion(self, context: Dict[str, Any])` - Use a healing potion to restore hit points.
- `_use_holy_nimbus(self)` - Activate Holy Nimbus transformation (Devotion level 20).
- `_use_lay_on_hands(self)` - Use paladin Lay on Hands healing with proper dialog.
- `_use_rage(self)` - Activate barbarian rage.
- `end_combat_session(self)` - Clear combat session and reset action availability.
- `get_action_economy_status(self)` - Get current action economy status for UI display.
- `inspiration_offensive_active(self)` - Inferred from name: inspiration offensive active.
- `inspiration_offensive_active(self, value)` - Inferred from name: inspiration offensive active.
- `load_character_equipment(self, equipped_items: Dict[str, Any], character_stats: Dict[str, Any])` - Load character equipment and stats to create weapon cards.
- `load_character_feats(self, character_feats: List[str])` - Load character feats for fighting style and other feat-based effects.
- `load_character_features(self, character_features: Dict[str, Any])` - Load character features and create feature-based action cards.
- `load_character_resources(self, character_data: Dict[str, Any])` - Load character advantage resources (Lucky, Inspiration).
- `load_weapon_masteries(self, weapon_masteries: List[str], assignments: Optional[List[Dict[str, Any]]]=None)` - Load character weapon masteries and assignment map.
- `lucky_offensive_active(self)` - Inferred from name: lucky offensive active.
- `lucky_offensive_active(self, value)` - Inferred from name: lucky offensive active.
- `on_level_selected(level)` - Inferred from name: on level selected.
- `on_smite_chosen(spell_slot_level: int, is_undead_or_fiend: bool, use_free_smite: bool)` - Inferred from name: on smite chosen.
- `on_spell_selected(spell)` - Inferred from name: on spell selected.
- `reset_action_economy(self)` - Reset action economy for a new turn.
- `set_character_context(self, context: Dict[str, Any])` - Set the character context for action availability.
- `set_combat_session(self, combat_session, character_id: str)` - Set the current combat session for action economy tracking.
- `set_target_monster(self, monster_id: str)` - Set the target monster for attacks.
- `set_turn_active(self, active: bool)` - Set whether it's currently the character's turn.
- `update_theme(self, theme_name: str)` - Update all action cards to use the specified theme.

## core - `action_cards/channel_divinity_dialog.py`

- `__init__(self, parent=None, character_data: Dict[str, Any]=None, current_uses: int=0, max_uses: int=2, available_options: List[Dict[str, Any]]=None)` - Initialize Channel Divinity dialog.
- `get_selected_option(self)` - Get the currently selected option.
- `option_selected(self, checked: bool)` - Handle option selection.
- `reject(self)` - Handle dialog cancellation.
- `setup_ui(self)` - Set up the user interface.
- `update_display(self)` - Update the display with current values.
- `update_use_button(self)` - Update use button availability.
- `use_channel_divinity(self)` - Use the selected Channel Divinity option.
- `create_channel_divinity_options(character_level: int, sacred_oath: str)` - Create Channel Divinity options based on character level and oath.

## core - `action_cards/cunning_strike_selector.py`

- `__init__(self, option_data: Dict[str, Any], parent=None)` - Inferred from name: init.
- `_on_toggled(self, checked: bool)` - Inferred from name: on toggled.
- `_setup_ui(self)` - Inferred from name: setup ui.
- `_update_style(self)` - Inferred from name: update style.
- `is_checked(self)` - Inferred from name: is checked.
- `set_checked(self, checked: bool)` - Inferred from name: set checked.
- `set_enabled(self, enabled: bool)` - Inferred from name: set enabled.
- `__init__(self, dice_cost: int, parent=None)` - Inferred from name: init.
- `_update_text(self)` - Inferred from name: update text.
- `__init__(self, character_id: str, db_path: str='talekeeper.db', sneak_attack_eligible: bool=True, parent=None)` - Inferred from name: init.
- `_clear_selection(self)` - Inferred from name: clear selection.
- `_confirm_selection(self)` - Inferred from name: confirm selection.
- `_load_options(self)` - Inferred from name: load options.
- `_on_option_toggled(self, effect_id: str, checked: bool)` - Inferred from name: on option toggled.
- `_setup_ui(self)` - Inferred from name: setup ui.
- `_update_preview(self)` - Inferred from name: update preview.
- `get_selected_effects(self)` - Inferred from name: get selected effects.

## core - `action_cards/divine_smite_dialog.py`

- `__init__(self, parent=None, is_critical: bool=False, available_spell_slots: Dict[int, int]=None, target_info: Dict[str, Any]=None, has_free_smite: bool=False)` - Initialize Divine Smite dialog.
- `_calculate_damage_dice(self, slot_level: int, is_undead_or_fiend: bool)` - Calculate base damage dice for Divine Smite.
- `_on_cancel(self)` - Handle cancel button.
- `_on_confirm(self)` - Handle confirm button.
- `_on_timeout(self)` - Handle timeout - don't use smite.
- `_setup_ui(self)` - Set up the dialog UI.
- `_update_countdown(self)` - Update the countdown display.
- `get_smite_damage_dice(self, slot_level: int)` - Get the damage dice string for a given spell slot level.

## core - `action_cards/epic_boon_dialog.py`

- `__init__(self, available_boons: List[Dict[str, Any]], parent=None)` - Inferred from name: init.
- `_on_confirm(self)` - Inferred from name: on confirm.
- `_on_selection_changed(self, current, previous)` - Inferred from name: on selection changed.
- `_setup_ui(self)` - Inferred from name: setup ui.
- `get_selected_boon(self)` - Inferred from name: get selected boon.
- `show_epic_boon_dialog(available_boons: List[Dict[str, Any]], parent=None)` - Inferred from name: show epic boon dialog.

## core - `action_cards/lay_on_hands_dialog.py`

- `__init__(self, parent=None, character_data: Dict[str, Any]=None, current_pool: int=0, max_pool: int=0, target_options: list=None)` - Initialize Lay on Hands dialog.
- `_update_condition_ui(self)` - Update UI based on selected conditions.
- `apply_healing(self)` - Apply the healing and emit signal.
- `get_healing_info(self)` - Get the current healing configuration.
- `reject(self)` - Handle dialog cancellation.
- `select_target(self, target_id: str)` - Select a healing target.
- `setup_ui(self)` - Set up the user interface.
- `update_apply_button(self)` - Update apply button availability.
- `update_condition_option(self, state: int)` - Update condition curing options.
- `update_display(self)` - Update the display with current values.
- `update_healing_points(self, value: int)` - Update healing points and effect description.
- `update_poison_option(self, state: int)` - Update poison curing option.

## core - `action_cards/tactical_master_dialog.py`

- `__init__(self, weapon_name: str, original_mastery: str, parent=None)` - Inferred from name: init.
- `_get_mastery_description(self, mastery: str)` - Get description for mastery type.
- `_on_confirm(self)` - Confirm selection and close dialog.
- `_on_selection_changed(self, mastery: str)` - Handle radio button selection.
- `_setup_ui(self)` - Build the dialog UI.
- `get_selected_mastery(self)` - Get the selected mastery type.
- `show_tactical_master_dialog(weapon_name: str, original_mastery: str, parent=None)` - Show tactical master dialog and return selected mastery.

## core - `action_cards/weapon_mastery_dialog.py`

- `__init__(self, options: List[Dict[str, str]], selected: List[str], max_selections: Optional[int]=None, parent=None)` - Inferred from name: init.
- `_checked_items(self)` - Inferred from name: checked items.
- `_enforce_limit(self)` - Inferred from name: enforce limit.
- `selected_options(self)` - Return the currently checked weapon mastery assignments.

## core - `audio/audio_player.py`

- `__init__(self, parent: Optional[QObject]=None)` - Inferred from name: init.
- `_on_error(self, error: QMediaPlayer.Error, error_string: str)` - Handle playback errors.
- `_on_state_changed(self, state: QMediaPlayer.PlaybackState)` - Handle playback state changes.
- `_play_next(self)` - Play the next file in the queue.
- `clear_queue(self)` - Clear the playback queue.
- `enqueue(self, audio_file: Path)` - Add an audio file to the playback queue.
- `get_queue_size(self)` - Get number of items in queue.
- `get_volume(self)` - Get current volume (0.0 to 1.0).
- `is_enabled(self)` - Check if narration is enabled.
- `set_enabled(self, enabled: bool)` - Enable or disable narration playback.
- `set_volume(self, volume: float)` - Set playback volume (0.0 to 1.0).
- `stop(self)` - Stop current playback.

## core - `audio/campaign_voice_registry.py`

- `__init__(self, profiles: Optional[Iterable[CampaignVoiceProfile]]=None, default_profile: Optional[CampaignVoiceProfile]=None)` - Inferred from name: init.
- `ensure_profile(self, campaign_style: str, voice_id: str, model_path: Path)` - Create a placeholder profile if one does not exist.
- `get_active_profile(self)` - Return the profile that should be used for narration.
- `register_profile(self, profile: CampaignVoiceProfile)` - Add or replace a campaign voice profile.
- `set_active_campaign(self, campaign_style: Optional[str])` - Update the active campaign style, falling back to the default.
- `to_dict(self)` - Return a serializable snapshot useful for debugging.

## core - `audio/file_cleanup.py`

- `__init__(self, output_directory: Path, max_age_hours: int=24, max_files: Optional[int]=500)` - Inferred from name: init.
- `cleanup_excess_files(self)` - Delete oldest files if count exceeds max_files.
- `cleanup_old_files(self)` - Delete narration files older than max_age_hours.
- `run_cleanup(self)` - Run both age-based and count-based cleanup.

## core - `audio/local_tts_engine.py`

- `__init__(self, model_path: Path, config_path: Optional[Path]=None, device: str='auto')` - Inferred from name: init.
- `_find_piper(self)` - Inferred from name: find piper.
- `_verify_piper(self)` - Inferred from name: verify piper.
- `synthesize(self, text: str, output_path: Path, voice_profile: CampaignVoiceProfile, *, speaker_wav: Optional[Path]=None, style_overrides: Optional[Dict[str, float]]=None)` - Generate an audio file that narrates ``text``.

## core - `audio/log_narration_pipeline.py`

- `from_payload(cls, payload: Dict[str, object])` - Inferred from name: from payload.
- `__init__(self, log_panel, voice_registry: CampaignVoiceRegistry, *, engine_factory: Optional[Callable[[CampaignVoiceProfile], LocalTTSEngine]]=None, output_directory: Path | str=Path('excess') / 'narration', batch_window_seconds: float=2.5, auto_start: bool=True, audio_player: Optional[NarrationPlayer]=None)` - Inferred from name: init.
- `_derive_style_overrides(self, batch: List[LogNarrationEvent], profile: CampaignVoiceProfile)` - Inferred from name: derive style overrides.
- `_get_engine(self, profile: CampaignVoiceProfile)` - Inferred from name: get engine.
- `_process_loop(self)` - Inferred from name: process loop.
- `_synthesize_batch(self, batch: List[LogNarrationEvent])` - Inferred from name: synthesize batch.
- `enqueue_event(self, event: LogNarrationEvent)` - Inferred from name: enqueue event.
- `enqueue_payload(self, payload: Dict[str, object])` - Inferred from name: enqueue payload.
- `process_entries_sync(self, events: Iterable[LogNarrationEvent])` - Inferred from name: process entries sync.
- `start(self)` - Inferred from name: start.
- `stop(self)` - Inferred from name: stop.
- `update_campaign_voice(self, campaign_style: Optional[str])` - Inferred from name: update campaign voice.
- `_format_details(self, event: LogNarrationEvent)` - Inferred from name: format details.
- `format_batch(self, events: Iterable[LogNarrationEvent])` - Inferred from name: format batch.

## core - `audio/piper_voice_trainer.py`

- `__init__(self, piper_training_dir: Optional[Path]=None, language: str='en-us')` - Inferred from name: init.
- `prepare_dataset(self, samples: Iterable[VoiceTrainingSample], output_dir: Path, *, sample_rate: int=22050, copy_audio: bool=True)` - Prepare LJSpeech-format dataset for Piper training.
- `setup_training_environment(self)` - Clone and set up Piper training repository.
- `train_voice(self, dataset_dir: Path, output_dir: Path, voice_name: str, *, quality: str='medium', epochs: Optional[int]=None, batch_size: int=32, validation_split: float=0.1)` - Train a Piper voice model.
- `verify_training_environment(self)` - Check if Piper training environment is set up.
- `sanitized_transcript(self)` - Inferred from name: sanitized transcript.
- `create_sample_dataset_from_directory(audio_dir: Path, transcript_file: Optional[Path]=None)` - Helper: Create training samples from a directory of audio files.

## core - `audio/voice_profiles.py`

- `normalized_style(self)` - Inferred from name: normalized style.
- `to_dict(self)` - Serialize profile for persistence or debugging.
- `build_synthesis_kwargs(self)` - Return keyword arguments understood by the local TTS engine.

## core - `audio/voice_trainer.py`

- `__init__(self, base_model_path: Optional[Path]=None, base_config_path: Optional[Path]=None, language: str='en')` - Inferred from name: init.
- `prepare_training_workspace(self, samples: Iterable[VoiceTrainingSample], workspace: Path, *, copy_audio: bool=True)` - Create an LJSpeech-style dataset from the provided samples.
- `train_voice(self, samples: Iterable[VoiceTrainingSample], output_directory: Path, voice_profile: CampaignVoiceProfile, *, epochs: int=150, copy_audio: bool=True)` - Fine-tune a base model on the provided samples.
- `sanitized_transcript(self)` - Inferred from name: sanitized transcript.

## core - `character_sheet/character_panel.py`

- `__init__(self, parent: Optional[QWidget]=None, layout_profile: Optional[LayoutProfile]=None)` - Inferred from name: init.
- `_add_xp_history_entry(self, description: str, xp_gain: int)` - Add an entry to the XP history list.
- `_apply_styles(self)` - No hardcoded styling - let main theme handle all colors.
- `_create_ability_row(self, short_name: str, full_name: str, skills: list)` - Create a complete ability row: [ABILITY BOX] [SAVING THROW] [SKILLS...]
- `_create_ability_row_with_stats(self, short_name: str, full_name: str)` - Create Constitution row with secondary stats instead of skills.
- `_create_ability_widget(self, short_name: str, full_name: str)` - Create an ability score widget like in D&D character sheet.
- `_create_pact_magic_widget(self)` - Create Warlock pact magic slots display.
- `_create_saving_throw_widget(self, ability_name: str)` - Create a saving throw widget with diamond indicator.
- `_create_skill_widget(self, skill_name: str, ability: str)` - Create a skill widget with proficiency indicator and bonus.
- `_create_spell_slot_circle(self, used: bool=False)` - Create a single spell slot circle indicator.
- `_create_spell_slot_level_widget(self, level: int)` - Create a spell slot level display widget.
- `_create_stat_widget(self, name: str, value: str)` - Create a secondary stat widget (AC, Init, HP, Speed).
- `_get_feature_description(self, feature_name: str, class_name: str='fighter')` - Get feature description from feature definitions.
- `_get_spell_slots_for_class_level(self, class_name: str, level: int)` - Get spell slots by level for a class/level combination.
- `_load_character_portrait(self, character_name: str)` - Load character portrait from data/images/characters directory.
- `_load_feats_and_features_from_db(self, character_id: str)` - Fetch feats and class features for a character from SQLite.
- `_log_feature_activation(self, feature_name: str, result: dict)` - Log feature activation to the game log.
- `_log_hp_change(self, current_hp: int, max_hp: int)` - Log HP change to game log.
- `_setup_basic_panel(self)` - Setup the basic character panel (always visible) with D&D layout.
- `_setup_detail_panel(self)` - Setup the detailed character panel (shown when expanded).
- `_setup_ui(self)` - Initialize the character panel UI components.
- `_toggle_expansion(self)` - Toggle the panel expansion - simple and reliable approach.
- `_update_conditions(self, character_data: Dict[str, Any])` - Update the condition display widget.
- `_update_detail_panel(self)` - Update the detailed panel with character-specific information.
- `_update_regular_spell_slots(self, spell_slots: Dict[int, int], character_data: Dict[str, Any])` - Update regular spell slot displays.
- `_update_spell_slots_display(self, character_data: Dict[str, Any])` - Update spell slot display based on character class and level.
- `_update_warlock_pact_slots(self, level: int, character_data: Dict[str, Any])` - Update Warlock pact magic slot display.
- `_update_xp_displays(self)` - Update all XP-related displays.
- `add_xp_gain(self, description: str, xp_gain: int)` - Public method to add XP gain and update displays.
- `clear_character_data(self)` - Clear the character display.
- `is_expanded(self)` - Return current expansion state.
- `load_character_data(self, character_data: Dict[str, Any])` - Load character data into the panel display.
- `refresh_conditions(self)` - Force refresh of condition display (for external updates).
- `update_ac(self, new_ac)` - Update the AC display when equipment changes.
- `update_hp(self, current_hp: int, max_hp: int)` - Update HP display - database should already be updated by game engine.

## core - `core/class_features.py`

- `__init__(self)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Use Action Surge.
- `__init__(self)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Use Cunning Action.
- `can_use(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Can use if bonus action is available.
- `__init__(self)` - Inferred from name: init.
- `__init__(self, feature_name: str='Extra Attack', min_level: int=5)` - Inferred from name: init.
- `_get_attacks(self, character: Dict[str, Any])` - Inferred from name: get attacks.
- `__init__(self, name: str, description: str, feature_type: FeatureType, requirements: Optional[FeatureRequirement]=None)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Apply the feature's effects to the character.
- `can_use(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Check if the feature can be used.
- `meets_requirements(self, character: Dict[str, Any])` - Check if character meets feature requirements.
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_build_feature_registry(self)` - Build registry of all available features keyed by normalized names.
- `_build_fighting_style_feature(self, feature_def: Any, character_id: str, level: int)` - Inferred from name: build fighting style feature.
- `_get_fighting_style(self, character_id: str)` - Get fighting style from database.
- `_load_class_features(self, character_id: str, class_name: str, level: int, subclass: Optional[str])` - Load features for a specific class up to a given level.
- `_normalize_feature_name(name: str)` - Normalize feature names to registry keys.
- `apply_passive_features(self, character: Dict[str, Any])` - Apply all passive features to character stats.
- `get_available_features(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Get list of features currently available to use.
- `load_character_features(self, character_id: str)` - Load all features for a character from the database.
- `process_rest(self, rest_type: str)` - Process rest and restore appropriate resources.
- `use_feature(self, feature_name: str, character: Dict[str, Any], context: Optional[Dict]=None)` - Use a specific feature.
- `restore(self, amount: Optional[int]=None)` - Restore resource uses.
- `use(self, amount: int=1)` - Attempt to use the resource.
- `__init__(self, style: str)` - Inferred from name: init.
- `__init__(self)` - Inferred from name: init.
- `__init__(self)` - Inferred from name: init.
- `__init__(self, name: str, description: str, modifiers: Dict[str, Any], **kwargs)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Apply passive modifiers to character.
- `can_use(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Passive features are always usable if requirements are met.
- `__init__(self)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Enter or maintain rage.
- `end_rage(self)` - End the rage.
- `__init__(self)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Activate Reckless Attack.
- `can_use(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Can use on first attack of turn.
- `__init__(self)` - Inferred from name: init.
- `__init__(self, name: str, description: str, uses_by_level: Dict[int, int], recharge: ResourceRecharge=ResourceRecharge.LONG_REST, **kwargs)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Use the feature.
- `can_use(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Check if the feature can be used.
- `update_uses(self, level: int)` - Update maximum uses based on level.
- `__init__(self)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Use Second Wind to heal.
- `__init__(self)` - Inferred from name: init.
- `apply_sneak_attack(character: Dict, context: Dict)` - Inferred from name: apply sneak attack.
- `check_trigger(character: Dict, context: Dict)` - Inferred from name: check trigger.
- `__init__(self)` - Inferred from name: init.
- `_apply_effect(self, character: Dict[str, Any], context: Dict[str, Any])` - Inferred from name: apply effect.
- `_can_trigger(self, character: Dict[str, Any], context: Dict[str, Any])` - Inferred from name: can trigger.
- `__init__(self)` - Inferred from name: init.
- `__init__(self)` - Inferred from name: init.
- `_apply_effect(self, character: Dict[str, Any], context: Dict[str, Any])` - Inferred from name: apply effect.
- `_can_trigger(self, character: Dict[str, Any], context: Dict[str, Any])` - Inferred from name: can trigger.
- `__init__(self)` - Inferred from name: init.
- `_apply_effect(self, character: Dict[str, Any], context: Dict[str, Any])` - Inferred from name: apply effect.
- `_can_trigger(self, character: Dict[str, Any], context: Dict[str, Any])` - Inferred from name: can trigger.
- `__init__(self)` - Inferred from name: init.
- `_apply_effect(self, character: Dict[str, Any], context: Dict[str, Any])` - Inferred from name: apply effect.
- `_can_trigger(self, character: Dict[str, Any], context: Dict[str, Any])` - Inferred from name: can trigger.
- `__init__(self, name: str, description: str, trigger_condition: Callable[[Dict, Dict], bool], effect: Callable[[Dict, Dict], Dict], **kwargs)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Apply the triggered effect.
- `can_use(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Check if trigger condition is met.
- `__init__(self)` - Inferred from name: init.
- `calculate_ac(character: Dict)` - Inferred from name: calculate ac.
- `__init__(self)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Use Uncanny Dodge.
- `can_use(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Can use once per turn when hit.
- `__init__(self)` - Inferred from name: init.
- `_get_slots(self, character: Dict[str, Any])` - Inferred from name: get slots.

## core - `core/combat_manager.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_build_initiative_context(self, combatant: Combatant)` - Assemble context data for initiative rolls.
- `_calculate_xp_reward(self, monster_id: str)` - Calculate XP reward for defeating monster
- `_execute_monster_attack(self, attacker: Combatant, target: Combatant, action: CombatAction)` - Execute a monster attack
- `_execute_single_attack(self, attacker: Combatant, target: Combatant, weapon_data: Dict[str, Any], attack_num: int, total_attacks: int)` - Execute a single attack roll and damage
- `_find_monster_action(self, monster: Combatant, action_name: str)` - Find monster action by name
- `_get_extra_attack_count(self, class_name: str, level: int)` - Get number of extra attacks based on D&D 2024 rules
- `_get_saving_throw_modifier(self, combatant: Combatant, ability: str)` - Get saving throw modifier for a given ability
- `_handle_automatic_condition(self, effect, target: Combatant, attacker: Combatant)` - Handle automatic conditions (e.g., restrained by web)
- `_handle_champion_turn_start(self, combatant: Optional[Combatant])` - Trigger Champion subclass automation at the start of a player turn.
- `_handle_save_or_condition(self, effect, target: Combatant, attacker: Combatant)` - Handle save-or-condition effects (e.g., paralysis, poisoned)
- `_handle_save_or_damage(self, effect, target: Combatant, attacker: Combatant)` - Handle save-or-damage effects (e.g., poison damage)
- `_handle_size_condition(self, effect, target: Combatant, attacker: Combatant)` - Handle size-based conditions (e.g., grapple large or smaller)
- `_has_remarkable_athlete(self, combatant: Combatant)` - Check and cache whether the combatant benefits from Remarkable Athlete.
- `_parse_monster_actions(self, actions_json: str)` - Parse monster actions from 5eTools JSON format
- `_parse_multiattack(self, actions: List[CombatAction])` - Parse Multiattack from monster data
- `_process_attack_effects(self, standardized_attack, target: Combatant, attacker: Combatant)` - Process standardized attack effects (saves, conditions, etc.)
- `_process_single_effect(self, effect, target: Combatant, attacker: Combatant)` - Process a single standardized effect
- `_roll_damage(self, damage_dice: str)` - Roll damage dice (e.g., '1d8+3')
- `_start_new_round(self)` - Start a new combat round
- `_trigger_fires_burn(self, attacker: Combatant, target: Combatant)` - Attempt to trigger Fire's Burn if the attacker qualifies and the target is still standing.
- `add_monster_combatant(self, monster_id: str, monster_data: Dict[str, Any])` - Add monster to combat
- `add_player_combatant(self, character_data: Dict[str, Any])` - Add player character to combat
- `advance_turn(self)` - Advance to the next combatant's turn.
- `end_combat(self)` - End combat and return summary
- `execute_monster_turn(self, monster_id: str)` - Execute monster's turn with proper Multiattack support.
- `execute_player_attack(self, character_id: str, weapon_data: Dict[str, Any], target_id: str)` - Execute player attack with proper Extra Attack support.
- `get_combat_log(self)` - Get all combat log messages
- `get_current_combatant(self)` - Get the combatant whose turn it is
- `is_combat_ended(self)` - Check if combat should end (one side defeated)
- `is_player_turn(self)` - Check if it's currently the player's turn
- `log(self, message: str)` - Add message to combat log
- `start_combat(self)` - Start combat by rolling initiative for all combatants.

## core - `core/config.py`

- `__init__(self, config_file: str='talekeeper_config.json')` - Inferred from name: init.
- `enable_developer_mode(self)` - Enable developer-friendly settings
- `enable_performance_mode(self)` - Enable performance-optimized settings
- `get_debug_setting(self, setting: str)` - Get a debug setting value
- `get_feature_setting(self, setting: str)` - Get a feature setting value
- `get_performance_profile(self)` - Get current performance profile description
- `get_performance_setting(self, setting: str)` - Get a performance setting value
- `is_debug_enabled(self, debug_option: str)` - Check if a debug option is enabled
- `is_feature_enabled(self, feature: str)` - Check if a feature is enabled
- `load_config(self)` - Load configuration from file
- `reset_to_defaults(self)` - Reset all configuration to defaults
- `save_config(self)` - Save current configuration to file
- `set_debug_setting(self, setting: str, value: Any)` - Set a debug setting value
- `set_feature_setting(self, setting: str, value: Any)` - Set a feature setting value
- `set_performance_setting(self, setting: str, value: Any)` - Set a performance setting value
- `__post_init__(self)` - Initialize default release subclasses if not set
- `enable_action_card_caching()` - Check if action card caching is enabled
- `enable_condition_caching()` - Check if condition caching is enabled
- `get_config()` - Get the global configuration instance
- `get_ui_update_throttle()` - Get UI update throttle in milliseconds
- `is_debug_enabled(debug_option: str)` - Quick check if a debug option is enabled
- `is_feature_enabled(feature: str)` - Quick check if a feature is enabled
- `should_log_database_queries()` - Check if database queries should be logged
- `use_enhanced_subclass_manager()` - Check if enhanced subclass manager should be used

## core - `core/debug_commands.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_register_commands(self)` - Register all available debug commands
- `cmd_cache(self, args: List[str])` - Show cache statistics
- `cmd_combat(self, args: List[str])` - Show combat state
- `cmd_conditions(self, args: List[str])` - Show active conditions for character
- `cmd_config(self, args: List[str])` - Show or modify configuration
- `cmd_dev_mode(self, args: List[str])` - Enable developer mode
- `cmd_economy(self, args: List[str])` - Display action economy state
- `cmd_features(self, args: List[str])` - List available features for character
- `cmd_help(self, args: List[str])` - Show help for debug commands
- `cmd_list(self, args: List[str])` - List all available commands
- `cmd_memory(self, args: List[str])` - Display memory usage
- `cmd_perf_mode(self, args: List[str])` - Enable performance mode
- `cmd_performance(self, args: List[str])` - Show timing metrics
- `cmd_queries(self, args: List[str])` - Toggle database query logging
- `cmd_reset_config(self, args: List[str])` - Reset configuration to defaults
- `cmd_status(self, args: List[str])` - Show system status
- `cmd_test_conditions(self, args: List[str])` - Apply test conditions
- `cmd_test_economy(self, args: List[str])` - Reset action economy
- `cmd_test_features(self, args: List[str])` - Reload character features
- `cmd_test_rage(self, args: List[str])` - Test rage mechanics
- `execute(self, command_line: str)` - Execute a debug command
- `log_performance(self, operation: str, duration_ms: float)` - Log performance metric
- `execute_debug_command(command_line: str)` - Execute a debug command (global function)
- `log_performance_metric(operation: str, duration_ms: float)` - Log a performance metric (global function)

## core - `core/feature_definitions.py`

- `get_feature_at_level(cls, class_name: str, level: int, subclass: Optional[str]=None)` - Get only the features gained at a specific level.
- `get_features_by_level(cls, class_name: str, level: int, subclass: Optional[str]=None)` - Get all features for a character of given class and level.

## core - `core/feature_integration.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_ensure_feature_tables(self)` - Ensure all required feature tables exist.
- `_get_fighting_style(self, cursor: sqlite3.Cursor, character_id: str)` - Get fighting style from character feats.
- `_initialize_class_features(self, cursor: sqlite3.Cursor, character_id: str, class_name: str, level: int)` - Initialize class-specific feature tables with fresh data.
- `_initialize_feature(self, cursor: sqlite3.Cursor, character_id: str, class_name: str, feature: FeatureDefinition, character_level: int)` - Initialize a single feature in the database.
- `_update_legacy_tables(self, cursor: sqlite3.Cursor, character_id: str, feature_name: str, result: Dict)` - Update legacy feature tables for backward compatibility.
- `apply_passive_features(self, character_id: str)` - Apply all passive feature modifiers to a character.
- `get_available_features(self, character_id: str, context: Optional[Dict]=None)` - Get all features available to a character.
- `initialize_character_features(self, character_id: str)` - Initialize features for a character based on class and level.
- `process_rest(self, character_id: str, rest_type: str)` - Process a rest and restore features.
- `use_feature(self, character_id: str, feature_name: str, context: Optional[Dict]=None)` - Use a character feature and update database state.
- `get_feature_integration(db_path: str='talekeeper.db')` - Get the singleton feature integration instance.

## core - `core/game_engine_sqlite.py`

- `__init__(self, id, name)` - Inferred from name: init.
- `__init__(self, id, name)` - Inferred from name: init.
- `__init__(self, id, name)` - Inferred from name: init.
- `__init__(self, db_path: str='talekeeper.db')` - Initialize SQLite game engine.
- `_add_starting_equipment(self, cursor, character_id: str, character_data: Dict)` - Add starting equipment based on class and background.
- `_apply_feat_effects_to_character(self, character_dict: Dict[str, Any], feats: List[str])` - Apply mechanical effects of feats to character stats.
- `_calculate_armor_class(self, character_id: str, strength: int, dexterity: int, constitution: int, class_id: str)` - Calculate AC based on equipped armor and class features like Unarmored Defense.
- `_calculate_movement_speed(self, character_id: str, class_id: str, level: int)` - Calculate movement speed based on class features and level.
- `_cleanup_orphaned_slots(self)` - Clean up save slots that are marked as occupied but have no character.
- `_ensure_tables_exist(self)` - Ensure all required tables exist in the database.
- `_get_armor_stats(self, armor_name: str)` - Get armor stats for inventory.
- `_get_background_name(self, background_id: str)` - Get display name for background from database.
- `_get_class_name(self, class_id: str)` - Get display name for class.
- `_get_connection(self)` - Get database connection with foreign keys enabled.
- `_get_full_caster_spell_slots(self, level: int)` - Get spell slot progression for full casters (Wizard, Cleric).
- `_get_race_name(self, race_id: str)` - Get display name for race.
- `_get_weapon_stats(self, weapon_name: str)` - Get weapon stats for inventory.
- `_initialize_barbarian_features(self, cursor, character_id: str, character_data: Dict)` - Initialize Barbarian-specific features.
- `_initialize_class_features(self, cursor, character_id: str, character_data: Dict)` - Initialize class-specific features table based on character's class.
- `_initialize_cleric_features(self, cursor, character_id: str, character_data: Dict)` - Initialize Cleric-specific features (full spellcaster + divine).
- `_initialize_fighter_features(self, cursor, character_id: str, character_data: Dict)` - Initialize Fighter-specific features.
- `_initialize_rogue_features(self, cursor, character_id: str, character_data: Dict)` - Initialize Rogue-specific features.
- `_initialize_warlock_features(self, cursor, character_id: str, character_data: Dict)` - Initialize Warlock-specific features (pact magic).
- `_initialize_wizard_features(self, cursor, character_id: str, character_data: Dict)` - Initialize Wizard-specific features (full spellcaster).
- `_load_settings(self)` - Load application settings from SQLite or file.
- `_normalize_item_name(self, item_name: str)` - Convert plural item names to singular forms for database lookup.
- `_parse_equipment_choice(self, choice_string: str)` - Parse equipment choice strings like 'Scimitar + Shortsword' or '2 Shortswords' into individual items.
- `_safe_get_row_value(self, row: sqlite3.Row, key: str, default=None)` - Safely get a value from sqlite3.Row with default fallback.
- `add_feat_to_character_sync(self, character_id: str, feat_name: str)` - Add a new feat to a character.
- `add_gold_to_character_sync(self, character_id: str, gold_amount: int)` - Add gold to character's inventory in the database.
- `apply_equipment_choices_sync(self, character_data, equipment_choices)` - Apply equipment choices made during character creation.
- `auto_save(self)` - Perform automatic save (just calls save_game_sync).
- `calc_modifier(score)` - Inferred from name: calc modifier.
- `can_equip_item(self, character_id: str, item_name: str)` - Check if character can equip a specific item. Returns (can_equip, reason).
- `create_new_character_sync(self, character_data: Dict, save_slot: int)` - Create a new character and save to database.
- `delete_character_sync(self, save_slot: int)` - Delete character from save slot.
- `get_available_backgrounds_sync(self)` - Get available backgrounds from database.
- `get_available_classes_sync(self)` - Get available classes from database.
- `get_available_races_sync(self)` - Get available races from database.
- `get_character_by_id_sync(self, character_id: str)` - Load character by character ID.
- `get_character_fighting_styles(self, character_id: str)` - Get character's fighting styles from character_features table.
- `get_character_inventory_sync(self, character_id: str)` - Get inventory items for a character.
- `get_class_equipment_choices_sync(self, class_id: str)` - Get equipment choices for a specific class from the database.
- `get_equipment_item_sync(self, item_name: str)` - Get equipment item data by name from database.
- `get_monsters_by_cr_sync(self, min_cr: float, max_cr: float)` - Get monsters within CR range from JSON data files.
- `get_save_slots_sync(self)` - Get all save slots.
- `load_character_sync(self, save_slot: int)` - Load character from save slot.
- `recalculate_character_stats_sync(self, character_id: str)` - Recalculate character stats including AC and feat effects.
- `save_character_sync(self, character_id: str=None)` - Save current character or specified character to database.
- `save_game_sync(self)` - Save current game state.
- `save_settings(self)` - Save application settings.
- `shutdown(self)` - Clean shutdown of game engine.
- `update_character_equipment_sync(self, character_id: str, equipment_slot: str, item_name: Optional[str]=None)` - Update character equipment in database.
- `update_character_hp_sync(self, current_hp: int, max_hp: int=None)` - Update character's HP in database.
- `update_character_resources_sync(self, character_id: str, resource_updates: Dict[str, Any])` - Update character resources in database.
- `update_character_xp_sync(self, character_id: str, new_xp: int)` - Update character's experience points in the database.

## core - `database/database_init.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_ensure_inventory_columns(self, cursor: sqlite3.Cursor)` - Ensure Bag of Holding columns exist on character_inventory.
- `check_and_apply_migrations(self)` - Legacy migration support - now redirects to schema versioning.
- `check_schema_version(self)` - Check and upgrade database schema if needed.
- `create_migrations_table(self)` - Inferred from name: create migrations table.
- `create_schema(self)` - Inferred from name: create schema.
- `initialize(self, force: bool=False, dev_mode: bool=False)` - Inferred from name: initialize.
- `load_dev_data(self)` - Inferred from name: load dev data.
- `load_game_data(self)` - Inferred from name: load game data.
- `verify_database(self)` - Inferred from name: verify database.
- `main()` - Inferred from name: main.

## core - `equipment_layout/equipment_panel.py`

- `__init__(self, parent: Optional[QWidget]=None, layout_profile: Optional[LayoutProfile]=None)` - Inferred from name: init.
- `_apply_styles(self)` - Apply initial styling using the active theme palette.
- `_calculate_main_hand_attack_bonus(self)` - Calculate attack bonus for main hand weapon.
- `_calculate_spell_attack_bonus(self)` - Calculate spell attack bonus.
- `_calculate_unarmed_attack_bonus(self)` - Calculate unarmed attack bonus.
- `_calculate_unarmed_damage(self)` - Calculate unarmed damage.
- `_calculate_weapon_attack_bonus(self, weapon: Dict[str, Any], is_off_hand: bool=False)` - Calculate attack bonus for a specific weapon.
- `_calculate_weapon_damage(self, weapon: Dict[str, Any], is_off_hand: bool=False)` - Format weapon damage string.
- `_create_equipment_slots(self)` - Create the equipment slot widgets.
- `_drop_selected_item(self)` - Drop the currently selected inventory item.
- `_equip_item(self, item: Dict[str, Any], slot: EquipmentSlot)` - Equip an item to a slot.
- `_extract_weapon_properties(self, weapon: Dict[str, Any])` - Return normalized weapon property tags for the provided weapon.
- `_is_two_handed_weapon(self, item: Dict[str, Any])` - Check if an item is a two-handed weapon.
- `_load_attunement_from_database(self)` - Load attunement state from database.
- `_save_attunement_to_database(self, item_key: str, attune: bool)` - Save or remove attunement state to/from database.
- `_setup_ui(self)` - Initialize the equipment panel UI components.
- `_switch_to_compact_layout(self)` - Switch to compact layout.
- `_switch_to_expanded_layout(self)` - Switch to expanded layout with more detailed information.
- `_toggle_expansion(self)` - Toggle the panel expansion - expands leftward to cover encounter pane.
- `_unequip_item(self, slot: EquipmentSlot)` - Unequip an item from a slot.
- `_update_attack_displays(self)` - Update all attack display rows.
- `_update_character_bonuses(self)` - Update character bonuses from equipped magical items.
- `_update_inventory_display(self)` - Update the inventory list display.
- `_update_stats_display(self)` - Update the stats display based on equipped items.
- `_use_item(self, item_widget: QListWidgetItem)` - Use an item from inventory.
- `_use_selected_item(self)` - Use the currently selected inventory item.
- `add_item_to_inventory(self, item: Dict[str, Any])` - Add an item to the inventory.
- `enable_attunement(self)` - Enable attunement after a rest.
- `get_equipped_items(self)` - Get currently equipped items with enriched database stats.
- `get_equipped_items_dict(self)` - Get currently equipped items as dictionary - alias for get_equipped_items.
- `get_inventory_items(self)` - Get inventory items.
- `is_expanded(self)` - Return current expansion state.
- `load_equipment_data(self, equipped_items: Dict[str, Any], inventory_items: List[Dict[str, Any]], character_strength: int=10, character_dexterity: int=10, character_class: str='', character_constitution: int=10)` - Load equipment and inventory data.
- `remove_item_from_inventory(self, item: Dict[str, Any])` - Remove an item from the inventory.
- `update_theme(self, theme_name: str)` - Update styling based on theme.
- `__init__(self, slot: EquipmentSlot, parent: Optional[QWidget]=None)` - Inferred from name: init.
- `_setup_ui(self)` - Setup the slot UI.
- `clear_item(self)` - Clear the item from this slot.
- `dragEnterEvent(self, event: QDragEnterEvent)` - Handle drag enter event.
- `dropEvent(self, event: QDropEvent)` - Handle drop event.
- `mousePressEvent(self, event)` - Handle mouse press for item removal.
- `set_item(self, item: Dict[str, Any])` - Set the item in this slot.

## core - `menu/game_menu.py`

- `__init__(self, parent: Optional[QWidget]=None)` - Inferred from name: init.
- `_apply_styles(self)` - Apply dark theme styling to menu components.
- `_setup_ui(self)` - Initialize the menu UI components.
- `set_character_loaded(self, loaded: bool)` - Enable/disable character-dependent buttons based on whether a character is loaded.
- `set_save_enabled(self, enabled: bool)` - Enable/disable the save & exit button based on game state.
- `update_game_info(self, character_name: str, level: int)` - Update the game information display with character name and level.

## core - `models/action_economy.py`

- `can_take_action(self, action_type: ActionEconomyType)` - Check if an action type can currently be taken.
- `end_turn(self)` - End the current turn.
- `from_dict(cls, data: Dict[str, Any])` - Create from dictionary.
- `get_action_status(self, action_type: ActionEconomyType)` - Get current availability status of an action type.
- `get_action_usage_count(self, action_id: str)` - Get number of times a specific action has been used this combat.
- `get_active_effects(self)` - Get all currently active effects.
- `get_remaining_movement(self)` - Get remaining movement for this turn.
- `get_resource_usage(self, resource_name: str)` - Get total usage of a specific resource this combat.
- `get_turn_summary(self)` - Get a summary of this turn's action economy state.
- `has_active_effect(self, action_id: str)` - Check if a specific action has an active ongoing effect.
- `start_new_round(self, round_number: int)` - Start a new round - minimal resets (reactions stay consumed until owner's turn).
- `start_new_turn(self, round_number: int, turn_position: int)` - Start a new turn - reset action economy.
- `to_dict(self)` - Convert to dictionary for storage.
- `track_class_action(self, action_id: str, action_name: str, resource_cost: Dict[str, int]=None, effect_duration: Optional[Dict[str, Any]]=None)` - Track usage of a class-specific action (Stage 3.2 Enhancement).
- `update_effect_durations(self)` - Update durations for ongoing effects - called at start of turn/round.
- `use_action(self, action_type: ActionEconomyType, action_name: str, action_data: Dict=None)` - Attempt to use an action. Returns True if successful, False if not available.
- `use_action_surge(self)` - Use Fighter Action Surge to gain an additional action.
- `_start_combatant_turn(self, combatant_id: str)` - Start a combatant's turn.
- `add_combatant(self, combatant_id: str, name: str, combatant_type: str='character', movement_speed: int=30, has_action_surge: bool=False)` - Add a combatant to the action economy tracking.
- `from_dict(cls, data: Dict[str, Any])` - Create from dictionary.
- `get_active_combatant(self)` - Get the ID of the currently active combatant.
- `get_combat_summary(self)` - Get a summary of the current combat state.
- `get_combatant_action_count(self, combatant_id: str, action_id: str)` - Get action usage count for a specific combatant.
- `get_combatant_active_effects(self, combatant_id: str)` - Get active effects for a specific combatant.
- `get_combatant_resource_usage(self, combatant_id: str, resource_name: str)` - Get resource usage for a specific combatant.
- `get_combatant_state(self, combatant_id: str)` - Get the action economy state for a specific combatant.
- `next_turn(self)` - Advance to the next turn. Returns the ID of the next active combatant.
- `start_combat(self, initiative_order: List[str])` - Start combat with the given initiative order.
- `to_dict(self)` - Convert to dictionary for storage.
- `track_class_action(self, combatant_id: str, action_id: str, action_name: str, resource_cost: Dict[str, int]=None, effect_duration: Optional[Dict[str, Any]]=None)` - Track a class-specific action for a combatant (Stage 3.2 Enhancement).
- `use_action(self, combatant_id: str, action_type: ActionEconomyType, action_name: str, action_data: Dict=None)` - Attempt to use an action for a combatant.

## core - `scripts/backfill_settlements.py`

- `backfill_settlements(db_path: str='talekeeper.db')` - Inferred from name: backfill settlements.
- `generate_settlement_type(seed: int)` - Inferred from name: generate settlement type.
- `get_position_seed(q: int, r: int)` - Inferred from name: get position seed.

## core - `scripts/character_tools/create_corey_barbarian.py`

- `main()` - Inferred from name: main.

## core - `scripts/character_tools/create_level5_rogue.py`

- `create_level5_rogue()` - Create a level 5 rogue character

## core - `scripts/character_tools/programmatic_character_creator.py`

- `__init__(self, db_path='talekeeper.db')` - Inferred from name: init.
- `_add_starting_inventory(self, character_id: str, starting_items: List[Dict[str, Any]])` - Add starting inventory items to character.
- `_find_available_slot(self)` - Find the next available save slot.
- `_get_class_ability_uses(self, class_id: str, class_features: dict)` - Get ability uses based on class and level.
- `_load_template(self, template_path: str)` - Load template from JSON or YAML file.
- `_select_barbarian_features(self, template: dict)` - Barbarian: Rage setup.
- `_select_fighter_features(self, template: dict)` - Fighter: Fighting style + weapon masteries.
- `_select_paladin_features(self, template: dict)` - Paladin: Fighting style + weapon masteries + Divine Smite.
- `_select_ranger_features(self, template: dict)` - Ranger: Fighting style + favored enemy + spells.
- `_select_rogue_features(self, template: dict)` - Rogue: Expertise skills + Sneak Attack.
- `_select_spellcaster_features(self, template: dict, class_id: str)` - Spellcaster: Cantrips + prepared/known spells.
- `_select_warlock_features(self, template: dict)` - Warlock: Pact boon + invocations + spells.
- `_step_10_prepare_for_save(self, payload: dict)` - Step 10: Convert to engine schema.
- `_step_11_persist_and_verify(self, save_data: dict, template: dict)` - Step 11: Persist to database and verify.
- `_step_2_load_class(self, template: dict)` - Step 2: Load class data (mirrors encounter_panel._load_class_data).
- `_step_3_select_class_features(self, template: dict, class_data: dict)` - Step 3: Select class-specific features.
- `_step_4_load_background_species(self, template: dict)` - Step 4: Load background and species data.
- `_step_5_select_feats(self, template: dict, background_data: dict, species_data: dict)` - Step 5: Select origin and bonus feats.
- `_step_6_allocate_abilities_skills(self, template: dict, class_data: dict, background_data: dict, species_data: dict)` - Step 6: Allocate ability scores and skill proficiencies.
- `_step_7_select_equipment(self, template: dict, class_data: dict)` - Step 7: Select starting equipment.
- `_step_8_generate_name(self, template: dict, species_data: dict, class_data: dict, background_data: dict)` - Step 8: Generate a campaign-aware name.
- `_step_9_assemble_payload(self, character_data: dict, template: dict)` - Step 9: Assemble the character creation payload.
- `create_from_dict(self, template: dict)` - Create a character from a template dictionary.
- `create_from_template(self, template_path: str)` - Create a character from a JSON or YAML template file.
- `main()` - CLI entry point.

## core - `scripts/comprehensive_monster_migration.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_convert_effect_to_standard(self, effect: AttackEffect)` - Convert AttackEffect to standardized format.
- `_convert_monster_actions(self, monster_name: str, actions_data: List[Dict])` - Convert monster actions from old to new format.
- `_convert_parsed_attack_to_standard(self, parsed_attack)` - Convert ParsedAttack to standardized format.
- `_determine_attack_type(self, parsed_attack)` - Determine attack type from parsed attack.
- `_is_already_converted(self, actions_data: List[Dict])` - Check if monster already uses standardized format.
- `_is_attack_action(self, action: Dict)` - Determine if an action is an attack.
- `_parse_damage_string(self, damage_str)` - Parse damage string like '2d6+3 slashing' into standardized format.
- `_print_migration_summary(self)` - Print summary of migration results.
- `_process_monster(self, cursor, monster_id: str, name: str, actions_json: str, dry_run: bool)` - Process a single monster.
- `migrate_all_monsters(self, dry_run: bool=True)` - Migrate all monsters in the database.
- `main()` - Main migration function.
- `test_sample()` - Test migration on a small sample first.

## core - `scripts/create_level_20_fighter.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_generate_stats_document(self, cursor, base_stats, max_hp)` - Generate detailed stats document
- `create_character(self)` - Create the level 20 Fighter in the database
- `main()` - Create the level 20 Fighter character

## core - `scripts/database_tools/add_paladin_spells_from_srd.py`

- `add_paladin_spells_to_database(db_path='talekeeper.db')` - Add all paladin spells from SRD to database.

## core - `scripts/database_tools/create_conan_campaigns.py`

- `create_campaigns_table(conn)` - Inferred from name: create campaigns table.
- `create_conan_campaigns(conn)` - Inferred from name: create conan campaigns.
- `get_level_range(cr)` - Inferred from name: get level range.
- `main()` - Inferred from name: main.
- `populate_conan_core(conn)` - Inferred from name: populate conan core.
- `populate_conan_like(conn)` - Inferred from name: populate conan like.

## core - `scripts/database_tools/delete_character_slots.py`

- `delete_character_slots(db_path: str, slot_range: str)` - Delete characters from specified save slots.

## core - `scripts/database_tools/fix_spell_slots.py`

- `fix_all_spellcasters()` - Initialize spell slots for all spellcaster characters that don't have them.

## core - `scripts/database_tools/populate_campaign_monsters.py`

- `create_campaign_monsters_table(conn)` - Inferred from name: create campaign monsters table.
- `main()` - Inferred from name: main.
- `populate_conan_campaign(conn, campaign_id='conan')` - Inferred from name: populate conan campaign.

## core - `scripts/database_tools/replace_conan_with_core.py`

- `replace_conan_campaign()` - Inferred from name: replace conan campaign.

## core - `scripts/database_tools/show_conan_campaigns.py`

- `main()` - Inferred from name: main.
- `show_campaign_stats(conn)` - Inferred from name: show campaign stats.
- `show_query_examples(conn)` - Inferred from name: show query examples.
- `show_sample_monsters(conn)` - Inferred from name: show sample monsters.
- `show_unique_to_conan_like(conn)` - Inferred from name: show unique to conan like.

## core - `scripts/database_tools/spell_diagnostic.py`

- `check_character_spells()` - Check what spells characters have in the database.
- `check_spells_table()` - Check what spells exist in the spells table.
- `simulate_action_panel_spell_query()` - Simulate what the action panel does to get spells.

## core - `scripts/database_tools/update_magic_item_pricing.py`

- `calculate_magic_item_price(cursor, item_id, name, rarity, current_cost, item_type)` - Inferred from name: calculate magic item price.
- `get_base_item_cost(cursor, magic_item_name)` - Inferred from name: get base item cost.
- `update_magic_item_pricing(db_path='../../talekeeper.db', dry_run=True)` - Inferred from name: update magic item pricing.

## core - `scripts/database_tools/validate_unified_system.py`

- `validate_unified_system()` - Validate the unified feature system database

## core - `scripts/database_tools/validate_warlock_db.py`

- `validate_warlock_database()` - Validate Warlock database schema and data.

## core - `scripts/database_tools/validate_warlock_schema_fix.py`

- `validate_schema_fix(db_path='talekeeper.db')` - Inferred from name: validate schema fix.

## core - `scripts/migrate_monster_attacks.py`

- `parse_attack(self, attack_data: Dict[str, Any])` - Parse a standardized attack into execution data.
- `parse_effect(self, effect_data: Dict[str, Any])` - Parse a standardized effect.
- `create_standardized_parser()` - Create a simple parser for standardized attack format.
- `migrate_monster_attacks(db_path: str='talekeeper.db', dry_run: bool=True)` - Migrate monster attacks to standardized format.
- `validate_standardized_format(attack_data: Dict[str, Any])` - Validate that an attack follows the standardized format.

## core - `scripts/populate_level_progression.py`

- `populate_level_progression()` - Inferred from name: populate level progression.

## core - `scripts/process_source_monster_images.py`

- `process_source_images(source_dir: str='assets/line_art_cropped/monsters', output_dir: str='data/images/monsters/golden_age', thumb_size: tuple=(80, 60), full_size: tuple=(320, 240))` - Process all source images and replace generated ones.
- `sanitize_filename(name: str)` - Convert image filename to match monster naming convention.

## core - `scripts/utilities/cleanup_hex_maps.py`

- `cleanup_hex_maps(db_path: str, character_id: str=None, confirm: bool=False)` - Inferred from name: cleanup hex maps.

## core - `scripts/utilities/fix_warlock_schema.py`

- `convert_insert(match)` - Inferred from name: convert insert.

## core - `scripts/utilities/generate_summary.py`

- `cr_sort_key(cr)` - Inferred from name: cr sort key.

## core - `scripts/utilities/manage_subclass_filter.py`

- `add_subclass(class_name: str, subclass_name: str)` - Add a subclass to the release list
- `disable_filtering()` - Disable subclass filtering
- `enable_filtering()` - Enable subclass filtering
- `main()` - Main function to handle command-line arguments
- `remove_subclass(class_name: str, subclass_name: str)` - Remove a subclass from the release list
- `show_current_config()` - Display current subclass filtering configuration

## core - `scripts/utilities/reorganize.py`

- `copy_directory(src, dst)` - Inferred from name: copy directory.
- `copy_file(src, dst_dir)` - Inferred from name: copy file.
- `update_imports(file_path)` - Inferred from name: update imports.

## core - `scripts/utilities/validate_unified_system.py`

- `validate_unified_system()` - Validate the unified feature system database

## core - `services/action_card_generator.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `create_legacy_action_card(self, enhanced_card: EnhancedActionCard, parent: Optional[QWidget]=None)` - Create a legacy ActionCard widget from an EnhancedActionCard.
- `generate_character_action_cards(self, character_id: str, combat_state: Optional[ActionEconomyState]=None)` - Generate all available action cards for a character.
- `generate_class_action_cards(self, character_id: str, class_name: str, level: int, combat_state: Optional[ActionEconomyState]=None)` - Generate action cards for a specific class at a given level
- `get_action_cards_by_economy_type(self, character_id: str, combat_state: Optional[ActionEconomyState]=None)` - Get action cards grouped by economy type.
- `get_available_action_cards(self, character_id: str, combat_state: Optional[ActionEconomyState]=None)` - Get only currently available action cards
- `get_resource_summary(self, character_id: str)` - Get summary of character resources for display.
- `get_unavailable_action_cards(self, character_id: str, combat_state: Optional[ActionEconomyState]=None)` - Get unavailable action cards with reasons.
- `__init__(self, action_def: ClassActionDefinition, validation_result: ActionValidationResult)` - Inferred from name: init.
- `_format_resource_costs(self)` - Format resource costs for display
- `_get_cost_display(self)` - Get cost display string for the card
- `_get_default_icon(self)` - Get default icon based on action type
- `_get_warning_badges(self)` - Get warning badges for the card
- `get_card_style_class(self)` - Get CSS class for card styling
- `get_enhanced_description(self)` - Get description with cost and availability info
- `generate_action_cards_for_character(character_id: str, combat_state: Optional[ActionEconomyState]=None)` - Global function to generate action cards for a character.
- `get_action_cards_by_availability(character_id: str, combat_state: Optional[ActionEconomyState]=None)` - Get action cards split by availability.

## core - `services/action_economy_enforcer.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_apply_action_effects(self, action_def: ClassActionDefinition, character_id: str, combat_economy: Optional[CombatActionEconomy], action_context: Dict[str, Any], result: ActionExecutionResult)` - Apply the actual effects of the action
- `_call_action_handler(self, action_def: ClassActionDefinition, character_id: str, action_context: Dict[str, Any], result: ActionExecutionResult)` - Call the appropriate handler function for the action
- `_consume_action_economy(self, action_def: ClassActionDefinition, combat_economy: CombatActionEconomy, character_id: str, result: ActionExecutionResult)` - Consume action economy slot.
- `_consume_resources(self, action_def: ClassActionDefinition, character_id: str, result: ActionExecutionResult)` - Consume character resources.
- `_consume_single_resource(self, cursor, character_id: str, resource_name: str, amount: int, result: ActionExecutionResult)` - Consume a single resource type
- `_rollback_economy_consumption(self, action_def: ClassActionDefinition, combat_economy: CombatActionEconomy, character_id: str)` - Rollback action economy consumption (simplified - would need more complex logic)
- `_rollback_resource_consumption(self, action_def: ClassActionDefinition, character_id: str, result: ActionExecutionResult)` - Rollback resource consumption
- `_track_action_usage(self, action_def: ClassActionDefinition, combat_economy: CombatActionEconomy, character_id: str, result: ActionExecutionResult)` - Track action usage in combat economy
- `can_execute_action(self, character_id: str, action_id: str, combat_economy: Optional[CombatActionEconomy]=None)` - Check if an action can be executed (non-destructive check).
- `execute_action(self, character_id: str, action_id: str, combat_economy: Optional[CombatActionEconomy]=None, action_context: Optional[Dict[str, Any]]=None)` - Execute an action with full economy enforcement.
- `get_available_actions(self, character_id: str, combat_economy: Optional[CombatActionEconomy]=None)` - Get list of currently available action IDs
- `__init__(self, success: bool, action_id: str='', reason: str='')` - Inferred from name: init.
- `add_economy_consumption(self, economy_type: str)` - Record action economy consumption
- `add_effect(self, effect_id: str, effect_data: Dict[str, Any])` - Record effect application
- `add_resource_consumption(self, resource_name: str, amount: int)` - Record resource consumption
- `add_state_change(self, key: str, old_value: Any, new_value: Any)` - Record state change
- `get_summary(self)` - Get execution summary
- `can_execute_class_action(character_id: str, action_id: str, combat_economy: Optional[CombatActionEconomy]=None)` - Global function to check if an action can be executed.
- `execute_class_action(character_id: str, action_id: str, combat_economy: Optional[CombatActionEconomy]=None, action_context: Optional[Dict[str, Any]]=None)` - Global function to execute a class action with full enforcement.

## core - `services/action_registry.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_check_action_economy(self, action: ClassActionDefinition, character_id: str)` - Check if character has action economy available
- `_check_combat_state(self, character_id: str, state_name: str)` - Check character's combat state
- `_check_prerequisite(self, prereq: ActionPrerequisite, character_data: Dict, character_id: str)` - Check a single prerequisite
- `_check_resources(self, action: ClassActionDefinition, character_id: str)` - Check if character has required resources
- `_compare_values(self, actual: Any, expected: Any, operator: str)` - Compare two values using the given operator
- `_get_character_data(self, character_id: str)` - Get character data from database
- `_get_resource_count(self, character_id: str, resource_name: str)` - Get current count of a resource
- `_meets_level_requirement(self, action: ClassActionDefinition, level: int)` - Check if action meets level requirement
- `_register_barbarian_actions(self)` - Register all Barbarian class actions
- `_register_core_actions(self)` - Register core D&D actions available to all characters
- `can_use_action(self, action_id: str, character_id: str)` - Check if character can currently use an action
- `get_action(self, action_id: str)` - Get action definition by ID
- `get_character_actions(self, character_id: str)` - Get all actions available to a specific character
- `get_class_actions(self, class_name: str, level: int=20)` - Get all actions available to a class at given level
- `get_subclass_actions(self, class_name: str, subclass_name: str, level: int=20)` - Get all actions available to a subclass at given level
- `register_action(self, action: ClassActionDefinition)` - Register a new action definition
- `validate_prerequisites(self, action: ClassActionDefinition, character_id: str)` - Validate all prerequisites for an action

## core - `services/action_validation.py`

- `__init__(self, can_use: bool, action_id: str='', reason: str='')` - Inferred from name: init.
- `add_economy_block(self, economy_type: str, reason: str)` - Add an action economy block
- `add_prerequisite_failure(self, prereq_type: str, expected: Any, actual: Any)` - Add a failed prerequisite
- `add_resource_shortage(self, resource: str, needed: int, available: int)` - Add a resource shortage
- `add_warning(self, warning: str)` - Add a warning message
- `get_user_friendly_message(self)` - Get a user-friendly explanation of why action can't be used
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_check_action_economy(self, action_def: ClassActionDefinition, combat_state: ActionEconomyState)` - Check if action economy allows this action
- `_check_single_prerequisite(self, prereq, character_data: Dict, character_id: str)` - Check a single prerequisite - reuse logic from action registry
- `_get_character_data(self, character_id: str)` - Get character data from database
- `_get_resource_count(self, character_id: str, resource_name: str)` - Get current count of a resource
- `_parse_registry_failures(self, result: ActionValidationResult, registry_check: Dict[str, Any], action_def: ClassActionDefinition, character_id: str)` - Parse failures from registry check into detailed result
- `can_use_class_action(self, character_id: str, action_id: str, combat_state: Optional[ActionEconomyState]=None)` - Check if a character can use a specific class action.
- `get_action_availability(self, character_id: str, combat_state: Optional[ActionEconomyState]=None)` - Get availability for all actions for a character.
- `log_action_attempt(self, character_id: str, action_id: str, success: bool, reason: str='')` - Log action attempts for debugging and analysis
- `validate_action_with_feedback(self, character_id: str, action_id: str, combat_state: Optional[ActionEconomyState]=None)` - Validate action and return detailed feedback.
- `can_use_class_action(character_id: str, action_id: str, combat_state: Optional[ActionEconomyState]=None)` - Global function for checking if a class action can be used.
- `get_action_feedback(character_id: str, action_id: str, combat_state: Optional[ActionEconomyState]=None)` - Global function for getting detailed action feedback.

## core - `services/advantage_system.py`

- `_collection_has_feature(cls, candidate: Any, candidate_names: Set[str])` - Check nested feature collections (dicts/lists) for a matching feature name.
- `_context_has_feature(cls, context: Dict[str, Any], *names: str)` - Determine if any of the provided feature names appear in the roll context.
- `_context_has_remarkable_athlete(cls, context: Dict[str, Any])` - Check whether Remarkable Athlete is present in the context.
- `_get_condition_advantage_sources(character_id: str, roll_type: RollType, context: Dict[str, Any])` - Get advantage sources from character conditions.
- `_get_condition_disadvantage_sources(character_id: str, roll_type: RollType, context: Dict[str, Any])` - Get disadvantage sources from character conditions.
- `_is_athletics_check(context: Dict[str, Any])` - Determine if the current context refers to an Athletics skill check.
- `_normalize_feature_name(candidate: Any)` - Normalize feature descriptors to lowercase names when possible.
- `append_unique(label: str)` - Inferred from name: append unique.
- `calculate_advantage_state(advantage_sources: List[str], disadvantage_sources: List[str])` - Calculate the final advantage state based on all sources.
- `format_roll_description(breakdown: Dict[str, Any])` - Format a roll breakdown into a human-readable description.
- `get_common_advantage_sources(roll_type: RollType, context: Dict[str, Any])` - Get common sources of advantage for different roll types.
- `get_common_advantage_sources(roll_type: RollType, context: Dict[str, Any])` - Get common sources of advantage for different roll types.
- `get_common_disadvantage_sources(roll_type: RollType, context: Dict[str, Any])` - Get common sources of disadvantage for different roll types.
- `roll_d20_with_advantage(advantage_state: AdvantageState, modifier: int=0)` - Roll a d20 with advantage/disadvantage and return result with breakdown.

## core - `services/aura_manager.py`

- `__post_init__(self)` - Inferred from name: post init.
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_character_own_auras(self, cursor, character_id: str)` - Get auras that a character generates for themselves.
- `_get_oath_aura(self, subclass: str, character_id: str, level: int, aura_range: int)` - Get oath-specific aura effect.
- `apply_aura_to_save(self, character_id: str, save_roll: int, save_type: str)` - Apply aura bonuses to a saving throw.
- `calculate_save_bonus(self, character_id: str, save_type: str)` - Calculate total saving throw bonus from auras.
- `check_aura_condition_immunity(self, character_id: str, condition: str)` - Check condition immunity and return the aura providing it.
- `get_active_aura_summary(self, character_id: str)` - Get a summary of all active auras for UI display.
- `get_aura_descriptions(self, character_id: str)` - Get descriptions of all active auras affecting a character.
- `get_aura_range(self, character_level: int)` - Get aura range based on character level.
- `get_character_auras(self, character_id: str)` - Get all auras affecting a character.
- `has_advantage_type(self, character_id: str, advantage_type: str)` - Check if character has advantage on specific types of rolls from auras.
- `has_condition_immunity(self, character_id: str, condition: str)` - Check if character has immunity to a condition from auras.
- `update_character_level(self, character_id: str, new_level: int)` - Update aura effects when character level changes.
- `get_aura_manager(db_path: str='talekeeper.db')` - Get singleton aura manager instance.

## core - `services/barbarian_abilities.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_connection(self)` - Get database connection.
- `add_primal_knowledge_skill(self, character_id: str, skill_name: str)` - Add a skill to Primal Knowledge (Animal Handling, Athletics, Intimidation, Nature, Perception, Survival).
- `check_relentless_rage(self, character_id: str, damage_taken: int)` - Check and potentially trigger Relentless Rage when dropping to 0 HP.
- `end_rage(self, character_id: str, reason: str='duration')` - End rage (duration, heavy armor, incapacitated, etc.).
- `get_barbarian_level(self, character_id: str)` - Get the barbarian class level for a character.
- `get_character_subclass(self, character_id: str)` - Get the barbarian subclass for a character.
- `get_primal_knowledge_skills(self, character_id: str)` - Get available Primal Knowledge skills for barbarian.
- `has_danger_sense_advantage(self, character_id: str, save_ability: str, conditions: List[str]=None)` - Check if character gets Danger Sense advantage on a Dexterity saving throw.
- `has_danger_sense_advantage_enhanced(self, character_id: str, save_ability: str='dexterity')` - Enhanced Danger Sense check using the formal condition system.
- `has_feral_instinct(self, character_id: str)` - Check if character has Feral Instinct (advantage on initiative, can act if surprised).
- `process_berserker_turn_start(self, character_id: str)` - Apply Berserker subclass start-of-turn effects.
- `rest_barbarian_resources(self, character_id: str, rest_type: str)` - Reset barbarian resources on rest.
- `update_barbarian_resources_for_level(self, character_id: str, level: int)` - Update barbarian resource maximums based on level.
- `use_berserker_retaliation(self, character_id: str, attacker_name: str='')` - Use Berserker Retaliation reaction (Level 10+).
- `use_brutal_strike(self, character_id: str, strike_type: str, target_name: str='')` - Use Brutal Strike when making a Reckless Attack.
- `use_intimidating_presence(self, character_id: str)` - Use Intimidating Presence (Berserker Level 14+).
- `use_rage(self, character_id: str)` - Use Rage ability.
- `use_reckless_attack(self, character_id: str)` - Toggle Reckless Attack for this turn.

## core - `services/campaign_description_service.py`

- `__init__(self, base_url: Optional[str]=None, default_model: Optional[str]=None, request_timeout: float=30.0)` - Inferred from name: init.
- `_build_prompt(self, request: DescriptionRequest)` - Inferred from name: build prompt.
- `_fallback_description(self, entity_type: str, entity_data: Dict[str, Any], campaign_frame: Any)` - Return a deterministic blurb when Ollama is unavailable.
- `_generate_from_prompt(self, prompt: str, campaign_frame: Any)` - Inferred from name: generate from prompt.
- `generate_combat_narrative(self, combat_events: List[Dict[str, Any]], campaign_frame: Any, context: Optional[Dict[str, Any]]=None)` - Inferred from name: generate combat narrative.
- `generate_description(self, entity_type: str, entity_data: Optional[Dict[str, Any]], campaign_frame: Any)` - Return a short description or ``None`` if generation fails.
- `generate_encounter_description(self, monsters: List[Dict[str, Any]], campaign_frame: Any, level: int, difficulty: str)` - Inferred from name: generate encounter description.
- `generate_round_summary(self, round_events: List[Dict[str, Any]], campaign_frame: Any)` - Inferred from name: generate round summary.
- `generate_victory_narrative(self, combat_summary: Dict[str, Any], campaign_frame: Any)` - Inferred from name: generate victory narrative.
- `post(self, *args, **kwargs)` - Inferred from name: post.
- `_load_requests_module()` - Inferred from name: load requests module.

## core - `services/character_resources.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_grant_human_long_rest_inspiration(self, cursor, character_id: str)` - Ensure humans regain Heroic Inspiration on long rest.
- `add_resource(self, character_id: str, resource_name: str, max_uses: int, rest_type: str, source_class: str, source_level: int)` - Add a new resource to a character (or update existing).
- `get_character_resources(self, character_id: str)` - Get all resources for a character.
- `get_resource(self, character_id: str, resource_name: str)` - Get a specific resource for a character.
- `get_resources_summary(self, character_id: str)` - Get a summary of all character resources for UI display.
- `initialize_barbarian_resources(self, character_id: str, level: int)` - Initialize Barbarian resources based on level.
- `initialize_fighter_resources(self, character_id: str, level: int)` - Initialize/update Fighter resources based on level.
- `restore_resources_by_rest_type(self, character_id: str, rest_type: str)` - Restore all resources of a specific rest type (short_rest or long_rest).
- `update_resource_max_uses(self, character_id: str, resource_name: str, new_max: int)` - Update max uses for a resource (for level progression).
- `use_resource(self, character_id: str, resource_name: str, uses: int=1)` - Use a resource (consume uses).

## core - `services/cleric_abilities.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_add_domain_spells(self, cursor, character_id: str, domain: str, level: int)` - Add domain spells to character's spell list.
- `_apply_channel_divinity_effect(self, cursor, character_id: str, option_id: str, targets: Optional[List[str]])` - Apply the specific effects of a Channel Divinity option.
- `_apply_domain_features(self, cursor, character_id: str, domain: str, level: int)` - Apply domain-specific features.
- `_initialize_channel_divinity(self, cursor, character_id: str, domain: str, level: int)` - Initialize Channel Divinity options for a cleric.
- `apply_blessed_healer(self, character_id: str, spell_level: int)` - Apply Blessed Healer self-healing for Life Domain clerics.
- `apply_disciple_of_life(self, character_id: str, spell_level: int, base_healing: int)` - Apply Disciple of Life bonus healing for Life Domain clerics.
- `get_character_cleric_info(self, character_id: str)` - Get complete cleric information for a character.
- `initialize_cleric_character(self, character_id: str, domain: str='life')` - Initialize a character as a Cleric with the specified domain.
- `reset_cleric_resources(self, character_id: str, rest_type: str='long')` - Reset cleric resources on rest.
- `use_channel_divinity(self, character_id: str, option_id: str, targets: Optional[List[str]]=None)` - Use a Channel Divinity option.

## core - `services/combat_log_parser.py`

- `__init__(self)` - Inferred from name: init.
- `parse_attack_event(self, log_text: str)` - Inferred from name: parse attack event.
- `parse_combat_round(self, log_entries: List[str])` - Inferred from name: parse combat round.
- `parse_condition_event(self, log_text: str)` - Inferred from name: parse condition event.
- `parse_damage_event(self, log_text: str)` - Inferred from name: parse damage event.
- `parse_death_event(self, log_text: str)` - Inferred from name: parse death event.
- `parse_event(self, log_text: str)` - Inferred from name: parse event.
- `parse_healing_event(self, log_text: str)` - Inferred from name: parse healing event.

## core - `services/concentration_system.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_get_concentration_save_proficiency(self, character_id: str)` - Get proficiency bonus for concentration saves.
- `_parse_spell_duration_to_rounds(self, duration: str)` - Parse spell duration string to number of rounds.
- `check_concentration_breaking_conditions(self, character_id: str)` - Check various conditions that could break concentration.
- `end_concentration(self, character_id: str, reason: str='voluntary')` - End concentration for a character.
- `get_all_concentrating_characters(self)` - Get all characters currently concentrating on spells.
- `get_concentration_spell(self, character_id: str)` - Get the spell a character is currently concentrating on.
- `handle_concentration_breaking_conditions(self, character_id: str)` - Automatically end concentration if breaking conditions are met.
- `make_concentration_save(self, character_id: str, damage_taken: int, constitution_modifier: int=0)` - Make a concentration saving throw when taking damage.
- `start_concentration(self, character_id: str, spell_id: str, spell_level: int, duration_rounds: Optional[int]=None)` - Start concentration on a spell for a character.
- `update_concentration_duration(self, character_id: str, rounds_passed: int=1)` - Update concentration duration during combat.
- `get_concentration_system(db_path: str='talekeeper.db')` - Factory function to get concentration system instance.

## core - `services/condition_manager.py`

- `from_dict(cls, data: Dict[str, Any])` - Create from dictionary.
- `to_dict(self)` - Convert to dictionary for database storage.
- `get_effects(cls, condition_type: ConditionType)` - Get the mechanical effects of a condition.
- `is_incapacitating(cls, condition_type: ConditionType)` - Check if a condition is incapacitating.
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_add_exhaustion_level(self, character_id: str, levels: int=1, source: str='effect')` - Add exhaustion levels (special stacking condition).
- `_ensure_tables(self)` - Create condition tables if they don't exist.
- `_get_log_effects_summary(self, condition: ActiveCondition)` - Get a brief summary of condition effects for logging.
- `_log_condition_change(self, character_id: str, action: str, condition: ActiveCondition, reason: str=None)` - Log condition changes to the UI.
- `_reduce_exhaustion_level(self, character_id: str, levels: int=1, reason: str='long_rest')` - Reduce exhaustion levels.
- `_update_duration(self, character_id: str, condition_type: ConditionType, new_duration: int)` - Update the duration of a condition.
- `add_condition(self, character_id: str, condition: ActiveCondition)` - Add a condition to a character.
- `add_immunity(self, character_id: str, condition_type: ConditionType, source: str='feature', duration: str='permanent')` - Add immunity to a condition.
- `clear_all_conditions(self, character_id: str, reason: str='effect')` - Remove all conditions from a character (e.g., Greater Restoration).
- `get_active_conditions(self, character_id: str)` - Get all active conditions on a character.
- `get_condition(self, character_id: str, condition_type: ConditionType)` - Get a specific condition on a character.
- `get_condition_summary(self, character_id: str)` - Get a readable summary of active conditions.
- `get_exhaustion_level(self, character_id: str)` - Get current exhaustion level (0-6).
- `has_condition(self, character_id: str, condition_type: ConditionType)` - Check if a character has a specific condition.
- `has_incapacitating_condition(self, character_id: str)` - Check if character has any incapacitating condition (for Danger Sense).
- `is_immune_to_condition(self, character_id: str, condition_type: ConditionType)` - Check if character is immune to a condition.
- `process_turn_end(self, character_id: str, current_round: int)` - Process condition effects at end of turn.
- `process_turn_start(self, character_id: str, current_round: int)` - Process condition effects at start of turn.
- `remove_condition(self, character_id: str, condition_type: ConditionType, reason: str='effect_ended')` - Remove a condition from a character.
- `remove_immunity(self, character_id: str, condition_type: ConditionType, source: str='feature')` - Remove immunity to a condition.
- `set_log_callback(self, callback)` - Set callback function for logging condition changes.

## core - `services/condition_stat_service.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `can_take_actions(self, character_id: str)` - Check what actions a character can take based on conditions.
- `get_ability_check_modifier(self, character_id: str, ability: str)` - Get ability check modifiers from conditions.
- `get_all_stat_modifiers(self, character_id: str, base_stats: Dict[str, Any])` - Get comprehensive stat modifications for a character.
- `get_armor_class_modifier(self, character_id: str)` - Get AC modifiers from conditions.
- `get_attack_roll_modifier(self, character_id: str, attack_type: str='any')` - Get attack roll modifiers from conditions.
- `get_character_base_speed(self, character_id: str)` - Get character's base movement speed from database.
- `get_damage_immunities(self, character_id: str)` - Get damage immunities from conditions.
- `get_damage_resistances(self, character_id: str)` - Get damage resistances from conditions.
- `get_initiative_modifier(self, character_id: str)` - Get initiative modifiers from conditions.
- `get_movement_speed_modifier(self, character_id: str, base_speed: int=None)` - Get modified movement speed based on conditions.
- `get_saving_throw_modifier(self, character_id: str, ability: str)` - Get saving throw modifiers from conditions.

## core - `services/cunning_strike_manager.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_calculate_sneak_attack_dice(self, level: int)` - Calculate sneak attack dice based on rogue level
- `_get_connection(self)` - Inferred from name: get connection.
- `_get_proficiency_bonus(self, level: int)` - Get proficiency bonus based on level
- `_is_sneak_attack_weapon(self, weapon: Dict[str, Any])` - Check if weapon is eligible for sneak attack
- `apply_cunning_strike(self, character_id: str, target_id: str, effects: List[CunningStrikeEffect], attack_damage: int)` - Apply Cunning Strike effects to target
- `calculate_save_dc(self, character_id: str)` - Calculate Cunning Strike save DC (8 + DEX mod + proficiency)
- `calculate_sneak_attack_with_cost(self, character_id: str, effects: List[CunningStrikeEffect])` - Calculate sneak attack damage after Cunning Strike costs
- `can_use_multiple_effects(self, character_id: str)` - Check if rogue can use multiple Cunning Strike effects (level 11+)
- `check_sneak_attack_eligibility(self, character_id: str, combat_context: Dict[str, Any])` - Check if Sneak Attack is eligible this attack
- `get_available_cunning_strikes(self, character_id: str)` - Get list of available Cunning Strike options for character
- `get_cunning_strike_preview(self, character_id: str, effects: List[CunningStrikeEffect])` - Get preview of Cunning Strike effects without applying
- `validate_cunning_strike_selection(self, character_id: str, effects: List[CunningStrikeEffect])` - Validate Cunning Strike effect selection

## core - `services/dice.py`

- `__init__(self, seed: Optional[int]=None)` - Initialize dice roller.
- `_roll_with_advantage(self, notation: str, advantage: bool)` - Handle advantage/disadvantage for d20 rolls
- `roll(self, notation: str, advantage: bool=False, disadvantage: bool=False)` - Roll dice using standard notation.
- `roll_exploding(self, notation: str, explode_on: Optional[List[int]]=None)` - Roll with exploding dice (roll again on max).
- `roll_hit_points(self, hit_die: int, con_modifier: int, level: int)` - Roll hit points for leveling up.
- `roll_initiative(self, dex_modifier: int, bonus: int=0)` - Roll initiative for combat.
- `roll_multiple(self, notation: str, count: int)` - Roll the same dice notation multiple times.
- `roll_on_table(self, table: List[Tuple[int, any]])` - Roll on a weighted table.
- `roll_percentile(self)` - Roll d100 (percentile dice)
- `roll_stats(self, method: str='standard')` - Roll ability scores for character creation.
- `roll_with_reroll(self, notation: str, reroll_on: List[int], max_rerolls: int=1)` - Roll with reroll mechanic.
- `attack_roll(bonus: int, advantage: bool=False, disadvantage: bool=False)` - Make an attack roll.
- `d20(modifier: int=0, advantage: bool=False, disadvantage: bool=False)` - Quick d20 roll with modifier
- `saving_throw(ability_mod: int, proficiency: int=0, advantage: bool=False)` - Make a saving throw
- `skill_check(ability_mod: int, proficiency: int=0, expertise: bool=False, advantage: bool=False)` - Make a skill check

## core - `services/dynamic_action_service.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_add_basic_actions(self, action_cards: Dict[str, List[Dict[str, Any]]])` - Add basic combat actions that all characters have
- `_create_action_cards(self, features: List[Dict[str, Any]], action_type: str)` - Create action cards from feature data
- `_customize_action_surge_card(self, feature: Dict[str, Any])` - Customize the Action Surge card
- `_customize_cunning_action_card(self, feature: Dict[str, Any])` - Customize the Cunning Action card
- `_customize_rage_card(self, feature: Dict[str, Any])` - Customize the rage action card with specific mechanics
- `_customize_second_wind_card(self, feature: Dict[str, Any])` - Customize the Second Wind card
- `_generate_tooltip(self, feature: Dict[str, Any])` - Generate a tooltip for the feature
- `_is_feature_available(self, feature: Dict[str, Any])` - Check if a feature is currently available for use
- `get_action_cards(self, character_id: str)` - Get all action cards for a character organized by action type
- `get_spellcasting_actions(self, character_id: str, class_id: str)` - Get spellcasting-related action cards

## core - `services/dynamic_feature_manager.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_calculate_feature_uses(self, mechanics: Dict[str, Any], level: int)` - Calculate max uses and recharge type based on feature mechanics
- `_character_has_feature(self, cursor, character_id: str, feature_name: str, source: str)` - Check if character already has this feature
- `_check_prerequisites(self, cursor, character_id: str, prerequisites: Dict[str, Any])` - Check if character meets prerequisites for a feature
- `_insert_character_feature(self, cursor, feature: FeatureInstance)` - Insert a character feature into the database
- `configure_feature(self, character_id: str, feature_name: str, configuration: Dict[str, Any])` - Update feature configuration (e.g., chosen fighting style, expertise skills)
- `get_character_features(self, character_id: str, active_only: bool=True)` - Get all features for a character
- `get_feature_progression_summary(self, class_id: str, subclass_id: Optional[str]=None)` - Get a summary of features by level for a class/subclass
- `grant_class_features_for_level(self, character_id: str, class_id: str, level: int)` - Grant all class features for a specific level
- `grant_subclass_features_for_level(self, character_id: str, subclass_id: str, level: int)` - Grant all subclass features for a specific level
- `recharge_features(self, character_id: str, recharge_type: str)` - Recharge features that use the specified recharge type
- `update_feature_uses(self, character_id: str, feature_name: str, current_uses: int)` - Update the current uses of a feature

## core - `services/encounter_avoidance.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_award_xp(self, character_id: str, xp_amount: int)` - Award XP to character.
- `_calculate_avoidance_xp(self, monsters: List[Dict])` - Calculate XP reward for avoiding encounter.
- `_get_xp_thresholds(self, level: int)` - Get XP thresholds for encounter difficulty by character level.
- `attempt_avoidance(self, character_id: str, character_data: Dict, monsters: List[Dict])` - Attempt to avoid an encounter using Stealth.
- `can_attempt_avoidance(self, character_id: str, monsters: List[Dict])` - Check if character can attempt to avoid this encounter.
- `get_encounter_difficulty(self, monsters: List[Dict], character_level: int)` - Estimate encounter difficulty for avoidance context.

## core - `services/enhanced_subclass_manager.py`

- `create()` - Create the Berserker subclass definition.
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_ensure_tables(self)` - Create enhanced subclass tables if needed.
- `apply_mindless_rage(self, character_id: str)` - Apply Mindless Rage immunity when raging.
- `check_frenzy_trigger(self, character_id: str)` - Check if Frenzy damage should be applied.
- `get_character_subclass_features(self, character_id: str, level: int)` - Get all subclass features available to a character at their level.
- `get_subclass_definition(self, class_name: str, subclass_name: str)` - Get a subclass definition using the registry.
- `remove_rage_immunities(self, character_id: str)` - Remove Mindless Rage immunities when rage ends.
- `reset_resources(self, character_id: str, rest_type: str)` - Reset subclass resources on rest.
- `use_intimidating_presence(self, character_id: str)` - Use Intimidating Presence ability.
- `get_features_at_level(self, level: int)` - Get all features available at a specific level.
- `get_features_by_type(self, feature_type: FeatureType)` - Get all features of a specific type.
- `from_dict(cls, data: Dict[str, Any])` - Create from dictionary.
- `to_dict(self)` - Convert to dictionary for storage.

## core - `services/equipment.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `get_armor_ac(self, armor_name: str, dex_modifier: int)` - Calculate AC for armor based on database properties and character's dex.
- `get_item(self, item_name: str)` - Get equipment item data by name from database.
- `get_items_by_type(self, item_type: str)` - Get all items of a specific type (weapon, armor, etc.).
- `get_shield_ac_bonus(self, shield_name: str)` - Get AC bonus from shield. Shields typically give +2 AC.
- `get_weapon_properties(self, weapon_name: str)` - Get weapon properties for damage calculations.
- `is_armor(self, item_name: str)` - Check if item is armor.
- `is_shield(self, item_name: str)` - Check if item is a shield.
- `is_weapon(self, item_name: str)` - Check if item is a weapon.

## core - `services/equipment_database.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_fetch_base_weapon(self, conn: sqlite3.Connection, base_name: str)` - Inferred from name: fetch base weapon.
- `_hydrate_weapon_defaults(self, conn: sqlite3.Connection, item: Dict[str, Any])` - Inferred from name: hydrate weapon defaults.
- `_infer_base_weapon_name(self, name: str)` - Infer the non-magical base weapon name from a variant.
- `get_all_equipment(self)` - Get all equipment from the database.
- `get_equipment_by_name(self, name: str)` - Get a specific equipment item by name.
- `get_equipment_by_rarity(self, rarities: List[str])` - Get equipment filtered by rarity.
- `get_equipment_lookup(self)` - Get all equipment as a lookup dictionary by name.
- `get_weapons(self)` - Get all weapons from the database.

## core - `services/feat_effects.py`

- `__init__(self, feats_file_path: str=None)` - Initialize with feat data.
- `_apply_ability_score_effect(self, character_data: Dict, effect: FeatEffect)` - Apply ability score bonuses from feats.
- `_apply_combat_effect(self, character_data: Dict, effect: FeatEffect)` - Apply combat-related effects from feats.
- `_apply_hit_point_effect(self, character_data: Dict, effect: FeatEffect)` - Apply hit point bonuses from feats.
- `_apply_proficiency_effect(self, character_data: Dict, effect: FeatEffect)` - Apply proficiency bonuses from feats.
- `_apply_resource_effect(self, character_data: Dict, effect: FeatEffect)` - Apply resource-based effects from feats.
- `_get_ability_score_effects(self, feat_data: Dict)` - Check if feat provides ability score improvements.
- `_get_combat_effects(self, feat_data: Dict)` - Check if feat provides combat-related effects.
- `_get_hit_point_effect(self, feat_data: Dict)` - Check if feat provides hit point bonuses.
- `_get_proficiency_effects(self, feat_data: Dict)` - Check if feat provides proficiency bonuses.
- `_get_spell_effects(self, feat_data: Dict)` - Check if feat provides additional spells.
- `_load_feats_data(self, feats_file_path: str=None)` - Load feat data from database.
- `apply_feat_effects_to_character(self, character_data: Dict, feat_names: List[str])` - Apply all feat effects to a character's data.
- `get_feat_effects(self, feat_name: str)` - Get all mechanical effects for a given feat.

## core - `services/feature_registry.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_get_class_feature_details(self, feature_id: int)` - Get detailed information about a class feature
- `_get_subclass_feature_details(self, feature_id: int)` - Get detailed information about a subclass feature
- `get_all_class_features(self, class_id: str, max_level: int=20)` - Get all class features up to max_level, organized by level
- `get_available_subclasses(self, class_id: str)` - Get available subclasses for a class
- `get_character_features(self, character_id: str)` - Get all active features for a character
- `get_class_features_for_level(self, class_id: str, level: int)` - Get all class features available at a specific level
- `get_features_by_type(self, character_id: str, feature_type: str)` - Get character features filtered by type (action, bonus_action, reaction, etc.)
- `get_subclass_features_for_level(self, subclass_id: str, level: int)` - Get all subclass features available at a specific level
- `get_subclass_selection_level(self, class_id: str)` - Get the level at which a class selects its subclass
- `grant_feature_to_character(self, character_id: str, feature_source: str, feature_id: int, feature_name: str, level_gained: int, max_uses: int=0, recharge_type: str='permanent', configuration: Dict[str, Any]=None)` - Grant a feature to a character
- `recharge_features(self, character_id: str, recharge_type: str)` - Recharge features based on rest type
- `update_feature_uses(self, character_id: str, feature_name: str, uses_spent: int)` - Update the current uses of a feature

## core - `services/fighter_abilities.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_apply_heroic_warrior(self, cursor: sqlite3.Cursor, character_id: str, character: Dict[str, Any], level: int)` - Internal helper to handle Heroic Warrior start-of-turn logic.
- `_apply_survivor(self, cursor: sqlite3.Cursor, character_id: str, character: Dict[str, Any], level: int)` - Internal helper to handle Survivor start-of-turn logic.
- `_dedupe(items)` - Inferred from name: dedupe.
- `_ensure_combat_state(self, cursor: sqlite3.Cursor, character_id: str)` - Ensure a combat state row exists for the character.
- `_get_connection(self)` - Get database connection.
- `check_heroic_warrior(self, character_id: str)` - Public wrapper to process Heroic Warrior start-of-turn effect.
- `check_survivor(self, character_id: str)` - Public wrapper to process Survivor start-of-turn effect.
- `get_character_subclass(self, character_id: str)` - Get the fighter subclass for a character.
- `get_fighter_level(self, character_id: str)` - Get the fighter class level for a character.
- `get_remarkable_athlete_jump_bonus(self, character_id: str)` - Get jump distance bonus from Remarkable Athlete.
- `has_defy_death(self, character_id: str)` - Check if character has Defy Death (Champion 18).
- `has_remarkable_athlete(self, character_id: str)` - Return True if the character qualifies for Remarkable Athlete.
- `has_studied_attacks_advantage(self, character_id: str, target_id: str)` - Check if character has advantage from Studied Attacks.
- `process_champion_turn_start(self, character_id: str)` - Apply Champion subclass start-of-turn effects and return outcome details.
- `rest_fighter_resources(self, character_id: str, rest_type: str)` - Reset fighter resources on rest.
- `roll_death_save(self, character_id: str)` - Roll a death saving throw with Defy Death if available.
- `roll_skill_check(self, character_id: str, skill_name: str, ability_modifier: int, proficiency_bonus: int=0, proficient: bool=False, expertise: bool=False, base_context: Optional[Dict[str, Any]]=None)` - Roll a skill check with automatic Remarkable Athlete integration.
- `update_fighter_resources_for_level(self, character_id: str, level: int)` - Update fighter resource maximums based on level.
- `update_studied_attacks(self, character_id: str, target_id: str, hit: bool)` - Update Studied Attacks state after an attack.
- `use_action_surge(self, character_id: str)` - Use Action Surge ability.
- `use_indomitable(self, character_id: str, save_roll: int, save_bonus: int)` - Use Indomitable to reroll a failed save.
- `use_second_wind(self, character_id: str)` - Use Second Wind ability.
- `use_tactical_mind(self, character_id: str, check_result: int, dc: int)` - Use Tactical Mind to boost an ability check.

## core - `services/hazard_service.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `apply_gear_bonus(self, hazard: Dict[str, Any], gear_items: List[str])` - Inferred from name: apply gear bonus.
- `get_hazard_by_id(self, hazard_id: int)` - Inferred from name: get hazard by id.
- `get_hazards_for_level(self, character_level: int)` - Inferred from name: get hazards for level.
- `get_random_hazard(self, character_level: int)` - Inferred from name: get random hazard.

## core - `services/item_effects.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_ensure_tables(self)` - Ensure magical bonuses table exists.
- `_get_attuned_items(self, character_id: str)` - Get set of attuned item keys for character.
- `_get_item_bonuses(self, item: Dict, is_attuned: bool=False)` - Extract magical bonuses from an item.
- `_get_item_key(self, item: Dict)` - Generate unique key for item for attunement tracking.
- `_requires_attunement(self, item_name: str)` - Check if item requires attunement by querying database.
- `_save_bonuses_to_database(self, character_id: str, bonuses: Dict[str, int])` - Save calculated bonuses to database.
- `calculate_bonuses_for_character(self, character_id: str, equipped_items: Dict)` - Calculate magical bonuses from all equipped items for a character.
- `get_character_bonuses(self, character_id: str)` - Get saved bonuses for a character from database.
- `set_attunement(self, character_id: str, item_key: str, attune: bool)` - Set or remove attunement for an item.

## core - `services/level_up.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_feat_hp_bonus(self, cursor, character_id: str)` - Get HP bonus per level from feats.
- `_get_hit_die_for_class(self, class_name: str)` - Get hit die size for class.
- `_get_species_hp_bonus(self, cursor, character_id: str)` - Get HP bonus per level from species traits.
- `_grant_class_features(self, cursor, character_id: str, class_name: str, class_level: int)` - Grant class features for the new level.
- `_grant_fighter_features(self, cursor, character_id: str, level: int)` - Grant Fighter-specific features.
- `_grant_rogue_features(self, cursor, character_id: str, level: int)` - Grant Rogue-specific features.
- `get_available_classes(self)` - Get list of available classes for leveling.
- `get_character_class_levels(self, character_id: str)` - Get current class levels for a character.
- `get_next_level_features(self, character_id: str, class_choice: str)` - Get features that would be gained at next level in chosen class.
- `is_asi_level(self, character_id: str, class_choice: str)` - Check if next level grants ASI for the selected class.
- `level_up_character(self, character_id: str, class_choice: str, subclass_choice: Optional[str]=None)` - Level up character in chosen class.
- `recalculate_character_hp(self, character_id: str)` - Recalculate a character's HP to include species and feat bonuses that may be missing.

## core - `services/level_up_integration.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_handle_class_specific_updates(self, cursor, character_id: str, class_id: str, level: int)` - Handle class-specific level up effects (HP, spell slots, etc.)
- `_update_barbarian_progression(self, cursor, character_id: str, level: int)` - Update barbarian-specific progression
- `_update_fighter_progression(self, cursor, character_id: str, level: int)` - Update fighter-specific progression
- `_update_rogue_progression(self, cursor, character_id: str, level: int)` - Update rogue-specific progression
- `_update_spellcaster_progression(self, cursor, character_id: str, class_id: str, level: int)` - Update spell slot progression for spellcasters
- `get_features_for_level(self, class_id: str, level: int, subclass_id: str=None)` - Get list of features that would be granted at a specific level
- `get_level_up_preview(self, character_id: str, target_level: int)` - Preview what features would be gained at target level
- `handle_level_up(self, character_id: str, new_level: int)` - Handle level up using dynamic feature system
- `is_subclass_selection_level(self, class_id: str, level: int)` - Check if this level requires subclass selection
- `migrate_character_to_dynamic_system(self, character_id: str)` - Migrate an existing character to use the dynamic feature system

## core - `services/loot_drop_service.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_equipment_by_name(self, item_name: str)` - Inferred from name: get equipment by name.
- `cr_to_rarity(self, cr_numeric: float)` - Inferred from name: cr to rarity.
- `drop_loot(self, character_id: str, character_data: dict, rarity: str)` - Inferred from name: drop loot.
- `get_bis_items_for_rarity(self, class_build: str, rarity: str)` - Inferred from name: get bis items for rarity.
- `get_character_build(self, character_data: dict)` - Inferred from name: get character build.
- `get_other_items_for_rarity(self, rarity: str, owned_items: Set[str])` - Inferred from name: get other items for rarity.
- `get_player_inventory(self, character_id: str)` - Inferred from name: get player inventory.

## core - `services/monster_attack_parser.py`

- `_determine_attack_type(self, text: str)` - Determine if attack is melee, ranged, or special.
- `_entries_to_text(self, entries: List[Any])` - Convert entries list to plain text.
- `_extract_additional_damage(self, text: str)` - Extract additional damage (like poison) beyond primary damage.
- `_extract_attack_bonus(self, text: str)` - Extract attack bonus from text.
- `_extract_automatic_conditions(self, text: str, attack_name: str)` - Extract conditions applied automatically on hit (no save required).
- `_extract_conditional_effects(self, text: str, attack_name: str)` - Extract effects with special triggers.
- `_extract_effects(self, text: str, attack_name: str)` - Extract special effects from attack text.
- `_extract_primary_damage(self, text: str)` - Extract primary damage dice and type.
- `_extract_range(self, text: str)` - Extract normal/long range for ranged attacks.
- `_extract_reach(self, text: str)` - Extract reach in feet.
- `_extract_save_effects(self, text: str, attack_name: str)` - Extract effects that require saving throws.
- `_is_attack_action(self, action: Dict[str, Any])` - Check if an action represents an attack.
- `_parse_attack_action(self, action: Dict[str, Any])` - Parse a single attack action into structured data.
- `get_attack_summary(self, attack: ParsedAttack)` - Get a human-readable summary of the attack.
- `parse_monster_actions(self, actions_json: str)` - Parse monster actions from database JSON.
- `__post_init__(self)` - Inferred from name: post init.

## core - `services/monster_attack_processor.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_calculate_average_damage(self, dice_expr: str)` - Calculate average damage from dice expression.
- `_extract_attack_bonus(self, text: str)` - Extract attack bonus from attack text.
- `_extract_automatic_conditions(self, text: str)` - Extract conditions applied automatically on hit.
- `_extract_condition_effects(self, text: str, attack_name: str)` - Extract conditions that require saving throws.
- `_extract_damage(self, text: str)` - Extract damage dice, type, and average from attack text.
- `_extract_effects(self, text: str, attack_name: str)` - Extract special effects from attack text.
- `_extract_poison_effects(self, text: str)` - Extract poison damage with potential condition effects.
- `_extract_reach(self, text: str)` - Extract reach from attack text.
- `_is_attack_action(self, action: Dict[str, Any])` - Check if an action is an attack.
- `_map_condition_name(self, condition_name: str)` - Map condition name strings to ConditionType enum.
- `_parse_attack_action(self, action: Dict[str, Any])` - Parse a single attack action.
- `_process_condition_effect(self, effect: AttackEffect, character_id: str, result: Dict[str, Any])` - Process a condition effect from an attack.
- `apply_saving_throw_result(self, character_id: str, save_data: Dict[str, Any], roll_result: int, success: bool)` - Apply the result of a saving throw.
- `execute_monster_attack(self, attack: MonsterAttack, target_character_id: str, attack_roll: int, target_ac: int)` - Execute a monster attack against a character.
- `parse_monster_actions(self, actions_json: str)` - Parse monster actions from database JSON into structured attacks.

## core - `services/paladin_abilities.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_add_oath_spells(self, cursor, character_id: str, oath: str, level: int)` - Add oath spells that are always prepared.
- `_apply_oath_features(self, cursor, character_id: str, oath: str, level: int)` - Apply oath features based on character level.
- `_get_spell_level(self, spell_id: str)` - Get spell level from spell registry.
- `_initialize_core_features(self, cursor, character_id: str, level: int)` - Initialize core paladin features.
- `divine_smite(self, character_id: str, spell_slot_level: int, target_is_undead_or_fiend: bool=False, use_free_smite: bool=False)` - Calculate Divine Smite damage.
- `get_paladin_info(self, character_id: str)` - Get comprehensive paladin information.
- `has_free_divine_smite(self, character_id: str)` - Check if the paladin has their free Divine Smite available.
- `initialize_paladin_character(self, character_id: str, oath: str='devotion')` - Initialize a character as a Paladin with the specified sacred oath.
- `long_rest_recovery(self, character_id: str)` - Handle long rest recovery for paladins.
- `use_channel_divinity(self, character_id: str, ability_name: str)` - Use Channel Divinity.
- `use_lay_on_hands(self, character_id: str, healing_points: int)` - Use Lay on Hands to heal.
- `get_paladin_service(db_path: str='talekeeper.db')` - Get singleton paladin service instance.

## core - `services/parlay_system.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_character_level(self, character_id: str)` - Get character level from database.
- `apply_parlay_success(self, character_id: str, xp_reward: int)` - Apply the rewards for successful parlay.
- `calculate_parlay_xp_reward(self, monsters: List[Dict])` - Calculate XP reward for successful parlay.
- `can_parlay_with_encounter(self, monsters: List[Dict])` - Check if an encounter can be parlayed with.
- `can_parlay_with_monster(self, monster: Dict)` - Determine if a monster can be parlayed with.
- `create_parlay_challenge(self, character_id: str, monsters: List[Dict])` - Create a skill challenge for parlay attempt.
- `get_parlay_skills(self)` - Get the skills available for parlay.

## core - `services/proficiency_bonus.py`

- `get_proficiency_bonus(character_level: int)` - Get proficiency bonus based on character level.
- `get_proficiency_bonus_from_character(character: dict)` - Get proficiency bonus from character dict.
- `get_proficiency_bonus_from_context(context: dict)` - Get proficiency bonus from character context.

## core - `services/proficiency_system.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_connection(self)` - Inferred from name: get connection.
- `_get_skill_expertise(self, cursor, character_id: str)` - Inferred from name: get skill expertise.
- `_normalize_skill_name(self, skill: Any)` - Inferred from name: normalize skill name.
- `_parse_skill_list(self, raw: Any)` - Inferred from name: parse skill list.
- `add_feat_proficiencies(self, character_id: str, feat_name: str, selected_proficiencies: List[str]=None, conn=None)` - Add proficiencies from a feat (like Skilled).
- `add_proficiency(self, character_id: str, prof_type: str, prof_name: str, source: str='manual', conn=None)` - Inferred from name: add proficiency.
- `calculate_skill_bonus(self, character_id: str, skill_name: str, ability_mod: int)` - Inferred from name: calculate skill bonus.
- `get_attack_bonus(self, character_id: str, weapon_name: str, ability_mod: int)` - Inferred from name: get attack bonus.
- `get_background_proficiencies(self, background_id: str)` - Get fixed proficiencies from a background.
- `get_character_proficiencies(self, character_id: str)` - Inferred from name: get character proficiencies.
- `get_class_skill_choices(self, class_id: str)` - Get skill selection options for a class.
- `get_saving_throw_bonus(self, character_id: str, ability: str)` - Inferred from name: get saving throw bonus.
- `get_species_proficiencies(self, species_id: str)` - Get proficiencies and choices from a species.
- `initialize_character_proficiencies(self, character_id: str, class_id: str, background: Optional[str]=None, race_id: Optional[str]=None, selected_skills: List[str]=None, selected_class_skills: List[str]=None, selected_species_skills: List[str]=None, conn=None)` - Inferred from name: initialize character proficiencies.
- `is_proficient_in_skill(self, character_id: str, skill_name: str)` - Inferred from name: is proficient in skill.
- `is_proficient_with_armor(self, character_id: str, armor_name: str)` - Inferred from name: is proficient with armor.
- `is_proficient_with_shield(self, character_id: str)` - Inferred from name: is proficient with shield.
- `is_proficient_with_weapon(self, character_id: str, weapon_name: str)` - Inferred from name: is proficient with weapon.
- `remove_proficiency(self, character_id: str, prof_type: str, prof_name: str)` - Inferred from name: remove proficiency.

## core - `services/ritual_casting_service.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_apply_ritual_spell_effects(self, cursor, character_id: str, spell_id: str, target_data: Dict[str, Any])` - Apply the effects of a ritual spell.
- `_calculate_ritual_casting_time(self, normal_casting_time: str)` - Calculate ritual casting time (normal + 10 minutes).
- `_character_has_ritual_casting(self, cursor, character_id: str)` - Check if character has ritual casting ability from any class.
- `_character_has_spell(self, cursor, character_id: str, spell_id: str)` - Check if character knows or has prepared the spell.
- `_log_ritual_casting(self, cursor, character_id: str, spell_id: str, casting_time: str)` - Log ritual spell casting for tracking.
- `can_cast_as_ritual(self, character_id: str, spell_id: str)` - Check if a character can cast a specific spell as a ritual.
- `cast_ritual_spell(self, character_id: str, spell_id: str, target_data: Dict[str, Any]=None)` - Cast a spell as a ritual (no spell slot consumed).
- `get_ritual_casting_log(self, character_id: str, limit: int=10)` - Get recent ritual casting history for a character.
- `get_ritual_spells_for_character(self, character_id: str)` - Get all ritual spells available to a character.
- `get_ritual_casting_service(db_path: str='talekeeper.db')` - Factory function to get ritual casting service instance.

## core - `services/rogue_abilities.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_calculate_sneak_attack_dice(self, level: int)` - Calculate sneak attack dice based on level.
- `_check_ally_within_5_feet(self, character_id: str, target_id: str, attack_context: Dict[str, Any])` - Check if an ally is within 5 feet of the target.
- `_get_connection(self)` - Get database connection.
- `_is_ally_incapacitated(self, ally_id: str)` - Check if an ally is incapacitated.
- `_is_character_incapacitated(self, character_id: str)` - Check if character is incapacitated.
- `_is_proficient_in_skill(self, character_id: str, skill_name: str)` - Check if character is proficient in a skill.
- `_is_sneak_attack_weapon(self, weapon: Dict[str, Any])` - Check if weapon is eligible for sneak attack (finesse or ranged).
- `apply_evasion(self, character_id: str, save_result: Dict[str, Any])` - Apply Evasion to a Dexterity saving throw.
- `apply_reliable_talent(self, character_id: str, skill_roll: int, skill_name: str)` - Apply Reliable Talent to a skill check.
- `calculate_sneak_attack_damage(self, character_id: str)` - Get sneak attack damage dice string for character.
- `check_sneak_attack_eligibility(self, character_id: str, target_id: str, attack_context: Dict[str, Any])` - Check if sneak attack is eligible for this attack.
- `get_character_subclass(self, character_id: str)` - Get character's subclass.
- `get_rogue_features(self, character_id: str)` - Get all rogue features for a character.
- `get_rogue_level(self, character_id: str)` - Get the rogue class level for a character.
- `rest_rogue_resources(self, character_id: str, rest_type: str)` - Reset rogue resources after a rest.
- `update_rogue_resources_for_level(self, character_id: str, level: int)` - Update rogue resource maximums based on level.
- `use_cunning_action(self, character_id: str, action_type: str)` - Use Cunning Action (Dash, Disengage, or Hide as bonus action).
- `use_steady_aim(self, character_id: str)` - Use Steady Aim to gain advantage on next attack.
- `use_stroke_of_luck(self, character_id: str, original_roll: int)` - Use Stroke of Luck to turn a failed d20 test into a 20.
- `use_uncanny_dodge(self, character_id: str, incoming_damage: int)` - Use Uncanny Dodge to halve incoming damage.

## core - `services/skill_challenge_manager.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_session_by_id(self, session_id: str)` - Get session by ID.
- `_get_skill_modifiers(self, skill_name: str, character_data: dict)` - Get ability modifier and proficiency bonus for a skill.
- `_save_attempt(self, session_id: str, skill_name: str, ability_modifier: int, proficiency_bonus: int, dc: int, roll_result: int, total_result: int, success: bool)` - Save skill attempt to database.
- `_update_session(self, session: SkillChallengeSession, outcome: Optional[str]=None)` - Update session in database.
- `attempt_skill(self, session_id: str, skill_name: str, character_data: dict)` - Attempt a skill check in the challenge.
- `create_session(self, character_id: str, template: SkillChallengeTemplate)` - Create a new skill challenge session.
- `get_active_session(self, character_id: str)` - Get the active skill challenge session for a character.
- `get_all_templates(self)` - Load all skill challenge templates from database.
- `get_challenge_info_text(self, session: SkillChallengeSession)` - Generate challenge information text for display.
- `get_skill_dc(self, session: SkillChallengeSession, skill_name: str)` - Calculate the DC for a skill based on usage count.
- `get_template_by_id(self, template_id: str)` - Get a specific template by ID.
- `refuse_challenge(self, session_id: str)` - Refuse the challenge and return the refuse outcome.

## core - `services/skill_challenge_rewards.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_add_item_to_inventory(self, character_id: str, item_name: str, item_type: str, quantity: int, weight_lb: float, description: str, value_gp: float)` - Add an item to character inventory, stacking if it already exists.
- `_apply_coin_loss(self, character_data: Dict)` - Apply coin loss.
- `_apply_coin_reward(self, character_data: Dict)` - Apply coin reward based on character level.
- `_apply_consumable_reward(self, character_data: Dict)` - Apply consumable item reward.
- `_apply_damage(self, character_data: Dict, damage_desc: str)` - Apply damage to character.
- `_apply_exhaustion(self, character_data: Dict)` - Apply exhaustion condition.
- `_apply_exploration_view(self, character_data: Dict, reward: str)` - Apply exploration view benefit.
- `_apply_forced_encounter(self, character_data: Dict, encounter_desc: str)` - Apply forced encounter effect.
- `_apply_healers_kit(self, character_data: Dict)` - Apply healer's kit to inventory.
- `_apply_healing_potion(self, character_data: Dict)` - Apply healing potion to inventory.
- `_apply_inspiration(self, character_data: Dict)` - Apply inspiration reward.
- `_apply_item_reward(self, character_data: Dict)` - Apply random item reward from equipment database.
- `_apply_poison_condition(self, character_data: Dict)` - Apply poisoned condition.
- `_apply_quest_modifier(self, character_data: Dict, modifier: str)` - Apply quest difficulty modifier.
- `_apply_rations_gain(self, character_data: Dict)` - Apply ration gain (food/water supplies).
- `_apply_rations_loss(self, character_data: Dict)` - Apply ration loss.
- `_apply_reputation_gain(self, character_data: Dict, reward: str)` - Apply reputation gain.
- `_apply_reputation_loss(self, character_data: Dict)` - Apply reputation loss.
- `_apply_rest(self, character_data: Dict)` - Apply long rest benefits.
- `_apply_vendor_modifier(self, character_data: Dict, modifier: str)` - Apply vendor price modifier.
- `_get_dangerous_trap_damage(self, level: int)` - Get dangerous trap damage based on character level using existing trap system.
- `_roll_damage_dice(self, dice_formula: str)` - Roll damage dice from a formula like '2d10' or '4d10'.
- `apply_penalty(self, character_data: Dict, penalty: str)` - Apply a failure penalty to the character. Returns updated character data and log messages.
- `apply_refuse_cost(self, character_data: Dict, cost: str)` - Apply the cost of refusing a challenge. Returns updated character data and log messages.
- `apply_reward(self, character_data: Dict, reward: str)` - Apply a success reward to the character. Returns updated character data and log messages.
- `log_reward_application(self, character_id: str, reward_type: str, description: str, details: str='')` - Log reward/penalty application to database for tracking.
- `save_character_data(self, character_data: Dict)` - Save updated character data to database.

## core - `services/spell_registry.py`

- `__post_init__(self)` - Inferred from name: post init.
- `from_dict(cls, data: Dict[str, Any])` - Create from dictionary.
- `is_available_to_class(self, class_name: str)` - Check if this spell is available to a specific class.
- `to_dict(self)` - Convert to dictionary for storage.
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `add_spell(self, spell: SpellDefinition)` - Add a new spell to the registry.
- `clear_cache(self)` - Clear all cached spell data.
- `get_available_classes(self)` - Get all classes that have spells defined.
- `get_ritual_spells(self, class_name: Optional[str]=None)` - Get all ritual spells, optionally filtered by class.
- `get_spell(self, spell_id: str)` - Get a spell definition by ID.
- `get_spell_count_by_class(self, class_name: str)` - Get count of spells by level for a class.
- `get_spells_by_class(self, class_name: str, level: Optional[int]=None)` - Get all spells available to a specific class.
- `get_spells_by_level(self, level: int)` - Get all spells of a specific level.
- `search_spells(self, name_filter: Optional[str]=None, school_filter: Optional[SpellSchool]=None, level_filter: Optional[int]=None, class_filter: Optional[str]=None, ritual_only: bool=False, concentration_only: bool=False)` - Advanced spell search with multiple filters.

## core - `services/spellcasting_service.py`

- `available_slots(self)` - Get number of available spell slots.
- `can_cast_spell(self, spell_level: int)` - Check if this slot can cast a spell of given level.
- `restore_slot(self, amount: int=1)` - Restore spell slots. Returns actual amount restored.
- `use_slot(self)` - Use one spell slot. Returns True if successful.
- `__init__(self, success: bool, spell_id: str='', reason: str='')` - Inferred from name: init.
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_ensure_spellcasting_tables(self)` - Ensure spellcasting tables exist (should be created by migration).
- `_initialize_spell_slots(self, cursor, character_id: str, class_name: str, level: int)` - Initialize spell slots for a character.
- `_parse_duration_to_rounds(self, duration: str)` - Parse spell duration to combat rounds.
- `can_cast_spell(self, character_id: str, spell_id: str, spell_level: Optional[int]=None)` - Check if a character can cast a specific spell.
- `cast_spell(self, character_id: str, spell_id: str, spell_level: Optional[int]=None, action_economy_type: Optional[ActionEconomyType]=None)` - Cast a spell, consuming appropriate resources.
- `end_concentration(self, character_id: str)` - End concentration for a character. Returns the spell that was ended.
- `get_character_spell_slots(self, character_id: str)` - Get all spell slots for a character.
- `get_character_spellcasting(self, character_id: str)` - Get a character's spellcasting information.
- `get_concentration_spell(self, character_id: str)` - Get the spell the character is concentrating on. Returns (spell_id, spell_level).
- `initialize_character_spellcasting(self, character_id: str, class_name: str)` - Initialize spellcasting for a character based on their class.
- `restore_spell_slots(self, character_id: str, rest_type: str='long')` - Restore spell slots on rest.
- `get_spellcasting_service(db_path: str='talekeeper.db')` - Get the spellcasting service singleton.

## core - `services/standardized_attack_processor.py`

- `__post_init__(self)` - Inferred from name: post init.
- `_is_attack(self, action_data: Dict[str, Any])` - Check if action data represents an attack.
- `_parse_effect(self, effect_data: Dict[str, Any])` - Parse effect data into AttackEffect object.
- `_parse_standardized_attack(self, action_data: Dict[str, Any])` - Parse standardized attack data into StandardizedAttack object.
- `get_attack_summary(self, attack: StandardizedAttack)` - Generate a human-readable summary of an attack.
- `get_effect_summary(self, effect: AttackEffect)` - Generate a human-readable summary of an effect.
- `process_monster_attacks(self, actions_json: str)` - Process monster actions JSON into standardized attack objects.
- `test_standardized_processor()` - Test the standardized processor with migrated data.

## core - `services/stealth_mechanics.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_connection(self)` - Get database connection.
- `apply_hidden_attack_bonuses(self, attack_context: Dict[str, Any])` - Apply bonuses for attacking from hidden.
- `check_encounter_stealth(self, character_id: str, character_data: Dict[str, Any], monsters: List[Dict[str, Any]])` - Check if character successfully hides at encounter start.
- `check_monster_perception(self, monster_data: Dict[str, Any], stealth_dc: int)` - Check if a monster spots the hidden character.
- `check_stealth_proficiency(self, character_id: str)` - Check if character has stealth proficiency.
- `end_hidden_state(self, character_id: str, reason: str='attacked')` - End the hidden state for a character.
- `get_stealth_modifiers(self, character_id: str)` - Get stealth roll modifiers from equipment.
- `perform_stealth_check(self, character_id: str, character_level: int)` - Perform a stealth check for encounter initialization.

## core - `services/subclass_action_integration.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_activate_heroic_warrior(self, character_id: str)` - Activate Heroic Warrior inspiration gain at turn start.
- `_activate_retaliation(self, character_id: str, feature: SubclassFeature)` - Activate Retaliation reaction.
- `_activate_survivor(self, character_id: str)` - Activate Survivor healing.
- `_get_frenzy_damage_dice(self, character_id: str)` - Get Frenzy damage dice based on character level.
- `_handle_additional_fighting_style(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Additional Fighting Style feature integration.
- `_handle_assassinate(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Assassinate feature integration.
- `_handle_assassins_tools(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Assassin's Tools feature integration.
- `_handle_death_strike(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Death Strike feature integration.
- `_handle_envenom_weapons(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Envenom Weapons feature integration.
- `_handle_fast_hands(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Fast Hands feature integration.
- `_handle_frenzy(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Frenzy feature integration.
- `_handle_heroic_warrior(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Heroic Warrior feature integration.
- `_handle_improved_critical(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Improved Critical feature integration.
- `_handle_infiltration_expertise(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Infiltration Expertise feature integration.
- `_handle_intimidating_presence(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Intimidating Presence feature integration.
- `_handle_mindless_rage(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Mindless Rage feature integration.
- `_handle_remarkable_athlete(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Remarkable Athlete feature integration.
- `_handle_retaliation(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Retaliation feature integration.
- `_handle_second_story_work(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Second-Story Work feature integration.
- `_handle_superior_critical(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Superior Critical feature integration.
- `_handle_supreme_sneak(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Supreme Sneak feature integration.
- `_handle_survivor(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Survivor feature integration.
- `_handle_thiefs_reflexes(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Thief's Reflexes feature integration.
- `_handle_use_magic_device(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Use Magic Device feature integration.
- `activate_feature(self, character_id: str, feature_name: str)` - Activate a subclass feature through the action system.
- `get_action_cards_for_character(self, character_id: str, level: int)` - Get action cards that should be created for a character's subclass features.
- `get_automatic_triggers_for_character(self, character_id: str, level: int)` - Get automatic triggers that should be set up for a character.
- `get_combat_modifiers_for_character(self, character_id: str, level: int)` - Get combat modifiers that should be applied for a character.
- `trigger_automatic_feature(self, character_id: str, trigger_type: str, context: Dict[str, Any]=None)` - Trigger automatic features based on game events.

## core - `services/subclass_feature_manager.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `get_all_subclass_features(self, subclass_id: str)` - Inferred from name: get all subclass features.
- `get_character_subclass_features(self, character_id: str)` - Inferred from name: get character subclass features.
- `get_oath_spells(self, subclass_id: str, paladin_level: int)` - Inferred from name: get oath spells.
- `get_subclass_features_for_level(self, subclass_id: str, level: int)` - Inferred from name: get subclass features for level.
- `grant_oath_spells_for_level(self, character_id: str, subclass_id: str, paladin_level: int)` - Inferred from name: grant oath spells for level.
- `grant_subclass_feature(self, character_id: str, feature_id: int, level_gained: int)` - Inferred from name: grant subclass feature.
- `recharge_features(self, character_id: str, rest_type: str)` - Inferred from name: recharge features.
- `use_feature(self, character_id: str, feature_instance_id: int)` - Inferred from name: use feature.

## core - `services/subclass_manager.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_apply_feature_mechanics(self, cursor, character_id: str, feature_name: str, mechanics_json: str)` - Apply mechanical effects of a feature.
- `_ensure_class_subclass_support(self, conn)` - Create tables and backfill data for per-class subclass tracking.
- `_grant_subclass_features(self, cursor, character_id: str, subclass_id: str, up_to_level: int)` - Grant subclass features up to specified level.
- `_run_migration(self)` - Ensure subclass tables exist.
- `apply_combat_modifiers(self, character_id: str, context: Dict[str, Any])` - Apply subclass-specific combat modifiers.
- `check_subclass_requirement(self, character_id: str)` - Check if character needs to select a subclass.
- `get_available_subclasses(self, class_id: str)` - Get all available subclasses for a class.
- `get_character_subclass(self, character_id: str, class_id: str)` - Return the subclass id for a given character/class pairing.
- `get_feature_uses(self, character_id: str, feature_name: str)` - Get current and max uses for a resource-based feature.
- `get_subclass_features(self, subclass_id: str, level: int)` - Get all features for a subclass up to specified level.
- `has_feature(self, character_id: str, feature_name: str)` - Check if character has a specific subclass feature.
- `select_subclass(self, character_id: str, subclass_id: str, class_level: Optional[int]=None)` - Assign a subclass to a character for its associated class.
- `update_features_for_class(self, character_id: str, class_id: str, class_level: int)` - Ensure subclass features are granted up to the specified class level.
- `update_features_for_level(self, character_id: str, new_level: int, class_id: Optional[str]=None)` - Update subclass features when a character gains a level.
- `use_feature(self, character_id: str, feature_name: str)` - Use a resource-based subclass feature.

## core - `services/subclass_registry.py`

- `__init__(self)` - Initialize the registry with an empty cache.
- `clear_cache(self)` - Clear the cached subclass definitions.
- `get_all_classes_with_subclasses(self)` - Get all classes that have subclasses defined.
- `get_available_subclasses(self, class_name: str)` - Get all available subclass names and descriptions for a class.
- `get_subclass(self, class_name: str, subclass_name: str)` - Get a subclass definition, loading it if necessary.
- `is_subclass_available(self, class_name: str, subclass_name: str)` - Check if a specific subclass is available.

## core - `services/subclasses/cleric/life.py`

- `create()` - Create the Life Domain subclass definition.

## core - `services/subclasses/fighter/champion.py`

- `create()` - Create the Champion subclass definition.

## core - `services/subclasses/paladin/__init__.py`

- `get_paladin_subclass(subclass_name: str)` - Get a paladin subclass definition by name.

## core - `services/subclasses/paladin/devotion.py`

- `calculate_sacred_weapon_bonus(charisma_modifier: int)` - Calculate Sacred Weapon attack bonus.
- `create()` - Create the Oath of Devotion subclass definition.
- `get_aura_range(level: int)` - Get Aura of Devotion range based on level.
- `get_channel_divinity_options(level: int)` - Get Channel Divinity options available at a given level.
- `get_oath_features(level: int)` - Get oath features available at a given level.
- `get_oath_spells(level: int)` - Get oath spells available at a given level.

## core - `services/subclasses/rogue/thief.py`

- `create()` - Create the Thief subclass definition.

## core - `services/subclasses/wizard/__init__.py`

- `get_wizard_subclass(subclass_name: str)` - Get a wizard subclass definition by name.

## core - `services/subclasses/wizard/evocation.py`

- `calculate_overchannel_damage(uses_today: int, spell_level: int)` - Calculate necrotic damage from Overchannel use.
- `create()` - Create the School of Evocation subclass definition.
- `get_school_bonus_spells()` - Get bonus spells known for School of Evocation.
- `get_tradition_features(level: int)` - Get tradition features available at a given level.

## core - `services/tarot_cards.py`

- `draw_tarot_card()` - Inferred from name: draw tarot card.
- `get_tarot_inspiration(card: Optional[Dict[str, Any]]=None)` - Inferred from name: get tarot inspiration.

## core - `services/treasure_rarity.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `get_level_bracket(self, character_level: int)` - Get the level bracket name for a character level.
- `get_rarity_for_level(self, character_level: int)` - Roll for item rarity based on character level.
- `get_rarity_for_level_and_roll(self, character_level: int, roll: int)` - Get item rarity for a specific level and roll.
- `get_rarity_probability(self, character_level: int, target_rarity: str)` - Get the probability (0.0-1.0) of getting a specific rarity at a level.
- `get_rarity_ranges_for_level(self, character_level: int)` - Get all possible rarity ranges for a given level.

## core - `services/unified_level_up.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_calculate_hp_gain(self, class_id: str, constitution: int)` - Calculate HP gain for level up
- `_get_character_data(self, cursor, character_id: str)` - Get character data from database
- `_grant_class_feature(self, cursor, character_id: str, feature: Dict[str, Any], level: int, results: Dict[str, Any])` - Grant a class feature to the character
- `_grant_subclass_feature(self, cursor, character_id: str, feature: Dict[str, Any], level: int, results: Dict[str, Any])` - Grant a subclass feature to the character
- `_has_epic_boon(self, cursor, character_id: str)` - Check if character already has an Epic Boon feat
- `apply_epic_boon(self, character_id: str, boon_name: str)` - Apply an Epic Boon feat to the character
- `apply_feature_choice(self, character_id: str, feature_instance_id: int, choice: str)` - Apply a choice for a feature (like fighting style, expertise skills)
- `apply_subclass_choice(self, character_id: str, subclass_id: str)` - Apply a subclass choice to a character
- `get_available_epic_boons(self)` - Get all available Epic Boon feats
- `level_up_character(self, character_id: str)` - Level up a character using the unified feature system

## core - `services/warlock_patrons/fiend_patron.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `dark_ones_blessing(self, character_id: str, target_cr: float=1.0)` - Apply Dark One's Blessing when a creature is reduced to 0 HP.
- `get_expanded_spells(self)` - Get the expanded spell list for Fiend patron.
- `get_patron_features(self, character_id: str)` - Get all patron features for this character.
- `initialize_patron_features(self, character_id: str, level: int)` - Initialize all Fiend patron features for the given level.
- `long_rest_recovery(self, character_id: str)` - Recover features that refresh on long rest.
- `set_fiendish_resilience(self, character_id: str, damage_type: str)` - Set the damage type for Fiendish Resilience.
- `short_rest_recovery(self, character_id: str)` - Recover features that refresh on short rest.
- `use_dark_ones_own_luck(self, character_id: str)` - Use Dark One's Own Luck ability.
- `use_hurl_through_hell(self, character_id: str, target_name: str='target')` - Use Hurl Through Hell ability.

## core - `services/warlock_patrons/patron_manager.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `get_available_patrons(self)` - Get list of available patron names.
- `get_expanded_spells(self, patron_name: str)` - Get expanded spells for a patron.
- `get_patron(self, patron_name: str)` - Get patron implementation by name.
- `get_patron_features(self, character_id: str, patron_name: str)` - Get all patron features for a character.
- `initialize_patron_features(self, character_id: str, patron_name: str, level: int)` - Initialize patron features for a character.
- `long_rest_recovery(self, character_id: str, patron_name: str)` - Handle long rest recovery for patron features.
- `short_rest_recovery(self, character_id: str, patron_name: str)` - Handle short rest recovery for patron features.
- `use_patron_feature(self, character_id: str, patron_name: str, feature_name: str, **kwargs)` - Use a specific patron feature.
- `get_patron_manager(db_path: str='talekeeper.db')` - Factory function to get a PatronManager instance.

## core - `services/warlock_patrons/sorcerer_king_patron.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `apply_intimidation_expertise(self, character_id: str)` - Apply Intimidation expertise from Tyrant's Herald.
- `enhance_command_spell(self, character_id: str, base_targets: int=1)` - Enhance Command spell with Absolute Tyranny.
- `get_expanded_spells(self)` - Get the expanded spell list for Sorcerer-King patron.
- `get_patron_features(self, character_id: str)` - Get all patron features for this character.
- `initialize_patron_features(self, character_id: str, level: int)` - Initialize all Sorcerer-King patron features for the given level.
- `long_rest_recovery(self, character_id: str)` - Recover features that refresh on long rest.
- `short_rest_recovery(self, character_id: str)` - Recover features that refresh on short rest.
- `use_decisive_edict(self, character_id: str, targets: List[Dict[str, Any]])` - Use Decisive Edict ability when casting a pact magic spell.
- `use_vindictive_rebuke(self, character_id: str, attacker_name: str='attacker')` - Use Vindictive Rebuke in response to being hit.
- `use_voice_of_tyranny(self, character_id: str)` - Use Voice of Tyranny to cast Command as bonus action.

## core - `services/warlock_service.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_apply_invocation_effects(self, character_id: str, invocation_id: str)` - Inferred from name: apply invocation effects.
- `_has_cantrip(self, character_id: str, cantrip: str)` - Inferred from name: has cantrip.
- `_knows_spell(self, character_id: str, spell_id: str)` - Inferred from name: knows spell.
- `_meets_prerequisites(self, level: int, pact_boon: str, prereqs: Dict, character_id: str)` - Inferred from name: meets prerequisites.
- `get_available_invocations(self, character_id: str)` - Inferred from name: get available invocations.
- `get_character_invocations(self, character_id: str)` - Inferred from name: get character invocations.
- `learn_invocation(self, character_id: str, invocation_id: str)` - Inferred from name: learn invocation.
- `__init__(self, db_path: str)` - Inferred from name: init.
- `_add_expanded_spells(self, character_id: str, patron: str)` - Inferred from name: add expanded spells.
- `apply_fiend_features(self, character_id: str, level: int)` - Inferred from name: apply fiend features.
- `dark_ones_blessing(self, character_id: str, creature_killed_cr: float)` - Inferred from name: dark ones blessing.
- `dark_ones_own_luck(self, character_id: str, roll_type: str)` - Inferred from name: dark ones own luck.
- `fiendish_resilience(self, character_id: str, damage_type: str)` - Inferred from name: fiendish resilience.
- `hurl_through_hell(self, character_id: str, target_id: str)` - Inferred from name: hurl through hell.
- `__init__(self, db_path: str)` - Inferred from name: init.
- `can_cast_spell_with_pact_slot(self, character_id: str, spell_level: int)` - Inferred from name: can cast spell with pact slot.
- `eldritch_master_recovery(self, character_id: str)` - Inferred from name: eldritch master recovery.
- `get_pact_slots(self, character_id: str)` - Inferred from name: get pact slots.
- `short_rest_recovery(self, character_id: str)` - Inferred from name: short rest recovery.
- `use_pact_slot(self, character_id: str)` - Inferred from name: use pact slot.
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_grant_book_of_shadows(self, character_id: str)` - Inferred from name: grant book of shadows.
- `_grant_find_familiar(self, character_id: str)` - Inferred from name: grant find familiar.
- `_grant_mystic_arcanum(self, character_id: str, level: int)` - Inferred from name: grant mystic arcanum.
- `_grant_pact_weapon(self, character_id: str)` - Inferred from name: grant pact weapon.
- `get_warlock_features(self, character_id: str)` - Inferred from name: get warlock features.
- `initialize_warlock_features(self, character_id: str, level: int=1, patron: str='Fiend')` - Inferred from name: initialize warlock features.
- `level_up_warlock(self, character_id: str, new_level: int)` - Inferred from name: level up warlock.
- `select_pact_boon(self, character_id: str, pact_boon: str)` - Inferred from name: select pact boon.

## core - `services/weapon_attack_service.py`

- `__init__(self, db_path: str)` - Initialize the weapon attack service.
- `_apply_cunning_strike_effects(self, character_id: str, effects: List[Dict[str, Any]], target: Optional[Dict[str, Any]])` - Apply Cunning Strike effects to the target with saves and conditions.
- `_apply_sneak_attack_if_eligible(self, character: Dict[str, Any], weapon: Dict[str, Any], target: Optional[Dict[str, Any]], has_advantage: bool, has_disadvantage: bool, is_hidden: bool=False)` - Apply Sneak Attack damage if the character is eligible.
- `_apply_specific_mastery(self, mastery_type: str, weapon_name: str, hit: bool, damage_total: int, character: Dict[str, Any])` - Apply specific weapon mastery effects.
- `_calculate_cunning_strike_save_dc(self, character_id: str)` - Calculate save DC for Cunning Strike effects: 8 + DEX mod + proficiency bonus.
- `_check_allies_near_target(self, character_id: str, target: Optional[Dict[str, Any]])` - Check for favorable tactical conditions for Sneak Attack in solo play.
- `_clear_cunning_strike_selection(self, character_id: str)` - Clear Cunning Strike selection after use.
- `_get_active_cunning_strike_effects(self, character_id: str)` - Get list of active Cunning Strike effects from character context.
- `_get_connection(self)` - Get a database connection.
- `_get_die_size_from_weapon(self, weapon: Dict[str, Any])` - Extract die size from weapon damage dice string.
- `_is_sneak_attack_weapon(self, weapon: Dict[str, Any])` - Check if weapon is eligible for sneak attack (finesse or ranged).
- `_mark_sneak_attack_used(self, character_id: str)` - Mark sneak attack as used this turn.
- `_no_sneak_attack(self, reason: str)` - Return a no-sneak-attack result.
- `_normalize_weapon_properties(self, weapon_props)` - Normalize weapon properties from various formats to a string.
- `_parse_damage_dice(self, damage_dice: str)` - Parse damage dice string into number of dice and die size.
- `_roll_saving_throw(self, target: Dict[str, Any], ability: str, dc: int)` - Roll a saving throw for a target.
- `_sneak_attack_used_this_turn(self, character_id: str)` - Check if sneak attack has been used this turn.
- `apply_fighting_style_effects(self, dice_rolls: List[int], fighting_styles: List[str], weapon: Dict[str, Any], character: Dict[str, Any], action_type: str='main_hand')` - Apply fighting style effects to damage dice.
- `apply_savage_attacker(self, dice_rolls: List[int], num_dice: int, die_size: int, character: Dict[str, Any], is_first_attack: bool=True)` - Apply Savage Attacker feat - reroll damage dice and use higher result.
- `apply_weapon_mastery_effects(self, weapon: Dict[str, Any], character: Dict[str, Any], target: Optional[Dict[str, Any]], hit: bool, damage_total: int=0, attack_total: int=0, chosen_mastery: Optional[str]=None)` - Apply weapon mastery effects based on the weapon's mastery property.
- `calculate_attack_damage(self, weapon: Dict[str, Any], character: Dict[str, Any], target: Optional[Dict[str, Any]]=None, is_critical: bool=False, advantage: bool=False, disadvantage: bool=False, action_type: str='main_hand', is_hidden: bool=False)` - Calculate attack roll and damage for a weapon attack.
- `can_use_tactical_master(self, character_id: str)` - Check if character can use Tactical Master (Fighter level 9+).
- `get_character_fighting_styles(self, character_id: str)` - Get all fighting styles for a character.
- `get_fighting_style_attack_bonus(self, weapon: Dict[str, Any], character: Dict[str, Any])` - Calculate attack bonuses from fighting styles.
- `get_fighting_style_damage_bonus(self, weapon: Dict[str, Any], character: Dict[str, Any], action_type: str, fighting_styles: List[str])` - Calculate flat damage bonuses from fighting styles.
- `get_weapon_mastery_effects(self, mastery_type: str, weapon_name: str, hit: bool, damage_total: int=0)` - Get the effects of a weapon mastery property.
- `has_character_unlimited_mastery(self, character_id: str)` - Check if a character has unlimited weapon mastery access.
- `update_character_mastery_resources(self, character_id: str)` - Update weapon mastery resources for a character.

## core - `services/weapon_mastery_effects.py`

- `__init__(self)` - Inferred from name: init.
- `_apply_mastery_effect(self, mastery: MasteryEffect, character_data: Dict[str, Any], target_data: Dict[str, Any], attack_roll: int, damage_roll: int)` - Apply a specific mastery effect and return the result.
- `_get_attack_ability_modifier(self, character_data: Dict[str, Any])` - Get the ability modifier used for attacks (usually Strength or Dexterity).
- `apply_on_hit_effects(self, character_data: Dict[str, Any], weapon_name: str, target_data: Dict[str, Any], attack_roll: int, damage_roll: int)` - Apply weapon mastery effects when an attack hits.
- `apply_on_miss_effects(self, character_data: Dict[str, Any], weapon_name: str, target_data: Dict[str, Any], attack_roll: int)` - Apply weapon mastery effects when an attack misses.
- `check_mastery_applicability(self, character_masteries: List[str], weapon_name: str, mastery_name: str)` - Check if a character can use a specific mastery with a weapon.
- `get_available_masteries_for_weapon(self, weapon_name: str)` - Get weapon masteries available for a specific weapon type from equipment data.

## core - `services/weapon_mastery_service.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_add_option(weapon_name: str, mastery_type: Optional[str], description: str='', equipped: bool=False)` - Inferred from name: add option.
- `_coerce_bool(value: Any)` - Coerce SQLite truthy values into a bool.
- `_get_connection(self)` - Inferred from name: get connection.
- `_normalize_mastery_key(mastery_name: str)` - Return a lowercase cache key for mastery lookups.
- `get_character_masteries(self, character_id: str)` - Return the weapon mastery assignments for a character.
- `get_character_weapon_options(self, character_id: str)` - Return mastery-bearing weapons the character currently owns or has equipped.
- `get_mastery_definition(self, mastery_name: str)` - Return the database-backed definition for a weapon mastery.
- `get_mastery_options(self)` - Return all weapons that carry a mastery property.
- `get_weapon_mastery_for_weapon(self, weapon_name: str)` - Return the default mastery for the requested weapon.
- `set_character_masteries(self, character_id: str, selections: Iterable[Dict[str, str]])` - Persist the provided mastery assignments and return normalized payload.

## core - `services/wizard_abilities.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_add_starting_spells(self, cursor, character_id: str, level: int)` - Add starting spells to wizard's spellbook.
- `_apply_tradition_features(self, cursor, character_id: str, tradition: str, level: int)` - Apply arcane tradition features based on character level.
- `_initialize_arcane_recovery(self, cursor, character_id: str, level: int)` - Initialize Arcane Recovery feature.
- `add_spell_to_spellbook(self, character_id: str, spell_id: str, source: str='level_up', cost: int=0)` - Add a spell to the wizard's spellbook.
- `get_wizard_info(self, character_id: str)` - Get comprehensive wizard information.
- `initialize_wizard_character(self, character_id: str, tradition: str='evocation')` - Initialize a character as a Wizard with the specified arcane tradition.
- `long_rest_recovery(self, character_id: str)` - Handle long rest recovery for wizards.
- `use_arcane_recovery(self, character_id: str)` - Use Arcane Recovery to regain spell slots.
- `get_wizard_service(db_path: str='talekeeper.db')` - Get singleton wizard service instance.

## core - `src/talekeeper/audio/audio_player.py`

- `__init__(self, parent: Optional[QObject]=None)` - Inferred from name: init.
- `_on_error(self, error: QMediaPlayer.Error, error_string: str)` - Handle playback errors.
- `_on_state_changed(self, state: QMediaPlayer.PlaybackState)` - Handle playback state changes.
- `_play_next(self)` - Play the next file in the queue.
- `clear_queue(self)` - Clear the playback queue.
- `enqueue(self, audio_file: Path)` - Add an audio file to the playback queue.
- `get_queue_size(self)` - Get number of items in queue.
- `get_volume(self)` - Get current volume (0.0 to 1.0).
- `is_enabled(self)` - Check if narration is enabled.
- `set_enabled(self, enabled: bool)` - Enable or disable narration playback.
- `set_volume(self, volume: float)` - Set playback volume (0.0 to 1.0).
- `stop(self)` - Stop current playback.

## core - `src/talekeeper/audio/campaign_voice_registry.py`

- `__init__(self, profiles: Optional[Iterable[CampaignVoiceProfile]]=None, default_profile: Optional[CampaignVoiceProfile]=None)` - Inferred from name: init.
- `ensure_profile(self, campaign_style: str, voice_id: str, model_path: Path)` - Create a placeholder profile if one does not exist.
- `get_active_profile(self)` - Return the profile that should be used for narration.
- `register_profile(self, profile: CampaignVoiceProfile)` - Add or replace a campaign voice profile.
- `set_active_campaign(self, campaign_style: Optional[str])` - Update the active campaign style, falling back to the default.
- `to_dict(self)` - Return a serializable snapshot useful for debugging.

## core - `src/talekeeper/audio/file_cleanup.py`

- `__init__(self, output_directory: Path, max_age_hours: int=24, max_files: Optional[int]=500)` - Inferred from name: init.
- `cleanup_excess_files(self)` - Delete oldest files if count exceeds max_files.
- `cleanup_old_files(self)` - Delete narration files older than max_age_hours.
- `run_cleanup(self)` - Run both age-based and count-based cleanup.

## core - `src/talekeeper/audio/local_tts_engine.py`

- `__init__(self, model_path: Path, config_path: Optional[Path]=None, device: str='auto')` - Inferred from name: init.
- `_find_piper(self)` - Inferred from name: find piper.
- `_verify_piper(self)` - Inferred from name: verify piper.
- `synthesize(self, text: str, output_path: Path, voice_profile: CampaignVoiceProfile, *, speaker_wav: Optional[Path]=None, style_overrides: Optional[Dict[str, float]]=None)` - Generate an audio file that narrates ``text``.

## core - `src/talekeeper/audio/log_narration_pipeline.py`

- `from_payload(cls, payload: Dict[str, object])` - Inferred from name: from payload.
- `__init__(self, log_panel, voice_registry: CampaignVoiceRegistry, *, engine_factory: Optional[Callable[[CampaignVoiceProfile], LocalTTSEngine]]=None, output_directory: Path | str=Path('excess') / 'narration', batch_window_seconds: float=2.5, auto_start: bool=True, audio_player: Optional[NarrationPlayer]=None)` - Inferred from name: init.
- `_derive_style_overrides(self, batch: List[LogNarrationEvent], profile: CampaignVoiceProfile)` - Inferred from name: derive style overrides.
- `_get_engine(self, profile: CampaignVoiceProfile)` - Inferred from name: get engine.
- `_process_loop(self)` - Inferred from name: process loop.
- `_synthesize_batch(self, batch: List[LogNarrationEvent])` - Inferred from name: synthesize batch.
- `enqueue_event(self, event: LogNarrationEvent)` - Inferred from name: enqueue event.
- `enqueue_payload(self, payload: Dict[str, object])` - Inferred from name: enqueue payload.
- `process_entries_sync(self, events: Iterable[LogNarrationEvent])` - Inferred from name: process entries sync.
- `start(self)` - Inferred from name: start.
- `stop(self)` - Inferred from name: stop.
- `update_campaign_voice(self, campaign_style: Optional[str])` - Inferred from name: update campaign voice.
- `_format_details(self, event: LogNarrationEvent)` - Inferred from name: format details.
- `format_batch(self, events: Iterable[LogNarrationEvent])` - Inferred from name: format batch.

## core - `src/talekeeper/audio/piper_voice_trainer.py`

- `__init__(self, piper_training_dir: Optional[Path]=None, language: str='en-us')` - Inferred from name: init.
- `prepare_dataset(self, samples: Iterable[VoiceTrainingSample], output_dir: Path, *, sample_rate: int=22050, copy_audio: bool=True)` - Prepare LJSpeech-format dataset for Piper training.
- `setup_training_environment(self)` - Clone and set up Piper training repository.
- `train_voice(self, dataset_dir: Path, output_dir: Path, voice_name: str, *, quality: str='medium', epochs: Optional[int]=None, batch_size: int=32, validation_split: float=0.1)` - Train a Piper voice model.
- `verify_training_environment(self)` - Check if Piper training environment is set up.
- `sanitized_transcript(self)` - Inferred from name: sanitized transcript.
- `create_sample_dataset_from_directory(audio_dir: Path, transcript_file: Optional[Path]=None)` - Helper: Create training samples from a directory of audio files.

## core - `src/talekeeper/audio/voice_profiles.py`

- `normalized_style(self)` - Inferred from name: normalized style.
- `to_dict(self)` - Serialize profile for persistence or debugging.
- `build_synthesis_kwargs(self)` - Return keyword arguments understood by the local TTS engine.

## core - `src/talekeeper/audio/voice_trainer.py`

- `__init__(self, base_model_path: Optional[Path]=None, base_config_path: Optional[Path]=None, language: str='en')` - Inferred from name: init.
- `prepare_training_workspace(self, samples: Iterable[VoiceTrainingSample], workspace: Path, *, copy_audio: bool=True)` - Create an LJSpeech-style dataset from the provided samples.
- `train_voice(self, samples: Iterable[VoiceTrainingSample], output_directory: Path, voice_profile: CampaignVoiceProfile, *, epochs: int=150, copy_audio: bool=True)` - Fine-tune a base model on the provided samples.
- `sanitized_transcript(self)` - Inferred from name: sanitized transcript.

## core - `src/talekeeper/core/class_features.py`

- `__init__(self)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Use Action Surge.
- `__init__(self)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Use Cunning Action.
- `can_use(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Can use if bonus action is available.
- `__init__(self)` - Inferred from name: init.
- `__init__(self, feature_name: str='Extra Attack', min_level: int=5)` - Inferred from name: init.
- `_get_attacks(self, character: Dict[str, Any])` - Inferred from name: get attacks.
- `__init__(self, name: str, description: str, feature_type: FeatureType, requirements: Optional[FeatureRequirement]=None)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Apply the feature's effects to the character.
- `can_use(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Check if the feature can be used.
- `meets_requirements(self, character: Dict[str, Any])` - Check if character meets feature requirements.
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_build_feature_registry(self)` - Build registry of all available features keyed by normalized names.
- `_build_fighting_style_feature(self, feature_def: Any, character_id: str, level: int)` - Inferred from name: build fighting style feature.
- `_get_fighting_style(self, character_id: str)` - Get fighting style from talekeeper.database.
- `_load_class_features(self, character_id: str, class_name: str, level: int, subclass: Optional[str])` - Load features for a specific class up to a given level.
- `_normalize_feature_name(name: str)` - Normalize feature names to registry keys.
- `apply_passive_features(self, character: Dict[str, Any])` - Apply all passive features to character stats.
- `get_available_features(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Get list of features currently available to use.
- `load_character_features(self, character_id: str)` - Load all features for a character from the database.
- `process_rest(self, rest_type: str)` - Process rest and restore appropriate resources.
- `use_feature(self, feature_name: str, character: Dict[str, Any], context: Optional[Dict]=None)` - Use a specific feature.
- `restore(self, amount: Optional[int]=None)` - Restore resource uses.
- `use(self, amount: int=1)` - Attempt to use the resource.
- `__init__(self, style: str)` - Inferred from name: init.
- `__init__(self)` - Inferred from name: init.
- `__init__(self)` - Inferred from name: init.
- `__init__(self, name: str, description: str, modifiers: Dict[str, Any], **kwargs)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Apply passive modifiers to character.
- `can_use(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Passive features are always usable if requirements are met.
- `__init__(self)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Enter or maintain rage.
- `end_rage(self)` - End the rage.
- `__init__(self)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Activate Reckless Attack.
- `can_use(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Can use on first attack of turn.
- `__init__(self)` - Inferred from name: init.
- `__init__(self, name: str, description: str, uses_by_level: Dict[int, int], recharge: ResourceRecharge=ResourceRecharge.LONG_REST, **kwargs)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Use the feature.
- `can_use(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Check if the feature can be used.
- `update_uses(self, level: int)` - Update maximum uses based on level.
- `__init__(self)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Use Second Wind to heal.
- `__init__(self)` - Inferred from name: init.
- `apply_sneak_attack(character: Dict, context: Dict)` - Inferred from name: apply sneak attack.
- `check_trigger(character: Dict, context: Dict)` - Inferred from name: check trigger.
- `__init__(self)` - Inferred from name: init.
- `_apply_effect(self, character: Dict[str, Any], context: Dict[str, Any])` - Inferred from name: apply effect.
- `_can_trigger(self, character: Dict[str, Any], context: Dict[str, Any])` - Inferred from name: can trigger.
- `__init__(self)` - Inferred from name: init.
- `__init__(self)` - Inferred from name: init.
- `_apply_effect(self, character: Dict[str, Any], context: Dict[str, Any])` - Inferred from name: apply effect.
- `_can_trigger(self, character: Dict[str, Any], context: Dict[str, Any])` - Inferred from name: can trigger.
- `__init__(self)` - Inferred from name: init.
- `_apply_effect(self, character: Dict[str, Any], context: Dict[str, Any])` - Inferred from name: apply effect.
- `_can_trigger(self, character: Dict[str, Any], context: Dict[str, Any])` - Inferred from name: can trigger.
- `__init__(self)` - Inferred from name: init.
- `_apply_effect(self, character: Dict[str, Any], context: Dict[str, Any])` - Inferred from name: apply effect.
- `_can_trigger(self, character: Dict[str, Any], context: Dict[str, Any])` - Inferred from name: can trigger.
- `__init__(self, name: str, description: str, trigger_condition: Callable[[Dict, Dict], bool], effect: Callable[[Dict, Dict], Dict], **kwargs)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Apply the triggered effect.
- `can_use(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Check if trigger condition is met.
- `__init__(self)` - Inferred from name: init.
- `calculate_ac(character: Dict)` - Inferred from name: calculate ac.
- `__init__(self)` - Inferred from name: init.
- `apply(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Use Uncanny Dodge.
- `can_use(self, character: Dict[str, Any], context: Optional[Dict]=None)` - Can use once per turn when hit.
- `__init__(self)` - Inferred from name: init.
- `_get_slots(self, character: Dict[str, Any])` - Inferred from name: get slots.

## core - `src/talekeeper/core/combat_manager.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_build_initiative_context(self, combatant: Combatant)` - Assemble context data for initiative rolls.
- `_calculate_loot_reward(self, monster_id: str)` - Calculate loot drops from defeated monster
- `_calculate_xp_reward(self, monster_id: str)` - Calculate XP reward for defeating monster
- `_check_and_handle_morale(self, target: Combatant, damage_dealer: Optional[Combatant]=None)` - Check if morale should be triggered and handle fleeing.
- `_execute_final_attack_on_fleeing(self, attacker: Combatant, fleeing_combatants: List[Combatant], weapon_data: Dict[str, Any])` - Execute one final attack against fleeing enemies.
- `_execute_monster_attack(self, attacker: Combatant, target: Combatant, action: CombatAction)` - Execute a monster attack
- `_execute_single_attack(self, attacker: Combatant, target: Combatant, weapon_data: Dict[str, Any], attack_num: int, total_attacks: int)` - Execute a single attack roll and damage
- `_find_monster_action(self, monster: Combatant, action_name: str)` - Find monster action by name
- `_get_extra_attack_count(self, class_name: str, level: int)` - Get number of extra attacks based on D&D 2024 rules
- `_get_living_monsters_by_name(self, monster_name: str)` - Get all living monsters with the same name
- `_get_monster_ids_by_name(self, monster_name: str)` - Get IDs of all living monsters with the same name
- `_get_saving_throw_modifier(self, combatant: Combatant, ability: str)` - Get saving throw modifier for a given ability
- `_handle_automatic_condition(self, effect, target: Combatant, attacker: Combatant)` - Handle automatic conditions (e.g., restrained by web)
- `_handle_champion_turn_start(self, combatant: Optional[Combatant])` - Trigger Champion subclass automation at the start of a player turn.
- `_handle_save_or_condition(self, effect, target: Combatant, attacker: Combatant)` - Handle save-or-condition effects (e.g., paralysis, poisoned)
- `_handle_save_or_damage(self, effect, target: Combatant, attacker: Combatant)` - Handle save-or-damage effects (e.g., poison damage)
- `_handle_size_condition(self, effect, target: Combatant, attacker: Combatant)` - Handle size-based conditions (e.g., grapple large or smaller)
- `_handle_spell_effects_turn_start(self, combatant: Optional[Combatant])` - Process spell effects at the start of a turn (Heroism temp HP, etc.).
- `_has_remarkable_athlete(self, combatant: Combatant)` - Check and cache whether the combatant benefits from Remarkable Athlete.
- `_parse_monster_actions(self, actions_json: str)` - Parse monster actions from 5eTools JSON format
- `_parse_multiattack(self, actions: List[CombatAction])` - Parse Multiattack from monster data
- `_process_attack_effects(self, standardized_attack, target: Combatant, attacker: Combatant)` - Process standardized attack effects (saves, conditions, etc.)
- `_process_single_effect(self, effect, target: Combatant, attacker: Combatant)` - Process a single standardized effect
- `_roll_damage(self, damage_dice: str)` - Roll damage dice (e.g., '1d8+3')
- `_start_new_round(self)` - Start a new combat round
- `_trigger_fires_burn(self, attacker: Combatant, target: Combatant)` - Attempt to trigger Fire's Burn if the attacker qualifies and the target is still standing.
- `add_monster_combatant(self, monster_id: str, monster_data: Dict[str, Any])` - Add monster to combat
- `add_player_combatant(self, character_data: Dict[str, Any])` - Add player character to combat
- `advance_turn(self)` - Advance to the next combatant's turn.
- `end_combat(self)` - End combat and return summary
- `execute_monster_turn(self, monster_id: str)` - Execute monster's turn with proper Multiattack support.
- `execute_player_attack(self, character_id: str, weapon_data: Dict[str, Any], target_id: str)` - Execute player attack with proper Extra Attack support.
- `get_combat_log(self)` - Get all combat log messages
- `get_current_combatant(self)` - Get the combatant whose turn it is
- `is_combat_ended(self)` - Check if combat should end (one side defeated)
- `is_player_turn(self)` - Check if it's currently the player's turn
- `log(self, message: str)` - Add message to combat log
- `start_combat(self)` - Start combat by rolling initiative for all combatants.

## core - `src/talekeeper/core/config.py`

- `__init__(self, config_file: str='talekeeper_config.json')` - Inferred from name: init.
- `enable_developer_mode(self)` - Enable developer-friendly settings
- `enable_performance_mode(self)` - Enable performance-optimized settings
- `get_debug_setting(self, setting: str)` - Get a debug setting value
- `get_feature_setting(self, setting: str)` - Get a feature setting value
- `get_performance_profile(self)` - Get current performance profile description
- `get_performance_setting(self, setting: str)` - Get a performance setting value
- `is_debug_enabled(self, debug_option: str)` - Check if a debug option is enabled
- `is_feature_enabled(self, feature: str)` - Check if a feature is enabled
- `load_config(self)` - Load configuration from file
- `reset_to_defaults(self)` - Reset all configuration to defaults
- `save_config(self)` - Save current configuration to file
- `set_debug_setting(self, setting: str, value: Any)` - Set a debug setting value
- `set_feature_setting(self, setting: str, value: Any)` - Set a feature setting value
- `set_performance_setting(self, setting: str, value: Any)` - Set a performance setting value
- `__post_init__(self)` - Initialize default release subclasses if not set
- `enable_action_card_caching()` - Check if action card caching is enabled
- `enable_condition_caching()` - Check if condition caching is enabled
- `get_config()` - Get the global configuration instance
- `get_ui_update_throttle()` - Get UI update throttle in milliseconds
- `is_debug_enabled(debug_option: str)` - Quick check if a debug option is enabled
- `is_feature_enabled(feature: str)` - Quick check if a feature is enabled
- `should_log_database_queries()` - Check if database queries should be logged
- `use_enhanced_subclass_manager()` - Check if enhanced subclass manager should be used

## core - `src/talekeeper/core/debug_commands.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_register_commands(self)` - Register all available debug commands
- `cmd_cache(self, args: List[str])` - Show cache statistics
- `cmd_combat(self, args: List[str])` - Show combat state
- `cmd_conditions(self, args: List[str])` - Show active conditions for character
- `cmd_config(self, args: List[str])` - Show or modify configuration
- `cmd_dev_mode(self, args: List[str])` - Enable developer mode
- `cmd_economy(self, args: List[str])` - Display action economy state
- `cmd_features(self, args: List[str])` - List available features for character
- `cmd_help(self, args: List[str])` - Show help for debug commands
- `cmd_list(self, args: List[str])` - List all available commands
- `cmd_memory(self, args: List[str])` - Display memory usage
- `cmd_perf_mode(self, args: List[str])` - Enable performance mode
- `cmd_performance(self, args: List[str])` - Show timing metrics
- `cmd_queries(self, args: List[str])` - Toggle database query logging
- `cmd_reset_config(self, args: List[str])` - Reset configuration to defaults
- `cmd_status(self, args: List[str])` - Show system status
- `cmd_test_conditions(self, args: List[str])` - Apply test conditions
- `cmd_test_economy(self, args: List[str])` - Reset action economy
- `cmd_test_features(self, args: List[str])` - Reload character features
- `cmd_test_rage(self, args: List[str])` - Test rage mechanics
- `execute(self, command_line: str)` - Execute a debug command
- `log_performance(self, operation: str, duration_ms: float)` - Log performance metric
- `execute_debug_command(command_line: str)` - Execute a debug command (global function)
- `log_performance_metric(operation: str, duration_ms: float)` - Log a performance metric (global function)

## core - `src/talekeeper/core/feature_definitions.py`

- `get_feature_at_level(cls, class_name: str, level: int, subclass: Optional[str]=None)` - Get only the features gained at a specific level.
- `get_features_by_level(cls, class_name: str, level: int, subclass: Optional[str]=None)` - Get all features for a character of given class and level.

## core - `src/talekeeper/core/feature_integration.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_ensure_feature_tables(self)` - Ensure all required feature tables exist.
- `_get_fighting_style(self, cursor: sqlite3.Cursor, character_id: str)` - Get fighting style from character feats.
- `_initialize_class_features(self, cursor: sqlite3.Cursor, character_id: str, class_name: str, level: int)` - Initialize class-specific feature tables with fresh data.
- `_initialize_feature(self, cursor: sqlite3.Cursor, character_id: str, class_name: str, feature: FeatureDefinition, character_level: int)` - Initialize a single feature in the database.
- `_update_legacy_tables(self, cursor: sqlite3.Cursor, character_id: str, feature_name: str, result: Dict)` - Update legacy feature tables for backward compatibility.
- `apply_passive_features(self, character_id: str)` - Apply all passive feature modifiers to a character.
- `get_available_features(self, character_id: str, context: Optional[Dict]=None)` - Get all features available to a character.
- `initialize_character_features(self, character_id: str)` - Initialize features for a character based on class and level.
- `process_rest(self, character_id: str, rest_type: str)` - Process a rest and restore features.
- `use_feature(self, character_id: str, feature_name: str, context: Optional[Dict]=None)` - Use a character feature and update database state.
- `get_feature_integration(db_path: str='talekeeper.db')` - Get the singleton feature integration instance.

## core - `src/talekeeper/core/game_engine_sqlite.py`

- `__init__(self, id, name)` - Inferred from name: init.
- `__init__(self, id, name)` - Inferred from name: init.
- `__init__(self, id, name)` - Inferred from name: init.
- `__init__(self, db_path: str='talekeeper.db')` - Initialize SQLite game engine.
- `_add_starting_equipment(self, cursor, character_id: str, character_data: Dict)` - Add starting equipment based on class and background.
- `_apply_feat_effects_to_character(self, character_dict: Dict[str, Any], feats: List[str])` - Apply mechanical effects of feats to character stats.
- `_calculate_armor_class(self, character_id: str, strength: int, dexterity: int, constitution: int, class_id: str)` - Calculate AC based on equipped armor and class features like Unarmored Defense.
- `_calculate_bag_weight(self, cursor: sqlite3.Cursor, character_id: str)` - Calculate bag weight using existing cursor to avoid nested connections.
- `_calculate_movement_speed(self, character_id: str, class_id: str, level: int)` - Calculate movement speed based on class features and level.
- `_cleanup_orphaned_slots(self)` - Clean up save slots that are marked as occupied but have no character.
- `_ensure_inventory_extension_columns(self, cursor: sqlite3.Cursor)` - Ensure Bag of Holding related columns exist on character_inventory.
- `_ensure_tables_exist(self)` - Ensure all required tables exist in the database.
- `_get_armor_stats(self, armor_name: str)` - Get armor stats for inventory.
- `_get_background_name(self, background_id: str)` - Get display name for background from talekeeper.database.
- `_get_class_name(self, class_id: str)` - Get display name for class.
- `_get_connection(self)` - Get database connection with foreign keys enabled.
- `_get_full_caster_spell_slots(self, level: int)` - Get spell slot progression for full casters (Wizard, Cleric).
- `_get_race_name(self, race_id: str)` - Get display name for race from database.
- `_get_weapon_stats(self, weapon_name: str)` - Get weapon stats for inventory.
- `_initialize_barbarian_features(self, cursor, character_id: str, character_data: Dict)` - Initialize Barbarian-specific features.
- `_initialize_class_features(self, cursor, character_id: str, character_data: Dict)` - Initialize class-specific features table based on character's class.
- `_initialize_cleric_features(self, cursor, character_id: str, character_data: Dict)` - Initialize Cleric-specific features (full spellcaster + divine).
- `_initialize_fighter_features(self, cursor, character_id: str, character_data: Dict)` - Initialize Fighter-specific features.
- `_initialize_paladin_features(self, cursor, character_id: str, character_data: Dict)` - Initialize Paladin-specific features (D&D 2024 rules - spellcasting from level 1).
- `_initialize_rogue_features(self, cursor, character_id: str, character_data: Dict)` - Initialize Rogue-specific features.
- `_initialize_warlock_features(self, cursor, character_id: str, character_data: Dict)` - Initialize Warlock-specific features (pact magic, D&D 2024 rules).
- `_initialize_wizard_features(self, cursor, character_id: str, character_data: Dict)` - Initialize Wizard-specific features (full spellcaster).
- `_load_settings(self)` - Load application settings from SQLite or file.
- `_normalize_item_name(self, item_name: str)` - Convert plural item names to singular forms for database lookup.
- `_parse_equipment_choice(self, choice_string: str)` - Parse equipment choice strings like 'Scimitar + Shortsword' or '2 Shortswords' into individual items.
- `_rebalance_gold_storage(self, cursor: sqlite3.Cursor, character_id: str)` - Shift gold from the character's person into the Bag of Holding when possible.
- `_safe_get_row_value(self, row: sqlite3.Row, key: str, default=None)` - Safely get a value from sqlite3.Row with default fallback.
- `add_feat_to_character_sync(self, character_id: str, feat_name: str)` - Add a new feat to a character.
- `add_gold_to_character_sync(self, character_id: str, gold_amount: float, store_in_bag: bool=None)` - Add gold to character's inventory with automatic Bag of Holding handling.
- `add_treasure_to_character_sync(self, character_id: str, treasure_item: Dict, store_in_bag: bool=None)` - Add treasure item (gem, art object, etc.) to character's inventory.
- `apply_equipment_choices_sync(self, character_data, equipment_choices)` - Apply equipment choices made during character creation.
- `auto_save(self)` - Perform automatic save (just calls save_game_sync).
- `calc_modifier(score)` - Inferred from name: calc modifier.
- `can_equip_item(self, character_id: str, item_name: str)` - Check if character can equip a specific item. Returns (can_equip, reason).
- `character_has_bag_of_holding(self, character_id: str)` - Check if character has a Bag of Holding in inventory.
- `create_new_character_sync(self, character_data: Dict, save_slot: int)` - Create a new character and save to database.
- `delete_character_sync(self, save_slot: int)` - Delete character from save slot.
- `get_available_backgrounds_sync(self)` - Get available backgrounds from talekeeper.database.
- `get_available_classes_sync(self)` - Get available classes from talekeeper.database.
- `get_available_races_sync(self)` - Get available races from talekeeper.database.
- `get_bag_of_holding_weight(self, character_id: str)` - Calculate total weight stored in Bag of Holding.
- `get_character_by_id_sync(self, character_id: str)` - Load character by character ID.
- `get_character_fighting_styles(self, character_id: str)` - Get character's fighting styles from character_features table.
- `get_character_inventory_sync(self, character_id: str)` - Get inventory items for a character.
- `get_class_equipment_choices_sync(self, class_id: str)` - Get equipment choices for a specific class from the database.
- `get_equipment_item_sync(self, item_name: str)` - Get equipment item data by name from talekeeper.database.
- `get_monsters_by_cr_sync(self, min_cr: float, max_cr: float)` - Get monsters within CR range from JSON data files.
- `get_save_slots_sync(self)` - Get all save slots.
- `load_character_sync(self, save_slot: int)` - Load character from save slot.
- `recalculate_character_stats_sync(self, character_id: str)` - Recalculate character stats including AC and feat effects.
- `save_character_sync(self, character_id: str=None)` - Save current character or specified character to database.
- `save_game_sync(self)` - Save current game state.
- `save_settings(self)` - Save application settings.
- `shutdown(self)` - Clean shutdown of game engine.
- `update_character_equipment_sync(self, character_id: str, equipment_slot: str, item_name: Optional[str]=None)` - Update character equipment in database.
- `update_character_hp_sync(self, current_hp: int, max_hp: int=None)` - Update character's HP in database.
- `update_character_resources_sync(self, character_id: str, resource_updates: Dict[str, Any])` - Update character resources in database.
- `update_character_xp_sync(self, character_id: str, new_xp: int)` - Update character's experience points in the database.

## core - `src/talekeeper/database/database_init.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_ensure_inventory_columns(self, cursor: sqlite3.Cursor)` - Ensure Bag of Holding columns exist on character_inventory.
- `check_and_apply_migrations(self)` - Legacy migration support - now redirects to schema versioning.
- `check_schema_version(self)` - Check and upgrade database schema if needed.
- `create_migrations_table(self)` - Inferred from name: create migrations table.
- `create_schema(self)` - Inferred from name: create schema.
- `initialize(self, force: bool=False, dev_mode: bool=False)` - Inferred from name: initialize.
- `load_dev_data(self)` - Inferred from name: load dev data.
- `load_game_data(self)` - Inferred from name: load game data.
- `verify_database(self)` - Inferred from name: verify database.
- `main()` - Inferred from name: main.

## core - `src/talekeeper/models/action_economy.py`

- `can_take_action(self, action_type: ActionEconomyType)` - Check if an action type can currently be taken.
- `end_turn(self)` - End the current turn.
- `from_dict(cls, data: Dict[str, Any])` - Create from dictionary.
- `get_action_status(self, action_type: ActionEconomyType)` - Get current availability status of an action type.
- `get_action_usage_count(self, action_id: str)` - Get number of times a specific action has been used this combat.
- `get_active_effects(self)` - Get all currently active effects.
- `get_remaining_movement(self)` - Get remaining movement for this turn.
- `get_resource_usage(self, resource_name: str)` - Get total usage of a specific resource this combat.
- `get_turn_summary(self)` - Get a summary of this turn's action economy state.
- `has_active_effect(self, action_id: str)` - Check if a specific action has an active ongoing effect.
- `start_new_round(self, round_number: int)` - Start a new round - minimal resets (reactions stay consumed until owner's turn).
- `start_new_turn(self, round_number: int, turn_position: int)` - Start a new turn - reset action economy.
- `to_dict(self)` - Convert to dictionary for storage.
- `track_class_action(self, action_id: str, action_name: str, resource_cost: Dict[str, int]=None, effect_duration: Optional[Dict[str, Any]]=None)` - Track usage of a class-specific action (Stage 3.2 Enhancement).
- `update_effect_durations(self)` - Update durations for ongoing effects - called at start of turn/round.
- `use_action(self, action_type: ActionEconomyType, action_name: str, action_data: Dict=None)` - Attempt to use an action. Returns True if successful, False if not available.
- `use_action_surge(self)` - Use Fighter Action Surge to gain an additional action.
- `_start_combatant_turn(self, combatant_id: str)` - Start a combatant's turn.
- `add_combatant(self, combatant_id: str, name: str, combatant_type: str='character', movement_speed: int=30, has_action_surge: bool=False)` - Add a combatant to the action economy tracking.
- `from_dict(cls, data: Dict[str, Any])` - Create from dictionary.
- `get_active_combatant(self)` - Get the ID of the currently active combatant.
- `get_combat_summary(self)` - Get a summary of the current combat state.
- `get_combatant_action_count(self, combatant_id: str, action_id: str)` - Get action usage count for a specific combatant.
- `get_combatant_active_effects(self, combatant_id: str)` - Get active effects for a specific combatant.
- `get_combatant_resource_usage(self, combatant_id: str, resource_name: str)` - Get resource usage for a specific combatant.
- `get_combatant_state(self, combatant_id: str)` - Get the action economy state for a specific combatant.
- `next_turn(self)` - Advance to the next turn. Returns the ID of the next active combatant.
- `start_combat(self, initiative_order: List[str])` - Start combat with the given initiative order.
- `to_dict(self)` - Convert to dictionary for storage.
- `track_class_action(self, combatant_id: str, action_id: str, action_name: str, resource_cost: Dict[str, int]=None, effect_duration: Optional[Dict[str, Any]]=None)` - Track a class-specific action for a combatant (Stage 3.2 Enhancement).
- `use_action(self, combatant_id: str, action_type: ActionEconomyType, action_name: str, action_data: Dict=None)` - Attempt to use an action for a combatant.

## core - `src/talekeeper/paths.py`

- `get_assets_path(relative_path='')` - Inferred from name: get assets path.
- `get_config_path(relative_path='')` - Inferred from name: get config path.
- `get_data_path(relative_path='')` - Inferred from name: get data path.
- `get_database_path(db_name='talekeeper.db')` - Inferred from name: get database path.
- `get_logs_path(relative_path='')` - Inferred from name: get logs path.
- `get_root_path()` - Inferred from name: get root path.

## core - `src/talekeeper/services/action_card_generator.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `create_legacy_action_card(self, enhanced_card: EnhancedActionCard, parent: Optional[QWidget]=None)` - Create a legacy ActionCard widget from an EnhancedActionCard.
- `generate_character_action_cards(self, character_id: str, combat_state: Optional[ActionEconomyState]=None)` - Generate all available action cards for a character.
- `generate_class_action_cards(self, character_id: str, class_name: str, level: int, combat_state: Optional[ActionEconomyState]=None)` - Generate action cards for a specific class at a given level
- `get_action_cards_by_economy_type(self, character_id: str, combat_state: Optional[ActionEconomyState]=None)` - Get action cards grouped by economy type.
- `get_available_action_cards(self, character_id: str, combat_state: Optional[ActionEconomyState]=None)` - Get only currently available action cards
- `get_resource_summary(self, character_id: str)` - Get summary of character resources for display.
- `get_unavailable_action_cards(self, character_id: str, combat_state: Optional[ActionEconomyState]=None)` - Get unavailable action cards with reasons.
- `__init__(self, action_def: ClassActionDefinition, validation_result: ActionValidationResult)` - Inferred from name: init.
- `_format_resource_costs(self)` - Format resource costs for display
- `_get_cost_display(self)` - Get cost display string for the card
- `_get_default_icon(self)` - Get default icon based on action type
- `_get_warning_badges(self)` - Get warning badges for the card
- `get_card_style_class(self)` - Get CSS class for card styling
- `get_enhanced_description(self)` - Get description with cost and availability info
- `generate_action_cards_for_character(character_id: str, combat_state: Optional[ActionEconomyState]=None)` - Global function to generate action cards for a character.
- `get_action_cards_by_availability(character_id: str, combat_state: Optional[ActionEconomyState]=None)` - Get action cards split by availability.

## core - `src/talekeeper/services/action_card_validator.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_feature_exists_in_db(self, character_id: str, mapping: FeatureActionMapping)` - Check if feature exists in character_features table
- `_get_character_data(self, character_id: str)` - Get character data from database
- `_get_expected_features(self, class_name: str, level: int, subclass_name: Optional[str]=None)` - Get all features expected for this class/level/subclass
- `_get_mapping_key(self, feature_name: str, class_name: str, subclass_name: Optional[str]=None)` - Generate unique key for feature mapping
- `_initialize_mappings(self)` - Initialize the feature -> action card mappings
- `_resource_exists_in_db(self, character_id: str, mapping: FeatureActionMapping)` - Check if resource exists in character_resources table
- `get_missing_features_report(self, character_id: str)` - Generate a detailed report of missing features
- `register_mapping(self, mapping: FeatureActionMapping)` - Register a feature -> action card mapping
- `validate_character_actions(self, character_id: str, raise_on_error: bool=True)` - Validate that all features with action economy have action cards.
- `validate_character_on_creation(character_id: str)` - Convenience function to validate character immediately after creation.

## core - `src/talekeeper/services/action_economy_enforcer.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_apply_action_effects(self, action_def: ClassActionDefinition, character_id: str, combat_economy: Optional[CombatActionEconomy], action_context: Dict[str, Any], result: ActionExecutionResult)` - Apply the actual effects of the action
- `_call_action_handler(self, action_def: ClassActionDefinition, character_id: str, action_context: Dict[str, Any], result: ActionExecutionResult)` - Call the appropriate handler function for the action
- `_consume_action_economy(self, action_def: ClassActionDefinition, combat_economy: CombatActionEconomy, character_id: str, result: ActionExecutionResult)` - Consume action economy slot.
- `_consume_resources(self, action_def: ClassActionDefinition, character_id: str, result: ActionExecutionResult)` - Consume character resources.
- `_consume_single_resource(self, cursor, character_id: str, resource_name: str, amount: int, result: ActionExecutionResult)` - Consume a single resource type
- `_rollback_economy_consumption(self, action_def: ClassActionDefinition, combat_economy: CombatActionEconomy, character_id: str)` - Rollback action economy consumption (simplified - would need more complex logic)
- `_rollback_resource_consumption(self, action_def: ClassActionDefinition, character_id: str, result: ActionExecutionResult)` - Rollback resource consumption
- `_track_action_usage(self, action_def: ClassActionDefinition, combat_economy: CombatActionEconomy, character_id: str, result: ActionExecutionResult)` - Track action usage in combat economy
- `can_execute_action(self, character_id: str, action_id: str, combat_economy: Optional[CombatActionEconomy]=None)` - Check if an action can be executed (non-destructive check).
- `execute_action(self, character_id: str, action_id: str, combat_economy: Optional[CombatActionEconomy]=None, action_context: Optional[Dict[str, Any]]=None)` - Execute an action with full economy enforcement.
- `get_available_actions(self, character_id: str, combat_economy: Optional[CombatActionEconomy]=None)` - Get list of currently available action IDs
- `__init__(self, success: bool, action_id: str='', reason: str='')` - Inferred from name: init.
- `add_economy_consumption(self, economy_type: str)` - Record action economy consumption
- `add_effect(self, effect_id: str, effect_data: Dict[str, Any])` - Record effect application
- `add_resource_consumption(self, resource_name: str, amount: int)` - Record resource consumption
- `add_state_change(self, key: str, old_value: Any, new_value: Any)` - Record state change
- `get_summary(self)` - Get execution summary
- `can_execute_class_action(character_id: str, action_id: str, combat_economy: Optional[CombatActionEconomy]=None)` - Global function to check if an action can be executed.
- `execute_class_action(character_id: str, action_id: str, combat_economy: Optional[CombatActionEconomy]=None, action_context: Optional[Dict[str, Any]]=None)` - Global function to execute a class action with full enforcement.

## core - `src/talekeeper/services/action_registry.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_check_action_economy(self, action: ClassActionDefinition, character_id: str)` - Check if character has action economy available
- `_check_combat_state(self, character_id: str, state_name: str)` - Check character's combat state
- `_check_prerequisite(self, prereq: ActionPrerequisite, character_data: Dict, character_id: str)` - Check a single prerequisite
- `_check_resources(self, action: ClassActionDefinition, character_id: str)` - Check if character has required resources
- `_compare_values(self, actual: Any, expected: Any, operator: str)` - Compare two values using the given operator
- `_get_character_data(self, character_id: str)` - Get character data from database
- `_get_resource_count(self, character_id: str, resource_name: str)` - Get current count of a resource
- `_meets_level_requirement(self, action: ClassActionDefinition, level: int)` - Check if action meets level requirement
- `_register_barbarian_actions(self)` - Register all Barbarian class actions
- `_register_core_actions(self)` - Register core D&D actions available to all characters
- `can_use_action(self, action_id: str, character_id: str)` - Check if character can currently use an action
- `get_action(self, action_id: str)` - Get action definition by ID
- `get_character_actions(self, character_id: str)` - Get all actions available to a specific character
- `get_class_actions(self, class_name: str, level: int=20)` - Get all actions available to a class at given level
- `get_subclass_actions(self, class_name: str, subclass_name: str, level: int=20)` - Get all actions available to a subclass at given level
- `register_action(self, action: ClassActionDefinition)` - Register a new action definition
- `validate_prerequisites(self, action: ClassActionDefinition, character_id: str)` - Validate all prerequisites for an action

## core - `src/talekeeper/services/action_validation.py`

- `__init__(self, can_use: bool, action_id: str='', reason: str='')` - Inferred from name: init.
- `add_economy_block(self, economy_type: str, reason: str)` - Add an action economy block
- `add_prerequisite_failure(self, prereq_type: str, expected: Any, actual: Any)` - Add a failed prerequisite
- `add_resource_shortage(self, resource: str, needed: int, available: int)` - Add a resource shortage
- `add_warning(self, warning: str)` - Add a warning message
- `get_user_friendly_message(self)` - Get a user-friendly explanation of why action can't be used
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_check_action_economy(self, action_def: ClassActionDefinition, combat_state: ActionEconomyState)` - Check if action economy allows this action
- `_check_single_prerequisite(self, prereq, character_data: Dict, character_id: str)` - Check a single prerequisite - reuse logic from action registry
- `_get_character_data(self, character_id: str)` - Get character data from database
- `_get_resource_count(self, character_id: str, resource_name: str)` - Get current count of a resource
- `_parse_registry_failures(self, result: ActionValidationResult, registry_check: Dict[str, Any], action_def: ClassActionDefinition, character_id: str)` - Parse failures from registry check into detailed result
- `can_use_class_action(self, character_id: str, action_id: str, combat_state: Optional[ActionEconomyState]=None)` - Check if a character can use a specific class action.
- `get_action_availability(self, character_id: str, combat_state: Optional[ActionEconomyState]=None)` - Get availability for all actions for a character.
- `log_action_attempt(self, character_id: str, action_id: str, success: bool, reason: str='')` - Log action attempts for debugging and analysis
- `validate_action_with_feedback(self, character_id: str, action_id: str, combat_state: Optional[ActionEconomyState]=None)` - Validate action and return detailed feedback.
- `can_use_class_action(character_id: str, action_id: str, combat_state: Optional[ActionEconomyState]=None)` - Global function for checking if a class action can be used.
- `get_action_feedback(character_id: str, action_id: str, combat_state: Optional[ActionEconomyState]=None)` - Global function for getting detailed action feedback.

## core - `src/talekeeper/services/advantage_system.py`

- `_collection_has_feature(cls, candidate: Any, candidate_names: Set[str])` - Check nested feature collections (dicts/lists) for a matching feature name.
- `_context_has_feature(cls, context: Dict[str, Any], *names: str)` - Determine if any of the provided feature names appear in the roll context.
- `_context_has_remarkable_athlete(cls, context: Dict[str, Any])` - Check whether Remarkable Athlete is present in the context.
- `_get_condition_advantage_sources(character_id: str, roll_type: RollType, context: Dict[str, Any])` - Get advantage sources from character conditions.
- `_get_condition_disadvantage_sources(character_id: str, roll_type: RollType, context: Dict[str, Any])` - Get disadvantage sources from character conditions.
- `_is_athletics_check(context: Dict[str, Any])` - Determine if the current context refers to an Athletics skill check.
- `_normalize_feature_name(candidate: Any)` - Normalize feature descriptors to lowercase names when possible.
- `append_unique(label: str)` - Inferred from name: append unique.
- `calculate_advantage_state(advantage_sources: List[str], disadvantage_sources: List[str])` - Calculate the final advantage state based on all sources.
- `format_roll_description(breakdown: Dict[str, Any])` - Format a roll breakdown into a human-readable description.
- `get_common_advantage_sources(roll_type: RollType, context: Dict[str, Any])` - Get common sources of advantage for different roll types.
- `get_common_advantage_sources(roll_type: RollType, context: Dict[str, Any])` - Get common sources of advantage for different roll types.
- `get_common_disadvantage_sources(roll_type: RollType, context: Dict[str, Any])` - Get common sources of disadvantage for different roll types.
- `roll_d20_with_advantage(advantage_state: AdvantageState, modifier: int=0)` - Roll a d20 with advantage/disadvantage and return result with breakdown.

## core - `src/talekeeper/services/aura_manager.py`

- `__post_init__(self)` - Inferred from name: post init.
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_character_own_auras(self, cursor, character_id: str)` - Get auras that a character generates for themselves.
- `_get_oath_aura(self, subclass: str, character_id: str, level: int, aura_range: int)` - Get oath-specific aura effect.
- `apply_aura_to_save(self, character_id: str, save_roll: int, save_type: str)` - Apply aura bonuses to a saving throw.
- `calculate_save_bonus(self, character_id: str, save_type: str)` - Calculate total saving throw bonus from auras.
- `check_aura_condition_immunity(self, character_id: str, condition: str)` - Check condition immunity and return the aura providing it.
- `get_active_aura_summary(self, character_id: str)` - Get a summary of all active auras for UI display.
- `get_aura_descriptions(self, character_id: str)` - Get descriptions of all active auras affecting a character.
- `get_aura_range(self, character_level: int)` - Get aura range based on character level.
- `get_character_auras(self, character_id: str)` - Get all auras affecting a character.
- `has_advantage_type(self, character_id: str, advantage_type: str)` - Check if character has advantage on specific types of rolls from auras.
- `has_condition_immunity(self, character_id: str, condition: str)` - Check if character has immunity to a condition from auras.
- `update_character_level(self, character_id: str, new_level: int)` - Update aura effects when character level changes.
- `get_aura_manager(db_path: str='talekeeper.db')` - Get singleton aura manager instance.

## core - `src/talekeeper/services/barbarian_abilities.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_connection(self)` - Get database connection.
- `add_primal_knowledge_skill(self, character_id: str, skill_name: str)` - Add a skill to Primal Knowledge (Animal Handling, Athletics, Intimidation, Nature, Perception, Survival).
- `check_relentless_rage(self, character_id: str, damage_taken: int)` - Check and potentially trigger Relentless Rage when dropping to 0 HP.
- `end_rage(self, character_id: str, reason: str='duration')` - End rage (duration, heavy armor, incapacitated, etc.).
- `get_barbarian_level(self, character_id: str)` - Get the barbarian class level for a character.
- `get_character_subclass(self, character_id: str)` - Get the barbarian subclass for a character.
- `get_primal_knowledge_skills(self, character_id: str)` - Get available Primal Knowledge skills for barbarian.
- `has_danger_sense_advantage(self, character_id: str, save_ability: str, conditions: List[str]=None)` - Check if character gets Danger Sense advantage on a Dexterity saving throw.
- `has_danger_sense_advantage_enhanced(self, character_id: str, save_ability: str='dexterity')` - Enhanced Danger Sense check using the formal condition system.
- `has_feral_instinct(self, character_id: str)` - Check if character has Feral Instinct (advantage on initiative, can act if surprised).
- `process_berserker_turn_start(self, character_id: str)` - Apply Berserker subclass start-of-turn effects.
- `rest_barbarian_resources(self, character_id: str, rest_type: str)` - Reset barbarian resources on rest.
- `update_barbarian_resources_for_level(self, character_id: str, level: int)` - Update barbarian resource maximums based on level.
- `use_berserker_retaliation(self, character_id: str, attacker_name: str='')` - Use Berserker Retaliation reaction (Level 10+).
- `use_brutal_strike(self, character_id: str, strike_type: str, target_name: str='')` - Use Brutal Strike when making a Reckless Attack.
- `use_intimidating_presence(self, character_id: str)` - Use Intimidating Presence (Berserker Level 14+).
- `use_rage(self, character_id: str)` - Use Rage ability.
- `use_reckless_attack(self, character_id: str)` - Toggle Reckless Attack for this turn.

## core - `src/talekeeper/services/beast_loot_service.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_cr_to_individual_treasure(self, cr: float)` - Convert CR to individual treasure GP value.
- `_parse_cr(self, cr_text: str)` - Parse CR string to numeric value
- `add_rations_to_inventory(self, character_id: str, quantity: int)` - Add rations to character inventory
- `calculate_ration_drop(self, monster_id: str)` - Calculate how many rations a beast drops.
- `generate_beast_loot(self, monster_id: str)` - Generate loot for a defeated beast.
- `get_individual_treasure_value(self, monster_id: str)` - Get individual treasure value for a monster.
- `get_monster_name(self, monster_id: str)` - Get monster name for logging
- `is_beast(self, monster_id: str)` - Check if a monster is a beast type

## core - `src/talekeeper/services/campaign_description_service.py`

- `__init__(self, base_url: Optional[str]=None, default_model: Optional[str]=None, request_timeout: float=10.0)` - Inferred from name: init.
- `_build_prompt(self, request: DescriptionRequest)` - Inferred from name: build prompt.
- `_fallback_description(self, entity_type: str, entity_data: Dict[str, Any], campaign_frame: Any)` - Return a deterministic blurb when Ollama is unavailable.
- `_generate_from_prompt(self, prompt: str, campaign_frame: Any)` - Inferred from name: generate from prompt.
- `generate_combat_narrative(self, combat_events: List[Dict[str, Any]], campaign_frame: Any, context: Optional[Dict[str, Any]]=None)` - Inferred from name: generate combat narrative.
- `generate_description(self, entity_type: str, entity_data: Optional[Dict[str, Any]], campaign_frame: Any)` - Return a short description or ``None`` if generation fails.
- `generate_encounter_description(self, monsters: List[Dict[str, Any]], campaign_frame: Any, level: int, difficulty: str)` - Inferred from name: generate encounter description.
- `generate_round_summary(self, round_events: List[Dict[str, Any]], campaign_frame: Any)` - Inferred from name: generate round summary.
- `generate_victory_narrative(self, combat_summary: Dict[str, Any], campaign_frame: Any)` - Inferred from name: generate victory narrative.
- `post(self, *args, **kwargs)` - Inferred from name: post.
- `_load_requests_module()` - Inferred from name: load requests module.

## core - `src/talekeeper/services/character_resources.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_grant_human_long_rest_inspiration(self, cursor, character_id: str)` - Ensure humans regain Heroic Inspiration on long rest.
- `add_resource(self, character_id: str, resource_name: str, max_uses: int, rest_type: str, source_class: str, source_level: int)` - Add a new resource to a character (or update existing).
- `get_character_resources(self, character_id: str)` - Get all resources for a character.
- `get_resource(self, character_id: str, resource_name: str)` - Get a specific resource for a character.
- `get_resources_summary(self, character_id: str)` - Get a summary of all character resources for UI display.
- `initialize_barbarian_resources(self, character_id: str, level: int)` - Initialize Barbarian resources based on level.
- `initialize_fighter_resources(self, character_id: str, level: int)` - Initialize/update Fighter resources based on level.
- `restore_resources_by_rest_type(self, character_id: str, rest_type: str)` - Restore all resources of a specific rest type (short_rest or long_rest).
- `update_resource_max_uses(self, character_id: str, resource_name: str, new_max: int)` - Update max uses for a resource (for level progression).
- `use_resource(self, character_id: str, resource_name: str, uses: int=1)` - Use a resource (consume uses).

## core - `src/talekeeper/services/class_abilities_service.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_calculate_sneak_attack_dice(self, level: int)` - Inferred from name: calculate sneak attack dice.
- `_evaluate_formula(self, formula: str, level: int)` - Inferred from name: evaluate formula.
- `_execute_ability_mechanics(self, character_id: str, ability_id: str, ability: sqlite3.Row, mechanics: Dict[str, Any], context: Dict[str, Any], cursor: sqlite3.Cursor)` - Inferred from name: execute ability mechanics.
- `_execute_action_surge(self, character_id: str, mechanics: Dict, cursor: sqlite3.Cursor)` - Inferred from name: execute action surge.
- `_execute_rage(self, character_id: str, mechanics: Dict, cursor: sqlite3.Cursor)` - Inferred from name: execute rage.
- `_execute_second_wind(self, character_id: str, mechanics: Dict, cursor: sqlite3.Cursor)` - Inferred from name: execute second wind.
- `_execute_sneak_attack(self, character_id: str, mechanics: Dict, context: Dict, cursor: sqlite3.Cursor)` - Inferred from name: execute sneak attack.
- `_get_connection(self)` - Inferred from name: get connection.
- `_get_proficiency_bonus(self, level: int)` - Inferred from name: get proficiency bonus.
- `_get_scaling_value(self, formula_name: str, level: int)` - Inferred from name: get scaling value.
- `calculate_max_uses(self, ability_id: str, level: int, character_stats: Dict=None)` - Inferred from name: calculate max uses.
- `get_character_abilities(self, character_id: str)` - Inferred from name: get character abilities.
- `restore_abilities(self, character_id: str, rest_type: str)` - Inferred from name: restore abilities.
- `update_ability_resources_for_level(self, character_id: str, new_level: int)` - Inferred from name: update ability resources for level.
- `use_ability(self, character_id: str, ability_id: str, context: Dict[str, Any]=None)` - Inferred from name: use ability.

## core - `src/talekeeper/services/cleric_abilities.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_add_domain_spells(self, cursor, character_id: str, domain: str, level: int)` - Add domain spells to character's spell list.
- `_apply_channel_divinity_effect(self, cursor, character_id: str, option_id: str, targets: Optional[List[str]])` - Apply the specific effects of a Channel Divinity option.
- `_apply_domain_features(self, cursor, character_id: str, domain: str, level: int)` - Apply domain-specific features.
- `_initialize_channel_divinity(self, cursor, character_id: str, domain: str, level: int)` - Initialize Channel Divinity options for a cleric.
- `apply_blessed_healer(self, character_id: str, spell_level: int)` - Apply Blessed Healer self-healing for Life Domain clerics.
- `apply_disciple_of_life(self, character_id: str, spell_level: int, base_healing: int)` - Apply Disciple of Life bonus healing for Life Domain clerics.
- `get_character_cleric_info(self, character_id: str)` - Get complete cleric information for a character.
- `initialize_cleric_character(self, character_id: str, domain: str='life')` - Initialize a character as a Cleric with the specified domain.
- `reset_cleric_resources(self, character_id: str, rest_type: str='long')` - Reset cleric resources on rest.
- `use_channel_divinity(self, character_id: str, option_id: str, targets: Optional[List[str]]=None)` - Use a Channel Divinity option.

## core - `src/talekeeper/services/combat_log_parser.py`

- `__init__(self)` - Inferred from name: init.
- `parse_attack_event(self, log_text: str)` - Inferred from name: parse attack event.
- `parse_combat_round(self, log_entries: List[str])` - Inferred from name: parse combat round.
- `parse_condition_event(self, log_text: str)` - Inferred from name: parse condition event.
- `parse_damage_event(self, log_text: str)` - Inferred from name: parse damage event.
- `parse_death_event(self, log_text: str)` - Inferred from name: parse death event.
- `parse_event(self, log_text: str)` - Inferred from name: parse event.
- `parse_healing_event(self, log_text: str)` - Inferred from name: parse healing event.

## core - `src/talekeeper/services/concentration_system.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_get_concentration_save_proficiency(self, character_id: str)` - Get proficiency bonus for concentration saves.
- `_parse_spell_duration_to_rounds(self, duration: str)` - Parse spell duration string to number of rounds.
- `check_concentration_breaking_conditions(self, character_id: str)` - Check various conditions that could break concentration.
- `end_concentration(self, character_id: str, reason: str='voluntary')` - End concentration for a character.
- `get_all_concentrating_characters(self)` - Get all characters currently concentrating on spells.
- `get_concentration_spell(self, character_id: str)` - Get the spell a character is currently concentrating on.
- `handle_concentration_breaking_conditions(self, character_id: str)` - Automatically end concentration if breaking conditions are met.
- `make_concentration_save(self, character_id: str, damage_taken: int, constitution_modifier: int=0)` - Make a concentration saving throw when taking damage.
- `start_concentration(self, character_id: str, spell_id: str, spell_level: int, duration_rounds: Optional[int]=None)` - Start concentration on a spell for a character.
- `update_concentration_duration(self, character_id: str, rounds_passed: int=1)` - Update concentration duration during combat.
- `get_concentration_system(db_path: str='talekeeper.db')` - Factory function to get concentration system instance.

## core - `src/talekeeper/services/condition_manager.py`

- `from_dict(cls, data: Dict[str, Any])` - Create from dictionary.
- `to_dict(self)` - Convert to dictionary for database storage.
- `get_effects(cls, condition_type: ConditionType)` - Get the mechanical effects of a condition.
- `is_incapacitating(cls, condition_type: ConditionType)` - Check if a condition is incapacitating.
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_add_exhaustion_level(self, character_id: str, levels: int=1, source: str='effect')` - Add exhaustion levels (special stacking condition).
- `_ensure_tables(self)` - Create condition tables if they don't exist.
- `_get_log_effects_summary(self, condition: ActiveCondition)` - Get a brief summary of condition effects for logging.
- `_log_condition_change(self, character_id: str, action: str, condition: ActiveCondition, reason: str=None)` - Log condition changes to the UI.
- `_reduce_exhaustion_level(self, character_id: str, levels: int=1, reason: str='long_rest')` - Reduce exhaustion levels.
- `_update_duration(self, character_id: str, condition_type: ConditionType, new_duration: int)` - Update the duration of a condition.
- `add_condition(self, character_id: str, condition: ActiveCondition)` - Add a condition to a character.
- `add_immunity(self, character_id: str, condition_type: ConditionType, source: str='feature', duration: str='permanent')` - Add immunity to a condition.
- `clear_all_conditions(self, character_id: str, reason: str='effect')` - Remove all conditions from a character (e.g., Greater Restoration).
- `get_active_conditions(self, character_id: str)` - Get all active conditions on a character.
- `get_condition(self, character_id: str, condition_type: ConditionType)` - Get a specific condition on a character.
- `get_condition_summary(self, character_id: str)` - Get a readable summary of active conditions.
- `get_exhaustion_level(self, character_id: str)` - Get current exhaustion level (0-6).
- `has_condition(self, character_id: str, condition_type: ConditionType)` - Check if a character has a specific condition.
- `has_incapacitating_condition(self, character_id: str)` - Check if character has any incapacitating condition (for Danger Sense).
- `is_immune_to_condition(self, character_id: str, condition_type: ConditionType)` - Check if character is immune to a condition.
- `process_turn_end(self, character_id: str, current_round: int)` - Process condition effects at end of turn.
- `process_turn_start(self, character_id: str, current_round: int)` - Process condition effects at start of turn.
- `remove_condition(self, character_id: str, condition_type: ConditionType, reason: str='effect_ended')` - Remove a condition from a character.
- `remove_immunity(self, character_id: str, condition_type: ConditionType, source: str='feature')` - Remove immunity to a condition.
- `set_log_callback(self, callback)` - Set callback function for logging condition changes.

## core - `src/talekeeper/services/condition_stat_service.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `can_take_actions(self, character_id: str)` - Check what actions a character can take based on conditions.
- `get_ability_check_modifier(self, character_id: str, ability: str)` - Get ability check modifiers from conditions.
- `get_all_stat_modifiers(self, character_id: str, base_stats: Dict[str, Any])` - Get comprehensive stat modifications for a character.
- `get_armor_class_modifier(self, character_id: str)` - Get AC modifiers from conditions.
- `get_attack_roll_modifier(self, character_id: str, attack_type: str='any')` - Get attack roll modifiers from conditions.
- `get_character_base_speed(self, character_id: str)` - Get character's base movement speed from talekeeper.database.
- `get_damage_immunities(self, character_id: str)` - Get damage immunities from conditions.
- `get_damage_resistances(self, character_id: str)` - Get damage resistances from conditions.
- `get_initiative_modifier(self, character_id: str)` - Get initiative modifiers from conditions.
- `get_movement_speed_modifier(self, character_id: str, base_speed: int=None)` - Get modified movement speed based on conditions.
- `get_saving_throw_modifier(self, character_id: str, ability: str)` - Get saving throw modifiers from conditions.

## core - `src/talekeeper/services/cr_to_xp.py`

- `cr_to_xp(challenge_rating: str)` - Convert Challenge Rating to Experience Points.
- `get_most_powerful_monster(monsters: list)` - Get the most powerful monster from a list based on CR.
- `get_xp_for_encounter(monsters: list)` - Calculate total XP for an encounter of monsters.

## core - `src/talekeeper/services/cunning_strike_manager.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_calculate_sneak_attack_dice(self, level: int)` - Calculate sneak attack dice based on rogue level
- `_get_connection(self)` - Inferred from name: get connection.
- `_get_proficiency_bonus(self, level: int)` - Get proficiency bonus based on level
- `_is_sneak_attack_weapon(self, weapon: Dict[str, Any])` - Check if weapon is eligible for sneak attack
- `apply_cunning_strike(self, character_id: str, target_id: str, effects: List[CunningStrikeEffect], attack_damage: int)` - Apply Cunning Strike effects to target
- `calculate_save_dc(self, character_id: str)` - Calculate Cunning Strike save DC (8 + DEX mod + proficiency)
- `calculate_sneak_attack_with_cost(self, character_id: str, effects: List[CunningStrikeEffect])` - Calculate sneak attack damage after Cunning Strike costs
- `can_use_multiple_effects(self, character_id: str)` - Check if rogue can use multiple Cunning Strike effects (level 11+)
- `check_sneak_attack_eligibility(self, character_id: str, combat_context: Dict[str, Any])` - Check if Sneak Attack is eligible this attack
- `get_available_cunning_strikes(self, character_id: str)` - Get list of available Cunning Strike options for character
- `get_cunning_strike_preview(self, character_id: str, effects: List[CunningStrikeEffect])` - Get preview of Cunning Strike effects without applying
- `validate_cunning_strike_selection(self, character_id: str, effects: List[CunningStrikeEffect])` - Validate Cunning Strike effect selection

## core - `src/talekeeper/services/dice.py`

- `__init__(self, seed: Optional[int]=None)` - Initialize dice roller.
- `_roll_with_advantage(self, notation: str, advantage: bool)` - Handle advantage/disadvantage for d20 rolls
- `roll(self, notation: str, advantage: bool=False, disadvantage: bool=False)` - Roll dice using standard notation.
- `roll_exploding(self, notation: str, explode_on: Optional[List[int]]=None)` - Roll with exploding dice (roll again on max).
- `roll_hit_points(self, hit_die: int, con_modifier: int, level: int)` - Roll hit points for leveling up.
- `roll_initiative(self, dex_modifier: int, bonus: int=0)` - Roll initiative for combat.
- `roll_multiple(self, notation: str, count: int)` - Roll the same dice notation multiple times.
- `roll_on_table(self, table: List[Tuple[int, any]])` - Roll on a weighted table.
- `roll_percentile(self)` - Roll d100 (percentile dice)
- `roll_stats(self, method: str='standard')` - Roll ability scores for character creation.
- `roll_with_reroll(self, notation: str, reroll_on: List[int], max_rerolls: int=1)` - Roll with reroll mechanic.
- `attack_roll(bonus: int, advantage: bool=False, disadvantage: bool=False)` - Make an attack roll.
- `d20(modifier: int=0, advantage: bool=False, disadvantage: bool=False)` - Quick d20 roll with modifier
- `saving_throw(ability_mod: int, proficiency: int=0, advantage: bool=False)` - Make a saving throw
- `skill_check(ability_mod: int, proficiency: int=0, expertise: bool=False, advantage: bool=False)` - Make a skill check

## core - `src/talekeeper/services/downtime_activities.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_calculate_lifestyle_cost(self, lifestyle: str, character_level: int)` - Inferred from name: calculate lifestyle cost.
- `_ensure_tables(self)` - Inferred from name: ensure tables.
- `_get_character_data(self, character_id: str)` - Inferred from name: get character data.
- `_resolve_carousing_result(self, roll: int, lifestyle_cost: int)` - Inferred from name: resolve carousing result.
- `carousing(self, character_id: str, character_level: int)` - Inferred from name: carousing.
- `get_activity_history(self, character_id: str, limit: int=10)` - Inferred from name: get activity history.
- `prayer(self, character_id: str, character_level: int)` - Inferred from name: prayer.

## core - `src/talekeeper/services/dynamic_action_service.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_add_basic_actions(self, action_cards: Dict[str, List[Dict[str, Any]]])` - Add basic combat actions that all characters have
- `_create_action_cards(self, features: List[Dict[str, Any]], action_type: str)` - Create action cards from feature data
- `_customize_action_surge_card(self, feature: Dict[str, Any])` - Customize the Action Surge card
- `_customize_cunning_action_card(self, feature: Dict[str, Any])` - Customize the Cunning Action card
- `_customize_rage_card(self, feature: Dict[str, Any])` - Customize the rage action card with specific mechanics
- `_customize_second_wind_card(self, feature: Dict[str, Any])` - Customize the Second Wind card
- `_generate_tooltip(self, feature: Dict[str, Any])` - Generate a tooltip for the feature
- `_is_feature_available(self, feature: Dict[str, Any])` - Check if a feature is currently available for use
- `get_action_cards(self, character_id: str)` - Get all action cards for a character organized by action type
- `get_spellcasting_actions(self, character_id: str, class_id: str)` - Get spellcasting-related action cards

## core - `src/talekeeper/services/dynamic_feature_manager.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_calculate_feature_uses(self, mechanics: Dict[str, Any], level: int)` - Calculate max uses and recharge type based on feature mechanics
- `_character_has_feature(self, cursor, character_id: str, feature_name: str, source: str)` - Check if character already has this feature
- `_check_prerequisites(self, cursor, character_id: str, prerequisites: Dict[str, Any])` - Check if character meets prerequisites for a feature
- `_insert_character_feature(self, cursor, feature: FeatureInstance)` - Insert a character feature into the database
- `configure_feature(self, character_id: str, feature_name: str, configuration: Dict[str, Any])` - Update feature configuration (e.g., chosen fighting style, expertise skills)
- `get_character_features(self, character_id: str, active_only: bool=True)` - Get all features for a character
- `get_feature_progression_summary(self, class_id: str, subclass_id: Optional[str]=None)` - Get a summary of features by level for a class/subclass
- `grant_class_features_for_level(self, character_id: str, class_id: str, level: int)` - Grant all class features for a specific level
- `grant_subclass_features_for_level(self, character_id: str, subclass_id: str, level: int)` - Grant all subclass features for a specific level
- `recharge_features(self, character_id: str, recharge_type: str)` - Recharge features that use the specified recharge type
- `update_feature_uses(self, character_id: str, feature_name: str, current_uses: int)` - Update the current uses of a feature

## core - `src/talekeeper/services/encounter_avoidance.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_award_xp(self, character_id: str, xp_amount: int)` - Award XP to character.
- `_calculate_avoidance_xp(self, monsters: List[Dict])` - Calculate XP reward for avoiding encounter.
- `_get_xp_thresholds(self, level: int)` - Get XP thresholds for encounter difficulty by character level.
- `attempt_avoidance(self, character_id: str, character_data: Dict, monsters: List[Dict])` - Attempt to avoid an encounter using Stealth.
- `can_attempt_avoidance(self, character_id: str, monsters: List[Dict])` - Check if character can attempt to avoid this encounter.
- `get_encounter_difficulty(self, monsters: List[Dict], character_level: int)` - Estimate encounter difficulty for avoidance context.

## core - `src/talekeeper/services/enhanced_subclass_manager.py`

- `create()` - Create the Berserker subclass definition.
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_ensure_tables(self)` - Create enhanced subclass tables if needed.
- `apply_mindless_rage(self, character_id: str)` - Apply Mindless Rage immunity when raging.
- `check_frenzy_trigger(self, character_id: str)` - Check if Frenzy damage should be applied.
- `get_character_subclass_features(self, character_id: str, level: int)` - Get all subclass features available to a character at their level.
- `get_subclass_definition(self, class_name: str, subclass_name: str)` - Get a subclass definition using the registry.
- `remove_rage_immunities(self, character_id: str)` - Remove Mindless Rage immunities when rage ends.
- `reset_resources(self, character_id: str, rest_type: str)` - Reset subclass resources on rest.
- `use_intimidating_presence(self, character_id: str)` - Use Intimidating Presence ability.
- `get_features_at_level(self, level: int)` - Get all features available at a specific level.
- `get_features_by_type(self, feature_type: FeatureType)` - Get all features of a specific type.
- `from_dict(cls, data: Dict[str, Any])` - Create from dictionary.
- `to_dict(self)` - Convert to dictionary for storage.

## core - `src/talekeeper/services/equipment.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `get_armor_ac(self, armor_name: str, dex_modifier: int)` - Calculate AC for armor based on database properties and character's dex.
- `get_item(self, item_name: str)` - Get equipment item data by name from talekeeper.database.
- `get_items_by_type(self, item_type: str)` - Get all items of a specific type (weapon, armor, etc.).
- `get_shield_ac_bonus(self, shield_name: str)` - Get AC bonus from shield. Shields typically give +2 AC.
- `get_weapon_properties(self, weapon_name: str)` - Get weapon properties for damage calculations.
- `is_armor(self, item_name: str)` - Check if item is armor.
- `is_shield(self, item_name: str)` - Check if item is a shield.
- `is_weapon(self, item_name: str)` - Check if item is a weapon.

## core - `src/talekeeper/services/equipment_database.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_fetch_base_weapon(self, conn: sqlite3.Connection, base_name: str)` - Inferred from name: fetch base weapon.
- `_hydrate_weapon_defaults(self, conn: sqlite3.Connection, item: Dict[str, Any])` - Inferred from name: hydrate weapon defaults.
- `_infer_base_weapon_name(self, name: str)` - Infer the non-magical base weapon name from a variant.
- `get_all_equipment(self)` - Get all equipment from the database.
- `get_equipment_by_name(self, name: str)` - Get a specific equipment item by name.
- `get_equipment_by_rarity(self, rarities: List[str])` - Get equipment filtered by rarity.
- `get_equipment_lookup(self)` - Get all equipment as a lookup dictionary by name.
- `get_weapons(self)` - Get all weapons from the database.

## core - `src/talekeeper/services/feat_effects.py`

- `__init__(self, feats_file_path: str=None)` - Initialize with feat data.
- `_apply_ability_score_effect(self, character_data: Dict, effect: FeatEffect)` - Apply ability score bonuses from feats.
- `_apply_combat_effect(self, character_data: Dict, effect: FeatEffect)` - Apply combat-related effects from feats.
- `_apply_hit_point_effect(self, character_data: Dict, effect: FeatEffect)` - Apply hit point bonuses from feats.
- `_apply_proficiency_effect(self, character_data: Dict, effect: FeatEffect)` - Apply proficiency bonuses from feats.
- `_apply_resource_effect(self, character_data: Dict, effect: FeatEffect)` - Apply resource-based effects from feats.
- `_get_ability_score_effects(self, feat_data: Dict)` - Check if feat provides ability score improvements.
- `_get_combat_effects(self, feat_data: Dict)` - Check if feat provides combat-related effects.
- `_get_hit_point_effect(self, feat_data: Dict)` - Check if feat provides hit point bonuses.
- `_get_proficiency_effects(self, feat_data: Dict)` - Check if feat provides proficiency bonuses.
- `_get_spell_effects(self, feat_data: Dict)` - Check if feat provides additional spells.
- `_load_feats_data(self, feats_file_path: str=None)` - Load feat data from talekeeper.database.
- `apply_feat_effects_to_character(self, character_data: Dict, feat_names: List[str])` - Apply all feat effects to a character's data.
- `get_feat_effects(self, feat_name: str)` - Get all mechanical effects for a given feat.

## core - `src/talekeeper/services/feature_registry.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_get_class_feature_details(self, feature_id: int)` - Get detailed information about a class feature
- `_get_subclass_feature_details(self, feature_id: int)` - Get detailed information about a subclass feature
- `get_all_class_features(self, class_id: str, max_level: int=20)` - Get all class features up to max_level, organized by level
- `get_available_subclasses(self, class_id: str)` - Get available subclasses for a class
- `get_character_features(self, character_id: str)` - Get all active features for a character
- `get_class_features_for_level(self, class_id: str, level: int)` - Get all class features available at a specific level
- `get_features_by_type(self, character_id: str, feature_type: str)` - Get character features filtered by type (action, bonus_action, reaction, etc.)
- `get_subclass_features_for_level(self, subclass_id: str, level: int)` - Get all subclass features available at a specific level
- `get_subclass_selection_level(self, class_id: str)` - Get the level at which a class selects its subclass
- `grant_feature_to_character(self, character_id: str, feature_source: str, feature_id: int, feature_name: str, level_gained: int, max_uses: int=0, recharge_type: str='permanent', configuration: Dict[str, Any]=None)` - Grant a feature to a character
- `recharge_features(self, character_id: str, recharge_type: str)` - Recharge features based on rest type
- `update_feature_uses(self, character_id: str, feature_name: str, uses_spent: int)` - Update the current uses of a feature

## core - `src/talekeeper/services/fighter_abilities.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_apply_heroic_warrior(self, cursor: sqlite3.Cursor, character_id: str, character: Dict[str, Any], level: int)` - Internal helper to handle Heroic Warrior start-of-turn logic.
- `_apply_survivor(self, cursor: sqlite3.Cursor, character_id: str, character: Dict[str, Any], level: int)` - Internal helper to handle Survivor start-of-turn logic.
- `_dedupe(items)` - Inferred from name: dedupe.
- `_ensure_combat_state(self, cursor: sqlite3.Cursor, character_id: str)` - Ensure a combat state row exists for the character.
- `_get_connection(self)` - Get database connection.
- `check_heroic_warrior(self, character_id: str)` - Public wrapper to process Heroic Warrior start-of-turn effect.
- `check_survivor(self, character_id: str)` - Public wrapper to process Survivor start-of-turn effect.
- `get_character_subclass(self, character_id: str)` - Get the fighter subclass for a character.
- `get_fighter_level(self, character_id: str)` - Get the fighter class level for a character.
- `get_remarkable_athlete_jump_bonus(self, character_id: str)` - Get jump distance bonus from Remarkable Athlete.
- `has_defy_death(self, character_id: str)` - Check if character has Defy Death (Champion 18).
- `has_remarkable_athlete(self, character_id: str)` - Return True if the character qualifies for Remarkable Athlete.
- `has_studied_attacks_advantage(self, character_id: str, target_id: str)` - Check if character has advantage from Studied Attacks.
- `process_champion_turn_start(self, character_id: str)` - Apply Champion subclass start-of-turn effects and return outcome details.
- `rest_fighter_resources(self, character_id: str, rest_type: str)` - Reset fighter resources on rest.
- `roll_death_save(self, character_id: str)` - Roll a death saving throw with Defy Death if available.
- `roll_skill_check(self, character_id: str, skill_name: str, ability_modifier: int, proficiency_bonus: int=0, proficient: bool=False, expertise: bool=False, base_context: Optional[Dict[str, Any]]=None)` - Roll a skill check with automatic Remarkable Athlete integration.
- `update_fighter_resources_for_level(self, character_id: str, level: int)` - Update fighter resource maximums based on level.
- `update_studied_attacks(self, character_id: str, target_id: str, hit: bool)` - Update Studied Attacks state after an attack.
- `use_action_surge(self, character_id: str)` - Use Action Surge ability.
- `use_indomitable(self, character_id: str, save_roll: int, save_bonus: int)` - Use Indomitable to reroll a failed save.
- `use_second_wind(self, character_id: str)` - Use Second Wind ability.
- `use_tactical_mind(self, character_id: str, check_result: int, dc: int)` - Use Tactical Mind to boost an ability check.

## core - `src/talekeeper/services/hazard_service.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `apply_gear_bonus(self, hazard: Dict[str, Any], gear_items: List[str])` - Inferred from name: apply gear bonus.
- `get_hazard_by_id(self, hazard_id: int)` - Inferred from name: get hazard by id.
- `get_hazards_for_level(self, character_level: int)` - Inferred from name: get hazards for level.
- `get_random_hazard(self, character_level: int)` - Inferred from name: get random hazard.

## core - `src/talekeeper/services/hex_coordinate_system.py`

- `get_all_neighbors(q: int, r: int)` - Inferred from name: get all neighbors.
- `get_direction_index(from_q: int, from_r: int, to_q: int, to_r: int)` - Inferred from name: get direction index.
- `get_direction_name(direction: int)` - Inferred from name: get direction name.
- `get_distance(q1: int, r1: int, q2: int, r2: int)` - Inferred from name: get distance.
- `get_hexes_in_radius(center_q: int, center_r: int, radius: int)` - Inferred from name: get hexes in radius.
- `get_neighbor(q: int, r: int, direction: int)` - Inferred from name: get neighbor.
- `hex_round(q: float, r: float)` - Inferred from name: hex round.
- `hex_to_pixel(q: int, r: int, hex_size: float)` - Inferred from name: hex to pixel.
- `pixel_to_hex(x: float, y: float, hex_size: float)` - Inferred from name: pixel to hex.

## core - `src/talekeeper/services/hex_event_logger.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_format_enemy_list(self, enemies: List[Dict])` - Inferred from name: format enemy list.
- `_generate_combat_narrative(self, combat_result: Dict)` - Inferred from name: generate combat narrative.
- `_get_character_level(self, character_id: str)` - Inferred from name: get character level.
- `_get_connection(self)` - Inferred from name: get connection.
- `get_all_character_events(self, character_id: str)` - Inferred from name: get all character events.
- `get_hex_events(self, character_id: str, q: int, r: int)` - Inferred from name: get hex events.
- `log_combat_event(self, character_id: str, q: int, r: int, combat_result: Dict)` - Inferred from name: log combat event.
- `log_landmark_event(self, character_id: str, q: int, r: int, landmark_data: Dict)` - Inferred from name: log landmark event.
- `log_resource_event(self, character_id: str, q: int, r: int, resource_data: Dict)` - Inferred from name: log resource event.
- `log_travel_event(self, character_id: str, q: int, r: int, hex_data: Dict)` - Inferred from name: log travel event.

## core - `src/talekeeper/services/hex_map_service.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_generate_hex(self, character_id: str, q: int, r: int)` - Inferred from name: generate hex.
- `_generate_settlement_type(self)` - Inferred from name: generate settlement type.
- `_get_connection(self)` - Inferred from name: get connection.
- `_get_position_seed(self, q: int, r: int)` - Inferred from name: get position seed.
- `_mark_hex_visited(self, character_id: str, q: int, r: int)` - Inferred from name: mark hex visited.
- `_reveal_hex(self, character_id: str, q: int, r: int)` - Inferred from name: reveal hex.
- `get_character_position(self, character_id: str)` - Inferred from name: get character position.
- `get_exploration_stats(self, character_id: str)` - Inferred from name: get exploration stats.
- `get_hex(self, character_id: str, q: int, r: int)` - Inferred from name: get hex.
- `get_hex_settlement(self, character_id: str, q: int, r: int)` - Inferred from name: get hex settlement.
- `get_visible_hexes(self, character_id: str, center_q: int, center_r: int, radius: int=3)` - Inferred from name: get visible hexes.
- `initialize_character_position(self, character_id: str)` - Inferred from name: initialize character position.
- `travel_to_hex(self, character_id: str, target_q: int, target_r: int)` - Inferred from name: travel to hex.

## core - `src/talekeeper/services/hex_scouting_service.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_assess_danger(self, encounter_data: Dict)` - Inferred from name: assess danger.
- `_basic_hex_info(self, hex_data: Dict)` - Inferred from name: basic hex info.
- `_calculate_encounter_cr(self, hex_data: Dict)` - Inferred from name: calculate encounter cr.
- `_check_for_encounter(self, hex_data: Dict)` - Inferred from name: check for encounter.
- `_get_character(self, character_id: str)` - Inferred from name: get character.
- `_get_connection(self)` - Inferred from name: get connection.
- `_get_encounter_dc(self, encounter_data: Dict)` - Inferred from name: get encounter dc.
- `_get_encounter_hints(self, character: Dict, encounter_data: Dict, margin: int)` - Inferred from name: get encounter hints.
- `_get_monster_type(self, biome: str)` - Inferred from name: get monster type.
- `_get_nature_details(self, hex_data: Dict, margin: int)` - Inferred from name: get nature details.
- `_get_skill_bonus(self, character: Dict, skill: str)` - Inferred from name: get skill bonus.
- `_get_survival_details(self, hex_data: Dict, margin: int)` - Inferred from name: get survival details.
- `_get_terrain_dc(self, biome: str)` - Inferred from name: get terrain dc.
- `_roll_check(self, bonus: int)` - Inferred from name: roll check.
- `format_scouting_html(self, scouting_info: Dict)` - Inferred from name: format scouting html.
- `scout_hex(self, character_id: str, hex_q: int, hex_r: int, hex_data: Dict)` - Inferred from name: scout hex.

## core - `src/talekeeper/services/item_effects.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_ensure_tables(self)` - Ensure magical bonuses table exists.
- `_get_attuned_items(self, character_id: str)` - Get set of attuned item keys for character.
- `_get_item_bonuses(self, item: Dict, is_attuned: bool=False)` - Extract magical bonuses from an item.
- `_get_item_key(self, item: Dict)` - Generate unique key for item for attunement tracking.
- `_requires_attunement(self, item_name: str)` - Check if item requires attunement by querying database.
- `_save_bonuses_to_database(self, character_id: str, bonuses: Dict[str, int])` - Save calculated bonuses to database.
- `calculate_bonuses_for_character(self, character_id: str, equipped_items: Dict)` - Calculate magical bonuses from all equipped items for a character.
- `get_character_bonuses(self, character_id: str)` - Get saved bonuses for a character from talekeeper.database.
- `set_attunement(self, character_id: str, item_key: str, attune: bool)` - Set or remove attunement for an item.

## core - `src/talekeeper/services/level_up.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_feat_hp_bonus(self, cursor, character_id: str)` - Get HP bonus per level from feats.
- `_get_hit_die_for_class(self, class_name: str)` - Get hit die size for class.
- `_get_species_hp_bonus(self, cursor, character_id: str)` - Get HP bonus per level from species traits.
- `_grant_class_features(self, cursor, character_id: str, class_name: str, class_level: int)` - Grant class features for the new level.
- `_grant_fighter_features(self, cursor, character_id: str, level: int)` - Grant Fighter-specific features.
- `_grant_rogue_features(self, cursor, character_id: str, level: int)` - Grant Rogue-specific features.
- `get_available_classes(self)` - Get list of available classes for leveling.
- `get_character_class_levels(self, character_id: str)` - Get current class levels for a character.
- `get_next_level_features(self, character_id: str, class_choice: str)` - Get features that would be gained at next level in chosen class.
- `is_asi_level(self, character_id: str, class_choice: str)` - Check if next level grants ASI for the selected class.
- `level_up_character(self, character_id: str, class_choice: str, subclass_choice: Optional[str]=None)` - Level up character in chosen class.
- `recalculate_character_hp(self, character_id: str)` - Recalculate a character's HP to include species and feat bonuses that may be missing.

## core - `src/talekeeper/services/level_up_integration.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_handle_class_specific_updates(self, cursor, character_id: str, class_id: str, level: int)` - Handle class-specific level up effects (HP, spell slots, etc.)
- `_update_barbarian_progression(self, cursor, character_id: str, level: int)` - Update barbarian-specific progression
- `_update_fighter_progression(self, cursor, character_id: str, level: int)` - Update fighter-specific progression
- `_update_rogue_progression(self, cursor, character_id: str, level: int)` - Update rogue-specific progression
- `_update_spellcaster_progression(self, cursor, character_id: str, class_id: str, level: int)` - Update spell slot progression for spellcasters
- `get_features_for_level(self, class_id: str, level: int, subclass_id: str=None)` - Get list of features that would be granted at a specific level
- `get_level_up_preview(self, character_id: str, target_level: int)` - Preview what features would be gained at target level
- `handle_level_up(self, character_id: str, new_level: int)` - Handle level up using dynamic feature system
- `is_subclass_selection_level(self, class_id: str, level: int)` - Check if this level requires subclass selection
- `migrate_character_to_dynamic_system(self, character_id: str)` - Migrate an existing character to use the dynamic feature system

## core - `src/talekeeper/services/long_rest_service.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_create_lifestyle_option(self, lifestyle: str, settlement_name: Optional[str], accommodation_name: Optional[str])` - Create lifestyle option dict.
- `_spend_gold(self, cursor: sqlite3.Cursor, character_id: str, amount_gp: float)` - Internal helper to deduct gold without closing the connection.
- `apply_condition(self, character_id: str, condition: str, duration_hours: int)` - Apply condition to character.
- `apply_damage(self, character_id: str, damage: int, damage_type: str)` - Apply damage to character.
- `apply_gold_loss(self, character_id: str, gold_formula: str)` - Apply gold loss to character.
- `apply_long_rest_benefits(self, character_id: str)` - Apply long rest benefits: restore HP, spell slots, abilities.
- `check_hazard_trigger(self, lifestyle: str)` - Check if wretched/squalid triggers hazard.
- `deduct_lifestyle_cost(self, character_id: str, lifestyle_cost: float)` - Deduct gold from character_inventory. Returns True if successful.
- `get_available_lifestyles(self, character_id: str, q: int, r: int)` - Get available lifestyle options for hex settlement.
- `get_character_gold(self, character_id: str)` - Get total gold (in gp) from the character's inventory.
- `get_character_rest_status(self, character_id: str)` - Return HP/Hit Dice snapshot for rest calculations (handles legacy schemas).
- `record_rest(self, character_id: str, q: int, r: int, lifestyle: str, lifestyle_cost: float, hazard_triggered: bool, hazard_type: Optional[str], hazard_result: Optional[str])` - Record long rest in database.
- `roll_damage(self, formula: str)` - Roll damage dice (e.g., '2d6', '1d8').
- `roll_unique_lifestyles(pool: List[str], rolls: int)` - Return up to `rolls` unique lifestyles from pool.

## core - `src/talekeeper/services/loot_drop_service.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_equipment_by_name(self, item_name: str)` - Inferred from name: get equipment by name.
- `cr_to_rarity(self, cr_numeric: float)` - Inferred from name: cr to rarity.
- `drop_loot(self, character_id: str, character_data: dict, rarity: str, exclude_items: Optional[Set[str]]=None)` - Drop loot for a character based on BiS system.
- `get_bis_items_for_rarity(self, class_build: str, rarity: str)` - Inferred from name: get bis items for rarity.
- `get_character_build(self, character_data: dict)` - Inferred from name: get character build.
- `get_other_items_for_rarity(self, rarity: str, owned_items: Set[str])` - Inferred from name: get other items for rarity.
- `get_player_inventory(self, character_id: str)` - Inferred from name: get player inventory.

## core - `src/talekeeper/services/monster_ability_manager.py`

- `to_dict(self)` - Convert to dictionary.
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_apply_condition(self, character_id: str, condition_name: str, source: str, save_dc: Optional[int]=None, save_ability: Optional[str]=None)` - Apply a condition to a character.
- `_ensure_tables(self)` - Create ability tracking tables if they don't exist.
- `_get_connection(self)` - Get database connection.
- `_roll_saving_throw(self, target: Dict[str, Any], ability: str, dc: int)` - Roll a saving throw for a target.
- `attempt_recharge(self, encounter_id: str, monster_id: str, ability_name: str)` - Attempt to recharge an ability at the start of the monster's turn.
- `execute_ability(self, encounter_id: str, monster_id: str, monster_name: str, ability: MonsterAbility, target_id: str, target_data: Dict[str, Any])` - Execute a monster ability against a target.
- `get_ability_state(self, encounter_id: str, monster_id: str, ability_name: str)` - Get the current state of an ability.
- `get_all_monster_abilities(self, encounter_id: str, monster_id: str)` - Get all abilities for a monster in an encounter.
- `initialize_ability(self, encounter_id: str, monster_id: str, ability: MonsterAbility)` - Initialize an ability for tracking in an encounter.
- `reset_daily_abilities(self, encounter_id: str, monster_id: str)` - Reset all daily abilities (called on long rest).
- `use_ability(self, encounter_id: str, monster_id: str, ability_name: str)` - Mark an ability as used.

## core - `src/talekeeper/services/monster_attack_parser.py`

- `_determine_attack_type(self, text: str)` - Determine if attack is melee, ranged, or special.
- `_entries_to_text(self, entries: List[Any])` - Convert entries list to plain text.
- `_extract_additional_damage(self, text: str)` - Extract additional damage (like poison) beyond primary damage.
- `_extract_attack_bonus(self, text: str)` - Extract attack bonus from text.
- `_extract_automatic_conditions(self, text: str, attack_name: str)` - Extract conditions applied automatically on hit (no save required).
- `_extract_conditional_effects(self, text: str, attack_name: str)` - Extract effects with special triggers.
- `_extract_effects(self, text: str, attack_name: str)` - Extract special effects from attack text.
- `_extract_primary_damage(self, text: str)` - Extract primary damage dice and type.
- `_extract_range(self, text: str)` - Extract normal/long range for ranged attacks.
- `_extract_reach(self, text: str)` - Extract reach in feet.
- `_extract_save_effects(self, text: str, attack_name: str)` - Extract effects that require saving throws.
- `_is_attack_action(self, action: Dict[str, Any])` - Check if an action represents an attack.
- `_parse_attack_action(self, action: Dict[str, Any])` - Parse a single attack action into structured data.
- `get_attack_summary(self, attack: ParsedAttack)` - Get a human-readable summary of the attack.
- `parse_monster_actions(self, actions_json: str)` - Parse monster actions from database JSON.
- `__post_init__(self)` - Inferred from name: post init.

## core - `src/talekeeper/services/monster_attack_processor.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_calculate_average_damage(self, dice_expr: str)` - Calculate average damage from dice expression.
- `_extract_attack_bonus(self, text: str)` - Extract attack bonus from attack text.
- `_extract_automatic_conditions(self, text: str)` - Extract conditions applied automatically on hit.
- `_extract_condition_effects(self, text: str, attack_name: str)` - Extract conditions that require saving throws.
- `_extract_damage(self, text: str)` - Extract damage dice, type, and average from attack text.
- `_extract_effects(self, text: str, attack_name: str)` - Extract special effects from attack text.
- `_extract_poison_effects(self, text: str)` - Extract poison damage with potential condition effects.
- `_extract_reach(self, text: str)` - Extract reach from attack text.
- `_is_attack_action(self, action: Dict[str, Any])` - Check if an action is an attack.
- `_map_condition_name(self, condition_name: str)` - Map condition name strings to ConditionType enum.
- `_parse_attack_action(self, action: Dict[str, Any])` - Parse a single attack action.
- `_process_condition_effect(self, effect: AttackEffect, character_id: str, result: Dict[str, Any])` - Process a condition effect from an attack.
- `apply_saving_throw_result(self, character_id: str, save_data: Dict[str, Any], roll_result: int, success: bool)` - Apply the result of a saving throw.
- `execute_monster_attack(self, attack: MonsterAttack, target_character_id: str, attack_roll: int, target_ac: int)` - Execute a monster attack against a character.
- `parse_monster_actions(self, actions_json: str)` - Parse monster actions from database JSON into structured attacks.

## core - `src/talekeeper/services/monster_knowledge.py`

- `__init__(self)` - Initialize the monster knowledge service.
- `_parse_attacks(self, actions_field)` - Parse and summarize attack actions.
- `_parse_cr(self, cr_string: str)` - Parse CR string to numeric value.
- `_parse_json_field(self, field_value)` - Parse a JSON field that might be a string or already a list.
- `_parse_special_abilities(self, abilities_field)` - Parse and summarize special abilities.
- `calculate_dc(self, challenge_rating: str)` - Calculate the DC for a monster knowledge check.
- `check_knowledge(self, monster_data: Dict, skill_check_result: int, skill_used: str)` - Perform a monster knowledge check and determine what information is revealed.
- `format_tooltip_html(self, knowledge: MonsterKnowledge, skill_used: str, roll_result: int)` - Format monster knowledge as HTML for tooltip display.
- `get_applicable_skills(self, monster_type: str)` - Get list of skills that can be used to identify this monster type.

## core - `src/talekeeper/services/morale_manager.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_ensure_morale_table(self)` - Ensure combat_morale_status table exists
- `check_morale_trigger(self, encounter_id: str, monster_id: str, current_hp: int, is_solo: bool=False)` - Check if morale threshold has been crossed.
- `clear_encounter_morale(self, encounter_id: str)` - Clear morale tracking for an encounter (called when combat ends)
- `get_highest_wisdom_modifier(self, monster_ids: List[str])` - Get highest Wisdom modifier from a group of monsters
- `get_morale_status(self, encounter_id: str, monster_id: str)` - Get current morale status for a monster
- `get_wisdom_modifier(self, monster_id: str)` - Get Wisdom modifier for a monster
- `roll_morale_check(self, encounter_id: str, monster_id: str, group_monster_ids: Optional[List[str]]=None)` - Roll a morale check (DC 15 Wisdom save).
- `track_combat_start(self, encounter_id: str, monster_id: str, monster_name: str, initial_count: int, initial_hp: int)` - Record initial monster state for morale tracking
- `update_monster_count(self, encounter_id: str, monster_id: str, current_count: int)` - Update current monster count for morale tracking

## core - `src/talekeeper/services/paladin_abilities.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_add_oath_spells(self, cursor, character_id: str, oath: str, level: int)` - Add oath spells that are always prepared.
- `_apply_oath_features(self, cursor, character_id: str, oath: str, level: int)` - Apply oath features based on character level.
- `_get_spell_level(self, spell_id: str)` - Get spell level from spell registry.
- `_initialize_core_features(self, cursor, character_id: str, level: int)` - Initialize core paladin features.
- `divine_smite(self, character_id: str, spell_slot_level: int, target_is_undead_or_fiend: bool=False, use_free_smite: bool=False)` - Calculate Divine Smite damage.
- `get_paladin_info(self, character_id: str)` - Get comprehensive paladin information.
- `has_free_divine_smite(self, character_id: str)` - Check if the paladin has their free Divine Smite available.
- `initialize_paladin_character(self, character_id: str, oath: str='devotion')` - Initialize a character as a Paladin with the specified sacred oath.
- `long_rest_recovery(self, character_id: str)` - Handle long rest recovery for paladins.
- `use_channel_divinity(self, character_id: str, ability_name: str)` - Use Channel Divinity.
- `use_lay_on_hands(self, character_id: str, healing_points: int)` - Use Lay on Hands to heal.
- `get_paladin_service(db_path: str='talekeeper.db')` - Get singleton paladin service instance.

## core - `src/talekeeper/services/parlay_system.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_add_treasure_to_inventory(self, character_id: str, treasure: Dict)` - Add treasure item to character inventory.
- `_award_pickpocket_xp(self, character_id: str, xp_amount: int)` - Award XP for successful pickpocket.
- `_determine_if_evil(self, alignment: str)` - Determine if creature is evil based on alignment.
- `_generate_individual_treasure(self, monster: Dict)` - Generate individual treasure based on monster CR.
- `_get_character_level(self, character_id: str)` - Get character level from talekeeper.database.
- `_get_character_skill_bonus(self, character_id: str, skill_name: str)` - Get character skill bonus (ability modifier + proficiency if applicable).
- `_get_intelligent_evil_skills(self)` - Deception + Intimidation + 1 random skill/tool (dangerous negotiation).
- `_get_intelligent_non_evil_skills(self)` - 2 random CHA skills + 1 random INT/WIS skill (diplomatic negotiation).
- `_get_monster_insight(self, monster: Dict)` - Get monster Insight DC.
- `_get_monster_perception(self, monster: Dict)` - Get monster Perception DC.
- `_get_most_powerful_monster(self, monsters: List[Dict])` - Get most powerful monster by XP.
- `_get_simple_evil_skills(self)` - Nature + Survival + 1 from very limited pool (desperate parlay).
- `_get_simple_non_evil_skills(self)` - Nature + Survival + 1 from limited pool (animal handling).
- `apply_parlay_success(self, character_id: str, xp_reward: int)` - Apply the rewards for successful parlay.
- `calculate_parlay_xp_reward(self, monsters: List[Dict])` - Calculate XP reward for successful parlay.
- `can_parlay_with_encounter(self, monsters: List[Dict])` - Check if an encounter can be parlayed with.
- `can_parlay_with_monster(self, monster: Dict)` - Determine if a monster can be parlayed with.
- `create_parlay_challenge(self, character_id: str, monsters: List[Dict])` - Create a skill challenge for parlay attempt.
- `execute_pickpocket_attempt(self, character_id: str, monsters: List[Dict])` - Execute pickpocket attempt with dual skill checks.
- `get_parlay_skills(self)` - Get the skills available for parlay (legacy method).
- `get_parlay_skills_for_encounter(self, monsters: List[Dict])` - Get parlay skills based on monster intelligence and alignment.

## core - `src/talekeeper/services/proficiency_bonus.py`

- `get_proficiency_bonus(character_level: int)` - Get proficiency bonus based on character level.
- `get_proficiency_bonus_from_character(character: dict)` - Get proficiency bonus from character dict.
- `get_proficiency_bonus_from_context(context: dict)` - Get proficiency bonus from character context.

## core - `src/talekeeper/services/proficiency_system.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_connection(self)` - Inferred from name: get connection.
- `_get_skill_expertise(self, cursor, character_id: str)` - Inferred from name: get skill expertise.
- `_normalize_skill_name(self, skill: Any)` - Inferred from name: normalize skill name.
- `_parse_skill_list(self, raw: Any)` - Inferred from name: parse skill list.
- `add_feat_proficiencies(self, character_id: str, feat_name: str, selected_proficiencies: List[str]=None, conn=None)` - Add proficiencies from a feat (like Skilled).
- `add_proficiency(self, character_id: str, prof_type: str, prof_name: str, source: str='manual', conn=None)` - Inferred from name: add proficiency.
- `calculate_skill_bonus(self, character_id: str, skill_name: str, ability_mod: int)` - Inferred from name: calculate skill bonus.
- `get_attack_bonus(self, character_id: str, weapon_name: str, ability_mod: int)` - Inferred from name: get attack bonus.
- `get_background_proficiencies(self, background_id: str)` - Get fixed proficiencies from a background.
- `get_character_proficiencies(self, character_id: str)` - Inferred from name: get character proficiencies.
- `get_class_skill_choices(self, class_id: str)` - Get skill selection options for a class.
- `get_saving_throw_bonus(self, character_id: str, ability: str)` - Inferred from name: get saving throw bonus.
- `get_species_proficiencies(self, species_id: str)` - Get proficiencies and choices from a species.
- `initialize_character_proficiencies(self, character_id: str, class_id: str, background: Optional[str]=None, race_id: Optional[str]=None, selected_skills: List[str]=None, selected_class_skills: List[str]=None, selected_species_skills: List[str]=None, conn=None)` - Inferred from name: initialize character proficiencies.
- `is_proficient_in_skill(self, character_id: str, skill_name: str)` - Inferred from name: is proficient in skill.
- `is_proficient_with_armor(self, character_id: str, armor_name: str)` - Inferred from name: is proficient with armor.
- `is_proficient_with_shield(self, character_id: str)` - Inferred from name: is proficient with shield.
- `is_proficient_with_weapon(self, character_id: str, weapon_name: str)` - Inferred from name: is proficient with weapon.
- `remove_proficiency(self, character_id: str, prof_type: str, prof_name: str)` - Inferred from name: remove proficiency.

## core - `src/talekeeper/services/racial_trait_effects.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_connection(self)` - Inferred from name: get connection.
- `_parse_trait_to_effect(self, trait_name: str, race_id: str, description: str)` - Inferred from name: parse trait to effect.
- `apply_racial_hp_bonus(self, race_id: str, level: int)` - Inferred from name: apply racial hp bonus.
- `check_racial_ability_available(self, character_id: str, ability_name: str)` - Inferred from name: check racial ability available.
- `get_race_traits(self, race_id: str)` - Inferred from name: get race traits.
- `get_racial_damage_bonus(self, character_id: str, character_race: str=None, target_hp_after_hit: int=None)` - Inferred from name: get racial damage bonus.
- `initialize_racial_resources(self, character_id: str, race_id: str, level: int)` - Inferred from name: initialize racial resources.
- `reset_fires_burn_tracking(self, character_id: str)` - Inferred from name: reset fires burn tracking.

## core - `src/talekeeper/services/ritual_casting_service.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_apply_ritual_spell_effects(self, cursor, character_id: str, spell_id: str, target_data: Dict[str, Any])` - Apply the effects of a ritual spell.
- `_calculate_ritual_casting_time(self, normal_casting_time: str)` - Calculate ritual casting time (normal + 10 minutes).
- `_character_has_ritual_casting(self, cursor, character_id: str)` - Check if character has ritual casting ability from any class.
- `_character_has_spell(self, cursor, character_id: str, spell_id: str)` - Check if character knows or has prepared the spell.
- `_log_ritual_casting(self, cursor, character_id: str, spell_id: str, casting_time: str)` - Log ritual spell casting for tracking.
- `can_cast_as_ritual(self, character_id: str, spell_id: str)` - Check if a character can cast a specific spell as a ritual.
- `cast_ritual_spell(self, character_id: str, spell_id: str, target_data: Dict[str, Any]=None)` - Cast a spell as a ritual (no spell slot consumed).
- `get_ritual_casting_log(self, character_id: str, limit: int=10)` - Get recent ritual casting history for a character.
- `get_ritual_spells_for_character(self, character_id: str)` - Get all ritual spells available to a character.
- `get_ritual_casting_service(db_path: str='talekeeper.db')` - Factory function to get ritual casting service instance.

## core - `src/talekeeper/services/rogue_abilities.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_calculate_sneak_attack_dice(self, level: int)` - Calculate sneak attack dice based on level.
- `_check_ally_within_5_feet(self, character_id: str, target_id: str, attack_context: Dict[str, Any])` - Check if an ally is within 5 feet of the target.
- `_get_connection(self)` - Get database connection.
- `_is_ally_incapacitated(self, ally_id: str)` - Check if an ally is incapacitated.
- `_is_character_incapacitated(self, character_id: str)` - Check if character is incapacitated.
- `_is_proficient_in_skill(self, character_id: str, skill_name: str)` - Check if character is proficient in a skill.
- `_is_sneak_attack_weapon(self, weapon: Dict[str, Any])` - Check if weapon is eligible for sneak attack (finesse or ranged).
- `apply_evasion(self, character_id: str, save_result: Dict[str, Any])` - Apply Evasion to a Dexterity saving throw.
- `apply_reliable_talent(self, character_id: str, skill_roll: int, skill_name: str)` - Apply Reliable Talent to a skill check.
- `calculate_sneak_attack_damage(self, character_id: str)` - Get sneak attack damage dice string for character.
- `check_sneak_attack_eligibility(self, character_id: str, target_id: str, attack_context: Dict[str, Any])` - Check if sneak attack is eligible for this attack.
- `get_character_subclass(self, character_id: str)` - Get character's subclass.
- `get_rogue_features(self, character_id: str)` - Get all rogue features for a character.
- `get_rogue_level(self, character_id: str)` - Get the rogue class level for a character.
- `rest_rogue_resources(self, character_id: str, rest_type: str)` - Reset rogue resources after a rest.
- `update_rogue_resources_for_level(self, character_id: str, level: int)` - Update rogue resource maximums based on level.
- `use_cunning_action(self, character_id: str, action_type: str)` - Use Cunning Action (Dash, Disengage, or Hide as bonus action).
- `use_steady_aim(self, character_id: str)` - Use Steady Aim to gain advantage on next attack.
- `use_stroke_of_luck(self, character_id: str, original_roll: int)` - Use Stroke of Luck to turn a failed d20 test into a 20.
- `use_uncanny_dodge(self, character_id: str, incoming_damage: int)` - Use Uncanny Dodge to halve incoming damage.

## core - `src/talekeeper/services/settlement_name_service.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_determine_highest_lifestyle(self, settlement_type: str)` - Determine highest available lifestyle for settlement type.
- `_generate_syllable_name(self, is_male: bool, rng: random.Random)` - Generate name from syllables (fallback when not using curated lists).
- `generate_inn_name(self, seed: int)` - Generate inn/tavern name using seed-based randomization.
- `generate_settlement_name(self, settlement_type: str, biome: str, seed: int)` - Generate settlement name based on type and biome.
- `generate_worthy_name(self, settlement_type: str, seed: int)` - Generate noble/leader name with title based on settlement type.
- `get_or_create_settlement_names(self, character_id: str, q: int, r: int)` - Get existing names or generate new ones for hex settlement.

## core - `src/talekeeper/services/settlement_population.py`

- `determine_population(settlement_type: Optional[str], seed: int)` - Return a deterministic population representative for a settlement.

## core - `src/talekeeper/services/shop_service.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_calculate_ability_modifier(self, ability_score: int)` - Inferred from name: calculate ability modifier.
- `_calculate_proficiency_bonus(self, level: int)` - Inferred from name: calculate proficiency bonus.
- `_settlement_to_shop_size(self, settlement_type: str)` - Inferred from name: settlement to shop size.
- `calculate_sell_price(self, item_cost: float)` - Inferred from name: calculate sell price.
- `calculate_sell_price_with_character(self, item_cost: float, character_data: Dict[str, Any])` - Inferred from name: calculate sell price with character.
- `generate_hex_shop_inventory(self, settlement_type: str, character_data: Dict[str, Any], hex_seed: int, population_override: Optional[int]=None)` - Inferred from name: generate hex shop inventory.
- `generate_shop_inventory(self, shop_size: ShopSize, markup_percent: float=25.0)` - Inferred from name: generate shop inventory.
- `get_charisma_skill_roll(self, character_data: Dict[str, Any])` - Inferred from name: get charisma skill roll.
- `get_shop_size_by_name(self, size_name: str)` - Inferred from name: get shop size by name.
- `has_crafter_feat(self, character_data: Dict[str, Any])` - Inferred from name: has crafter feat.
- `__init__(self, size_name: str, gold_limit: int, base_items: int, dice_count: int)` - Inferred from name: init.
- `format_currency(gold_amount: float)` - Convert gold amount to appropriate currency display.

## core - `src/talekeeper/services/skill_challenge_manager.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_session_by_id(self, session_id: str)` - Get session by ID.
- `_get_session_disadvantage_mode(self, template_id: str)` - Get disadvantage mode from skill_challenge_metadata.
- `_get_skill_modifiers(self, skill_name: str, character_data: dict)` - Get ability modifier and proficiency bonus for a skill.
- `_save_attempt(self, session_id: str, skill_name: str, ability_modifier: int, proficiency_bonus: int, dc: int, roll_result: int, total_result: int, success: bool)` - Save skill attempt to database.
- `_update_session(self, session: SkillChallengeSession, outcome: Optional[str]=None)` - Update session in database.
- `attempt_skill(self, session_id: str, skill_name: str, character_data: dict)` - Attempt a skill check in the challenge.
- `create_session(self, character_id: str, template: SkillChallengeTemplate)` - Create a new skill challenge session.
- `get_active_session(self, character_id: str)` - Get the active skill challenge session for a character.
- `get_all_templates(self)` - Load all skill challenge templates from talekeeper.database.
- `get_challenge_info_text(self, session: SkillChallengeSession)` - Generate challenge information text for display.
- `get_skill_dc(self, session: SkillChallengeSession, skill_name: str)` - Calculate the DC for a skill based on usage count.
- `get_template_by_id(self, template_id: str)` - Get a specific template by ID.
- `refuse_challenge(self, session_id: str)` - Refuse the challenge and return the refuse outcome.

## core - `src/talekeeper/services/skill_challenge_rewards.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_add_item_to_inventory(self, character_id: str, item_name: str, item_type: str, quantity: int, weight_lb: float, description: str, value_gp: float)` - Add an item to character inventory, stacking if it already exists.
- `_apply_coin_loss(self, character_data: Dict)` - Apply coin loss.
- `_apply_coin_reward(self, character_data: Dict)` - Apply coin reward based on character level.
- `_apply_consumable_reward(self, character_data: Dict)` - Apply consumable item reward.
- `_apply_damage(self, character_data: Dict, damage_desc: str)` - Apply damage to character.
- `_apply_exhaustion(self, character_data: Dict)` - Apply exhaustion condition.
- `_apply_exploration_view(self, character_data: Dict, reward: str)` - Apply exploration view benefit.
- `_apply_forced_encounter(self, character_data: Dict, encounter_desc: str)` - Apply forced encounter effect.
- `_apply_healers_kit(self, character_data: Dict)` - Apply healer's kit to inventory.
- `_apply_healing_potion(self, character_data: Dict)` - Apply healing potion to inventory.
- `_apply_inspiration(self, character_data: Dict)` - Apply inspiration reward.
- `_apply_item_reward(self, character_data: Dict)` - Apply random item reward from equipment database.
- `_apply_poison_condition(self, character_data: Dict)` - Apply poisoned condition.
- `_apply_quest_modifier(self, character_data: Dict, modifier: str)` - Apply quest difficulty modifier.
- `_apply_rations_gain(self, character_data: Dict)` - Apply ration gain (food/water supplies).
- `_apply_rations_loss(self, character_data: Dict)` - Apply ration loss.
- `_apply_reputation_gain(self, character_data: Dict, reward: str)` - Apply reputation gain.
- `_apply_reputation_loss(self, character_data: Dict)` - Apply reputation loss.
- `_apply_rest(self, character_data: Dict)` - Apply long rest benefits.
- `_apply_vendor_modifier(self, character_data: Dict, modifier: str)` - Apply vendor price modifier.
- `_get_dangerous_trap_damage(self, level: int)` - Get dangerous trap damage based on character level using existing trap system.
- `_roll_damage_dice(self, dice_formula: str)` - Roll damage dice from a formula like '2d10' or '4d10'.
- `apply_penalty(self, character_data: Dict, penalty: str)` - Apply a failure penalty to the character. Returns updated character data and log messages.
- `apply_refuse_cost(self, character_data: Dict, cost: str)` - Apply the cost of refusing a challenge. Returns updated character data and log messages.
- `apply_reward(self, character_data: Dict, reward: str)` - Apply a success reward to the character. Returns updated character data and log messages.
- `log_reward_application(self, character_id: str, reward_type: str, description: str, details: str='')` - Log reward/penalty application to database for tracking.
- `save_character_data(self, character_data: Dict)` - Save updated character data to database.

## core - `src/talekeeper/services/spell_effects_service.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `apply_buff(self, target_id: str, buff_data: Dict[str, Any], duration_rounds: int, caster_id: Optional[str]=None, concentration: bool=False)` - Inferred from name: apply buff.
- `apply_damage(self, target_id: str, damage: int, damage_type: str, source_spell: str)` - Inferred from name: apply damage.
- `apply_healing(self, target_id: str, healing_amount: int, source_spell: str)` - Inferred from name: apply healing.
- `apply_temp_hp(self, target_id: str, temp_hp: int, source_spell: str)` - Inferred from name: apply temp hp.
- `cleanup_expired_effects(self)` - Inferred from name: cleanup expired effects.
- `clear_temp_hp(self, character_id: str)` - Inferred from name: clear temp hp.
- `decrement_effect_durations(self, character_id: str)` - Inferred from name: decrement effect durations.
- `get_ac_modifier(self, character_id: str)` - Inferred from name: get ac modifier.
- `get_active_buffs(self, character_id: str, buff_type: Optional[str]=None)` - Inferred from name: get active buffs.
- `get_attack_bonus(self, character_id: str)` - Inferred from name: get attack bonus.
- `get_buff(self, character_id: str, spell_id: str)` - Inferred from name: get buff.
- `get_condition_immunities(self, character_id: str)` - Inferred from name: get condition immunities.
- `get_damage_bonus(self, character_id: str)` - Inferred from name: get damage bonus.
- `get_resistances(self, character_id: str)` - Inferred from name: get resistances.
- `get_temp_hp(self, character_id: str)` - Inferred from name: get temp hp.
- `has_buff(self, character_id: str, spell_id: str)` - Inferred from name: has buff.
- `process_turn_end_effects(self, character_id: str)` - Inferred from name: process turn end effects.
- `process_turn_start_effects(self, character_id: str)` - Inferred from name: process turn start effects.
- `remove_all_buffs(self, character_id: str)` - Inferred from name: remove all buffs.
- `remove_buff(self, character_id: str, spell_id: str)` - Inferred from name: remove buff.
- `remove_condition(self, character_id: str, condition_name: str)` - Inferred from name: remove condition.
- `set_temp_hp(self, character_id: str, amount: int, source: str)` - Inferred from name: set temp hp.

## core - `src/talekeeper/services/spell_handlers/advanced_handlers.py`

- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `_create_summon(self, caster_id: str, form: str, stat_block: Dict)` - Inferred from name: create summon.
- `_dismiss_summon(self, caster_id: str, summon: Dict[str, Any])` - Inferred from name: dismiss summon.
- `_get_active_summon(self, caster_id: str)` - Inferred from name: get active summon.
- `_get_steed_stats(self, form: str)` - Inferred from name: get steed stats.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `_reduce_exhaustion(self, character_id: str)` - Inferred from name: reduce exhaustion.
- `_restore_ability_scores(self, character_id: str)` - Inferred from name: restore ability scores.
- `_restore_max_hp(self, character_id: str)` - Inferred from name: restore max hp.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.

## core - `src/talekeeper/services/spell_handlers/base_handler.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_ability_mod(self, character_id: str, ability: str)` - Inferred from name: get ability mod.
- `_get_spell_save_dc(self, caster_id: str)` - Inferred from name: get spell save dc.
- `_make_save(self, target_id: str, save_ability: str, dc: int)` - Inferred from name: make save.
- `can_cast(self, caster_id: str, context: Dict[str, Any])` - Inferred from name: can cast.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `on_turn_end(self, character_id: str)` - Inferred from name: on turn end.
- `on_turn_start(self, character_id: str)` - Inferred from name: on turn start.
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `execute_spell(self, spell_id: str, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute spell.
- `get_handler(self, spell_id: str)` - Inferred from name: get handler.
- `process_turn_end_effects(self, character_id: str)` - Inferred from name: process turn end effects.
- `process_turn_start_effects(self, character_id: str)` - Inferred from name: process turn start effects.
- `register(self, spell_id: str, handler: SpellHandler)` - Inferred from name: register.
- `roll_dice(num_dice: int, die_size: int)` - Inferred from name: roll dice.

## core - `src/talekeeper/services/spell_handlers/buff_handlers.py`

- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.

## core - `src/talekeeper/services/spell_handlers/concentration_handlers.py`

- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `_scan_for_creatures(self, caster_id: str, context: Dict[str, Any])` - Inferred from name: scan for creatures.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `_scan_for_magic(self, caster_id: str, context: Dict[str, Any])` - Inferred from name: scan for magic.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `_scan_for_poison_disease(self, caster_id: str, context: Dict[str, Any])` - Inferred from name: scan for poison disease.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `_locate_creature(self, description: str, context: Dict[str, Any])` - Inferred from name: locate creature.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `_locate_object(self, description: str, context: Dict[str, Any])` - Inferred from name: locate object.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.

## core - `src/talekeeper/services/spell_handlers/healing_handlers.py`

- `can_cast(self, caster_id: str, context: Dict[str, Any])` - Inferred from name: can cast.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `can_cast(self, caster_id: str, context: Dict[str, Any])` - Inferred from name: can cast.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.

## core - `src/talekeeper/services/spell_handlers/utility_handlers.py`

- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.
- `execute(self, caster_id: str, targets: List[str], slot_level: int, context: Dict[str, Any])` - Inferred from name: execute.

## core - `src/talekeeper/services/spell_registry.py`

- `__post_init__(self)` - Inferred from name: post init.
- `from_dict(cls, data: Dict[str, Any])` - Create from dictionary.
- `is_available_to_class(self, class_name: str)` - Check if this spell is available to a specific class.
- `to_dict(self)` - Convert to dictionary for storage.
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `add_spell(self, spell: SpellDefinition)` - Add a new spell to the registry.
- `clear_cache(self)` - Clear all cached spell data.
- `get_available_classes(self)` - Get all classes that have spells defined.
- `get_ritual_spells(self, class_name: Optional[str]=None)` - Get all ritual spells, optionally filtered by class.
- `get_spell(self, spell_id: str)` - Get a spell definition by ID.
- `get_spell_count_by_class(self, class_name: str)` - Get count of spells by level for a class.
- `get_spells_by_class(self, class_name: str, level: Optional[int]=None)` - Get all spells available to a specific class.
- `get_spells_by_level(self, level: int)` - Get all spells of a specific level.
- `search_spells(self, name_filter: Optional[str]=None, school_filter: Optional[SpellSchool]=None, level_filter: Optional[int]=None, class_filter: Optional[str]=None, ritual_only: bool=False, concentration_only: bool=False)` - Advanced spell search with multiple filters.

## core - `src/talekeeper/services/spellcasting_progression.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_update_spell_slots(self, cursor, character_id: str, class_id: str, prog: SpellSlotProgression)` - Inferred from name: update spell slots.
- `get_spells_that_can_be_prepared(self, character_id: str, class_id: str, new_level: int)` - Inferred from name: get spells that can be prepared.
- `update_spellcasting_on_level_up(self, character_id: str, new_level: int, class_id: str)` - Inferred from name: update spellcasting on level up.

## core - `src/talekeeper/services/spellcasting_service.py`

- `available_slots(self)` - Get number of available spell slots.
- `can_cast_spell(self, spell_level: int)` - Check if this slot can cast a spell of given level.
- `restore_slot(self, amount: int=1)` - Restore spell slots. Returns actual amount restored.
- `use_slot(self)` - Use one spell slot. Returns True if successful.
- `__init__(self, success: bool, spell_id: str='', reason: str='')` - Inferred from name: init.
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_ensure_spellcasting_tables(self)` - Ensure spellcasting tables exist (should be created by migration).
- `_initialize_spell_slots(self, cursor, character_id: str, class_name: str, level: int)` - Initialize spell slots for a character.
- `_parse_duration_to_rounds(self, duration: str)` - Parse spell duration to combat rounds.
- `can_cast_spell(self, character_id: str, spell_id: str, spell_level: Optional[int]=None)` - Check if a character can cast a specific spell.
- `cast_spell(self, character_id: str, spell_id: str, spell_level: Optional[int]=None, action_economy_type: Optional[ActionEconomyType]=None)` - Cast a spell, consuming appropriate resources.
- `end_concentration(self, character_id: str)` - End concentration for a character. Returns the spell that was ended.
- `get_character_spell_slots(self, character_id: str)` - Get all spell slots for a character.
- `get_character_spellcasting(self, character_id: str)` - Get a character's spellcasting information.
- `get_concentration_spell(self, character_id: str)` - Get the spell the character is concentrating on. Returns (spell_id, spell_level).
- `initialize_character_spellcasting(self, character_id: str, class_name: str)` - Initialize spellcasting for a character based on their class.
- `restore_spell_slots(self, character_id: str, rest_type: str='long')` - Restore spell slots on rest.
- `get_spellcasting_service(db_path: str='talekeeper.db')` - Get the spellcasting service singleton.

## core - `src/talekeeper/services/standardized_attack_processor.py`

- `__post_init__(self)` - Inferred from name: post init.
- `_is_attack(self, action_data: Dict[str, Any])` - Check if action data represents an attack.
- `_parse_effect(self, effect_data: Dict[str, Any])` - Parse effect data into AttackEffect object.
- `_parse_standardized_attack(self, action_data: Dict[str, Any])` - Parse standardized attack data into StandardizedAttack object.
- `get_attack_summary(self, attack: StandardizedAttack)` - Generate a human-readable summary of an attack.
- `get_effect_summary(self, effect: AttackEffect)` - Generate a human-readable summary of an effect.
- `process_monster_attacks(self, actions_json: str)` - Process monster actions JSON into standardized attack objects.
- `test_standardized_processor()` - Test the standardized processor with migrated data.

## core - `src/talekeeper/services/stealth_mechanics.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_get_connection(self)` - Get database connection.
- `apply_hidden_attack_bonuses(self, attack_context: Dict[str, Any])` - Apply bonuses for attacking from hidden.
- `check_encounter_stealth(self, character_id: str, character_data: Dict[str, Any], monsters: List[Dict[str, Any]])` - Check if character successfully hides at encounter start.
- `check_monster_perception(self, monster_data: Dict[str, Any], stealth_dc: int)` - Check if a monster spots the hidden character.
- `check_stealth_proficiency(self, character_id: str)` - Check if character has stealth proficiency.
- `end_hidden_state(self, character_id: str, reason: str='attacked')` - End the hidden state for a character.
- `get_stealth_modifiers(self, character_id: str)` - Get stealth roll modifiers from equipment.
- `perform_stealth_check(self, character_id: str, character_level: int)` - Perform a stealth check for encounter initialization.

## core - `src/talekeeper/services/subclass_action_integration.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_activate_heroic_warrior(self, character_id: str)` - Activate Heroic Warrior inspiration gain at turn start.
- `_activate_retaliation(self, character_id: str, feature: SubclassFeature)` - Activate Retaliation reaction.
- `_activate_survivor(self, character_id: str)` - Activate Survivor healing.
- `_get_frenzy_damage_dice(self, character_id: str)` - Get Frenzy damage dice based on character level.
- `_handle_additional_fighting_style(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Additional Fighting Style feature integration.
- `_handle_assassinate(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Assassinate feature integration.
- `_handle_assassins_tools(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Assassin's Tools feature integration.
- `_handle_death_strike(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Death Strike feature integration.
- `_handle_envenom_weapons(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Envenom Weapons feature integration.
- `_handle_fast_hands(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Fast Hands feature integration.
- `_handle_frenzy(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Frenzy feature integration.
- `_handle_heroic_warrior(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Heroic Warrior feature integration.
- `_handle_improved_critical(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Improved Critical feature integration.
- `_handle_infiltration_expertise(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Infiltration Expertise feature integration.
- `_handle_intimidating_presence(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Intimidating Presence feature integration.
- `_handle_mindless_rage(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Mindless Rage feature integration.
- `_handle_remarkable_athlete(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Remarkable Athlete feature integration.
- `_handle_retaliation(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Retaliation feature integration.
- `_handle_second_story_work(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Second-Story Work feature integration.
- `_handle_superior_critical(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Superior Critical feature integration.
- `_handle_supreme_sneak(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Supreme Sneak feature integration.
- `_handle_survivor(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Survivor feature integration.
- `_handle_thiefs_reflexes(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Thief's Reflexes feature integration.
- `_handle_use_magic_device(self, character_id: str, feature: SubclassFeature, integration_type)` - Handle Use Magic Device feature integration.
- `activate_feature(self, character_id: str, feature_name: str)` - Activate a subclass feature through the action system.
- `get_action_cards_for_character(self, character_id: str, level: int)` - Get action cards that should be created for a character's subclass features.
- `get_automatic_triggers_for_character(self, character_id: str, level: int)` - Get automatic triggers that should be set up for a character.
- `get_combat_modifiers_for_character(self, character_id: str, level: int)` - Get combat modifiers that should be applied for a character.
- `trigger_automatic_feature(self, character_id: str, trigger_type: str, context: Dict[str, Any]=None)` - Trigger automatic features based on game events.

## core - `src/talekeeper/services/subclass_feature_manager.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `get_all_subclass_features(self, subclass_id: str)` - Inferred from name: get all subclass features.
- `get_character_subclass_features(self, character_id: str)` - Inferred from name: get character subclass features.
- `get_oath_spells(self, subclass_id: str, paladin_level: int)` - Inferred from name: get oath spells.
- `get_subclass_features_for_level(self, subclass_id: str, level: int)` - Inferred from name: get subclass features for level.
- `grant_oath_spells_for_level(self, character_id: str, subclass_id: str, paladin_level: int)` - Inferred from name: grant oath spells for level.
- `grant_subclass_feature(self, character_id: str, feature_id: int, level_gained: int)` - Inferred from name: grant subclass feature.
- `recharge_features(self, character_id: str, rest_type: str)` - Inferred from name: recharge features.
- `use_feature(self, character_id: str, feature_instance_id: int)` - Inferred from name: use feature.

## core - `src/talekeeper/services/subclass_manager.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_apply_feature_mechanics(self, cursor, character_id: str, feature_name: str, mechanics_json: str)` - Apply mechanical effects of a feature.
- `_ensure_class_subclass_support(self, conn)` - Create tables and backfill data for per-class subclass tracking.
- `_grant_subclass_features(self, cursor, character_id: str, subclass_id: str, up_to_level: int)` - Grant subclass features up to specified level.
- `_run_migration(self)` - Ensure subclass tables exist.
- `apply_combat_modifiers(self, character_id: str, context: Dict[str, Any])` - Apply subclass-specific combat modifiers.
- `check_subclass_requirement(self, character_id: str)` - Check if character needs to select a subclass.
- `get_available_subclasses(self, class_id: str)` - Get all available subclasses for a class.
- `get_character_subclass(self, character_id: str, class_id: str)` - Return the subclass id for a given character/class pairing.
- `get_feature_uses(self, character_id: str, feature_name: str)` - Get current and max uses for a resource-based feature.
- `get_subclass_features(self, subclass_id: str, level: int)` - Get all features for a subclass up to specified level.
- `has_feature(self, character_id: str, feature_name: str)` - Check if character has a specific subclass feature.
- `select_subclass(self, character_id: str, subclass_id: str, class_level: Optional[int]=None)` - Assign a subclass to a character for its associated class.
- `update_features_for_class(self, character_id: str, class_id: str, class_level: int)` - Ensure subclass features are granted up to the specified class level.
- `update_features_for_level(self, character_id: str, new_level: int, class_id: Optional[str]=None)` - Update subclass features when a character gains a level.
- `use_feature(self, character_id: str, feature_name: str)` - Use a resource-based subclass feature.

## core - `src/talekeeper/services/subclass_registry.py`

- `__init__(self)` - Initialize the registry with an empty cache.
- `clear_cache(self)` - Clear the cached subclass definitions.
- `get_all_classes_with_subclasses(self)` - Get all classes that have subclasses defined.
- `get_available_subclasses(self, class_name: str)` - Get all available subclass names and descriptions for a class.
- `get_subclass(self, class_name: str, subclass_name: str)` - Get a subclass definition, loading it if necessary.
- `is_subclass_available(self, class_name: str, subclass_name: str)` - Check if a specific subclass is available.

## core - `src/talekeeper/services/subclasses/cleric/life.py`

- `create()` - Create the Life Domain subclass definition.

## core - `src/talekeeper/services/subclasses/fighter/champion.py`

- `create()` - Create the Champion subclass definition.

## core - `src/talekeeper/services/subclasses/paladin/__init__.py`

- `get_paladin_subclass(subclass_name: str)` - Get a paladin subclass definition by name.

## core - `src/talekeeper/services/subclasses/paladin/devotion.py`

- `calculate_sacred_weapon_bonus(charisma_modifier: int)` - Calculate Sacred Weapon attack bonus.
- `create()` - Create the Oath of Devotion subclass definition.
- `get_aura_range(level: int)` - Get Aura of Devotion range based on level.
- `get_channel_divinity_options(level: int)` - Get Channel Divinity options available at a given level.
- `get_oath_features(level: int)` - Get oath features available at a given level.
- `get_oath_spells(level: int)` - Get oath spells available at a given level.

## core - `src/talekeeper/services/subclasses/rogue/thief.py`

- `create()` - Create the Thief subclass definition.

## core - `src/talekeeper/services/subclasses/wizard/__init__.py`

- `get_wizard_subclass(subclass_name: str)` - Get a wizard subclass definition by name.

## core - `src/talekeeper/services/subclasses/wizard/evocation.py`

- `calculate_overchannel_damage(uses_today: int, spell_level: int)` - Calculate necrotic damage from Overchannel use.
- `create()` - Create the School of Evocation subclass definition.
- `get_school_bonus_spells()` - Get bonus spells known for School of Evocation.
- `get_tradition_features(level: int)` - Get tradition features available at a given level.

## core - `src/talekeeper/services/tarot_cards.py`

- `draw_tarot_card()` - Inferred from name: draw tarot card.
- `get_tarot_inspiration(card: Optional[Dict[str, Any]]=None)` - Inferred from name: get tarot inspiration.

## core - `src/talekeeper/services/treasure_generator.py`

- `convert_gold_to_treasure(gold_amount: int, cr: float=1.0)` - Inferred from name: convert gold to treasure.
- `generate_art_object(min_value: int=25, max_value: int=2500)` - Inferred from name: generate art object.
- `generate_beast_rations(individual_treasure_gp: float)` - Generate rations from beast individual treasure value.
- `generate_gem(min_value: int=10, max_value: int=5000)` - Inferred from name: generate gem.
- `should_use_treasure_conversion(gold_amount: int, threshold: int=1000)` - Inferred from name: should use treasure conversion.

## core - `src/talekeeper/services/treasure_rarity.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `get_level_bracket(self, character_level: int)` - Get the level bracket name for a character level.
- `get_rarity_for_level(self, character_level: int)` - Roll for item rarity based on character level.
- `get_rarity_for_level_and_roll(self, character_level: int, roll: int)` - Get item rarity for a specific level and roll.
- `get_rarity_probability(self, character_level: int, target_rarity: str)` - Get the probability (0.0-1.0) of getting a specific rarity at a level.
- `get_rarity_ranges_for_level(self, character_level: int)` - Get all possible rarity ranges for a given level.

## core - `src/talekeeper/services/unified_level_up.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_calculate_ability_max_uses(self, cursor, character_id: str, uses_formula: Optional[str], level: int)` - Calculate max uses for an ability based on formula
- `_calculate_hp_gain(self, class_id: str, constitution: int)` - Calculate HP gain for level up
- `_calculate_total_hp_for_level(self, cursor, character_id: str, class_id: str, level: int, constitution: int)` - Calculate expected total HP for a given level
- `_get_character_data(self, cursor, character_id: str)` - Get character data from database
- `_grant_class_feature(self, cursor, character_id: str, feature: Dict[str, Any], level: int, results: Dict[str, Any])` - Grant a class feature to the character
- `_grant_subclass_feature(self, cursor, character_id: str, feature: Dict[str, Any], level: int, results: Dict[str, Any])` - Grant a subclass feature to the character
- `_handle_fighter_level_up(self, cursor, character_id: str, level: int)` - Handle Fighter-specific level-up updates
- `_handle_paladin_level_up(self, cursor, character_id: str, level: int, subclass_id: Optional[str])` - Handle Paladin-specific level-up updates
- `_handle_rogue_level_up(self, cursor, character_id: str, level: int)` - Handle Rogue-specific level-up updates
- `_handle_warlock_level_up(self, cursor, character_id: str, new_level: int)` - Handle Warlock-specific level-up choices (invocations and pact boon)
- `_has_epic_boon(self, cursor, character_id: str)` - Check if character already has an Epic Boon feat
- `apply_epic_boon(self, character_id: str, boon_name: str)` - Apply an Epic Boon feat to the character
- `apply_feature_choice(self, character_id: str, feature_instance_id: int, choice: str)` - Apply a choice for a feature (like fighting style, expertise skills)
- `apply_pact_boon(self, character_id: str, pact_boon: str)` - Apply Pact Boon choice to Warlock
- `apply_spell_selection(self, character_id: str, spell_ids: List[str], spellcasting_class: str=None)` - Apply selected spells to character's known/prepared spells
- `apply_subclass_choice(self, character_id: str, subclass_id: str)` - Apply a subclass choice to a character
- `apply_warlock_invocations(self, character_id: str, invocation_ids: List[str])` - Apply selected Eldritch Invocations to character
- `get_available_classes(self)` - Get list of available classes for leveling.
- `get_available_epic_boons(self)` - Get all available Epic Boon feats
- `get_character_class_levels(self, character_id: str)` - Get current class levels for a character.
- `is_asi_level(self, character_id: str, class_choice: str)` - Check if next level grants ASI for the selected class.
- `level_up_character(self, character_id: str)` - Level up a character using the unified feature system

## core - `src/talekeeper/services/warlock_patrons/fiend_patron.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `dark_ones_blessing(self, character_id: str, target_cr: float=1.0)` - Apply Dark One's Blessing when a creature is reduced to 0 HP.
- `get_expanded_spells(self)` - Get the expanded spell list for Fiend patron.
- `get_patron_features(self, character_id: str)` - Get all patron features for this character.
- `initialize_patron_features(self, character_id: str, level: int, cursor=None)` - Initialize all Fiend patron features for the given level.
- `long_rest_recovery(self, character_id: str)` - Recover features that refresh on long rest.
- `set_fiendish_resilience(self, character_id: str, damage_type: str)` - Set the damage type for Fiendish Resilience.
- `short_rest_recovery(self, character_id: str)` - Recover features that refresh on short rest.
- `use_dark_ones_own_luck(self, character_id: str)` - Use Dark One's Own Luck ability.
- `use_hurl_through_hell(self, character_id: str, target_name: str='target')` - Use Hurl Through Hell ability.

## core - `src/talekeeper/services/warlock_patrons/patron_manager.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `get_available_patrons(self)` - Get list of available patron names.
- `get_expanded_spells(self, patron_name: str)` - Get expanded spells for a patron.
- `get_patron(self, patron_name: str)` - Get patron implementation by name.
- `get_patron_features(self, character_id: str, patron_name: str)` - Get all patron features for a character.
- `initialize_patron_features(self, character_id: str, patron_name: str, level: int, cursor=None)` - Initialize patron features for a character.
- `long_rest_recovery(self, character_id: str, patron_name: str)` - Handle long rest recovery for patron features.
- `short_rest_recovery(self, character_id: str, patron_name: str)` - Handle short rest recovery for patron features.
- `use_patron_feature(self, character_id: str, patron_name: str, feature_name: str, **kwargs)` - Use a specific patron feature.
- `get_patron_manager(db_path: str='talekeeper.db')` - Factory function to get a PatronManager instance.

## core - `src/talekeeper/services/warlock_service.py`

- `__init__(self, db_path: str)` - Inferred from name: init.
- `_apply_invocation_effects(self, character_id: str, invocation_id: str)` - Inferred from name: apply invocation effects.
- `_has_cantrip(self, character_id: str, cantrip: str)` - Inferred from name: has cantrip.
- `_knows_spell(self, character_id: str, spell_id: str)` - Inferred from name: knows spell.
- `_meets_prerequisites(self, level: int, pact_boon: str, prereqs: Dict, character_id: str)` - Inferred from name: meets prerequisites.
- `get_available_invocations(self, character_id: str)` - Inferred from name: get available invocations.
- `get_character_invocations(self, character_id: str)` - Inferred from name: get character invocations.
- `learn_invocation(self, character_id: str, invocation_id: str)` - Inferred from name: learn invocation.
- `__init__(self, db_path: str)` - Inferred from name: init.
- `_add_expanded_spells(self, character_id: str, patron: str)` - Inferred from name: add expanded spells.
- `apply_fiend_features(self, character_id: str, level: int)` - Inferred from name: apply fiend features.
- `dark_ones_blessing(self, character_id: str, creature_killed_cr: float)` - Inferred from name: dark ones blessing.
- `dark_ones_own_luck(self, character_id: str, roll_type: str)` - Inferred from name: dark ones own luck.
- `fiendish_resilience(self, character_id: str, damage_type: str)` - Inferred from name: fiendish resilience.
- `hurl_through_hell(self, character_id: str, target_id: str)` - Inferred from name: hurl through hell.
- `__init__(self, db_path: str)` - Inferred from name: init.
- `can_cast_spell_with_pact_slot(self, character_id: str, spell_level: int)` - Inferred from name: can cast spell with pact slot.
- `eldritch_master_recovery(self, character_id: str)` - Inferred from name: eldritch master recovery.
- `get_pact_slots(self, character_id: str)` - Inferred from name: get pact slots.
- `short_rest_recovery(self, character_id: str)` - Inferred from name: short rest recovery.
- `use_pact_slot(self, character_id: str)` - Inferred from name: use pact slot.
- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_grant_book_of_shadows(self, character_id: str)` - Inferred from name: grant book of shadows.
- `_grant_find_familiar(self, character_id: str)` - Inferred from name: grant find familiar.
- `_grant_mystic_arcanum(self, character_id: str, level: int)` - Inferred from name: grant mystic arcanum.
- `_grant_pact_weapon(self, character_id: str)` - Inferred from name: grant pact weapon.
- `get_warlock_features(self, character_id: str)` - Inferred from name: get warlock features.
- `initialize_warlock_features(self, character_id: str, level: int=1, patron: str='Fiend')` - Inferred from name: initialize warlock features.
- `level_up_warlock(self, character_id: str, new_level: int)` - Inferred from name: level up warlock.
- `select_pact_boon(self, character_id: str, pact_boon: str)` - Inferred from name: select pact boon.

## core - `src/talekeeper/services/weapon_attack_service.py`

- `__init__(self, db_path: str)` - Initialize the weapon attack service.
- `_apply_cunning_strike_effects(self, character_id: str, effects: List[Dict[str, Any]], target: Optional[Dict[str, Any]])` - Apply Cunning Strike effects to the target with saves and conditions.
- `_apply_sneak_attack_if_eligible(self, character: Dict[str, Any], weapon: Dict[str, Any], target: Optional[Dict[str, Any]], has_advantage: bool, has_disadvantage: bool, is_hidden: bool=False)` - Apply Sneak Attack damage if the character is eligible.
- `_apply_specific_mastery(self, mastery_type: str, weapon_name: str, hit: bool, damage_total: int, character: Dict[str, Any])` - Apply specific weapon mastery effects.
- `_calculate_cunning_strike_save_dc(self, character_id: str)` - Calculate save DC for Cunning Strike effects: 8 + DEX mod + proficiency bonus.
- `_check_allies_near_target(self, character_id: str, target: Optional[Dict[str, Any]])` - Check for favorable tactical conditions for Sneak Attack in solo play.
- `_clear_cunning_strike_selection(self, character_id: str)` - Clear Cunning Strike selection after use.
- `_get_active_cunning_strike_effects(self, character_id: str)` - Get list of active Cunning Strike effects from character context.
- `_get_connection(self)` - Get a database connection.
- `_get_die_size_from_weapon(self, weapon: Dict[str, Any])` - Extract die size from weapon damage dice string.
- `_get_weapon_magic_bonus(self, weapon: Dict[str, Any])` - Extract magic bonus from weapon name.
- `_is_sneak_attack_weapon(self, weapon: Dict[str, Any])` - Check if weapon is eligible for sneak attack (finesse or ranged).
- `_mark_sneak_attack_used(self, character_id: str)` - Mark sneak attack as used this turn.
- `_no_sneak_attack(self, reason: str)` - Return a no-sneak-attack result.
- `_normalize_weapon_properties(self, weapon_props)` - Normalize weapon properties from various formats to a string.
- `_parse_damage_dice(self, damage_dice: str)` - Parse damage dice string into number of dice and die size.
- `_roll_saving_throw(self, target: Dict[str, Any], ability: str, dc: int)` - Roll a saving throw for a target.
- `_sneak_attack_used_this_turn(self, character_id: str)` - Check if sneak attack has been used this turn.
- `apply_fighting_style_effects(self, dice_rolls: List[int], fighting_styles: List[str], weapon: Dict[str, Any], character: Dict[str, Any], action_type: str='main_hand')` - Apply fighting style effects to damage dice.
- `apply_fires_burn_if_eligible(self, character_id: str, character_race: str, target_hp_after_hit: int)` - Inferred from name: apply fires burn if eligible.
- `apply_savage_attacker(self, dice_rolls: List[int], num_dice: int, die_size: int, character: Dict[str, Any], is_first_attack: bool=True)` - Apply Savage Attacker feat - reroll damage dice and use higher result.
- `apply_weapon_mastery_effects(self, weapon: Dict[str, Any], character: Dict[str, Any], target: Optional[Dict[str, Any]], hit: bool, damage_total: int=0, attack_total: int=0, chosen_mastery: Optional[str]=None)` - Apply weapon mastery effects based on the weapon's mastery property.
- `calculate_attack_damage(self, weapon: Dict[str, Any], character: Dict[str, Any], target: Optional[Dict[str, Any]]=None, is_critical: bool=False, advantage: bool=False, disadvantage: bool=False, action_type: str='main_hand', is_hidden: bool=False)` - Calculate attack roll and damage for a weapon attack.
- `can_use_tactical_master(self, character_id: str)` - Check if character can use Tactical Master (Fighter level 9+).
- `get_character_fighting_styles(self, character_id: str)` - Get all fighting styles for a character.
- `get_fighting_style_attack_bonus(self, weapon: Dict[str, Any], character: Dict[str, Any])` - Calculate attack bonuses from fighting styles.
- `get_fighting_style_damage_bonus(self, weapon: Dict[str, Any], character: Dict[str, Any], action_type: str, fighting_styles: List[str])` - Calculate flat damage bonuses from fighting styles.
- `get_weapon_mastery_effects(self, mastery_type: str, weapon_name: str, hit: bool, damage_total: int=0)` - Get the effects of a weapon mastery property.
- `has_character_unlimited_mastery(self, character_id: str)` - Check if a character has unlimited weapon mastery access.
- `update_character_mastery_resources(self, character_id: str)` - Update weapon mastery resources for a character.

## core - `src/talekeeper/services/weapon_mastery_effects.py`

- `__init__(self)` - Inferred from name: init.
- `_apply_mastery_effect(self, mastery: MasteryEffect, character_data: Dict[str, Any], target_data: Dict[str, Any], attack_roll: int, damage_roll: int)` - Apply a specific mastery effect and return the result.
- `_get_attack_ability_modifier(self, character_data: Dict[str, Any])` - Get the ability modifier used for attacks (usually Strength or Dexterity).
- `apply_on_hit_effects(self, character_data: Dict[str, Any], weapon_name: str, target_data: Dict[str, Any], attack_roll: int, damage_roll: int)` - Apply weapon mastery effects when an attack hits.
- `apply_on_miss_effects(self, character_data: Dict[str, Any], weapon_name: str, target_data: Dict[str, Any], attack_roll: int)` - Apply weapon mastery effects when an attack misses.
- `check_mastery_applicability(self, character_masteries: List[str], weapon_name: str, mastery_name: str)` - Check if a character can use a specific mastery with a weapon.
- `get_available_masteries_for_weapon(self, weapon_name: str)` - Get weapon masteries available for a specific weapon type from equipment data.

## core - `src/talekeeper/services/weapon_mastery_service.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_add_option(weapon_name: str, mastery_type: Optional[str], description: str='', equipped: bool=False)` - Inferred from name: add option.
- `_coerce_bool(value: Any)` - Coerce SQLite truthy values into a bool.
- `_get_connection(self)` - Inferred from name: get connection.
- `_normalize_mastery_key(mastery_name: str)` - Return a lowercase cache key for mastery lookups.
- `get_character_masteries(self, character_id: str)` - Return the weapon mastery assignments for a character.
- `get_character_weapon_options(self, character_id: str)` - Return mastery-bearing weapons the character currently owns or has equipped.
- `get_mastery_definition(self, mastery_name: str)` - Return the database-backed definition for a weapon mastery.
- `get_mastery_options(self)` - Return all weapons that carry a mastery property.
- `get_weapon_mastery_for_weapon(self, weapon_name: str)` - Return the default mastery for the requested weapon.
- `set_character_masteries(self, character_id: str, selections: Iterable[Dict[str, str]])` - Persist the provided mastery assignments and return normalized payload.

## core - `src/talekeeper/services/wizard_abilities.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_add_starting_spells(self, cursor, character_id: str, level: int)` - Add starting spells to wizard's spellbook.
- `_apply_tradition_features(self, cursor, character_id: str, tradition: str, level: int)` - Apply arcane tradition features based on character level.
- `_initialize_arcane_recovery(self, cursor, character_id: str, level: int)` - Initialize Arcane Recovery feature.
- `add_spell_to_spellbook(self, character_id: str, spell_id: str, source: str='level_up', cost: int=0)` - Add a spell to the wizard's spellbook.
- `get_wizard_info(self, character_id: str)` - Get comprehensive wizard information.
- `initialize_wizard_character(self, character_id: str, tradition: str='evocation')` - Initialize a character as a Wizard with the specified arcane tradition.
- `long_rest_recovery(self, character_id: str)` - Handle long rest recovery for wizards.
- `use_arcane_recovery(self, character_id: str)` - Use Arcane Recovery to regain spell slots.
- `get_wizard_service(db_path: str='talekeeper.db')` - Get singleton wizard service instance.

## core - `src/talekeeper/ui/action_cards/action_panel.py`

- `__init__(self, action_type, icon: str, name: str, description: str, parent: Optional[QWidget]=None)` - Inferred from name: init.
- `_apply_assassin_surprising_strikes(self, context: Dict[str, Any])` - Apply Assassin Surprising Strikes bonus damage if conditions are met.
- `_apply_death_strike(self, context: Dict[str, Any], damage_breakdown: dict)` - Apply Death Strike if conditions are met (Assassin level 17+).
- `_apply_styles(self)` - Apply styling to the action card.
- `_is_assassin(self)` - Check if character is an Assassin.
- `_is_attack_action(self)` - Check if this action card represents an attack that can benefit from advantage.
- `_is_first_round_of_combat(self)` - Check if it's the first round of combat.
- `_on_advantage_resource_used(self, resource_type)` - Handle advantage resource usage.
- `_persist_advantage_counts(self, lucky_current: int, lucky_max: int, inspiration_current: int, inspiration_max: int)` - Persist advantage counts to the characters table.
- `_setup_ui(self)` - Setup the action card UI.
- `_trigger_action(self)` - Trigger the action.
- `_update_advantage_halo(self)` - Update and position the advantage halo.
- `_use_brutal_strike(self, strike_type: str)` - Use a Brutal Strike with the specified effect.
- `_use_fast_hands_sleight_of_hand(self)` - Make a Sleight of Hand check as a bonus action with Fast Hands.
- `_use_fast_hands_thieves_tools(self)` - Use thieves' tools as a bonus action with Fast Hands.
- `_use_fast_hands_utilise(self)` - Use Utilise action as a bonus action with Fast Hands.
- `_use_heroic_warrior(self)` - Trigger Heroic Warrior inspiration gain.
- `_use_instinctive_pounce(self)` - Use Instinctive Pounce movement when entering Rage.
- `_use_intimidating_presence(self)` - Use Intimidating Presence to frighten nearby enemies.
- `_use_masterful_mimicry(self)` - Use Masterful Mimicry to mimic speech or handwriting.
- `_use_retaliation(self)` - Use Retaliation reaction to attack an enemy that damaged you.
- `_use_survivor(self)` - Trigger Survivor healing if conditions are met.
- `clear_cooldown(self)` - Clear the cooldown.
- `enterEvent(self, event)` - Handle mouse enter for hover effect.
- `leaveEvent(self, event)` - Handle mouse leave.
- `set_available(self, available: bool)` - Set whether the action is available.
- `set_cooldown(self, turns: int)` - Set cooldown remaining.
- `set_description(self, description: str)` - Update the description text.
- `set_resource_manager(self, resource_manager)` - Set the advantage resource manager.
- `set_tooltip_suffix(self, suffix: str)` - Add a suffix to the action card tooltip (for action economy status).
- `update_theme_styles(self, theme_name: str)` - Update styling based on theme.
- `__init__(self, parent: Optional[QWidget]=None, layout_profile: Optional[LayoutProfile]=None)` - Inferred from name: init.
- `_action_hovered(self, action_type: ActionType, description: str)` - Handle action hover from card.
- `_advance_combat_turn(self, encounter_panel)` - Advance to the next combatant's turn using the CombatManager.
- `_apply_channel_divinity_effect(self, option_name: str, option_data: Dict[str, Any])` - Apply Channel Divinity effect and update resources.
- `_apply_cunning_strike_effects(self, damage_breakdown: dict, dice_cost: int)` - Apply cunning strike effects and log them.
- `_apply_damage_to_player(self, damage: int, encounter_panel, damage_type: str='physical')` - Apply damage to the player character, with class-specific resistances.
- `_apply_dueling_bonus(self, context: Dict[str, Any])` - Apply Dueling fighting style bonus (+2 damage when wielding one melee weapon in one hand and no other weapons).
- `_apply_fighting_style_effects(self, dice_rolls: list, context: Dict[str, Any])` - Apply fighting style effects to damage dice rolls.
- `_apply_great_weapon_fighting(self, dice_rolls: list, context: Dict[str, Any])` - Apply Great Weapon Fighting: reroll 1s and 2s on melee weapons with two-handed or heavy property.
- `_apply_healing_to_player(self, healing: int)` - Apply healing to the player character.
- `_apply_lay_on_hands_healing(self, healing_points: int, cure_conditions: dict, target_id: str)` - Apply Lay on Hands healing and update resources.
- `_apply_mastery_effect(self, mastery_name: str, hit: bool, context: Dict[str, Any])` - Apply the specific mastery effect using the service definitions.
- `_apply_savage_attacker(self, dice_rolls: list, num_dice: int, die_size: int, context: Dict[str, Any])` - Apply Savage Attacker feat - roll weapon damage dice twice, use higher roll (first attack per round only).
- `_apply_smite_of_protection(self)` - Apply Smite of Protection buff (Devotion level 15).
- `_apply_sneak_attack(self, context: Dict[str, Any], damage_breakdown: dict)` - Apply sneak attack damage if conditions are met.
- `_apply_styles(self)` - Apply initial styling based on the active theme.
- `_apply_styles_for_theme(self, theme_name: str)` - Inferred from name: apply styles for theme.
- `_apply_weapon_mastery_effects(self, weapon_name: str, attack_total: int, target_ac: int, hit: bool, damage_total: int, context: Dict[str, Any])` - Apply weapon mastery effects using simplified database-driven logic.
- `_attach_resource_manager(self, card)` - Ensure a newly created card is wired to the current advantage manager.
- `_build_off_hand_context(self, base_context: Dict[str, Any])` - Build context for off-hand attack.
- `_build_weapon_dict_from_context(self, context: Dict[str, Any])` - Build weapon dictionary from action context for service calls.
- `_calculate_cunning_strike_cost(self)` - Calculate total dice cost for active cunning strike effects.
- `_calculate_hit_bonus(self, weapon: Dict[str, Any], hand: str)` - Calculate attack bonus for a weapon.
- `_calculate_spell_attack_bonus(self)` - Calculate spell attack bonus = proficiency + spellcasting ability modifier.
- `_calculate_spell_damage(self, spell_name: str, spell_level: int, cast_level: int)` - Calculate spell damage based on spell and cast level. Returns (total_damage, log_string).
- `_calculate_spell_save_dc(self)` - Calculate spell save DC = 8 + proficiency + spellcasting ability modifier.
- `_can_dual_wield(self)` - Check if character can dual wield with current equipment.
- `_can_sneak_attack(self, context: Dict[str, Any])` - Check if sneak attack can be applied.
- `_cast_hellish_rebuke(self, target_monster: dict, character_id: str)` - Cast Hellish Rebuke as a reaction.
- `_cast_spell(self, action_type: ActionType, context: Dict[str, Any])` - Handle spell casting from slot cards.
- `_cast_spell_from_slot(self, slot_data: Dict[str, Any], character_id: str)` - Cast spell from new slot card system.
- `_cast_spell_legacy(self, action_type: ActionType, spell_data: Dict[str, Any], character_id: str)` - Legacy spell casting for old system compatibility.
- `_character_has_potions(self)` - Check if character has any healing potions.
- `_character_has_spell(self, spell_name: str)` - Check if character has a specific spell prepared.
- `_character_has_weapon_mastery_feature(self)` - Check if character class gets weapon masteries (Fighter, Rogue, Barbarian, Paladin).
- `_check_and_roll_initiative(self, encounter_panel, context: Dict[str, Any])` - Check if initiative needs to be rolled and roll it.
- `_check_concentration_save(self, character_id: str, damage: int)` - Check for concentration saves when character takes damage.
- `_check_damage_reaction_spells(self, encounter_panel, damage: int, character_data: dict)` - Check for reaction spells that trigger when taking damage.
- `_check_divine_smite(self, is_critical: bool, target_monster: Any, context: Dict[str, Any], base_damage: int=0)` - Check if Paladin wants to use Divine Smite after hitting.
- `_clear_feature_cards(self)` - Clear all feature-based action cards (like Second Wind).
- `_consume_healing_potion(self, character_id: str, potion_name: str)` - Remove one healing potion from character's inventory.
- `_consume_ration(self, character_id: str)` - Consume one ration from character inventory.
- `_continue_combat_turn_cycle(self, encounter_panel)` - Continue the combat turn cycle with a small delay to prevent infinite recursion.
- `_continue_monster_attacks(self, remaining_monsters, monster_data, encounter_panel)` - Continue executing remaining monster attacks.
- `_create_action_cards(self)` - Create action cards for different action types.
- `_create_feature_cards(self)` - Create action cards for character features like Second Wind.
- `_create_slots_display(self, available: int, maximum: int)` - Create visual display of spell slots like ●●●○○ (3/5).
- `_create_spell_action_cards(self)` - Create spell hand cards grouped by level AND casting time.
- `_create_spell_description(self, spell: Dict[str, Any])` - Create a concise description for the spell action card.
- `_create_spell_slot_card(self, spell_level: int, cast_type: str, default_spell: Dict[str, Any], available_spells: List[Dict[str, Any]], available_slots: int, max_slots: int)` - Create a spell card stack widget.
- `_create_weapon_cards(self)` - Create weapon attack cards based on equipped weapons.
- `_determine_spell_action_type(self, spell: Dict[str, Any])` - Determine the appropriate action type for a spell.
- `_end_combat(self, encounter_panel)` - End combat when all monsters are defeated.
- `_ensure_combat_session(self)` - Ensure there is an action-economy combat session available.
- `_execute_attack_without_initiative(self, action_type: ActionType, context: Dict[str, Any], encounter_panel)` - Execute the attack without rolling initiative (used for immediate attacks and pending attacks).
- `_execute_channel_divinity_effect(self, option_name: str, option_data: Dict[str, Any])` - Execute the specific Channel Divinity effect.
- `_execute_mastery_effect(self, mastery_name: str, special_effects: str, context: Dict[str, Any], requires_save: bool, save_ability: Optional[str], save_dc_formula: Optional[str], damage_formula: Optional[str])` - Execute the specific mastery effect.
- `_execute_monster_attack(self, monster_instance, monster_stats: dict, encounter_panel)` - Execute a single monster's attack against the player.
- `_execute_monster_attacks_with_delay(self, living_monsters, monster_data, encounter_panel)` - Execute monster attacks with a small delay between each attack.
- `_execute_monster_turns_before_player(self, encounter_panel, initiative_order: list, monster_data: dict)` - Execute monster attacks for all monsters that go before the player.
- `_execute_multiple_attacks(self, action_type: ActionType, context: Dict[str, Any], encounter_panel, num_attacks: int)` - Execute multiple attacks, allowing target switching if enemies are killed.
- `_execute_pending_attack(self)` - Execute the player's attack that was held due to losing initiative.
- `_execute_remaining_initiative_turns(self, encounter_panel, current_encounter)` - Execute remaining monster turns in initiative order after player's turn.
- `_execute_single_attack(self, action_type: ActionType, context: Dict[str, Any], encounter_panel)` - Execute a single attack (used by two-weapon fighting system).
- `_execute_single_monster_attack(self, monster_instance, action, monster_stats: dict, encounter_panel, attack_num: int=1, total_attacks: int=1)` - Execute a single attack from a monster action.
- `_execute_spell_cast(self, spell: Dict[str, Any], character_id: str, target=None)` - Execute the actual spell cast.
- `_execute_two_weapon_attack(self, context: Dict[str, Any], encounter_panel)` - Execute both main-hand and off-hand attacks if dual wielding.
- `_extract_weapon_properties(weapon: Dict[str, Any])` - Safely extract weapon property tags as a list.
- `_feature_name_to_action_type(self, feature_name: str)` - Convert a feature name to its corresponding ActionType.
- `_format_damage(self, weapon: Dict[str, Any], is_off_hand: bool=False)` - Format weapon damage string.
- `_get_ability_uses_remaining(self, ability_name: str)` - Get remaining uses for an ability from character resources.
- `_get_action_cooldown(self, action_type: ActionType)` - Get the cooldown turns for an action.
- `_get_all_damage_bonuses(self, context: Dict[str, Any])` - Get all feature-based damage bonuses and their values.
- `_get_attack_count(self, context: Dict[str, Any])` - Get number of attacks based on class features and levels.
- `_get_barbarian_level_from_database(self)` - Get the character's barbarian class level from database (for multiclass support).
- `_get_best_healing_potion(self, character_id: str)` - Get the best available healing potion from inventory.
- `_get_cantrip_dice_by_level(self, char_level: int)` - Get number of damage dice for cantrips based on character level.
- `_get_channel_divinity_uses_text(self)` - Get Channel Divinity uses as text (e.g., '2/2', '1/2', '0/2').
- `_get_character_castable_spells(self, character_id: str)` - Get list of spells the character can currently cast.
- `_get_character_hit_die(self)` - Get the character's hit die size based on their class.
- `_get_character_spell_slots(self, character_id: str)` - Get character's spell slots using the spellcasting service.
- `_get_combat_manager(self)` - Lazily construct the combat manager with the active DB path.
- `_get_constitution_modifier(self)` - Get character's Constitution modifier.
- `_get_context_damage_profile(self, context: Dict[str, Any])` - Return damage dice/type, falling back to weapon metadata when absent.
- `_get_context_weapon_properties(self, context: Dict[str, Any])` - Extract weapon properties from attack context dictionaries.
- `_get_dueling_bonus(self, context: Dict[str, Any])` - Check if character gets Dueling fighting style bonus (+2 damage).
- `_get_economy_unavailability_reason(self, action_type: ActionType)` - Get reason why an action is unavailable due to action economy.
- `_get_encounter_panel(self)` - Get the encounter panel from the main window.
- `_get_equipment_database(self)` - Lazily construct the equipment database helper with the active DB path.
- `_get_feat_resource_remaining(self, feat_name: str, resource_type: str)` - Get remaining uses for a feat resource.
- `_get_feature_data(self, feature_name: str)` - Retrieve feature metadata by display name.
- `_get_fighting_style_ac_bonus(self)` - Get AC bonus from fighting styles.
- `_get_fighting_style_attack_bonus(self, context: Dict[str, Any])` - Get attack bonus from fighting styles.
- `_get_fighting_style_damage_bonus(self, context: Dict[str, Any])` - Get damage bonus from fighting styles.
- `_get_lay_on_hands_pool_text(self)` - Get Lay on Hands pool as text (e.g., '5/5', '3/10', '0/15').
- `_get_mastery_definition(self, mastery_name: str)` - Retrieve and cache mastery metadata from the service.
- `_get_monster_data_for_combat_manager(self, monster_instance)` - Get monster data in the format expected by combat manager.
- `_get_radiant_strikes_bonus(self, context: Dict[str, Any])` - Get Radiant Strikes bonus for Paladins at level 11+.
- `_get_rage_damage_bonus(self, context: Dict[str, Any])` - Check if Barbarian gets rage damage bonus for melee weapon attacks using Strength.
- `_get_rage_damage_from_database(self, barbarian_level: int)` - Get rage damage bonus from database by looking up barbarian features.
- `_get_resource_service(self)` - Lazily construct the character resource service.
- `_get_sneak_attack_damage(self)` - Get sneak attack damage based on rogue level.
- `_get_spell_buff_effects(self, spell_name: str, cast_level: int)` - Get the buff effects of a spell for display.
- `_get_spell_icon(self, spell: Dict[str, Any])` - Get an appropriate icon for the spell based on school and properties.
- `_get_spell_mechanics(self, spell_name: str)` - Determine spell mechanics: 'attack', 'save', or 'auto'.
- `_get_spell_save_type(self, spell_name: str)` - Get the type of saving throw required for a spell.
- `_get_spell_slots(self, level: int)` - Get available spell slots of given level.
- `_get_spellcasting_service(self)` - Lazily construct the spellcasting service with the active DB path.
- `_get_two_weapon_fighting_damage_bonus(self, context: Dict[str, Any])` - Get damage bonus from Two-Weapon Fighting style for off-hand attacks.
- `_get_unavailability_reasons(self, action_type: ActionType)` - Get reasons why an action is unavailable.
- `_get_weapon_attack_service(self)` - Lazily construct the weapon attack service with the active DB path.
- `_get_weapon_mastery(self, weapon_name: str)` - Get mastery for a weapon from cached assignments or equipment data.
- `_get_weapon_mastery_service(self)` - Lazily construct the weapon mastery service with the active DB path.
- `_handle_cleave_followup(self, action_type: ActionType, context: Dict[str, Any], encounter_panel, original_target_id: str, weapon_name: str)` - Resolve Cleave mastery follow-up attack against a random nearby foe.
- `_handle_combat_manager_result(self, result, monster_instance, encounter_panel)` - Handle the results from combat manager monster attack.
- `_handle_rest_action(self, context: Dict[str, Any])` - Handle rest action - prompt for short or long rest.
- `_handle_spell_attack(self, spell_data: Dict[str, Any], context: Dict[str, Any])` - Handle attack spell effects.
- `_handle_spell_effects(self, action_type: ActionType, spell_data: Dict[str, Any], cast_level: int)` - Handle spell effects based on action type.
- `_handle_spell_reaction(self, spell_data: Dict[str, Any], context: Dict[str, Any])` - Handle reaction spell effects.
- `_handle_spell_utility(self, spell_data: Dict[str, Any], context: Dict[str, Any])` - Handle utility/buff spell effects on self.
- `_has_channel_divinity_uses(self)` - Check if paladin has Channel Divinity uses remaining.
- `_has_class_feature(self, feature_name: str)` - Check if character has a specific class feature.
- `_has_healing_potion(self, character_id: str)` - Check if character has any healing potions in inventory.
- `_has_lay_on_hands_uses(self)` - Check if paladin has Lay on Hands uses remaining.
- `_has_rage_uses(self)` - Check if character has rage uses remaining.
- `_has_rations(self, character_id: str)` - Check if character has at least one ration in inventory.
- `_has_stroke_of_luck_uses(self)` - Check if character has Stroke of Luck uses remaining.
- `_hazards_present(self)` - Check if any hazards are currently active.
- `_hydrate_equipped_weapon(self, weapon: Dict[str, Any])` - Ensure equipped weapon entries include mastery-critical metadata.
- `_infer_base_weapon_name(weapon_name: str)` - Best-effort extraction of the non-magical base weapon name.
- `_is_action_available(self, action_type: ActionType)` - Check if an action is currently available.
- `_is_action_available_by_economy(self, action_type: ActionType)` - Check if an action is available based on action economy rules.
- `_is_combat_action(self, action_type: ActionType)` - Check if an action should trigger turn advancement (end player turn).
- `_is_concentration_spell(self, spell_name: str)` - Check if a spell requires concentration.
- `_is_critical_hit(self, attack_breakdown: dict, context: Dict[str, Any])` - Check if an attack is a critical hit based on character class/subclass.
- `_is_monster_alive_in_encounter(self, encounter_panel, monster_id: str)` - Check if a monster is still alive in the encounter panel.
- `_is_player_turn_d20(self)` - Check if it's the player's turn using D&D 2024 rules.
- `_is_self_targeting_spell(self, spell_data: Dict[str, Any])` - Determine if spell should default to self-targeting when no target selected.
- `_load_monster_data(self)` - Load monster data from database for stats lookups.
- `_log_action_economy_usage(self, action_type: ActionType, economy_type)` - Log action economy usage to combat log.
- `_log_attack_result(self, hit: bool, weapon: str, target: str, attack_breakdown: dict, target_ac: int, damage_breakdown: dict=None)` - Log the result of an attack with detailed dice breakdown.
- `_log_fighting_style(self, style_name: str, bonus_type: str, description: str)` - Log fighting style bonuses to combat log.
- `_log_initiative_results(self, player_initiative: int, initiative_order: list, player_dex_mod: int)` - Log the initiative results to show turn order.
- `_log_mastery_effect(self, mastery_name: str, description: str)` - Log mastery effect to combat log.
- `_log_monster_attack_result(self, hit: bool, monster_name: str, action_name: str, attack_roll: int, player_ac: int, damage: int, attack_info: dict, roll_breakdown: dict=None, attack_num: int=1, total_attacks: int=1)` - Log monster attack results with advantage/disadvantage information.
- `_log_player_turn_start(self)` - Log that it's the player's turn again.
- `_log_to_combat_panel(self, message: str)` - Log message to combat panel.
- `_log_to_parent(self, message: str)` - Log message to parent's log panel.
- `_log_weapon_mastery_effects(self, mastery_effects: Dict[str, Any])` - Log weapon mastery effects to combat log.
- `_log_weapon_mastery_effects_old(self, mastery_effects: Dict[str, Any])` - OLD VERSION - Log weapon mastery effects to combat log.
- `_long_rest_healing(self)` - Full healing during long rest.
- `_map_action_to_economy_type(self, action_type: ActionType)` - Map ActionType to ActionEconomyType.
- `_monsters_present(self)` - Check if any monsters are currently present/alive.
- `_new_execute_attack(self, action_type: ActionType, context: Dict[str, Any])` - NEW ATTACK SYSTEM - Built from scratch with Fighter Extra Attacks support.
- `_normalize_feature_name(name: str)` - Normalize feature names for internal lookups.
- `_normalize_weapon_properties(properties: Any)` - Normalize weapon property payloads into a lowercase list.
- `_on_spell_cast_from_stack(self, spell: Dict[str, Any])` - Handle spell cast from spell card stack.
- `_parse_monster_attack(self, action: dict, monster_stats: dict)` - Parse monster attack info from action entry.
- `_prepare_equipped_item(self, item: Any)` - Deep-copy equipped items and hydrate weapons with database metadata.
- `_refresh_action_availability(self)` - Refresh the availability state of all action cards and tabs.
- `_refresh_advantage_resources(self)` - Sync Lucky/Inspiration counts from the database after rests.
- `_refresh_spell_action_cards(self)` - Refresh spell action cards to reflect current spell slot availability.
- `_resolve_character_id(self)` - Resolve the active character ID from context or parent widgets.
- `_resolve_db_path(self)` - Resolve the database path for resource operations.
- `_restore_all_abilities(self)` - Restore all abilities (long rest).
- `_restore_short_rest_abilities(self)` - Restore abilities that recharge on short rest.
- `_roll_attack(self, context: Dict[str, Any])` - Roll an attack roll (d20 + modifiers) with advantage/disadvantage. Returns (total, breakdown).
- `_roll_damage(self, context: Dict[str, Any])` - Roll damage dice with ability modifier. Returns (total, breakdown).
- `_roll_monster_damage(self, damage_dice: str, damage_bonus: int)` - Roll damage for monster attack.
- `_roll_monster_save(self, target_monster, save_type: str)` - Roll a saving throw for a monster.
- `_roll_spell_attack(self)` - Roll a spell attack (1d20 + spell attack bonus).
- `_save_character_xp(self)` - Save character XP to database.
- `_set_category(self, category: ActionCategory)` - Set the active action category.
- `_setup_combat_manager(self, encounter_panel, initiative_order)` - Set up the combat manager with player and monster combatants.
- `_setup_ui(self)` - Initialize the action panel UI components.
- `_short_rest_healing(self)` - Allow hit die healing during short rest.
- `_show_action_unavailable_feedback(self, action_type: ActionType, reason: str)` - Show feedback when an action cannot be taken.
- `_show_cunning_strike_dialog(self)` - Show Cunning Strike selection dialog
- `_show_spell_level_selection_dialog(self, spell: Dict[str, Any], character_id: str)` - Show dialog to select which spell level to cast at.
- `_show_spell_selection_dialog(self, available_spells: List[Dict[str, Any]])` - Show dialog to select which spell to cast from available options.
- `_store_cunning_strike_selection(self, character_id: str, effects: List)` - Store Cunning Strike selection in character_combat_state
- `_take_long_rest(self, dialog)` - Execute long rest.
- `_take_short_rest(self, dialog)` - Execute short rest.
- `_toggle_reckless_attack(self)` - Toggle Reckless Attack state for barbarian.
- `_trigger_action(self, action_type: ActionType, context: Dict[str, Any])` - Handle action trigger from card.
- `_trigger_action_with_economy(self, action_type: ActionType, context: Dict[str, Any])` - Trigger an action with action economy enforcement.
- `_trigger_feature_action(self, action_type)` - Handle feature-based action triggers.
- `_trigger_monster_counter_attacks(self, encounter_panel)` - Trigger counter-attacks from all living monsters after player's action.
- `_trigger_rogue_action(self, action_type)` - Handle rogue feature actions.
- `_trigger_subclass_action(self, action_type)` - Handle subclass feature actions.
- `_update_action_availability(self)` - Update action card availability based on action economy.
- `_update_action_economy(self, used_action: ActionType)` - Update action economy after using an action.
- `_update_action_economy_display(self)` - Update action economy display including tabs and cards.
- `_update_card_availability(self)` - Update the availability state of all action cards.
- `_update_cooldowns(self)` - Update action cooldowns (called by timer).
- `_update_economy_status_display(self)` - Update the action economy status display in the header.
- `_update_potion_card(self)` - Update the potion card to show current potion count and best available potion.
- `_update_rage_state(self)` - Update rage state at the start of each turn.
- `_update_reckless_attack_state(self)` - Update Reckless Attack state at the start of each turn.
- `_update_tab_availability(self, status: Dict[str, Any])` - Update the visual state of category tabs based on action economy.
- `_update_visible_cards(self)` - Update which action cards are visible based on current category.
- `_use_ability(self, ability_name: str)` - Use an ability - decrement uses remaining via resource service.
- `_use_channel_divinity(self)` - Use Channel Divinity with proper dialog.
- `_use_feat_resource(self, feat_name: str, resource_type: str)` - Use a feat resource - decrement remaining uses.
- `_use_healing_potion(self, context: Dict[str, Any])` - Use a healing potion to restore hit points.
- `_use_holy_nimbus(self)` - Activate Holy Nimbus transformation (Devotion level 20).
- `_use_lay_on_hands(self)` - Use paladin Lay on Hands healing with proper dialog.
- `_use_rage(self)` - Activate barbarian rage.
- `end_combat_session(self)` - Clear combat session and reset action availability.
- `get_action_economy_status(self)` - Get current action economy status for UI display.
- `inspiration_offensive_active(self)` - Inferred from name: inspiration offensive active.
- `inspiration_offensive_active(self, value)` - Inferred from name: inspiration offensive active.
- `load_character_equipment(self, equipped_items: Dict[str, Any], character_stats: Dict[str, Any])` - Load character equipment and stats to create weapon cards.
- `load_character_feats(self, character_feats: List[str])` - Load character feats for fighting style and other feat-based effects.
- `load_character_features(self, character_features: Dict[str, Any])` - Load character features and create feature-based action cards.
- `load_character_resources(self, character_data: Dict[str, Any])` - Load character advantage resources (Lucky, Inspiration).
- `load_weapon_masteries(self, weapon_masteries: List[str], assignments: Optional[List[Dict[str, Any]]]=None)` - Load character weapon masteries and assignment map.
- `lucky_offensive_active(self)` - Inferred from name: lucky offensive active.
- `lucky_offensive_active(self, value)` - Inferred from name: lucky offensive active.
- `on_level_selected(level)` - Inferred from name: on level selected.
- `on_smite_chosen(spell_slot_level: int, is_undead_or_fiend: bool, use_free_smite: bool)` - Inferred from name: on smite chosen.
- `on_spell_selected(spell)` - Inferred from name: on spell selected.
- `reset_action_economy(self)` - Reset action economy for a new turn.
- `set_character_context(self, context: Dict[str, Any])` - Set the character context for action availability.
- `set_combat_session(self, combat_session, character_id: str)` - Set the current combat session for action economy tracking.
- `set_target_monster(self, monster_id: str)` - Set the target monster for attacks.
- `set_turn_active(self, active: bool)` - Set whether it's currently the character's turn.
- `update_theme(self, theme_name: str)` - Update all action cards to use the specified theme.

## core - `src/talekeeper/ui/action_cards/channel_divinity_dialog.py`

- `__init__(self, parent=None, character_data: Dict[str, Any]=None, current_uses: int=0, max_uses: int=2, available_options: List[Dict[str, Any]]=None)` - Initialize Channel Divinity dialog.
- `get_selected_option(self)` - Get the currently selected option.
- `option_selected(self, checked: bool)` - Handle option selection.
- `reject(self)` - Handle dialog cancellation.
- `setup_ui(self)` - Set up the user interface.
- `update_display(self)` - Update the display with current values.
- `update_use_button(self)` - Update use button availability.
- `use_channel_divinity(self)` - Use the selected Channel Divinity option.
- `create_channel_divinity_options(character_level: int, sacred_oath: str)` - Create Channel Divinity options based on character level and oath.

## core - `src/talekeeper/ui/action_cards/cunning_strike_selector.py`

- `__init__(self, option_data: Dict[str, Any], parent=None)` - Inferred from name: init.
- `_on_toggled(self, checked: bool)` - Inferred from name: on toggled.
- `_setup_ui(self)` - Inferred from name: setup ui.
- `_update_style(self)` - Inferred from name: update style.
- `is_checked(self)` - Inferred from name: is checked.
- `set_checked(self, checked: bool)` - Inferred from name: set checked.
- `set_enabled(self, enabled: bool)` - Inferred from name: set enabled.
- `__init__(self, dice_cost: int, parent=None)` - Inferred from name: init.
- `_update_text(self)` - Inferred from name: update text.
- `__init__(self, character_id: str, db_path: str='talekeeper.db', sneak_attack_eligible: bool=True, parent=None)` - Inferred from name: init.
- `_clear_selection(self)` - Inferred from name: clear selection.
- `_confirm_selection(self)` - Inferred from name: confirm selection.
- `_load_options(self)` - Inferred from name: load options.
- `_on_option_toggled(self, effect_id: str, checked: bool)` - Inferred from name: on option toggled.
- `_setup_ui(self)` - Inferred from name: setup ui.
- `_update_preview(self)` - Inferred from name: update preview.
- `get_selected_effects(self)` - Inferred from name: get selected effects.

## core - `src/talekeeper/ui/action_cards/divine_smite_dialog.py`

- `__init__(self, parent=None, is_critical: bool=False, available_spell_slots: Dict[int, int]=None, target_info: Dict[str, Any]=None, has_free_smite: bool=False)` - Initialize Divine Smite dialog.
- `_calculate_damage_dice(self, slot_level: int, is_undead_or_fiend: bool)` - Calculate base damage dice for Divine Smite.
- `_on_cancel(self)` - Handle cancel button.
- `_on_confirm(self)` - Handle confirm button.
- `_on_timeout(self)` - Handle timeout - don't use smite.
- `_setup_ui(self)` - Set up the dialog UI.
- `_update_countdown(self)` - Update the countdown display.
- `get_smite_damage_dice(self, slot_level: int)` - Get the damage dice string for a given spell slot level.

## core - `src/talekeeper/ui/action_cards/epic_boon_dialog.py`

- `__init__(self, available_boons: List[Dict[str, Any]], parent=None)` - Inferred from name: init.
- `_on_confirm(self)` - Inferred from name: on confirm.
- `_on_selection_changed(self, current, previous)` - Inferred from name: on selection changed.
- `_setup_ui(self)` - Inferred from name: setup ui.
- `get_selected_boon(self)` - Inferred from name: get selected boon.
- `show_epic_boon_dialog(available_boons: List[Dict[str, Any]], parent=None)` - Inferred from name: show epic boon dialog.

## core - `src/talekeeper/ui/action_cards/lay_on_hands_dialog.py`

- `__init__(self, parent=None, character_data: Dict[str, Any]=None, current_pool: int=0, max_pool: int=0, target_options: list=None)` - Initialize Lay on Hands dialog.
- `_update_condition_ui(self)` - Update UI based on selected conditions.
- `apply_healing(self)` - Apply the healing and emit signal.
- `get_healing_info(self)` - Get the current healing configuration.
- `reject(self)` - Handle dialog cancellation.
- `select_target(self, target_id: str)` - Select a healing target.
- `setup_ui(self)` - Set up the user interface.
- `update_apply_button(self)` - Update apply button availability.
- `update_condition_option(self, state: int)` - Update condition curing options.
- `update_display(self)` - Update the display with current values.
- `update_healing_points(self, value: int)` - Update healing points and effect description.
- `update_poison_option(self, state: int)` - Update poison curing option.

## core - `src/talekeeper/ui/action_cards/spell_card_stack.py`

- `__init__(self, spell_level: int, cast_type: str, spells: List[Dict[str, Any]], available_slots: int, max_slots: int, parent=None)` - Inferred from name: init.
- `_get_spell_effect(self, spell: Dict[str, Any])` - Inferred from name: get spell effect.
- `_on_cast_clicked(self)` - Inferred from name: on cast clicked.
- `_on_label_clicked(self, event)` - Inferred from name: on label clicked.
- `_setup_ui(self)` - Inferred from name: setup ui.
- `_update_display(self)` - Inferred from name: update display.
- `set_available(self, available: bool)` - Inferred from name: set available.
- `update_slots(self, available: int, max_slots: int)` - Inferred from name: update slots.
- `update_theme_styles(self, theme: str)` - Inferred from name: update theme styles.

## core - `src/talekeeper/ui/action_cards/tactical_master_dialog.py`

- `__init__(self, weapon_name: str, original_mastery: str, parent=None)` - Inferred from name: init.
- `_get_mastery_description(self, mastery: str)` - Get description for mastery type.
- `_on_confirm(self)` - Confirm selection and close dialog.
- `_on_selection_changed(self, mastery: str)` - Handle radio button selection.
- `_setup_ui(self)` - Build the dialog UI.
- `get_selected_mastery(self)` - Get the selected mastery type.
- `show_tactical_master_dialog(weapon_name: str, original_mastery: str, parent=None)` - Show tactical master dialog and return selected mastery.

## core - `src/talekeeper/ui/action_cards/weapon_mastery_dialog.py`

- `__init__(self, options: List[Dict[str, str]], selected: List[str], max_selections: Optional[int]=None, parent=None)` - Inferred from name: init.
- `_checked_items(self)` - Inferred from name: checked items.
- `_enforce_limit(self)` - Inferred from name: enforce limit.
- `selected_options(self)` - Return the currently checked weapon mastery assignments.

## core - `src/talekeeper/ui/advantage_halo.py`

- `__init__(self, parent=None)` - Inferred from name: init.
- `mousePressEvent(self, event)` - Handle clicks to use the resource.
- `mouseReleaseEvent(self, event)` - Ensure mouse release is handled properly.
- `paintEvent(self, event)` - Draw a triangle in the top-right corner.
- `position_over_card(self, card_widget)` - Position the halo in the top-right quarter of the given card.
- `show_with_timeout(self, timeout_ms=3000)` - Show the halo and auto-hide after timeout (for defensive usage).
- `update_resources(self, lucky_current, lucky_max, inspiration_current, inspiration_max)` - Update the triangle based on available resources (Inspiration priority).
- `__init__(self, character_data)` - Inferred from name: init.
- `consume_pending_advantage(self)` - Consume pending advantage and return which type was used.
- `consume_resource(self, resource_type)` - Consume a resource and return updated counts.
- `get_primary_resource(self)` - Get the primary resource to display (Inspiration priority).
- `get_resource_counts(self)` - Get all current resource counts.
- `has_pending_advantage(self)` - Check if there's pending advantage for next attack.
- `has_resources(self)` - Check if any advantage resources are available.
- `update_from_character(self, character_data)` - Update resource counts from character data.

## core - `src/talekeeper/ui/character_sheet/character_panel.py`

- `__init__(self, parent: Optional[QWidget]=None, layout_profile: Optional[LayoutProfile]=None)` - Inferred from name: init.
- `_add_xp_history_entry(self, description: str, xp_gain: int)` - Add an entry to the XP history list.
- `_apply_styles(self)` - No hardcoded styling - let main theme handle all colors.
- `_create_ability_row(self, short_name: str, full_name: str, skills: list)` - Create a complete ability row: [ABILITY BOX] [SAVING THROW] [SKILLS...]
- `_create_ability_row_with_stats(self, short_name: str, full_name: str)` - Create Constitution row with secondary stats instead of skills.
- `_create_ability_widget(self, short_name: str, full_name: str)` - Create an ability score widget like in D&D character sheet.
- `_create_pact_magic_widget(self)` - Create Warlock pact magic slots display.
- `_create_saving_throw_widget(self, ability_name: str)` - Create a saving throw widget with diamond indicator.
- `_create_skill_widget(self, skill_name: str, ability: str)` - Create a skill widget with proficiency indicator and bonus.
- `_create_spell_slot_circle(self, used: bool=False)` - Create a single spell slot circle indicator.
- `_create_spell_slot_level_widget(self, level: int)` - Create a spell slot level display widget.
- `_create_stat_widget(self, name: str, value: str)` - Create a secondary stat widget (AC, Init, HP, Speed).
- `_get_feature_description(self, feature_name: str, class_name: str='fighter')` - Get feature description from feature definitions.
- `_get_spell_slots_for_class_level(self, class_name: str, level: int)` - Get spell slots by level for a class/level combination.
- `_load_character_portrait(self, character_name: str)` - Load character portrait from data/images/characters directory.
- `_load_character_spells(self, character_id: str)` - Load and format character spells from database.
- `_load_feats_and_features_from_db(self, character_id: str)` - Fetch feats and class features for a character from SQLite.
- `_log_feature_activation(self, feature_name: str, result: dict)` - Log feature activation to the game log.
- `_log_hp_change(self, current_hp: int, max_hp: int)` - Log HP change to game log.
- `_setup_basic_panel(self)` - Setup the basic character panel (always visible) with D&D layout.
- `_setup_detail_panel(self)` - Setup the detailed character panel (shown when expanded).
- `_setup_ui(self)` - Initialize the character panel UI components.
- `_toggle_expansion(self)` - Toggle the panel expansion - simple and reliable approach.
- `_update_conditions(self, character_data: Dict[str, Any])` - Update the condition display widget.
- `_update_detail_panel(self)` - Update the detailed panel with character-specific information.
- `_update_regular_spell_slots(self, spell_slots: Dict[int, int], character_data: Dict[str, Any])` - Update regular spell slot displays.
- `_update_spell_slots_display(self, character_data: Dict[str, Any])` - Update spell slot display based on character class and level.
- `_update_warlock_pact_slots(self, level: int, character_data: Dict[str, Any])` - Update Warlock pact magic slot display.
- `_update_xp_displays(self)` - Update all XP-related displays.
- `add_xp_gain(self, description: str, xp_gain: int)` - Public method to add XP gain and update displays.
- `clear_character_data(self)` - Clear the character display.
- `is_expanded(self)` - Return current expansion state.
- `load_character_data(self, character_data: Dict[str, Any])` - Load character data into the panel display.
- `refresh_conditions(self)` - Force refresh of condition display (for external updates).
- `update_ac(self, new_ac)` - Update the AC display when equipment changes.
- `update_hp(self, current_hp: int, max_hp: int)` - Update HP display - database should already be updated by game engine.

## core - `src/talekeeper/ui/condition_display.py`

- `__init__(self, condition: ActiveCondition, parent=None)` - Inferred from name: init.
- `_build_tooltip(self)` - Build detailed HTML tooltip.
- `_get_badge_text(self)` - Get 3-letter abbreviation for condition.
- `_get_condition_severity(self)` - Determine severity level for color coding.
- `_get_effects_summary(self)` - Get brief summary of condition's mechanical effects.
- `_setup_badge(self)` - Initialize the badge appearance and content.
- `__init__(self, character_id: str=None, db_path: str='talekeeper.db', parent=None)` - Inferred from name: init.
- `_clear_badges(self)` - Remove all existing badge widgets.
- `_clear_display(self)` - Clear all condition badges.
- `_setup_ui(self)` - Initialize the widget layout.
- `_update_display(self, conditions: List, spell_effects: List[Dict])` - Inferred from name: update display.
- `add_test_conditions(self)` - Add test conditions for UI development (debug only).
- `get_condition_summary_for_log(self)` - Get a detailed text summary for log panel.
- `refresh_conditions(self)` - Inferred from name: refresh conditions.
- `set_character_id(self, character_id: str)` - Update the character ID and refresh display.
- `__init__(self, spell_name: str, effect_type: str, effect_data: Dict, rounds_remaining: int=None, concentration: bool=False, parent=None)` - Inferred from name: init.
- `_build_tooltip(self)` - Inferred from name: build tooltip.
- `_get_badge_text(self)` - Inferred from name: get badge text.
- `_get_effect_description(self)` - Inferred from name: get effect description.
- `_setup_badge(self)` - Inferred from name: setup badge.

## core - `src/talekeeper/ui/dialogs/downtime_dialog.py`

- `__init__(self, character_data: Dict[str, Any], db_path: str='talekeeper.db', parent=None)` - Inferred from name: init.
- `_calculate_carousing_cost(self, level: int)` - Inferred from name: calculate carousing cost.
- `_calculate_prayer_cost(self, level: int)` - Inferred from name: calculate prayer cost.
- `_create_activity_frame(self, title: str, description: str, cost: int, character_gold: int, callback)` - Inferred from name: create activity frame.
- `_get_character_gold(self, character_id: str)` - Inferred from name: get character gold.
- `_load_activity_history(self)` - Inferred from name: load activity history.
- `_setup_ui(self)` - Inferred from name: setup ui.
- `_start_carousing(self)` - Inferred from name: start carousing.
- `_start_prayer(self)` - Inferred from name: start prayer.

## core - `src/talekeeper/ui/dialogs/spell_preparation_dialog.py`

- `__init__(self, character_id: str, character_name: str, db_path: str='talekeeper.db', parent=None)` - Inferred from name: init.
- `_load_character_data(self)` - Inferred from name: load character data.
- `_load_spells(self)` - Inferred from name: load spells.
- `_on_spell_toggled(self, spell_id: str, checked: bool)` - Inferred from name: on spell toggled.
- `_setup_ui(self)` - Inferred from name: setup ui.
- `_update_count(self)` - Inferred from name: update count.
- `get_prepared_spells(self)` - Inferred from name: get prepared spells.
- `save_prepared_spells(self)` - Inferred from name: save prepared spells.

## core - `src/talekeeper/ui/dialogs/warlock_level_up_dialog.py`

- `__init__(self, character_id: str, character_name: str, level: int, invocations_to_learn: int, db_path: str='talekeeper.db', parent=None)` - Inferred from name: init.
- `_load_data(self)` - Inferred from name: load data.
- `_load_invocations(self)` - Inferred from name: load invocations.
- `_load_spells(self)` - Inferred from name: load spells.
- `_meets_invocation_prerequisites(self, prereqs: dict, pact_boon: Optional[str])` - Inferred from name: meets invocation prerequisites.
- `_on_confirm(self)` - Inferred from name: on confirm.
- `_on_invocation_clicked(self, item: QListWidgetItem)` - Inferred from name: on invocation clicked.
- `_on_spell_clicked(self, item: QListWidgetItem)` - Inferred from name: on spell clicked.
- `_setup_ui(self)` - Inferred from name: setup ui.
- `get_selections(self)` - Inferred from name: get selections.

## core - `src/talekeeper/ui/encounter_pane/alt_encounters.py`

- `_article_for(word: str)` - Inferred from name: article for.
- `_build_effect_text(base_effect: str, variant: dict)` - Inferred from name: build effect text.
- `_build_variant_description(variant: dict, base_description: str)` - Inferred from name: build variant description.
- `_choose_trap_variant(trap_type: str, level: int)` - Inferred from name: choose trap variant.
- `_format_variant_effect(variant: dict)` - Inferred from name: format variant effect.
- `_trap_level_range(level: int)` - Inferred from name: trap level range.
- `format_resource(resource: dict, tier_value: int)` - Inferred from name: format resource.
- `generate_hazard(level: int=1)` - Inferred from name: generate hazard.
- `generate_skill_challenge(level: int)` - Inferred from name: generate skill challenge.
- `generate_trap(level: int)` - Inferred from name: generate trap.

## core - `src/talekeeper/ui/encounter_pane/campaign_frame.py`

- `__init__(self, data=None, name: str=None, monster_type_weights: Optional[Dict[str, float]]=None, difficulty_distribution: Dict[str, float]=None, rest_rules: Dict[str, float]=None, style: str='', available_classes: Optional[List[str]]=None, monster_alignment_rules: Optional[Dict[str, any]]=None, guaranteed_hoards: bool=False, description: str='', llm_model: Optional[str]=None, lora_adapter: Optional[str]=None, narrative_prompt: Optional[str]=None, tags: Optional[List[str]]=None)` - Inferred from name: init.
- `load_from_file(path: str)` - Inferred from name: load from file.
- `save_to_file(self, path: str)` - Inferred from name: save to file.
- `to_dict(self)` - Inferred from name: to dict.

## core - `src/talekeeper/ui/encounter_pane/encounter_generator.py`

- `__init__(self, data: Dict[str, Any])` - Inferred from name: init.
- `__init__(self, frame: CampaignFrame, description_service: Optional['CampaignDescriptionService']=None)` - Inferred from name: init.
- `_attach_monster_narrative(self, monsters: List[Dict[str, Any]], level: int, difficulty: str)` - Return copies of ``monsters`` with a unified encounter description.
- `_can_pair_with_beast(self, monster: Dict[str, Any])` - Check if a monster can be paired with a beast (both must have Int 6+)
- `_generate_leader_minions_encounter(self, available: List[Dict[str, Any]], budget: int)` - 1 leader + 1-4 minions of same type (aberration, fiend, humanoid, undead, etc)
- `_generate_pair_encounter(self, available: List[Dict[str, Any]], budget: int)` - Pair of 2 random types (if one is beast, other must be beast or Int 6+)
- `_generate_solo_encounter(self, available: List[Dict[str, Any]], budget: int)` - High difficulty: Single strongest monster
- `_get_available_monsters(self, level: int)` - Get monsters available for this level based on CR and campaign rules
- `generate_encounter(self, level: int)` - Inferred from name: generate encounter.
- `get_budget(self, level: int, difficulty: str)` - Inferred from name: get budget.
- `__init__(self, items: List[Any])` - Inferred from name: init.
- `draw(self)` - Inferred from name: draw.
- `load_monsters(campaign_id: Optional[str]=None)` - Load monsters from database, optionally filtered by campaign
- `roll_monster_hp(hp_formula: str)` - Roll HP using dice formula like '3d8' or '18d10 + 36'.

## core - `src/talekeeper/ui/encounter_pane/encounter_panel.py`

- `can_take_action(self, combatant_id: str, action_type: str)` - Check if a combatant can take a specific type of action.
- `start_combat_with_action_economy(self, character_id: str)` - Initialize combat session with action economy tracking.
- `use_action(self, combatant_id: str, action_type: str, action_name: str, action_data: Dict=None)` - Attempt to use an action and record it.
- `add_defeated_monster(self, xp_value: int)` - Add a defeated monster to the encounter.
- `complete_encounter(self)` - Mark encounter as completed.
- `from_encounter_data(cls, encounter_data: Dict[str, Any], character_id: str)` - Create an Encounter from encounter data.
- `get_initiative_order(self, monster_instances: list)` - Get initiative order for all participants.
- `is_complete(self)` - Check if encounter is completed.
- `roll_initiative(self, player_dex_mod: int, monster_instances: list, monster_data: dict, character_context: dict=None, character_features: dict=None)` - Roll initiative for player and all monsters with advantage/disadvantage support.
- `start_combat(self)` - Start combat mode for this encounter.
- `from_monster_data(cls, monster_data: Dict[str, Any], encounter_id: str, rolled_hp: Optional[int]=None)` - Create encounter instance from monster generator data.
- `heal(self, healing: int)` - Apply healing and return actual healing done.
- `hp_percentage(self)` - Calculate HP percentage for health bar displays.
- `take_damage(self, damage: int)` - Apply damage and return actual damage dealt.
- `to_dict(self)` - Convert to dictionary for serialization.
- `__init__(self, parent: Optional[QWidget]=None, layout_profile: Optional[LayoutProfile]=None)` - Inferred from name: init.
- `_add_gold_to_character(self, gold_amount: int)` - Add gold to the current character.
- `_add_items_to_character(self, items: list)` - Add dropped items to character inventory and auto-equip if better.
- `_add_magic_items_to_character(self, magic_items: list)` - Add magical items to character inventory.
- `_add_treasure_with_conversion(self, gold_amount: int, monster_cr: float=1.0)` - Add treasure with automatic conversion to gems/art for large amounts.
- `_add_xp_to_character(self, xp_value: int)` - Add XP to the current character.
- `_apply_class_defaults(self)` - Apply class-specific default ability scores.
- `_apply_class_defaults_auto(self)` - Automatically apply class defaults when class is selected.
- `_apply_damage_to_monster(self, instance_id: str, damage: int)` - Apply damage to a specific monster instance and update UI.
- `_apply_styles(self)` - Apply dark theme styling to encounter panel components.
- `_attempt_dangerous_trap_disarm(self, trap: dict, ctx: Dict[str, Any])` - Inferred from name: attempt dangerous trap disarm.
- `_auto_select_background_feat(self, bg_data)` - Auto-select the default feat for the chosen background.
- `_award_trap_xp(self, xp_amount: int, trap_label: str)` - Inferred from name: award trap xp.
- `_award_xp_for_defeated_monster(self, instance: EncounterInstance)` - Award XP to character for defeating a monster.
- `_build_trap_context(self)` - Build context data used when resolving traps.
- `_calculate_skill_challenge_xp(self, character_level: int, success: bool=True)` - Calculate XP reward for skill challenge based on character level.
- `_can_character_level_up(self)` - Check if current character can level up
- `_categorize_monster(self, monster_name: str)` - Categorize monster type for loot table purposes.
- `_character_has_item(self, item_name: str, character_id: str)` - Check if character already has this item.
- `_check_attunement_requirement(self, item_name: str, character_class: str)` - Check if character meets attunement requirements for magic item.
- `_check_danger_sense_advantage(self, ctx: Dict[str, Any], ability: str)` - Check if character gets Danger Sense advantage on saving throw.
- `_check_encounter_stealth(self, monsters: List[Dict[str, Any]])` - Check if player can start encounter hidden.
- `_check_for_hoard(self, difficulty: str)` - Check for hoard treasure based on encounter difficulty.
- `_check_if_beast(self, monster_name: str)` - Check if a monster is a beast type (should drop rations instead of gold).
- `_check_item_proficiency(self, item_name: str, character_class: str)` - Check if character can use this magic item.
- `_check_item_type_proficiency(self, item_type: str, character_class: str)` - Check if character class is proficient with this item type.
- `_check_pickpocket_opportunity(self)` - Check if pickpocket action card should be shown.
- `_check_skill_conflicts(self)` - Check if background skills conflict with selected class skills and allow re-selection.
- `_check_weapon_proficiency(self, weapon_name: str, character_class: str)` - Check if character class is proficient with weapon type.
- `_cleanup_active_widgets(self)` - Clean up any active encounter widgets (vendor, skill challenge, hazard, etc.).
- `_clear_encounter_after_parlay(self)` - Clear the encounter after successful parlay or refusal.
- `_clear_monster_cards(self)` - Clear all monster cards from the grid layout.
- `_clear_trap_cards(self)` - Clear any trap cards from the layout.
- `_combine_trap_text(self, *parts: str)` - Inferred from name: combine trap text.
- `_create_abilities_step(self)` - Create ability score assignment step.
- `_create_background_species_step(self)` - Create background and species selection step.
- `_create_class_features_step(self)` - Create the class features selection step.
- `_create_class_selection_step(self)` - Create the class selection step widget.
- `_create_dangerous_trap_card(self, trap: dict, level: int)` - Inferred from name: create dangerous trap card.
- `_create_equipment_step(self)` - Create equipment selection step.
- `_create_loot_action_card(self)` - Create the Loot action card for post-combat.
- `_create_monster_card(self, instance: EncounterInstance)` - Create a compact monster card using action card styling.
- `_create_review_step(self)` - Create final review and confirmation step.
- `_create_setback_trap_card(self, trap: dict, level: int)` - Inferred from name: create setback trap card.
- `_create_short_rest_action_card(self)` - Create the Short Rest action card for post-combat.
- `_create_temporary_settlement(self, character_id: str, q: int, r: int)` - Create a temporary settlement in the hex map for encounter-based resting.
- `_creation_next_step(self)` - Move to next character creation step.
- `_creation_previous_step(self)` - Move to previous character creation step.
- `_deal_trap_damage(self, amount: int, source: str)` - Inferred from name: deal trap damage.
- `_determine_detection_check(self, ctx: Dict[str, Any])` - Determine the best skill check for trap detection, with potential advantage.
- `_determine_item_type(self, item_name: str)` - Determine the item type based on the item name.
- `_end_combat_session(self)` - End combat session and notify action panel.
- `_end_rage_on_rest(self)` - End rage when character takes any rest.
- `_ensure_trap_context(self)` - Ensure trap context includes current game engine and character data.
- `_finish_character_creation(self)` - Complete character creation and emit the character data.
- `_flee_encounter(self)` - Handle fleeing from encounter while hidden.
- `_force_reload_character(self)` - Force reload character data in all panels.
- `_format_trap_summary(self, trap: dict, extra: Optional[str]=None)` - Inferred from name: format trap summary.
- `_generate_hazard_encounter(self)` - Inferred from name: generate hazard encounter.
- `_generate_hoard_magic_items(self, count: int, monster_cr: float)` - Generate magical items for hoard treasure based on CR and loot plan.
- `_generate_monster_encounter(self)` - Generate a random monster encounter based on active character level.
- `_generate_selected_encounter(self)` - Generate encounter based on selected type.
- `_generate_skill_challenge(self)` - Generate an interactive skill challenge.
- `_generate_trap_encounter(self)` - Generate a trap encounter with automated resolution.
- `_generate_vendor_encounter(self)` - Inferred from name: generate vendor encounter.
- `_get_armor_upgrade(self, character_equipment: dict, rarity: str)` - Get armor upgrade based on current armor.
- `_get_character_equipment(self)` - Get current character's equipped items and class info.
- `_get_character_level(self)` - Get the level of the current active character.
- `_get_character_proficient_skills(self)` - Get list of skills the character is proficient in from their selections.
- `_get_class_dump_stats(self, class_name: str)` - Get dump stat for a class.
- `_get_creation_skill_proficiencies(self)` - Get skill proficiencies already selected during character creation.
- `_get_current_character_data(self)` - Get current character data from game engine
- `_get_current_character_data(self)` - Get full character data for current character.
- `_get_current_character_id(self)` - Get the ID of the current active character.
- `_get_current_character_id(self)` - Get the current character's ID.
- `_get_game_engine(self)` - Fetch the active game engine reference from the widget hierarchy.
- `_get_item_cr_appropriateness(self, item: dict, monster_type: str)` - Get the CR level this item is appropriate for based on monster type.
- `_get_max_affordable_value(self, changed_spinbox)` - Find the highest value we can set without exceeding budget.
- `_get_monster_image_path(self, monster_name: str)` - Get the path to a monster's image file.
- `_get_priority_item(self, rarity: str, character_equipment: dict)` - Get priority item based on current equipment and proficiency.
- `_get_protection_item(self, character_equipment: dict, rarity: str)` - Get protection item based on character needs.
- `_get_random_item(self, rarity: str)` - Get random item from remaining pool.
- `_get_rarity_for_bonus(self, bonus: str)` - Get rarity based on bonus.
- `_get_saving_throw_bonus_for_trap(self, ctx: Dict[str, Any], ability: str)` - Inferred from name: get saving throw bonus for trap.
- `_get_skill_bonus(self, ctx: Dict[str, Any], skill_name: str)` - Inferred from name: get skill bonus.
- `_get_weapon_upgrade(self, current_weapon: str, character_class: str, bonus: str)` - Get weapon upgrade based on current weapon.
- `_handle_loot_action(self)` - Handle clicking the Loot action card.
- `_handle_short_rest_action(self)` - Handle clicking the Short Rest action card.
- `_has_thieves_tools_equipped(self, ctx: Dict[str, Any])` - Check if thieves tools are equipped in the belt slot.
- `_heal_monster(self, instance_id: str, healing: int)` - Heal a specific monster instance and update UI.
- `_init_combat_session(self)` - Initialize combat session and notify action panel.
- `_initiate_surprise_attack(self)` - Handle surprise attack from hidden state.
- `_is_in_combat(self)` - Check if currently in combat
- `_item_allows_duplicates(self, item: dict)` - Check if item can drop multiple times (potions and one-handed weapons).
- `_load_background_species_data(self)` - Load background and species data from JSON files.
- `_load_campaign_frame(self)` - Load campaign frame from specified file and initialize encounter generator.
- `_load_class_data(self)` - Load class data from talekeeper.database.
- `_load_feats_data(self)` - Load available feats from talekeeper.database.
- `_log_monster_action(self, message: str)` - Log monster-related actions to the log panel if available.
- `_log_xp_gain(self, monster_name: str, xp_value: int)` - Log XP gain to the combat log.
- `_maybe_award_trap_treasure(self, trap_type: str, level: int)` - Inferred from name: maybe award trap treasure.
- `_on_ability_value_changed(self, value)` - Handle ability score changes with budget enforcement.
- `_on_background_selected(self, current, previous)` - Handle background selection change.
- `_on_class_selected(self, current, previous)` - Handle class selection change.
- `_on_class_skill_toggled(self, skill_name: str, state: int, max_skills: int)` - Handle class skill checkbox toggle with selection limit.
- `_on_expertise_skill_toggled(self, skill_name: str, checked: bool)` - Handle expertise skill checkbox toggle with selection limit.
- `_on_feat_selected(self)` - Handle feat selection and update description.
- `_on_fighting_style_selected(self)` - Handle Fighting Style selection change.
- `_on_hazard_completed(self, success: bool, xp_gained: int, damage_taken: int, exhaustion_gained: int, roll_summary: str)` - Inferred from name: on hazard completed.
- `_on_hero_mode_toggled(self, state)` - Handle Hero Mode checkbox toggle.
- `_on_invocation_selected(self)` - Handle Eldritch Invocation selection change.
- `_on_long_rest_completed(self, result, hex_q, hex_r)` - Handle successful long rest completion.
- `_on_long_rest_encounter(self, encounter_data)` - Handle encounter that interrupted rest.
- `_on_mouse_release(event)` - Inferred from name: on mouse release.
- `_on_parlay_completed(self, outcome: str, reward_text: str, xp_reward: int, monsters: List[Dict])` - Handle parlay challenge completion.
- `_on_parlay_refused(self, refuse_cost: str)` - Handle parlay refusal.
- `_on_rest_cancelled()` - Inferred from name: on rest cancelled.
- `_on_rest_completed(result: dict)` - Inferred from name: on rest completed.
- `_on_rest_encounter(payload: dict)` - Inferred from name: on rest encounter.
- `_on_skill_challenge_completed(self, outcome: str, reward_text: str)` - Handle skill challenge completion.
- `_on_skill_challenge_refused(self, refuse_cost: str)` - Handle skill challenge refusal.
- `_on_species_selected(self, current, previous)` - Handle species selection change.
- `_on_species_skill_selected(self, combo_widget)` - Handle single species skill selection from combo box.
- `_on_species_skill_toggled(self, skill_name: str, state: int, max_skills: int)` - Handle species skill checkbox toggle with selection limit.
- `_on_spells_changed(self)` - Inferred from name: on spells changed.
- `_perform_long_rest(self)` - Perform long rest - restore all resources according to D&D 5e rules.
- `_perform_short_rest(self)` - Perform short rest - instant ability recovery and optional hit dice spending.
- `_populate_class_features(self)` - Populate class-specific features based on selected class.
- `_populate_equipment_choices(self)` - Populate equipment choices based on selected class.
- `_populate_feat_lists(self)` - Populate the feat selection dropdowns with available feats.
- `_refresh_equipment_panel(self, game_engine, character_id)` - Refresh the equipment panel to show updated inventory.
- `_refresh_expertise_options(self)` - Refresh the expertise selection options when skills change.
- `_resolve_dangerous_trap_avoid(self, trap: dict, output_label: QLabel, buttons: tuple)` - Inferred from name: resolve dangerous trap avoid.
- `_resolve_dangerous_trap_take_risk(self, trap: dict, level: int, output_label: QLabel, buttons: tuple)` - Inferred from name: resolve dangerous trap take risk.
- `_resolve_setback_trap(self, trap: dict, level: int)` - Inferred from name: resolve setback trap.
- `_restore_parlay_encounter_for_combat(self)` - Restore the parlay encounter and start combat.
- `_roll_4d6_overlay(self)` - Roll 4d6 drop lowest for each ability score and auto-apply higher values.
- `_roll_d20(self, bonus: int, advantage: bool=False)` - Inferred from name: roll d20.
- `_roll_damage_formula(self, formula: str)` - Inferred from name: roll damage formula.
- `_roll_equipment_drops(self, monster_name: str, monster_cr)` - Roll for equipment drops based on monster CR using BiS system.
- `_roll_hit_dice(self, dialog, game_engine, character, num_dice, hit_die, status_label)` - Roll hit dice and apply healing.
- `_roll_individual_treasure(self, monster_cr)` - Roll individual treasure based on monster CR.
- `_save_encounter_instances_to_db(self)` - Save current encounter instances to the database.
- `_save_encounter_to_db(self)` - Save the current encounter to the database.
- `_select_monster_card(self, instance_id: str)` - Select a monster card for targeting.
- `_set_action_card_click_handler(self, card: QWidget, handler)` - Make the entire action card clickable by wiring a mouse release handler.
- `_set_campaign_file(self, filename: str)` - Set the campaign file to load.
- `_setup_character_creation_steps(self)` - Setup the character creation step widgets.
- `_setup_class_skill_selection(self, class_id: str)` - Setup skill selection interface for the selected class.
- `_setup_fighter_features(self)` - Setup Fighter Level 1 class features.
- `_setup_rogue_features(self)` - Setup Rogue Level 1 class features.
- `_setup_species_skill_selection(self, species_id: str)` - Setup skill selection interface for the selected species.
- `_setup_spell_selection(self, class_name: str)` - Inferred from name: setup spell selection.
- `_setup_ui(self)` - Initialize the encounter panel UI components.
- `_setup_warlock_features(self)` - Setup Warlock Level 1 class features.
- `_show_defensive_halo(self, monster_card)` - Show defensive halo when hovering over monster card.
- `_show_hidden_action_buttons(self)` - Show special action buttons when player is hidden.
- `_show_hit_dice_dialog(self, game_engine, character)` - Show dialog for optional hit dice spending.
- `_show_initial_random_encounter(self)` - Display a randomly selected encounter on startup.
- `_show_long_rest_widget(self)` - Show the new Long Rest widget with lifestyle options and hazard system.
- `_show_parlay_skill_challenge(self, session_id: str, xp_reward: int, monsters: List[Dict])` - Display the parlay skill challenge widget.
- `_show_post_combat_actions(self)` - Add Loot and Short Rest action cards after the monster cards.
- `_start_combat(self)` - Start combat with current encounter.
- `_trigger_trap_effect(self, trap: dict, ctx: Dict[str, Any])` - Inferred from name: trigger trap effect.
- `_update_action_buttons(self)` - Update button states based on current mode.
- `_update_background_bonuses(self)` - D&D 2024: Background provides up to 3 points distributed as +1/+1/+1 or +2/+1.
- `_update_bg_species_description(self)` - Update the combined background/species description.
- `_update_card_selection_display(self, instance_id: str, selected: bool)` - Update the visual display of a monster card's selection state.
- `_update_character_sheet_hp(self, current_hp: int, max_hp: int)` - Update the character sheet HP display.
- `_update_character_sheet_xp(self, monster_name: str, xp_value: int)` - Update the character sheet XP display.
- `_update_creation_step(self)` - Update the current creation step display and navigation.
- `_update_final_scores(self)` - Update final ability scores with point buy/rolled + background bonuses (D&D 2024).
- `_update_hidden_status_ui(self)` - Update the UI to show hidden status.
- `_update_monster_card_display(self, instance_id: str)` - Update the visual display of a monster card after HP changes.
- `_update_monster_tooltip(self, monster_id: str, knowledge, skill: str, roll_result: int)` - Update a monster card's tooltip with revealed knowledge.
- `_update_point_buy(self)` - Update point buy calculations.
- `_update_racial_bonuses(self)` - Legacy method - now calls background bonuses.
- `_update_town_tab_state(self)` - Update town tab tooltip and enabled state based on combat status
- `_use_defensive_resource(self, resource_type: str, monster_id: str)` - Handle defensive resource usage (imposing disadvantage on monster attacks).
- `_would_exceed_budget(self, changed_spinbox, new_value)` - Check if changing a spinbox to new_value would exceed point budget.
- `add_encounter(self, encounter_data: Dict[str, Any])` - Add an encounter to the list.
- `attempt_parlay(self)` - Attempt to parlay with the current encounter.
- `clear_encounters(self)` - Clear all encounters.
- `exit_character_creation(self)` - Exit character creation and return to exploration.
- `get_all_encounter_instances(self)` - Get all current encounter instances.
- `get_current_mode(self)` - Get the current encounter mode.
- `get_encounter_instance(self, instance_id: str)` - Get an encounter instance by ID.
- `get_living_monsters(self)` - Get all living monsters in the current encounter.
- `get_selected_encounter(self)` - Get the currently selected encounter data.
- `get_selected_monster(self)` - Get the currently selected monster instance.
- `hide_town_encounter(self)` - Hide the town encounter tab
- `is_encounter_complete(self)` - Check if all monsters in the encounter are defeated.
- `monster_enter_event(event)` - Inferred from name: monster enter event.
- `monster_leave_event(event)` - Inferred from name: monster leave event.
- `perform_monster_study(self)` - Perform a monster knowledge check when Study button is clicked.
- `refresh_character_data(self)` - Refresh character data and check if town tab should be shown/hidden
- `remove_town_encounter(self)` - Remove the town encounter tab completely
- `set_character_creation_mode(self)` - Switch to character creation mode.
- `set_combat_mode(self)` - Switch to combat mode.
- `set_difficulty(self, difficulty: str)` - Set the difficulty indicator.
- `set_encounter_mode(self)` - Switch to encounter mode.
- `set_exploration_mode(self)` - Switch to exploration mode.
- `show_town_encounter(self)` - Show the town encounter tab if level up is available
- `update_environment_details(self, details: str)` - Update environmental information (environment tab removed).
- `update_scene_description(self, description: str)` - Update the main scene description.
- `update_status(self, status: str)` - Update the status message.
- `update_theme(self, theme_name: str)` - Update styling based on theme.
- `restore_hit_dice_on_long_rest(character)` - Restore hit dice per long rest rules and sync with level.
- `sync_hit_dice_with_level(character)` - Ensure hit dice maximum matches level and add only new dice.

## core - `src/talekeeper/ui/encounter_pane/hazard_widget.py`

- `__init__(self, parent=None)` - Inferred from name: init.
- `_populate_gear_list(self)` - Inferred from name: populate gear list.
- `attempt_hazard(self)` - Inferred from name: attempt hazard.
- `set_character_data(self, character_data: Dict)` - Inferred from name: set character data.
- `setup_ui(self)` - Inferred from name: setup ui.
- `start_hazard(self, hazard: Dict)` - Inferred from name: start hazard.

## core - `src/talekeeper/ui/encounter_pane/hex_shop_interface.py`

- `__init__(self, character_data: Dict[str, Any], settlement_type: str, hex_seed: int, hex_coords: tuple, parent=None, population: Optional[int]=None)` - Inferred from name: init.
- `_add_negotiation_info(self)` - Inferred from name: add negotiation info.
- `_get_negotiation_summary(self)` - Inferred from name: get negotiation summary.
- `_get_shop_size(self, settlement_type: str)` - Inferred from name: get shop size.
- `_handle_transaction(self)` - Inferred from name: handle transaction.
- `_load_character_inventory(self)` - Inferred from name: load character inventory.
- `_load_shop_inventory(self)` - Inferred from name: load shop inventory.
- `_populate_items_list(self)` - Inferred from name: populate items list.
- `_settlement_display_name(self, settlement_type: str)` - Inferred from name: settlement display name.
- `_update_total_cost(self)` - Inferred from name: update total cost.

## core - `src/talekeeper/ui/encounter_pane/skill_challenge_widget.py`

- `__init__(self, skill_name: str, current_dc: int, parent=None)` - Inferred from name: init.
- `update_dc(self, new_dc: int)` - Inferred from name: update dc.
- `update_text(self)` - Inferred from name: update text.
- `__init__(self, parent=None)` - Inferred from name: init.
- `attempt_skill(self, skill_name: str)` - Attempt a skill check.
- `clear_skill_buttons(self)` - Remove all skill buttons.
- `display_attempt_result(self, result: SkillAttemptResult)` - Display the result of a skill attempt.
- `get_random_challenge_template(self)` - Get a random challenge template for testing.
- `handle_challenge_completion(self, outcome: str)` - Handle when a challenge is completed.
- `load_active_session(self, character_id: str)` - Load an existing active session for the character.
- `refuse_challenge(self)` - Refuse the current challenge.
- `request_new_challenge(self)` - Request a new challenge (should be handled by parent).
- `set_character_data(self, character_data: Dict)` - Set the current character data.
- `setup_ui(self)` - Inferred from name: setup ui.
- `start_challenge(self, template: SkillChallengeTemplate)` - Start a new skill challenge.
- `update_skill_buttons(self)` - Update the skill buttons based on current session.
- `update_theme(self, is_dark: bool)` - Update widget theme.
- `update_ui_state(self)` - Update the UI based on current session state.

## core - `src/talekeeper/ui/encounter_pane/skill_selection_dialog.py`

- `__init__(self, character_id: str, num_skills: int=3, parent=None)` - Inferred from name: init.
- `_confirm_selection(self)` - Inferred from name: confirm selection.
- `_get_character_skill_proficiencies(self)` - Inferred from name: get character skill proficiencies.
- `_load_available_skills(self)` - Inferred from name: load available skills.
- `_on_selection_changed(self)` - Inferred from name: on selection changed.
- `_setup_ui(self)` - Inferred from name: setup ui.
- `get_selected_skills(self)` - Inferred from name: get selected skills.

## core - `src/talekeeper/ui/encounter_pane/spell_selection_widget.py`

- `__init__(self, parent=None, db_path='talekeeper.db')` - Inferred from name: init.
- `_clear_widgets(self)` - Inferred from name: clear widgets.
- `_load_spells_for_class(self, class_id: str, level: int)` - Inferred from name: load spells for class.
- `_on_cantrip_selected(self, combo: QComboBox)` - Inferred from name: on cantrip selected.
- `_on_spell_toggled(self, spell_id: str, checked: bool, max_spells: int)` - Inferred from name: on spell toggled.
- `_setup_cantrip_selection(self, class_id: str, count: int)` - Inferred from name: setup cantrip selection.
- `_setup_preparation_info(self, class_id: str)` - Inferred from name: setup preparation info.
- `_setup_spell_selection(self, class_id: str, count: int)` - Inferred from name: setup spell selection.
- `_setup_ui(self)` - Inferred from name: setup ui.
- `_show_spell_description(self, spell: Dict)` - Inferred from name: show spell description.
- `get_selected_cantrips(self)` - Inferred from name: get selected cantrips.
- `get_selected_spells(self)` - Inferred from name: get selected spells.
- `is_selection_complete(self, class_name: str)` - Inferred from name: is selection complete.
- `setup_for_class(self, class_name: str)` - Inferred from name: setup for class.

## core - `src/talekeeper/ui/encounter_pane/town_encounter.py`

- `__init__(self, character_data: Dict[str, Any], shop_size: ShopSize=ShopSize.MEDIUM, parent=None)` - Inferred from name: init.
- `_add_gold(self, amount: float)` - Add gold to character inventory with Bag of Holding support
- `_add_item_to_inventory(self, item_data: Dict[str, Any], quantity: int)` - Add purchased item to character inventory
- `_deduct_gold(self, amount: float)` - Deduct gold from character inventory
- `_display_item_details(self, item: Dict[str, Any])` - Display detailed information about selected item
- `_get_character_gold(self)` - Get character's current gold
- `_handle_transaction(self)` - Handle buying or selling transaction
- `_item_selected(self, row: int)` - Handle item selection
- `_load_character_inventory(self)` - Load character's sellable inventory items
- `_load_shop_inventory(self)` - Load shop inventory based on shop size
- `_populate_items_list(self)` - Populate items list based on mode
- `_remove_item_from_inventory(self, item_data: Dict[str, Any], quantity: int)` - Remove item from character inventory
- `_set_shop_mode(self, mode: str)` - Set shop mode (buy or sell)
- `_setup_ui(self)` - Setup shop interface
- `_update_character_gold(self)` - Update display of character's gold
- `_update_total_cost(self)` - Update total cost display
- `__init__(self, card_type: str, icon: str, title: str, description: str, enabled: bool=True)` - Inferred from name: init.
- `mousePressEvent(self, event)` - Inferred from name: mousePressEvent.
- `__init__(self, character_data: Dict[str, Any], parent=None)` - Inferred from name: init.
- `_can_character_level_up(self)` - Check if character has enough XP to level up
- `_handle_card_activation(self, card_type: str)` - Handle clicking on a town card
- `_leave_town(self)` - Leave town and return to exploration
- `_setup_ui(self)` - Setup the town encounter interface
- `_shopping_completed(self)` - Handle shopping completion - refresh the town panel
- `_show_downtime_activities(self)` - Show downtime activities dialog
- `_show_shop(self)` - Show shop size selection dialog, then shop interface
- `_show_training_hall(self)` - Show the training hall interface
- `_training_completed(self)` - Handle training completion - refresh the town panel
- `__init__(self, character_data: Dict[str, Any], parent=None)` - Inferred from name: init.
- `_apply_asi_increases(self, character_id: str)` - Apply ability score increases to character
- `_apply_expertise_selections(self, character_id: str)` - Apply expertise skill selections to character
- `_apply_feat_selection(self, character_id: str)` - Apply selected feat to character
- `_begin_training(self)` - Begin the training process
- `_check_asi_level(self)` - Check if this is an ASI level and show/hide ASI selection
- `_check_expertise_level(self)` - Check if this is Rogue level 6 (expertise upgrade) and show/hide expertise selection
- `_check_subclass_level(self)` - Check if this is the level for subclass selection.
- `_class_selected(self, class_name: str, checked: bool)` - Handle class selection
- `_deduct_gold(self, character_id: str, amount: int)` - Deduct gold from character inventory
- `_get_character_gold(self)` - Get character's current gold from inventory
- `_get_training_cost(self, target_level: int)` - Get training cost and days for target level
- `_load_available_feats(self)` - Load available feats from database
- `_on_asi_allocation_changed(self)` - Handle ASI point allocation changes
- `_on_expertise_skill_toggled(self, skill_name: str, checked: bool)` - Handle expertise skill checkbox toggle with selection limit
- `_on_feat_selected(self, feat_name)` - Handle feat selection
- `_on_feat_selection_changed(self, text)` - Handle feat/ASI selection changes
- `_populate_expertise_options(self)` - Populate expertise skill options for Rogue level 6
- `_populate_subclass_options(self)` - Populate subclass options based on selected class.
- `_setup_asi_feat_selection(self)` - Setup ASI/feat selection interface for ASI levels
- `_setup_expertise_selection(self)` - Setup expertise selection interface for Rogue level 6
- `_setup_subclass_selection(self)` - Setup the subclass selection UI.
- `_setup_ui(self)` - Setup the training hall interface
- `_subclass_selected(self, subclass_data: Dict, checked: bool)` - Handle subclass selection.
- `_update_features_preview(self)` - Update the features preview based on selected class (simplified for training hall)
- `_update_points_remaining(self)` - Update the points remaining display and button state
- `_update_train_button_state(self)` - Update train button state based on all conditions
- `_update_training_info(self)` - Update training information display

## core - `src/talekeeper/ui/encounter_pane/web_form.py`

- `index()` - Inferred from name: index.

## core - `src/talekeeper/ui/equipment_layout/equipment_panel.py`

- `__init__(self, parent: Optional[QWidget]=None, layout_profile: Optional[LayoutProfile]=None)` - Inferred from name: init.
- `_apply_styles(self)` - Apply initial styling using the active theme palette.
- `_calculate_main_hand_attack_bonus(self)` - Calculate attack bonus for main hand weapon.
- `_calculate_spell_attack_bonus(self)` - Calculate spell attack bonus.
- `_calculate_unarmed_attack_bonus(self)` - Calculate unarmed attack bonus.
- `_calculate_unarmed_damage(self)` - Calculate unarmed damage.
- `_calculate_weapon_attack_bonus(self, weapon: Dict[str, Any], is_off_hand: bool=False)` - Calculate attack bonus for a specific weapon.
- `_calculate_weapon_damage(self, weapon: Dict[str, Any], is_off_hand: bool=False)` - Format weapon damage string.
- `_create_equipment_slots(self)` - Create the equipment slot widgets.
- `_drop_selected_item(self)` - Drop the currently selected inventory item.
- `_equip_item(self, item: Dict[str, Any], slot: EquipmentSlot)` - Equip an item to a slot.
- `_extract_weapon_properties(self, weapon: Dict[str, Any])` - Return normalized weapon property tags for the provided weapon.
- `_is_two_handed_weapon(self, item: Dict[str, Any])` - Check if an item is a two-handed weapon.
- `_load_attunement_from_database(self)` - Load attunement state from talekeeper.database.
- `_save_attunement_to_database(self, item_key: str, attune: bool)` - Save or remove attunement state to/from talekeeper.database.
- `_setup_ui(self)` - Initialize the equipment panel UI components.
- `_switch_to_compact_layout(self)` - Switch to compact layout.
- `_switch_to_expanded_layout(self)` - Switch to expanded layout with more detailed information.
- `_toggle_expansion(self)` - Toggle the panel expansion - expands leftward to cover encounter pane.
- `_unequip_item(self, slot: EquipmentSlot)` - Unequip an item from a slot.
- `_update_attack_displays(self)` - Update all attack display rows.
- `_update_character_bonuses(self)` - Update character bonuses from equipped magical items.
- `_update_inventory_display(self)` - Update the inventory list display.
- `_update_stats_display(self)` - Update the stats display based on equipped items.
- `_use_item(self, item_widget: QListWidgetItem)` - Use an item from inventory.
- `_use_selected_item(self)` - Use the currently selected inventory item.
- `add_item_to_inventory(self, item: Dict[str, Any])` - Add an item to the inventory.
- `enable_attunement(self)` - Enable attunement after a rest.
- `get_equipped_items(self)` - Get currently equipped items with enriched database stats.
- `get_equipped_items_dict(self)` - Get currently equipped items as dictionary - alias for get_equipped_items.
- `get_inventory_items(self)` - Get inventory items.
- `is_expanded(self)` - Return current expansion state.
- `load_equipment_data(self, equipped_items: Dict[str, Any], inventory_items: List[Dict[str, Any]], character_strength: int=10, character_dexterity: int=10, character_class: str='', character_constitution: int=10)` - Load equipment and inventory data.
- `remove_item_from_inventory(self, item: Dict[str, Any])` - Remove an item from the inventory.
- `update_theme(self, theme_name: str)` - Update styling based on theme.
- `__init__(self, slot: EquipmentSlot, parent: Optional[QWidget]=None)` - Inferred from name: init.
- `_setup_ui(self)` - Setup the slot UI.
- `clear_item(self)` - Clear the item from this slot.
- `dragEnterEvent(self, event: QDragEnterEvent)` - Handle drag enter event.
- `dropEvent(self, event: QDropEvent)` - Handle drop event.
- `mousePressEvent(self, event)` - Handle mouse press for item removal.
- `set_item(self, item: Dict[str, Any])` - Set the item in this slot.

## core - `src/talekeeper/ui/hex_map/hex_map_widget.py`

- `__init__(self, db_path: str, parent=None)` - Inferred from name: init.
- `_create_hex_polygon(self, center_x: float, center_y: float)` - Inferred from name: create hex polygon.
- `_draw_hex(self, hex_data: Dict)` - Inferred from name: draw hex.
- `_get_hex_color(self, hex_data: Dict)` - Inferred from name: get hex color.
- `_on_vendor_button_clicked(self)` - Inferred from name: on vendor button clicked.
- `_on_view_click(self, event)` - Inferred from name: on view click.
- `_select_hex(self, q: int, r: int)` - Inferred from name: select hex.
- `_setup_theme(self)` - Inferred from name: setup theme.
- `_setup_ui(self)` - Inferred from name: setup ui.
- `_travel_to_hex(self, q: int, r: int)` - Inferred from name: travel to hex.
- `_update_stats(self)` - Inferred from name: update stats.
- `close_map(self)` - Inferred from name: close map.
- `keyPressEvent(self, event)` - Inferred from name: keyPressEvent.
- `refresh_map(self)` - Inferred from name: refresh map.
- `set_character(self, character_id: str, character_name: str)` - Inferred from name: set character.

## core - `src/talekeeper/ui/layout_profiles.py`

- `character_panel_max_width(self)` - Expanded width for animated character sheet.
- `encounter_panel_height(self)` - Height for the encounter column above the action panel.
- `equipment_panel_width(self)` - Right column equipment width matches the log width.
- `usable_width(self)` - Horizontal span inside the left/right margins.

## core - `src/talekeeper/ui/main_window.py`

- `__init__(self, layout_profile: LayoutProfile | None=None)` - Inferred from name: init.
- `_apply_campaign_frame(self, filename: str, campaign_name: str)` - Apply the selected campaign frame to the encounter panel.
- `_apply_feat_effects(self, character_data: Dict, feat_names: List[str])` - Apply mechanical effects from selected feats to character data.
- `_apply_theme(self, theme_name: str)` - Apply the specified theme to the main window and all child widgets.
- `_build_engine_factory(self)` - Inferred from name: build engine factory.
- `_build_voice_profile(self, style_key: str, payload: Dict[str, object])` - Inferred from name: build voice profile.
- `_connect_signals(self)` - Connect all widget signals
- `_convert_dto_to_display(self, character_dict)` - Convert character dictionary to format expected by character sheet.
- `_delete_selected_character(self, char_list, dialog)` - Delete the currently selected character from the dialog list.
- `_force_reload_character(self)` - Refresh inventory and action panels to show updated data.
- `_format_character_for_display(self, character_data)` - Convert character creation data to display format.
- `_get_active_campaign_style(self)` - Inferred from name: get active campaign style.
- `_get_background_id_by_name(self, name)` - Get background ID by name from talekeeper.database.
- `_get_class_id_by_name(self, name)` - Get class ID by name from talekeeper.database.
- `_get_race_id_by_name(self, name)` - Get race ID by name from talekeeper.database.
- `_handle_exploration_action(self, action: str)` - Handle exploration actions like study, search, hide, etc.
- `_initialize_narration_pipeline(self)` - Set up the optional log narration pipeline.
- `_load_campaign_voice_registry(self)` - Inferred from name: load campaign voice registry.
- `_load_character_from_slot(self, slot_number)` - Load a character from a specific save slot.
- `_load_character_into_ui(self, character, log_message)` - Helper method to load a character into the UI.
- `_on_ac_changed(self, new_ac)` - Handle AC change from equipment panel - update character sheet display.
- `_on_character_created(self, character_data)` - Handle completed character creation.
- `_on_hex_map_closed(self)` - Handle hex map being closed.
- `_on_hex_shop_requested(self, q: int, r: int, settlement_type: str)` - Open shop interface for hex-based vendor.
- `_on_hex_travel(self, q: int, r: int)` - Handle player traveling to a new hex.
- `_on_inventory_changed(self)` - Handle inventory changes - save equipment and inventory to database.
- `_on_item_equipped(self, item, slot)` - Handle item equipped - update database and recalculate AC.
- `_on_item_unequipped(self, slot)` - Handle item unequipped - update database and recalculate AC.
- `_on_monster_selected(self, monster_id: str)` - Handle monster selection for targeting.
- `_on_settings_changed(self)` - Handle settings changes.
- `_prepare_character_for_save(self, character_data)` - Convert character creation data to format expected by game engine.
- `_save_and_exit(self)` - Save the current game state and exit the application.
- `_save_character_inventory(self, character_id: str, inventory_items: list)` - Save character's inventory to the database, replacing all existing items.
- `_setup_menu_bar(self)` - Menu bar removed per user request.
- `_setup_ui(self)` - Setup fixed position UI layout - no splitters, no animations
- `_show_campaign_selection(self)` - Show dialog to select campaign frame.
- `_show_load_character_dialog(self)` - Show dialog to load a saved character.
- `_show_settings_dialog(self)` - Show settings dialog.
- `_start_character_creation(self)` - Start the character creation process.
- `_sync_narration_campaign(self)` - Inferred from name: sync narration campaign.
- `_toggle_hex_map(self)` - Toggle hex map display.
- `_toggle_theme(self)` - Toggle between light and dark themes.
- `_try_load_last_character(self)` - Try to load the most recent character, otherwise load test data.
- `_update_character_equipment_slots(self, equipped_items: dict)` - Update the current character's equipment slots in the database.
- `closeEvent(self, event: QCloseEvent)` - Ensure background workers are stopped when window closes.
- `factory(profile: CampaignVoiceProfile)` - Inferred from name: factory.
- `keyPressEvent(self, event)` - Handle global keyboard shortcuts.
- `load_test_data(self)` - Load demo data into all widgets - only used when no saved characters exist
- `on_campaign_selected()` - Inferred from name: on campaign selected.

## core - `src/talekeeper/ui/menu/game_menu.py`

- `__init__(self, parent: Optional[QWidget]=None)` - Inferred from name: init.
- `_apply_styles(self)` - Apply dark theme styling to menu components.
- `_setup_ui(self)` - Initialize the menu UI components.
- `set_character_loaded(self, loaded: bool)` - Enable/disable character-dependent buttons based on whether a character is loaded.
- `set_save_enabled(self, enabled: bool)` - Enable/disable the save & exit button based on game state.
- `update_game_info(self, character_name: str, level: int)` - Update the game information display with character name and level.

## core - `src/talekeeper/ui/monster_knowledge_label.py`

- `__init__(self, monster_data: Dict, character_data: Dict, parent=None)` - Inferred from name: init.
- `auto_roll(self)` - Auto-roll a d20 and add character's skill modifier.
- `get_skill_modifier(self, skill: str)` - Calculate skill modifier for the character.
- `init_ui(self)` - Initialize the user interface.
- `perform_check(self)` - Perform the knowledge check and display results.
- `__init__(self, monster_data: Dict, character_data: Optional[Dict]=None, parent=None)` - Inferred from name: init.
- `enterEvent(self, event: QEnterEvent)` - Show tooltip when mouse enters.
- `mousePressEvent(self, event)` - Handle mouse click to open knowledge check dialog.
- `open_knowledge_dialog(self)` - Open the knowledge check dialog.
- `set_knowledge_result(self, knowledge: MonsterKnowledge)` - Manually set a knowledge check result.
- `update_tooltip(self)` - Update the tooltip with stored knowledge.

## core - `src/talekeeper/ui/rest_pane/event_resolution_widget.py`

- `__init__(self, event_type: str, event_data: Dict, character_data: Dict, rest_service: LongRestService, parent=None)` - Inferred from name: init.
- `_apply_hazard_effects(self)` - Inferred from name: apply hazard effects.
- `_display_encounter(self)` - Inferred from name: display encounter.
- `_display_event(self)` - Inferred from name: display event.
- `_display_hazard(self)` - Inferred from name: display hazard.
- `_format_effects(self, effects: Dict)` - Inferred from name: format effects.
- `_get_ability_modifier(self, ability: str)` - Inferred from name: get ability modifier.
- `_on_action_clicked(self)` - Inferred from name: on action clicked.
- `_on_continue_clicked(self)` - Inferred from name: on continue clicked.
- `_resolve_encounter(self)` - Inferred from name: resolve encounter.
- `_roll_saving_throw(self)` - Inferred from name: roll saving throw.
- `_setup_ui(self)` - Inferred from name: setup ui.

## core - `src/talekeeper/ui/rest_pane/long_rest_widget.py`

- `__init__(self, db_path: str, character_data: Dict, hex_q: int, hex_r: int, parent=None)` - Inferred from name: init.
- `_complete_rest_safely(self, lifestyle: str, cost: float)` - Inferred from name: complete rest safely.
- `_create_lifestyle_option(self, option: Dict, index: int)` - Inferred from name: create lifestyle option.
- `_format_hazard_effects(self, effects: Dict)` - Inferred from name: format hazard effects.
- `_format_settlement_type(self, settlement_type: str)` - Inferred from name: format settlement type.
- `_handle_hazard_event(self, event_type: str, event_data: Dict, lifestyle: str, cost: float)` - Inferred from name: handle hazard event.
- `_load_settlement_data(self)` - Inferred from name: load settlement data.
- `_on_cancel_clicked(self)` - Inferred from name: on cancel clicked.
- `_on_hazard_resolved(self, result: Dict, lifestyle: str, cost: float)` - Inferred from name: on hazard resolved.
- `_on_lifestyle_selected(self, button)` - Inferred from name: on lifestyle selected.
- `_on_rest_clicked(self)` - Inferred from name: on rest clicked.
- `_populate_lifestyle_options(self)` - Inferred from name: populate lifestyle options.
- `_refresh_character_snapshot(self)` - Inferred from name: refresh character snapshot.
- `_setup_ui(self)` - Inferred from name: setup ui.
- `_show_wilderness_rest(self)` - Inferred from name: show wilderness rest.
- `_update_character_status(self)` - Inferred from name: update character status.

## core - `src/talekeeper/ui/settings_dialog.py`

- `__init__(self, parent: Optional[QWidget]=None)` - Inferred from name: init.
- `_on_settings_changed(self)` - Handle settings change.
- `_setup_ui(self)` - Initialize the narrative settings UI.
- `apply_settings(self)` - Apply current settings to config.
- `__init__(self, parent: Optional[QWidget]=None)` - Inferred from name: init.
- `_apply_settings(self)` - Apply all settings.
- `_apply_theme(self)` - Apply theme styling to dialog.
- `_ok_clicked(self)` - Handle OK button click.
- `_on_settings_changed(self)` - Handle settings changed signal.
- `_setup_ui(self)` - Initialize the settings dialog UI.

## core - `src/talekeeper/ui/subclass_features_widget.py`

- `__init__(self, feature: SubclassFeature, character_id: str, parent=None)` - Inferred from name: init.
- `_check_feature_availability(self)` - Check if the feature is currently available to use.
- `_get_action_display(self, action_cost: ActionCost)` - Get display text for action cost.
- `_get_action_style(self, action_cost: ActionCost)` - Get CSS style for action cost badge.
- `_get_type_display(self, feature_type: FeatureType)` - Get display text for feature type.
- `_get_type_style(self, feature_type: FeatureType)` - Get CSS style for feature type badge.
- `_get_unavailability_reason(self)` - Get the reason why the feature is unavailable.
- `_on_activation_clicked(self)` - Handle feature activation button click.
- `_setup_resource_tracking(self, layout: QVBoxLayout)` - Setup resource tracking display.
- `_setup_ui(self)` - Setup the feature widget UI.
- `_update_availability(self)` - Update the feature availability indicator.
- `_update_resource_display(self)` - Update the resource tracking display.
- `eventFilter(self, obj, event)` - Handle mouse events for tooltips.
- `__init__(self, parent=None)` - Inferred from name: init.
- `_setup_ui(self)` - Setup the main features widget UI.
- `refresh_features(self)` - Refresh the display of subclass features.
- `set_character(self, character_id: str, character_level: int)` - Set the character to display features for.
- `update_feature_availability(self)` - Update availability indicators for all features.

## core - `src/talekeeper/ui/themes.py`

- `build_stylesheet(palette: dict[str, str])` - Return a comprehensive PyQt6 stylesheet for the provided color palette.
- `get_theme_names()` - Return list of available theme names.
- `get_theme_palette(theme_name: str)` - Get color palette for the specified theme.

## core - `ui/advantage_halo.py`

- `__init__(self, parent=None)` - Inferred from name: init.
- `mousePressEvent(self, event)` - Handle clicks to use the resource.
- `mouseReleaseEvent(self, event)` - Ensure mouse release is handled properly.
- `paintEvent(self, event)` - Draw a triangle in the top-right corner.
- `position_over_card(self, card_widget)` - Position the halo in the top-right quarter of the given card.
- `show_with_timeout(self, timeout_ms=3000)` - Show the halo and auto-hide after timeout (for defensive usage).
- `update_resources(self, lucky_current, lucky_max, inspiration_current, inspiration_max)` - Update the triangle based on available resources (Inspiration priority).
- `__init__(self, character_data)` - Inferred from name: init.
- `consume_pending_advantage(self)` - Consume pending advantage and return which type was used.
- `consume_resource(self, resource_type)` - Consume a resource and return updated counts.
- `get_primary_resource(self)` - Get the primary resource to display (Inspiration priority).
- `get_resource_counts(self)` - Get all current resource counts.
- `has_pending_advantage(self)` - Check if there's pending advantage for next attack.
- `has_resources(self)` - Check if any advantage resources are available.
- `update_from_character(self, character_data)` - Update resource counts from character data.

## core - `ui/condition_display.py`

- `__init__(self, condition: ActiveCondition, parent=None)` - Inferred from name: init.
- `_build_tooltip(self)` - Build detailed HTML tooltip.
- `_get_badge_text(self)` - Get 3-letter abbreviation for condition.
- `_get_condition_severity(self)` - Determine severity level for color coding.
- `_get_effects_summary(self)` - Get brief summary of condition's mechanical effects.
- `_setup_badge(self)` - Initialize the badge appearance and content.
- `__init__(self, character_id: str=None, db_path: str='talekeeper.db', parent=None)` - Inferred from name: init.
- `_clear_badges(self)` - Remove all existing badge widgets.
- `_clear_display(self)` - Clear all condition badges.
- `_setup_ui(self)` - Initialize the widget layout.
- `_update_display(self, conditions: List[ActiveCondition])` - Update the badge display with current conditions.
- `add_test_conditions(self)` - Add test conditions for UI development (debug only).
- `get_condition_summary_for_log(self)` - Get a detailed text summary for log panel.
- `refresh_conditions(self)` - Update the condition display from database.
- `set_character_id(self, character_id: str)` - Update the character ID and refresh display.

## core - `ui/layout_profiles.py`

- `character_panel_max_width(self)` - Expanded width for animated character sheet.
- `encounter_panel_height(self)` - Height for the encounter column above the action panel.
- `equipment_panel_width(self)` - Right column equipment width matches the log width.
- `usable_width(self)` - Horizontal span inside the left/right margins.

## core - `ui/main_window.py`

- `__init__(self, layout_profile: LayoutProfile | None=None)` - Inferred from name: init.
- `_apply_campaign_frame(self, filename: str, campaign_name: str)` - Apply the selected campaign frame to the encounter panel.
- `_apply_feat_effects(self, character_data: Dict, feat_names: List[str])` - Apply mechanical effects from selected feats to character data.
- `_apply_theme(self, theme_name: str)` - Apply the specified theme to the main window and all child widgets.
- `_build_engine_factory(self)` - Inferred from name: build engine factory.
- `_build_voice_profile(self, style_key: str, payload: Dict[str, object])` - Inferred from name: build voice profile.
- `_connect_signals(self)` - Connect all widget signals
- `_convert_dto_to_display(self, character_dict)` - Convert character dictionary to format expected by character sheet.
- `_delete_selected_character(self, char_list, dialog)` - Delete the currently selected character from the dialog list.
- `_force_reload_character(self)` - Refresh inventory and action panels to show updated data.
- `_format_character_for_display(self, character_data)` - Convert character creation data to display format.
- `_get_active_campaign_style(self)` - Inferred from name: get active campaign style.
- `_get_background_id_by_name(self, name)` - Get background ID by name from database.
- `_get_class_id_by_name(self, name)` - Get class ID by name from database.
- `_get_race_id_by_name(self, name)` - Get race ID by name from database.
- `_initialize_narration_pipeline(self)` - Set up the optional log narration pipeline.
- `_load_campaign_voice_registry(self)` - Inferred from name: load campaign voice registry.
- `_load_character_from_slot(self, slot_number)` - Load a character from a specific save slot.
- `_load_character_into_ui(self, character, log_message)` - Helper method to load a character into the UI.
- `_on_ac_changed(self, new_ac)` - Handle AC change from equipment panel - update character sheet display.
- `_on_character_created(self, character_data)` - Handle completed character creation.
- `_on_inventory_changed(self)` - Handle inventory changes - save equipment and inventory to database.
- `_on_item_equipped(self, item, slot)` - Handle item equipped - update database and recalculate AC.
- `_on_item_unequipped(self, slot)` - Handle item unequipped - update database and recalculate AC.
- `_on_monster_selected(self, monster_id: str)` - Handle monster selection for targeting.
- `_on_settings_changed(self)` - Handle settings changes.
- `_prepare_character_for_save(self, character_data)` - Convert character creation data to format expected by game engine.
- `_save_and_exit(self)` - Save the current game state and exit the application.
- `_save_character_inventory(self, character_id: str, inventory_items: list)` - Save character's inventory to the database, replacing all existing items.
- `_setup_menu_bar(self)` - Menu bar removed per user request.
- `_setup_ui(self)` - Setup fixed position UI layout - no splitters, no animations
- `_show_campaign_selection(self)` - Show dialog to select campaign frame.
- `_show_load_character_dialog(self)` - Show dialog to load a saved character.
- `_show_settings_dialog(self)` - Show settings dialog.
- `_start_character_creation(self)` - Start the character creation process.
- `_sync_narration_campaign(self)` - Inferred from name: sync narration campaign.
- `_toggle_theme(self)` - Toggle between light and dark themes.
- `_try_load_last_character(self)` - Try to load the most recent character, otherwise load test data.
- `_update_character_equipment_slots(self, equipped_items: dict)` - Update the current character's equipment slots in the database.
- `closeEvent(self, event: QCloseEvent)` - Ensure background workers are stopped when window closes.
- `factory(profile: CampaignVoiceProfile)` - Inferred from name: factory.
- `load_test_data(self)` - Load demo data into all widgets - only used when no saved characters exist
- `on_campaign_selected()` - Inferred from name: on campaign selected.

## core - `ui/settings_dialog.py`

- `__init__(self, parent: Optional[QWidget]=None)` - Inferred from name: init.
- `_on_settings_changed(self)` - Handle settings change.
- `_setup_ui(self)` - Initialize the narrative settings UI.
- `apply_settings(self)` - Apply current settings to config.
- `__init__(self, parent: Optional[QWidget]=None)` - Inferred from name: init.
- `_apply_settings(self)` - Apply all settings.
- `_apply_theme(self)` - Apply theme styling to dialog.
- `_ok_clicked(self)` - Handle OK button click.
- `_on_settings_changed(self)` - Handle settings changed signal.
- `_setup_ui(self)` - Initialize the settings dialog UI.

## core - `ui/subclass_features_widget.py`

- `__init__(self, feature: SubclassFeature, character_id: str, parent=None)` - Inferred from name: init.
- `_check_feature_availability(self)` - Check if the feature is currently available to use.
- `_get_action_display(self, action_cost: ActionCost)` - Get display text for action cost.
- `_get_action_style(self, action_cost: ActionCost)` - Get CSS style for action cost badge.
- `_get_type_display(self, feature_type: FeatureType)` - Get display text for feature type.
- `_get_type_style(self, feature_type: FeatureType)` - Get CSS style for feature type badge.
- `_get_unavailability_reason(self)` - Get the reason why the feature is unavailable.
- `_on_activation_clicked(self)` - Handle feature activation button click.
- `_setup_resource_tracking(self, layout: QVBoxLayout)` - Setup resource tracking display.
- `_setup_ui(self)` - Setup the feature widget UI.
- `_update_availability(self)` - Update the feature availability indicator.
- `_update_resource_display(self)` - Update the resource tracking display.
- `eventFilter(self, obj, event)` - Handle mouse events for tooltips.
- `__init__(self, parent=None)` - Inferred from name: init.
- `_setup_ui(self)` - Setup the main features widget UI.
- `refresh_features(self)` - Refresh the display of subclass features.
- `set_character(self, character_id: str, character_level: int)` - Set the character to display features for.
- `update_feature_availability(self)` - Update availability indicators for all features.

## core - `ui/themes.py`

- `build_stylesheet(palette: dict[str, str])` - Return a comprehensive PyQt6 stylesheet for the provided color palette.
- `get_theme_names()` - Return list of available theme names.
- `get_theme_palette(theme_name: str)` - Get color palette for the specified theme.

## core - `utilities/save_slot_cleanup.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `clean_orphaned_slots(self)` - Clean up orphaned save slots (marked as occupied but no character exists).
- `consolidate_slots(self, dry_run=True)` - Consolidate characters to use lower-numbered slots.
- `get_slot_statistics(self)` - Get statistics about current save slots.
- `print_statistics(self)` - Print current save slot statistics.
- `remove_empty_slots(self, keep_slots=10)` - Remove empty save slots above a certain number.
- `main()` - Main cleanup function.

## redundant - `scripts/character_tools/create_all_templates.py`

- `main()` - Inferred from name: main.

## redundant - `scripts/character_tools/template_validator.py`

- `__init__(self, db_path='talekeeper.db')` - Inferred from name: init.
- `_validate_ability_scores(self, template: dict)` - Validate ability scores.
- `_validate_background(self, template: dict)` - Validate background exists in database.
- `_validate_class(self, template: dict)` - Validate class exists in database.
- `_validate_class_specific_features(self, template: dict)` - Validate class-specific features.
- `_validate_equipment(self, template: dict)` - Validate equipment selections.
- `_validate_feats(self, template: dict)` - Validate feat selections.
- `_validate_fighting_style(self, template: dict)` - Validate fighting style selection.
- `_validate_required_fields(self, template: dict)` - Validate required template fields.
- `_validate_rogue_features(self, template: dict)` - Validate rogue-specific features.
- `_validate_skills(self, template: dict)` - Validate skill selections.
- `_validate_species(self, template: dict)` - Validate species exists in database.
- `_validate_spellcaster_features(self, template: dict)` - Validate spellcaster features.
- `_validate_warlock_features(self, template: dict)` - Validate warlock-specific features.
- `_validate_weapon_masteries(self, template: dict)` - Validate weapon mastery selections.
- `validate(self, template: dict)` - Validate a template dictionary.
- `validate_template_file(template_path: str, db_path='talekeeper.db')` - Validate a template file and print results.

## test - `add_legacy_test_categories.py`

- `add_category_to_legacy_test_files()` - Inferred from name: add category to legacy test files.

## test - `add_test_categories.py`

- `add_category_to_test_files()` - Inferred from name: add category to test files.

## test - `database/populate_test_characters.py`

- `__init__(self, db_path='talekeeper.db')` - Inferred from name: init.
- `add_features(self, char_id, char_data)` - Add character features and feats.
- `add_inventory(self, char_id, char_data)` - Add inventory items for the character.
- `add_proficiencies(self, char_id, char_data)` - Add character proficiencies (saving throws, skills, tools).
- `calculate_ac(self, char_data)` - Calculate AC for a character.
- `calculate_hp(self, char_data)` - Calculate HP for a character.
- `cleanup_existing(self)` - Remove any existing test characters.
- `close(self)` - Close database connection.
- `create_character(self, char_data)` - Create the character record.
- `create_save_slot(self, char_data)` - Create a save slot for the character.
- `get_feat_description(self, feat)` - Get description for feat.
- `get_fighting_style_description(self, style)` - Get description for fighting style.
- `populate_all(self)` - Populate all test characters.
- `main()` - Main entry point.

## test - `excess/test_character_loading.py`

- `test_character_loading()` - Test how characters are loaded from database.

## test - `excess/test_debug_halo.py`

- `test_database_resources()` - Test loading character resources from database.

## test - `excess/test_halo_click.py`

- `test_halo_click()` - Test if the halo can be clicked.

## test - `excess/test_halo_debug.py`

- `run_all_tests()` - Run all tests in sequence.
- `test_action_card_integration()` - Test ActionCard halo integration.
- `test_halo_widget()` - Test the AdvantageHalo widget.
- `test_imports()` - Test that all required modules can be imported.
- `test_mouse_events()` - Test mouse event handling on ActionCard.
- `test_resource_manager()` - Test the AdvantageResourceManager with test data.

## test - `excess/test_triangle_advantage.py`

- `test_triangle_advantage()` - Test if clicking triangle applies advantage to next attack.

## test - `scripts/database_tools/populate_test_characters.py`

- `__init__(self, db_path='talekeeper.db')` - Inferred from name: init.
- `add_features(self, char_id, char_data)` - Add character features and feats.
- `add_inventory(self, char_id, char_data)` - Add inventory items for the character.
- `add_proficiencies(self, char_id, char_data)` - Add character proficiencies (saving throws, skills, tools).
- `calculate_ac(self, char_data)` - Calculate AC for a character.
- `calculate_hp(self, char_data)` - Calculate HP for a character.
- `cleanup_existing(self)` - Remove any existing test characters.
- `close(self)` - Close database connection.
- `create_character(self, char_data)` - Create the character record.
- `create_save_slot(self, char_data)` - Create a save slot for the character.
- `get_feat_description(self, feat)` - Get description for feat.
- `get_fighting_style_description(self, style)` - Get description for fighting style.
- `populate_all(self)` - Populate all test characters.
- `main()` - Main entry point.

## test - `scripts/test_bag_of_holding.py`

- `test_bag_of_holding_system()` - Inferred from name: test bag of holding system.
- `test_treasure_generator()` - Inferred from name: test treasure generator.

## test - `scripts/test_downtime.py`

- `main()` - Inferred from name: main.
- `test_downtime_service()` - Inferred from name: test downtime service.
- `test_inspiration_on_load()` - Inferred from name: test inspiration on load.

## test - `scripts/utilities/test_narrative_log.py`

- `test_narrative_log()` - Inferred from name: test narrative log.

## test - `test/action_cards/test_action_panel_weapon_mastery.py`

- `mastery_db(tmp_path)` - Inferred from name: mastery db.
- `test_variant_weapon_hydrates_and_applies_mastery(qtbot, mastery_db)` - Inferred from name: test variant weapon hydrates and applies mastery.

## test - `test/core/test_features.py`

- `fighter_feature_db()` - Inferred from name: fighter feature db.
- `integration_db()` - Inferred from name: integration db.
- `qt_app()` - Inferred from name: qt app.
- `test_action_panel_uses_resource_service(qt_app, integration_db)` - Inferred from name: test action panel uses resource service.
- `test_feature_manager_loads_champion_features(fighter_feature_db)` - Inferred from name: test feature manager loads champion features.
- `test_feature_manager_loads_fighter_progression(fighter_feature_db)` - Inferred from name: test feature manager loads fighter progression.
- `test_initialize_character_features_seeds_resources(integration_db)` - Inferred from name: test initialize character features seeds resources.

## test - `test/features/test_champion_subclass.py`

- `combat_manager(self, fighter_db)` - Create CombatManager with test database.
- `fighter_db(self)` - Create Fighter test database.
- `test_champion_features_in_full_combat(self, combat_manager, fighter_db)` - Test Champion features work together in complete combat scenario.
- `test_remarkable_athlete_with_champion_combat(self, fighter_db)` - Test Remarkable Athlete enhances Champion's versatility.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `test_heroic_warrior_grants_inspiration(self, fighter_service)` - Test Heroic Warrior grants inspiration at start of turn.
- `test_heroic_warrior_level_requirement(self, fighter_service)` - Test Heroic Warrior requires Champion level 10.
- `test_heroic_warrior_no_duplicate_inspiration(self, fighter_service, fighter_db)` - Test Heroic Warrior doesn't grant inspiration if already at max.
- `fighter_db(self)` - Create Fighter test database.
- `test_improved_critical_19_20_range(self, weapon_service)` - Test Champion crits on 19-20 instead of just 20.
- `test_non_champion_normal_critical_range(self, weapon_service, fighter_db)` - Test non-Champions still crit only on 20.
- `test_superior_critical_18_19_20_range(self, weapon_service, fighter_db)` - Test Champion Superior Critical at level 15 (crits on 18-20).
- `weapon_service(self, fighter_db)` - Create WeaponAttackService with test database.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `test_remarkable_athlete_availability_level_3(self, fighter_service)` - Test Remarkable Athlete is available at Champion level 3.
- `test_remarkable_athlete_constitution_saves(self, fighter_service)` - Test Remarkable Athlete grants advantage on CON saving throws.
- `test_remarkable_athlete_dexterity_acrobatics(self, fighter_service)` - Test Remarkable Athlete grants advantage on DEX (Acrobatics) checks.
- `test_remarkable_athlete_initiative_rolls(self, fighter_service)` - Test Remarkable Athlete grants advantage on initiative.
- `test_remarkable_athlete_not_applied_to_other_skills(self, fighter_service)` - Test Remarkable Athlete doesn't apply to non-covered skills.
- `test_remarkable_athlete_strength_athletics(self, fighter_service)` - Test Remarkable Athlete grants advantage on STR (Athletics) checks.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `test_studied_attacks_advantage_after_miss(self, weapon_service, fighter_service, fighter_db)` - Test Studied Attacks grants advantage after missing same target.
- `test_studied_attacks_resets_on_hit(self, fighter_service)` - Test Studied Attacks advantage resets after hitting.
- `test_studied_attacks_target_specific(self, fighter_service)` - Test Studied Attacks advantage is specific to each target.
- `weapon_service(self, fighter_db)` - Create WeaponAttackService with test database.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `test_survivor_defy_death_at_zero_hp(self, fighter_service, fighter_db)` - Test Survivor prevents death at 0 HP.
- `test_survivor_healing_when_bloodied(self, fighter_service)` - Test Survivor heals when starting turn at half HP or less.
- `test_survivor_level_requirement(self, fighter_service)` - Test Survivor requires Champion level 18.
- `test_survivor_no_healing_when_healthy(self, fighter_service, fighter_db)` - Test Survivor doesn't heal when above half HP.

## test - `test/features/test_fighter_action_surge.py`

- `fighter_db(self)` - Create Fighter test database.
- `test_action_surge_level_scaling_persistence(self, fighter_db)` - Test Action Surge max uses scale correctly with level.
- `test_action_surge_resource_tracking_persistence(self, fighter_db)` - Test Action Surge usage is properly tracked in database.
- `test_multiple_characters_independent_action_surge(self, fighter_db)` - Test Action Surge tracking is independent per character.
- `combat_setup(self, fighter_db)` - Set up combat scenario for testing.
- `fighter_db(self)` - Create Fighter test database.
- `test_action_surge_allows_multiple_attacks(self, combat_setup, fighter_db)` - Test Action Surge allows multiple Attack actions in one turn.
- `test_action_surge_dash_and_attack_combination(self, combat_setup, fighter_db)` - Test Action Surge allows Dash and Attack in same turn.
- `test_action_surge_spell_and_attack_combination(self, combat_setup, fighter_db)` - Test Action Surge allows casting spell and attacking (for Eldritch Knight).
- `combat_manager(self, fighter_db)` - Create CombatManager with test database.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `game_engine(self, fighter_db)` - Create GameEngine with test database.
- `test_action_surge_availability_at_level_2(self, fighter_service)` - Test Action Surge becomes available at Fighter level 2.
- `test_action_surge_combat_state_tracking(self, fighter_service, fighter_db)` - Test Action Surge state is tracked in combat.
- `test_action_surge_grants_additional_action(self, fighter_service, combat_manager)` - Test Action Surge grants one additional action on the current turn.
- `test_action_surge_multiclass_availability(self, fighter_service, fighter_db)` - Test Action Surge uses Fighter levels for multiclass characters.
- `test_action_surge_multiple_uses_at_high_level(self, fighter_service, fighter_db)` - Test Action Surge gets multiple uses at higher levels.
- `test_action_surge_no_additional_bonus_action(self, fighter_service)` - Test Action Surge does not grant additional bonus actions.
- `test_action_surge_no_additional_movement(self, fighter_service)` - Test Action Surge does not grant additional movement.
- `test_action_surge_resource_consumption(self, fighter_service)` - Test Action Surge consumes one use per short rest.
- `test_action_surge_rest_recovery(self, game_engine, fighter_service, fighter_db)` - Test Action Surge recovers on short and long rests.
- `test_action_surge_turn_end_cleanup(self, fighter_service, combat_manager)` - Test Action Surge effects end at the end of the turn.
- `test_action_surge_unconscious_character(self, fighter_service, fighter_db)` - Test Action Surge cannot be used when unconscious.

## test - `test/features/test_fighter_combat_flow.py`

- `fighter_db(self)` - Create Fighter test database.
- `test_attack_roll_natural_1_always_misses(self, weapon_service)` - Test natural 1 always misses regardless of bonuses.
- `test_attack_roll_natural_20_always_hits(self, weapon_service)` - Test natural 20 always hits and crits regardless of AC.
- `test_attack_with_missing_weapon(self, weapon_service)` - Test attack calculation with weapon not in inventory.
- `test_attack_with_unequipped_weapon(self, weapon_service, fighter_db)` - Test attack with weapon in inventory but not equipped.
- `test_unconscious_character_cannot_attack(self, weapon_service, fighter_db)` - Test unconscious characters cannot make attacks.
- `weapon_service(self, fighter_db)` - Create WeaponAttackService with test database.
- `combat_manager(self, fighter_db)` - Create CombatManager with test database.
- `fighter_db(self)` - Create Fighter test database.
- `test_action_surge_doubles_attacks(self, combat_manager, weapon_service, fighter_db)` - Test Action Surge allows doubling attack actions.
- `test_critical_hit_damage_doubling(self, weapon_service)` - Test critical hits double damage dice correctly.
- `test_damage_resistance_interaction(self, weapon_service, fighter_db)` - Test Fighter damage vs resistant creatures.
- `test_fighting_style_and_mastery_combination(self, weapon_service)` - Test fighting style effects combine with weapon mastery.
- `test_full_attack_sequence_with_extra_attack(self, combat_manager, weapon_service)` - Test complete attack sequence with Extra Attack.
- `weapon_service(self, fighter_db)` - Create WeaponAttackService with test database.
- `fighter_db(self)` - Create Fighter test database.
- `test_archery_fighting_style_attack_bonus(self, weapon_service)` - Test Archery adds +2 to ranged weapon attack rolls.
- `test_archery_no_bonus_for_melee(self, weapon_service)` - Test Archery doesn't apply to melee attacks.
- `test_defense_fighting_style_ac_bonus(self, weapon_service, fighter_db)` - Test Defense fighting style adds +1 AC when wearing armor.
- `test_dueling_fighting_style_damage_bonus(self, weapon_service)` - Test Dueling adds +2 damage to one-handed weapon attacks.
- `test_dueling_no_bonus_with_shield_and_two_handed(self, weapon_service, fighter_db)` - Test Dueling doesn't apply with two-handed weapons.
- `test_great_weapon_fighting_no_effect_on_normal_rolls(self, weapon_service)` - Test Great Weapon Fighting doesn't affect rolls of 3 or higher.
- `test_great_weapon_fighting_treats_low_rolls_as_three(self, weapon_service)` - Test Great Weapon Fighting treats 1s and 2s as 3s per D&D 2024.
- `test_protection_fighting_style_reaction(self, weapon_service, fighter_db)` - Test Protection fighting style allows imposing disadvantage as reaction.
- `test_two_weapon_fighting_offhand_modifier(self, weapon_service, fighter_db)` - Test Two-Weapon Fighting adds ability modifier to off-hand damage.
- `weapon_service(self, fighter_db)` - Create WeaponAttackService with test database.

## test - `test/features/test_fighter_indomitable.py`

- `fighter_db(self)` - Create Fighter test database.
- `test_indomitable_with_advantage(self, fighter_db)` - Test Indomitable interaction with advantage on saves.
- `test_indomitable_with_disadvantage(self, fighter_db)` - Test Indomitable interaction with disadvantage on saves.
- `fighter_db(self)` - Create Fighter test database.
- `test_indomitable_resource_tracking_persistence(self, fighter_db)` - Test Indomitable usage is properly tracked in database.
- `test_indomitable_save_history_tracking(self, fighter_db)` - Test saving throw history is tracked for analysis.
- `test_multiple_characters_independent_indomitable(self, fighter_db)` - Test Indomitable tracking is independent per character.
- `advantage_system(self, fighter_db)` - Create AdvantageSystem with test database.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `game_engine(self, fighter_db)` - Create GameEngine with test database.
- `test_indomitable_ability_modifier_application(self, fighter_service)` - Test Indomitable properly applies ability modifiers to saves.
- `test_indomitable_availability_at_level_9(self, fighter_service)` - Test Indomitable becomes available at Fighter level 9.
- `test_indomitable_death_save_interaction(self, fighter_service, fighter_db)` - Test Indomitable can be used on death saving throws.
- `test_indomitable_legendary_resistance_interaction(self, fighter_service)` - Test Indomitable doesn't stack with legendary resistance.
- `test_indomitable_level_17_three_uses(self, fighter_service, fighter_db)` - Test Indomitable gets 3 uses at level 17.
- `test_indomitable_long_rest_recovery(self, game_engine, fighter_service, fighter_db)` - Test Indomitable recovers on long rest only.
- `test_indomitable_multiclass_availability(self, fighter_service, fighter_db)` - Test Indomitable uses Fighter levels for multiclass characters.
- `test_indomitable_multiple_uses_at_high_level(self, fighter_service, fighter_db)` - Test Indomitable gets multiple uses at higher levels.
- `test_indomitable_must_use_reroll(self, fighter_service)` - Test that Indomitable forces you to use the reroll result.
- `test_indomitable_no_proficiency_bonus_for_non_proficient(self, fighter_service)` - Test Indomitable doesn't apply proficiency for non-proficient saves.
- `test_indomitable_proficiency_bonus_application(self, fighter_service)` - Test Indomitable applies proficiency bonus for proficient saves.
- `test_indomitable_reroll_mechanic(self, fighter_service)` - Test Indomitable allows rerolling a failed saving throw.
- `test_indomitable_resource_consumption(self, fighter_service)` - Test Indomitable consumes one use per long rest.

## test - `test/features/test_fighter_second_wind.py`

- `fighter_db(self)` - Create Fighter test database.
- `test_multiple_characters_independent_tracking(self, fighter_db)` - Test Second Wind tracking is independent per character.
- `test_second_wind_resource_tracking_persistence(self, fighter_db)` - Test Second Wind usage is properly tracked in database.
- `test_second_wind_updates_character_hp(self, fighter_db)` - Test Second Wind properly updates character HP in database.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `game_engine(self, fighter_db)` - Create GameEngine with test database.
- `test_second_wind_healing_calculation(self, fighter_service, fighter_db)` - Test Second Wind healing: 1d10 + Fighter level.
- `test_second_wind_healing_cap_at_max_hp(self, fighter_service, fighter_db)` - Test Second Wind healing cannot exceed maximum HP.
- `test_second_wind_high_level_scaling(self, fighter_service, fighter_db)` - Test Second Wind scales with Fighter level.
- `test_second_wind_minimum_healing(self, fighter_service, fighter_db)` - Test Second Wind minimum healing (1 + level).
- `test_second_wind_multiclass_levels(self, fighter_service, fighter_db)` - Test Second Wind uses Fighter levels only for multiclass characters.
- `test_second_wind_resource_consumption(self, fighter_service, fighter_db)` - Test Second Wind consumes one use per short rest.
- `test_second_wind_rest_recovery(self, game_engine, fighter_db)` - Test Second Wind recovers on short and long rests.
- `test_second_wind_unconscious_character(self, fighter_service, fighter_db)` - Test Second Wind cannot be used when unconscious.
- `test_second_wind_wont_heal_at_max_hp(self, fighter_service)` - Test Second Wind cannot be used at maximum HP.

## test - `test/features/test_fighter_weapon_mastery.py`

- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `test_tactical_master_level_requirement(self, fighter_service)` - Test Tactical Master only available at level 9+.
- `test_tactical_master_only_specific_masteries(self, fighter_service)` - Test Tactical Master only allows substituting Push, Sap, and Slow.
- `test_tactical_master_push_substitution(self, fighter_service, fighter_db)` - Test level 9+ Fighters can substitute Push mastery.
- `test_tactical_master_sap_substitution(self, fighter_service, fighter_db)` - Test level 9+ Fighters can substitute Sap mastery.
- `test_tactical_master_slow_substitution(self, fighter_service, fighter_db)` - Test level 9+ Fighters can substitute Slow mastery.
- `test_tactical_master_ui_interaction(self, fighter_service, fighter_db)` - Test UI shows substitution options for Tactical Master.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `test_fighter_weapon_mastery_availability(self, weapon_service)` - Test Fighters get weapon mastery from level 1.
- `test_graze_mastery_effect(self, weapon_service)` - Test Graze mastery deals damage on miss.
- `test_non_mastery_class_no_effects(self, weapon_service, fighter_db)` - Test non-mastery classes don't get mastery effects.
- `test_sap_mastery_effect(self, weapon_service)` - Test Sap mastery effect reduces target's next attack roll.
- `test_slow_mastery_effect(self, weapon_service)` - Test Slow mastery reduces target movement.
- `test_topple_mastery_effect(self, weapon_service)` - Test Topple mastery can knock target prone.
- `test_vex_mastery_effect(self, weapon_service)` - Test Vex mastery grants advantage on next attack against same target.
- `weapon_service(self, fighter_db)` - Create WeaponAttackService with test database.
- `fighter_db(self)` - Create Fighter test database.
- `test_mastery_multiclass_interaction(self, fighter_db)` - Test weapon mastery for multiclass characters.
- `test_mastery_with_improvised_weapons(self, fighter_db)` - Test mastery behavior with improvised weapons.
- `test_mastery_with_magical_weapons(self, fighter_db)` - Test weapon mastery works with magical weapon variants.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `game_engine(self, fighter_db)` - Create GameEngine with test database.
- `test_mastery_persistence_across_rests(self, game_engine, fighter_service)` - Test Fighter retains all weapon masteries after rest.
- `test_mastery_reordering_during_long_rest(self, game_engine, fighter_service)` - Test Fighters can reorder weapon masteries during long rest.
- `test_mastery_reordering_preserves_substitutions(self, fighter_service)` - Test reordering preserves Tactical Master substitutions.
- `test_no_mastery_slot_tracking(self, fighter_service)` - Test Fighters don't have limited mastery slots (per documentation).
- `fighter_db(self)` - Create Fighter test database.
- `test_mastery_reordering_ui_feedback(self, fighter_db)` - Test UI provides feedback during mastery reordering.
- `test_mastery_substitution_ui_indication(self, fighter_db)` - Test UI indicates when masteries are substituted.
- `test_mastery_tooltip_display(self, fighter_db)` - Test weapon tooltips show correct mastery information.

## test - `test/features/test_paladin_action_integration.py`

- `__init__(self)` - Inferred from name: init.
- `print_summary(self)` - Print test results summary.
- `run_all_tests(self)` - Run all paladin action integration tests.
- `run_test(self, test_name: str, test_function)` - Run a single test and record results.
- `setup(self)` - Set up test environment.
- `test_action_type_mapping(self)` - Test that Lay on Hands action type is properly mapped.
- `test_apply_lay_on_hands_healing_method_exists(self)` - Test that _apply_lay_on_hands_healing method exists.
- `test_has_lay_on_hands_method_exists(self)` - Test that _has_lay_on_hands_uses method exists.
- `test_lay_on_hands_action_card_creation(self)` - Test that Lay on Hands action card can be created.
- `test_lay_on_hands_action_type_exists(self)` - Test that LAY_ON_HANDS action type is defined.
- `test_lay_on_hands_feature_check(self)` - Test checking for Lay on Hands feature.
- `test_lay_on_hands_import_in_action_panel(self)` - Test that LayOnHandsDialog is imported in action panel.
- `test_paladin_character_context_setup(self)` - Test setting up paladin character context.
- `test_use_lay_on_hands_method_exists(self)` - Test that _use_lay_on_hands method exists.
- `main()` - Run the paladin action integration test suite.

## test - `test/features/test_paladin_auras.py`

- `__init__(self)` - Inferred from name: init.
- `create_test_paladin(self, character_id: str, level: int, charisma: int, subclass: str='devotion')` - Create a test paladin character in the database.
- `print_summary(self)` - Print test results summary.
- `run_all_tests(self)` - Run all paladin aura tests.
- `run_test(self, test_name: str, test_function)` - Run a single test and record results.
- `setup(self)` - Set up test environment.
- `test_aura_expansion_level_18(self)` - Test aura expansion at level 18.
- `test_aura_manager_creation(self)` - Test that aura manager can be created.
- `test_aura_of_courage(self)` - Test Aura of Courage (level 10, fear immunity).
- `test_aura_of_devotion(self)` - Test Aura of Devotion (level 7 Devotion oath, charm immunity).
- `test_aura_of_protection(self)` - Test Aura of Protection (level 6, +Cha mod to saves).
- `test_aura_range_calculation(self)` - Test aura range calculation by level.
- `test_different_oath_auras(self)` - Test auras from different oaths.
- `test_low_charisma_protection(self)` - Test Aura of Protection with low Charisma (minimum +1 bonus).
- `test_multiple_auras(self)` - Test character with multiple auras (high level).
- `test_non_paladin_no_auras(self)` - Test that non-paladins don't get auras.
- `main()` - Run the paladin aura test suite.

## test - `test/features/test_paladin_channel_divinity.py`

- `__init__(self)` - Inferred from name: init.
- `print_summary(self)` - Print test results summary.
- `run_all_tests(self)` - Run all Channel Divinity tests.
- `run_test(self, test_name: str, test_function)` - Run a single test and record results.
- `setup(self)` - Set up test environment.
- `test_button_enable_disable(self)` - Test use button enable/disable logic.
- `test_channel_divinity_options_level_3_devotion(self)` - Test Channel Divinity options for level 3 Devotion paladin.
- `test_channel_divinity_options_level_9(self)` - Test Channel Divinity options for level 9 paladin.
- `test_dialog_creation(self)` - Test that Channel Divinity dialog can be created.
- `test_different_oaths(self)` - Test Channel Divinity options for different oaths.
- `test_option_data_structure(self)` - Test that option data has required fields.
- `test_option_selection(self)` - Test option selection functionality.
- `test_paladin_service_channel_divinity(self)` - Test Channel Divinity through paladin service.
- `test_uses_tracking(self)` - Test Channel Divinity uses tracking.
- `main()` - Run the Channel Divinity test suite.

## test - `test/features/test_paladin_channel_divinity_integration.py`

- `__init__(self)` - Inferred from name: init.
- `print_summary(self)` - Print test results summary.
- `run_all_tests(self)` - Run all Channel Divinity action integration tests.
- `run_test(self, test_name: str, test_function)` - Run a single test and record results.
- `setup(self)` - Set up test environment.
- `test_action_type_mapping_channel_divinity(self)` - Test that Channel Divinity action type is properly mapped.
- `test_channel_divinity_action_card_creation(self)` - Test that Channel Divinity action card can be created.
- `test_channel_divinity_action_type_exists(self)` - Test that CHANNEL_DIVINITY action type is defined.
- `test_channel_divinity_feature_check(self)` - Test checking for Channel Divinity feature.
- `test_channel_divinity_import_in_action_panel(self)` - Test that ChannelDivinityDialog is imported in action panel.
- `test_channel_divinity_methods_exist(self)` - Test that Channel Divinity methods exist in action panel.
- `test_channel_divinity_options_generation(self)` - Test Channel Divinity options generation.
- `test_different_oath_options(self)` - Test Channel Divinity options for different oaths.
- `test_paladin_character_context_with_channel_divinity(self)` - Test setting up paladin character context for Channel Divinity.
- `main()` - Run the Channel Divinity action integration test suite.

## test - `test/features/test_paladin_divine_smite.py`

- `action_panel(self, qapp, temp_db, paladin_character)` - Create ActionPanel with Paladin character.
- `capture_damage(monster_id, damage)` - Inferred from name: capture damage.
- `mock_exec(self)` - Inferred from name: mock exec.
- `mock_exec(self)` - Inferred from name: mock exec.
- `mock_exec(self)` - Inferred from name: mock exec.
- `mock_exec(self)` - Inferred from name: mock exec.
- `mock_exec(self)` - Inferred from name: mock exec.
- `paladin_character(self, temp_db)` - Create a test Paladin character with spell slots.
- `qapp(self)` - Create or get QApplication instance.
- `temp_db(self)` - Create temporary database with test data.
- `test_no_dialog_for_non_paladin(self, qapp, temp_db)` - Test that Divine Smite dialog doesn't appear for non-Paladin classes.
- `test_smite_damage_on_critical_hit(self, action_panel, temp_db)` - Test that Divine Smite damage is doubled on critical hits.
- `test_smite_dialog_appears_when_monster_survives(self, action_panel, temp_db)` - Test that Divine Smite dialog appears when monster would survive base damage.
- `test_smite_dialog_not_shown_when_monster_dies(self, action_panel, temp_db)` - Test that Divine Smite dialog doesn't appear when monster would die anyway.
- `test_spell_slot_consumption(self, action_panel, temp_db, paladin_character)` - Test that using Divine Smite properly consumes spell slots.

## test - `test/features/test_paladin_lay_on_hands.py`

- `__init__(self)` - Inferred from name: init.
- `print_summary(self)` - Print test results summary.
- `run_all_tests(self)` - Run all Lay on Hands tests.
- `run_test(self, test_name: str, test_function)` - Run a single test and record results.
- `setup(self)` - Set up test environment.
- `test_dialog_creation(self)` - Test that Lay on Hands dialog can be created.
- `test_healing_info_retrieval(self)` - Test getting healing information from dialog.
- `test_healing_point_limits(self)` - Test healing point usage limits.
- `test_healing_pool_calculation(self)` - Test healing pool calculations.
- `test_low_pool_limits(self)` - Test behavior with low healing pool.
- `test_paladin_service_lay_on_hands(self)` - Test Lay on Hands through paladin service.
- `test_poison_curing_option(self)` - Test poison curing functionality.
- `main()` - Run the Lay on Hands test suite.

## test - `test/fixtures/fighter_test_database.py`

- `__enter__(self)` - Context manager entry.
- `__exit__(self, exc_type, exc_val, exc_tb)` - Context manager exit with cleanup.
- `__init__(self, db_path=None)` - Initialize with optional database path.
- `_configure_fighting_styles(self)` - Assign fighting styles to test various combinations.
- `_create_fighter_characters(self)` - Create Fighter characters at various levels for comprehensive testing.
- `_setup_combat_state(self)` - Initialize combat state tables for testing.
- `_setup_fighter_equipment(self)` - Equip Fighter characters with appropriate weapons and armor.
- `cleanup(self)` - Clean up temporary database if needed.
- `get_character_ids(self)` - Get all Fighter character IDs for testing.
- `reset_resources(self, character_id)` - Reset all limited-use resources for testing.
- `setup_damaged_character(self, character_id, damage_amount)` - Damage a character for healing testing.
- `setup_database(self)` - Initialize database with full schema and Fighter test data.
- `create_fighter_test_db()` - Convenience function to create a Fighter test database.

## test - `test/helpers/ui_test_helpers.py`

- `find_attack_buttons(action_panel)` - Find all weapon attack buttons in the action panel.
- `find_class_feature_buttons(action_panel)` - Find Fighter class feature buttons.
- `find_resource_buttons(action_panel)` - Find buttons that consume limited resources.
- `get_damage_roll_from_log(action_panel, attack_number: int=-1)` - Extract damage information from the most recent log entry.
- `simulate_combat_target_selection(action_panel, target_data: dict)` - Mock target selection for combat testing.
- `verify_resource_count_display(action_panel, feature_name: str, expected_current: int, expected_max: int)` - Verify resource count display shows correct values.
- `create_mock_character_data(character_id: str, level: int=1, class_id: str='fighter')` - Create mock character data for testing.
- `create_mock_target(ac: int=12, hp: int=10, name: str='Test Target')` - Create a mock combat target.
- `click_button_safe(button: QPushButton, wait_ms: int=50)` - Safely click a button with error handling.
- `count_enabled_buttons(buttons: List[QPushButton])` - Count how many buttons in a list are enabled.
- `drag_and_drop(source: QWidget, target: QWidget, source_pos: QPoint=None, target_pos: QPoint=None)` - Perform drag and drop operation between widgets.
- `enter_text_safe(line_edit: QLineEdit, text: str, clear_first: bool=True)` - Safely enter text into a line edit widget.
- `find_button_by_text(parent: QWidget, text: str, partial_match: bool=True)` - Find a button by its text content.
- `find_buttons_containing_text(parent: QWidget, text_fragments: List[str])` - Find all buttons containing any of the specified text fragments.
- `find_widget_by_object_name(parent: QWidget, object_name: str)` - Find a widget by its objectName property.
- `get_action_buttons_from_layout(parent: QWidget)` - Extract all action buttons from a layout.
- `get_label_text(parent: QWidget, object_name: str)` - Get text from a label widget by object name.
- `select_combobox_item(combo: QComboBox, text: str)` - Select an item in a combobox by text.
- `simulate_key_sequence(widget: QWidget, key_sequence: str)` - Simulate a key sequence on a widget.
- `trigger_context_menu_action(widget: QWidget, action_text: str)` - Trigger a context menu action on a widget.
- `verify_button_state(button: QPushButton, expected_enabled: bool, expected_text: str=None)` - Verify button state matches expectations.
- `verify_tooltip_contains(widget: QWidget, expected_text: str)` - Verify widget tooltip contains expected text.
- `wait_for_condition(condition: Callable[[], bool], timeout_ms: int=5000, check_interval_ms: int=100)` - Wait for a condition to become true within a timeout.
- `wait_for_ui_update(ms: int=100)` - Wait for UI to update and process events.

## test - `test/run_fighter_tests.py`

- `main()` - Main test execution function.
- `run_pytest_with_output(test_files, markers=None)` - Run pytest on specific test files and return results.

## test - `test/services/test_concentration_system.py`

- `setUp(self)` - Set up test database with minimal data.
- `tearDown(self)` - Clean up test database.
- `test_concentration_replaces_previous(self)` - Test that new concentration replaces previous concentration.
- `test_concentration_save_high_damage(self)` - Test concentration save with high damage.
- `test_concentration_save_success(self)` - Test successful concentration saving throw.
- `test_duration_parsing(self)` - Test spell duration parsing to rounds.
- `test_end_concentration_voluntary(self)` - Test voluntarily ending concentration.
- `test_get_all_concentrating_characters(self)` - Test getting all characters currently concentrating.
- `test_start_concentration_non_concentration_spell(self)` - Test trying to start concentration on a non-concentration spell.
- `test_start_concentration_success(self)` - Test successfully starting concentration on a spell.
- `test_update_concentration_duration(self)` - Test updating concentration duration during combat.

## test - `test/services/test_condition_manager.py`

- `_create_test_schema(self)` - Create minimal schema for testing.
- `setUp(self)` - Create a test database and condition manager.
- `tearDown(self)` - Clean up test database.
- `test_add_simple_condition(self)` - Test adding a simple condition.
- `test_clear_all_conditions(self)` - Test clearing all conditions.
- `test_condition_caching(self)` - Test that condition caching works correctly.
- `test_condition_duration_tracking(self)` - Test duration countdown on turns.
- `test_condition_effects_lookup(self)` - Test looking up mechanical effects of conditions.
- `test_condition_immunity(self)` - Test condition immunity system.
- `test_condition_summary(self)` - Test readable condition summary.
- `test_condition_type_enum(self)` - Test that all D&D 2024 conditions are defined.
- `test_conditions_dont_stack(self)` - Test that conditions don't stack (except exhaustion).
- `test_exhaustion_death_at_level_6(self)` - Test exhaustion caps at level 6 (death).
- `test_exhaustion_stacking(self)` - Test that exhaustion levels stack.
- `test_incapacitating_conditions(self)` - Test detection of incapacitating conditions.
- `test_remove_condition_with_immunity(self)` - Test that gaining immunity removes existing condition.
- `test_save_ends_conditions(self)` - Test conditions that require saves.
- `test_unconscious_condition_effects(self)` - Test that unconscious has all correct nested conditions.
- `setUp(self)` - Set up for Danger Sense tests.
- `tearDown(self)` - Clean up.
- `test_danger_sense_blocked_by_incapacitated(self)` - Danger Sense should be blocked by incapacitated.
- `test_danger_sense_blocked_by_paralyzed(self)` - Danger Sense should be blocked by paralyzed (includes incapacitated).
- `test_danger_sense_not_blocked_by_frightened(self)` - Danger Sense should work when only frightened.
- `test_danger_sense_with_no_conditions(self)` - Danger Sense should work when not incapacitated.

## test - `test/services/test_condition_stat_service.py`

- `_create_test_schema(self)` - Create minimal schema for testing.
- `setUp(self)` - Create a test database and services.
- `tearDown(self)` - Clean up test database.
- `test_ability_check_modifiers(self)` - Test ability check modifiers from conditions.
- `test_action_economy_restrictions(self)` - Test action economy restrictions from conditions.
- `test_attack_roll_modifiers(self)` - Test attack roll modifiers from conditions.
- `test_comprehensive_stat_modifiers(self)` - Test the comprehensive stat modifier function.
- `test_damage_resistances_and_immunities(self)` - Test damage resistance and immunity from conditions.
- `test_exhaustion_penalties(self)` - Test exhaustion level penalties across all systems.
- `test_movement_speed_modification(self)` - Test movement speed modifications from conditions.
- `test_saving_throw_modifiers(self)` - Test saving throw modifiers from conditions.

## test - `test/services/test_fighter_champion.py`

- `_init_champion_schema(conn: sqlite3.Connection)` - Inferred from name: init champion schema.
- `temp_db_path(prefix: str)` - Inferred from name: temp db path.
- `test_combat_manager_applies_remarkable_athlete_to_initiative(monkeypatch)` - Inferred from name: test combat manager applies remarkable athlete to initiative.
- `test_heroic_warrior_awards_inspiration_and_sets_state()` - Inferred from name: test heroic warrior awards inspiration and sets state.
- `test_roll_skill_check_applies_remarkable_athlete(monkeypatch)` - Inferred from name: test roll skill check applies remarkable athlete.
- `test_survivor_heals_when_bloodied_and_tracks_defy_death()` - Inferred from name: test survivor heals when bloodied and tracks defy death.

## test - `test/services/test_monster_attack_parser.py`

- `setUp(self)` - Set up database connection.
- `test_parse_database_monsters(self)` - Test parsing attacks from actual database monsters.
- `setUp(self)` - Set up test environment.
- `test_air_elemental_whirlwind(self)` - Test parsing Air Elemental's whirlwind with prone effect.
- `test_ankheg_bite_grapple(self)` - Test parsing Ankheg's bite with automatic grapple.
- `test_attack_summary(self)` - Test attack summary generation.
- `test_automatic_vs_save_distinction(self)` - Test that parser distinguishes automatic effects from save-based effects.
- `test_basilisk_bite_simple(self)` - Test parsing Basilisk's simple bite (no special effects).
- `test_charge_attack_with_save(self)` - Test parsing charge attacks that require saves to avoid prone.
- `test_complex_save_patterns(self)` - Test parsing various save patterns from real monster data.
- `test_condition_mapping(self)` - Test that condition names are mapped correctly.
- `test_damage_extraction_patterns(self)` - Test various damage format patterns.
- `test_ghast_claws_paralysis(self)` - Test parsing Ghast's claws with paralysis save.
- `test_giant_spider_bite(self)` - Test parsing Giant Spider's bite attack with poison save.
- `test_giant_spider_web(self)` - Test parsing Giant Spider's web attack with restrained condition.
- `test_multiattack_parsing(self)` - Test that multiattack entries are not parsed as attacks.
- `test_non_attack_actions_ignored(self)` - Test that non-attack actions are ignored.
- `test_parsing_errors_handled(self)` - Test that parsing errors are handled gracefully.
- `test_size_based_grapple(self)` - Test parsing size-based automatic grapple effects.
- `test_trample_attack_automatic_prone(self)` - Test parsing trample attacks that automatically knock prone.

## test - `test/services/test_paladin_devotion.py`

- `_init_paladin_schema(conn: sqlite3.Connection)` - Inferred from name: init paladin schema.
- `temp_db_path(prefix: str)` - Inferred from name: temp db path.
- `test_channel_divinity()` - Test Channel Divinity usage.
- `test_devotion_oath_features()` - Test that Oath of Devotion features are properly applied.
- `test_divine_smite_calculation()` - Test Divine Smite damage calculation.
- `test_get_paladin_info()` - Test retrieving comprehensive paladin information.
- `test_half_caster_spell_progression()` - Test that paladins get appropriate spell slots as half-casters.
- `test_lay_on_hands()` - Test Lay on Hands healing feature.
- `test_lay_on_hands_empty_pool()` - Test Lay on Hands when pool is empty.
- `test_long_rest_recovery()` - Test long rest recovery for paladins.
- `test_paladin_initialization()` - Test basic paladin character initialization.

## test - `test/services/test_ritual_casting.py`

- `setUp(self)` - Set up test database with minimal data.
- `tearDown(self)` - Clean up test database.
- `test_cannot_ritual_cast_non_ritual_spell(self)` - Test that non-ritual spells cannot be cast as rituals.
- `test_cast_ritual_spell_failure(self)` - Test failed ritual spell casting.
- `test_cast_ritual_spell_success(self)` - Test successful ritual spell casting.
- `test_cleric_can_ritual_cast_detect_magic(self)` - Test that cleric can ritual cast Detect Magic.
- `test_fighter_cannot_ritual_cast(self)` - Test that fighter cannot ritual cast.
- `test_get_ritual_spells_for_cleric(self)` - Test getting available ritual spells for cleric.
- `test_get_ritual_spells_for_wizard(self)` - Test getting available ritual spells for wizard.
- `test_ritual_casting_time_calculation(self)` - Test ritual casting time calculation.
- `test_wizard_can_ritual_cast_from_spellbook(self)` - Test that wizard can ritual cast spells from spellbook.

## test - `test/services/test_rogue_abilities.py`

- `_create_test_database(self)` - Create minimal test database structure.
- `_create_test_rogue(self, level: int=1, character_id: str='test_rogue')` - Create a test rogue character.
- `setUp(self)` - Set up test database and service.
- `tearDown(self)` - Clean up test database.
- `test_calculate_sneak_attack_damage(self)` - Test Sneak Attack damage string calculation.
- `test_cunning_action(self)` - Test Cunning Action usage.
- `test_get_rogue_features(self)` - Test getting rogue features.
- `test_get_rogue_level(self)` - Test getting rogue level for characters.
- `test_reliable_talent(self)` - Test Reliable Talent application.
- `test_rest_rogue_resources(self)` - Test resource restoration on rest.
- `test_sneak_attack_dice_scaling(self)` - Test Sneak Attack dice scaling by level.
- `test_sneak_attack_eligibility(self)` - Test Sneak Attack eligibility checks.
- `test_steady_aim(self)` - Test Steady Aim usage.
- `test_stroke_of_luck(self)` - Test Stroke of Luck usage.
- `test_uncanny_dodge(self)` - Test Uncanny Dodge usage.
- `test_update_rogue_resources_for_level(self)` - Test resource updates for different levels.
- `test_weapon_eligibility_for_sneak_attack(self)` - Test weapon eligibility for Sneak Attack.

## test - `test/services/test_warlock_fiend.py`

- `create_test_warlock(self, level=1, patron='Fiend')` - Helper to create a test warlock character.
- `setup_class(cls)` - Set up test database once for all tests.
- `setup_method(self)` - Clear character data before each test.
- `teardown_class(cls)` - Clean up test database.
- `test_can_cast_spell_with_pact_slot(self)` - Test checking if spell can be cast with pact slot.
- `test_dark_ones_own_luck(self)` - Test Dark One's Own Luck usage.
- `test_eldritch_invocations(self)` - Test learning and applying eldritch invocations.
- `test_eldritch_master(self)` - Test Eldritch Master feature at level 20.
- `test_fiend_level_progression(self)` - Test Fiend patron features at different levels.
- `test_fiend_patron_features(self)` - Test Fiend patron specific features.
- `test_fiendish_resilience(self)` - Test Fiendish Resilience damage type selection.
- `test_hurl_through_hell(self)` - Test Hurl Through Hell ability.
- `test_invocation_prerequisites(self)` - Test that invocations with prerequisites are properly filtered.
- `test_mystic_arcanum(self)` - Test Mystic Arcanum feature at high levels.
- `test_pact_boon_selection(self)` - Test selecting pact boons at level 3.
- `test_pact_magic_slots(self)` - Test pact magic slot progression.
- `test_pact_slot_usage_and_recovery(self)` - Test using and recovering pact slots.
- `test_spell_casting_integration(self)` - Test that Warlock integrates with spellcasting system.
- `test_warlock_initialization(self)` - Test basic Warlock initialization.

## test - `test/services/test_weapon_attack_service.py`

- `_create_test_schema(self)` - Create minimal database schema for testing.
- `_insert_test_data(self)` - Insert test character data.
- `setUp(self)` - Set up test database and service.
- `tearDown(self)` - Clean up test database.
- `test_archery_attack_bonus(self)` - Test Archery fighting style attack bonus.
- `test_dueling_damage_bonus(self)` - Test Dueling fighting style damage bonus.
- `test_get_character_fighting_styles(self)` - Test retrieving character fighting styles.
- `test_great_weapon_fighting(self)` - Test Great Weapon Fighting style effects.
- `test_mastery_class_requires_mastery_property(self)` - Test that mastery classes require weapons to have mastery property.
- `test_non_mastery_class_no_errors(self)` - Test that non-mastery classes don't cause errors when weapons lack mastery.
- `test_parse_damage_dice(self)` - Test damage dice parsing.
- `test_parse_damage_dice_invalid_formats(self)` - Test that invalid damage dice formats raise ValueError.
- `test_savage_attacker_feat(self, mock_random)` - Test Savage Attacker feat application.
- `test_savage_attacker_first_roll_better(self, mock_random)` - Test Savage Attacker when first roll is better.
- `test_savage_attacker_not_first_attack(self)` - Test Savage Attacker doesn't apply if not first attack.
- `test_weapon_mastery_effects_cleave(self)` - Test Cleave weapon mastery effect.
- `test_weapon_mastery_effects_graze(self)` - Test Graze weapon mastery effect.
- `test_weapon_mastery_effects_topple(self)` - Test Topple weapon mastery save DC calculation.
- `test_weapon_mastery_unlimited_access(self)` - Test characters with unlimited weapon mastery access.

## test - `test/services/test_wizard_evocation.py`

- `_init_wizard_schema(conn: sqlite3.Connection)` - Inferred from name: init wizard schema.
- `temp_db_path(prefix: str)` - Inferred from name: temp db path.
- `test_add_spell_to_spellbook()` - Test adding spells to wizard spellbook.
- `test_arcane_recovery_already_used()` - Test Arcane Recovery when already used.
- `test_arcane_recovery_basic()` - Test basic Arcane Recovery functionality.
- `test_arcane_recovery_higher_level()` - Test Arcane Recovery at higher levels with mixed slot usage.
- `test_evocation_subclass_features()` - Test that Evocation school features are properly applied.
- `test_get_wizard_info()` - Test retrieving comprehensive wizard information.
- `test_long_rest_recovery()` - Test long rest recovery for wizards.
- `test_wizard_initialization()` - Test basic wizard character initialization.
- `test_wizard_spell_preparation_limit()` - Test that wizard spell preparation respects Intelligence modifier + level.

## test - `test/test_action_economy_enforcement.py`

- `test_action_economy_logic()` - Test the logic for action economy enforcement.
- `test_action_mapping()` - Test that actions are properly mapped to economy types.

## test - `test/test_action_registry.py`

- `_create_test_character(self, character_id='test_char', class_name='barbarian', level=1, subclass='berserker')` - Create a test character
- `_setup_test_database(self)` - Setup minimal database schema for testing
- `setup_method(self)` - Setup test database and registry
- `teardown_method(self)` - Cleanup test database
- `test_action_definition_completeness(self)` - Test that action definitions have required fields
- `test_action_registration(self)` - Test registering and retrieving actions
- `test_barbarian_actions_registered(self)` - Test that all barbarian actions are registered
- `test_character_actions(self)` - Test getting actions for a specific character
- `test_class_actions_by_level(self)` - Test getting class actions filtered by level
- `test_combat_state_prerequisites(self)` - Test combat state prerequisite checking
- `test_economy_type_mapping(self)` - Test that actions have correct economy types
- `test_prerequisite_validation(self)` - Test prerequisite validation system
- `test_resource_checking(self)` - Test resource availability checking
- `test_subclass_actions(self)` - Test getting subclass-specific actions
- `test_trigger_types(self)` - Test that automatic triggers are properly set
- `test_action_registry()` - Test registry in isolation as specified in roadmap

## test - `test/test_action_tracking.py`

- `setup_method(self)` - Setup test action economy
- `test_action_logging(self)` - Test that actions are properly logged
- `test_class_action_tracking(self)` - Test tracking of class-specific actions
- `test_duration_management(self)` - Test effect duration tracking and expiration
- `test_existing_economy_still_works(self)` - Test that existing action economy functionality is preserved
- `test_parallel_tracking(self)` - Test that class action tracking works alongside basic action economy
- `test_resource_consumption_tracking(self)` - Test resource consumption tracking across multiple actions
- `test_action_tracking()` - Main test function as specified in roadmap

## test - `test/test_action_validation.py`

- `_create_test_character(self, character_id='test_char', class_name='barbarian', level=1, subclass='berserker', rage_uses=2)` - Create a test character
- `_setup_test_database(self)` - Setup minimal database schema for testing
- `setup_method(self)` - Setup test database and validator
- `teardown_method(self)` - Cleanup test database
- `test_action_availability_calculator(self)` - Test getting availability for all character actions
- `test_action_economy_blocking(self)` - Test validation respects action economy
- `test_detailed_feedback_system(self)` - Test the feedback system provides user-friendly messages
- `test_level_prerequisite_failure(self)` - Test validation fails appropriately for level requirements
- `test_resource_shortage_detection(self)` - Test validation detects resource shortages
- `test_user_friendly_messages(self)` - Test that error messages are user-friendly
- `test_valid_action_validation(self)` - Test validation of valid actions
- `test_warning_logs_without_blocking(self)` - Test that warnings are logged but actions aren't blocked
- `test_action_validation()` - Main test function as specified in roadmap

## test - `test/test_alt_encounters.py`

- `controlled_choice(options)` - Inferred from name: controlled choice.
- `test_generate_skill_challenge_resource_swap_text()` - Inferred from name: test generate skill challenge resource swap text.
- `test_generate_skill_challenge_structure()` - Inferred from name: test generate skill challenge structure.

## test - `test/test_barbarian_level_progression.py`

- `_calculate_brutal_critical_dice(level)` - Calculate brutal critical extra dice by level
- `_calculate_rage_uses(level)` - Calculate rage uses per long rest by level
- `_create_barbarian_character(db_path, character_id, level)` - Create a Barbarian character at the specified level
- `_setup_test_database(db_path)` - Setup minimal database schema for testing
- `_test_level_features(db_path, character_id, level)` - Test features available at specific level
- `test_barbarian_level_progression()` - Test Barbarian progression from level 1 to 20

## test - `test/test_bis_loot_system.py`

- `clean_test_character(character_id)` - Inferred from name: clean test character.
- `create_test_character(class_name, strength=15, dexterity=10, constitution=14)` - Inferred from name: create test character.
- `test_bis_drops()` - Inferred from name: test bis drops.

## test - `test/test_campaign_frame_simple.py`

- `test_campaign_frame()` - Inferred from name: test campaign frame.

## test - `test/test_character_creation.py`

- `__init__(self)` - Inferred from name: init.
- `run(self)` - Run the test application
- `__init__(self)` - Inferred from name: init.
- `_setup_ui(self)` - Setup test interface
- `clear_results(self)` - Clear test results
- `log_test(self, test_name: str, success: bool, message: str='', error: Exception=None)` - Log test result
- `test_character_creation_mode(self)` - Test 3: Specifically test character creation mode activation
- `test_encounter_panel(self)` - Test 2: Create encounter panel with dummy data
- `test_full_creation_flow(self)` - Test 4: Full character creation flow
- `test_imports(self)` - Test 1: Basic imports

## test - `test/test_character_creation_automated.py`

- `log_test(test_name: str, success: bool, message: str='', error: Exception=None)` - Log test result
- `run_automated_tests()` - Run all character creation tests automatically

## test - `test/test_character_creation_fixed.py`

- `test_character_creation_fix()` - Inferred from name: test character creation fix.

## test - `test/test_class_filtering.py`

- `test_class_filtering()` - Inferred from name: test class filtering.

## test - `test/test_class_filtering_final.py`

- `test_class_filtering_final()` - Inferred from name: test class filtering final.

## test - `test/test_cleric_life.py`

- `setUp(self)` - Set up test database with full schema.
- `tearDown(self)` - Clean up test database.
- `test_blessed_healer_bonus(self)` - Test Blessed Healer self-healing.
- `test_channel_divinity_initialization(self)` - Test Channel Divinity options are set up correctly.
- `test_channel_divinity_usage(self)` - Test using Channel Divinity abilities.
- `test_cleric_info_retrieval(self)` - Test getting complete cleric information.
- `test_cleric_initialization(self)` - Test basic cleric initialization.
- `test_disciple_of_life_bonus(self)` - Test Disciple of Life healing bonus calculation.
- `test_life_domain_spells(self)` - Test Life Domain spells are added correctly.
- `test_resource_restoration(self)` - Test cleric resource restoration on rest.
- `test_spell_slot_progression(self)` - Test cleric spell slot progression.
- `test_subclass_registry_integration(self)` - Test Life Domain is properly registered in subclass system.

## test - `test/test_condition_integration.py`

- `check_danger_sense_enhanced(character_id)` - Enhanced Danger Sense that checks for incapacitating conditions.
- `test_condition_system_standalone()` - Test that condition system works independently.
- `test_danger_sense_integration_prep()` - Test that we're ready for Danger Sense integration.

## test - `test/test_cunning_strike_end_to_end.py`

- `_create_goblin(self, goblin_id: str='goblin1')` - Create test goblin target
- `_create_rogue(self, level: int=5, rogue_id: str='rogue1', dex: int=18)` - Create test rogue
- `_setup_test_database(self)` - Setup complete database schema
- `_store_cunning_strike_selection(self, character_id: str, effects: list)` - Store Cunning Strike selection
- `setup_method(self)` - Setup test database with full schema
- `teardown_method(self)` - Cleanup
- `test_knock_out_strike_high_cost(self)` - Test Knock Out Strike with 6d6 cost
- `test_multiple_effects_level_11(self)` - Test using 2 Cunning Strike effects at level 11+
- `test_poison_strike_requires_kit(self)` - Test Poison Strike requires Poisoner's Kit
- `test_trip_strike_combat_flow(self)` - Test Trip Strike: Select -> Attack -> Save -> Apply Prone
- `main()` - Run all end-to-end tests

## test - `test/test_cunning_strike_integration.py`

- `_create_test_rogue(self, level: int=5, character_id: str='test_rogue', dexterity: int=18)` - Create a test rogue character
- `_setup_test_database(self)` - Setup minimal database schema
- `setup_method(self)` - Setup test database
- `teardown_method(self)` - Cleanup test database
- `test_apply_cunning_strike(self)` - Test applying Cunning Strike effects
- `test_available_options_level_14(self)` - Test available Cunning Strike options at level 14
- `test_available_options_level_5(self)` - Test available Cunning Strike options at level 5
- `test_can_use_multiple_effects_level_10(self)` - Test that level 10 rogue cannot use multiple effects
- `test_can_use_multiple_effects_level_11(self)` - Test that level 11+ rogue CAN use multiple effects
- `test_damage_calculation_high_cost(self)` - Test damage calculation with high-cost Devious Strike
- `test_damage_calculation_multiple_effects(self)` - Test damage calculation with multiple Cunning Strike effects
- `test_damage_calculation_single_effect(self)` - Test damage calculation with single Cunning Strike effect
- `test_poisoners_kit_requirement(self)` - Test Poison Strike requires Poisoner's Kit
- `test_preview_generation(self)` - Test Cunning Strike preview generation
- `test_save_dc_calculation(self)` - Test Cunning Strike save DC calculation (8 + DEX + prof)
- `test_sneak_attack_eligibility_non_finesse_weapon(self)` - Test Sneak Attack not eligible with non-finesse weapon
- `test_sneak_attack_eligibility_with_advantage(self)` - Test Sneak Attack eligibility with advantage
- `test_sneak_attack_eligibility_with_disadvantage(self)` - Test Sneak Attack NOT eligible with disadvantage
- `test_validation_allows_multiple_effects_level_11(self)` - Test validation allows multiple effects for level 11 rogue
- `test_validation_too_many_effects_level_5(self)` - Test validation rejects multiple effects for level 5 rogue
- `main()` - Run all integration tests

## test - `test/test_danger_sense_integration.py`

- `test_backwards_compatibility()` - Test that existing code still works unchanged.
- `test_danger_sense_integration()` - Test that enhanced Danger Sense works with condition system.

## test - `test/test_divine_smite_simple.py`

- `main()` - Run all simple tests.
- `test_critical_hit_indication()` - Test that critical hits are properly indicated in dialog.
- `test_hp_threshold_logic()` - Test the logic for when to show the smite dialog.
- `test_smite_damage_calculation()` - Test that smite damage is calculated correctly.

## test - `test/test_dynamic_feature_system.py`

- `_setup_test_database(self)` - Setup test database with minimal schema and data
- `setUp(self)` - Inferred from name: setUp.
- `tearDown(self)` - Inferred from name: tearDown.
- `test_feature_progression_summary(self)` - Test getting feature progression summary
- `test_get_character_features(self)` - Test retrieving character features
- `test_grant_class_features_level_1(self)` - Test granting level 1 rogue features
- `test_grant_class_features_level_2(self)` - Test granting level 2 rogue features
- `test_grant_subclass_features(self)` - Test granting thief subclass features at level 3
- `test_level_up_integration(self)` - Test complete level up process
- `test_level_up_preview(self)` - Test level up preview functionality
- `test_subclass_selection_detection(self)` - Test detecting subclass selection level

## test - `test/test_dynamic_system_validation.py`

- `test_dynamic_feature_system()` - Test the dynamic feature system with existing database

## test - `test/test_encounter_avoidance.py`

- `__init__(self)` - Inferred from name: init.
- `run_all_tests(self)` - Inferred from name: run all tests.
- `setup_test_character(self)` - Get a test character from the database.
- `test_avoidance_attempt_simulation(self)` - Inferred from name: test avoidance attempt simulation.
- `test_avoidance_eligibility(self)` - Inferred from name: test avoidance eligibility.
- `test_encounter_difficulty(self)` - Inferred from name: test encounter difficulty.
- `test_multiple_avoidance_attempts(self)` - Inferred from name: test multiple avoidance attempts.
- `test_stealth_vs_perception(self)` - Inferred from name: test stealth vs perception.
- `test_xp_calculation(self)` - Inferred from name: test xp calculation.

## test - `test/test_encounter_panel_debug.py`

- `test_encounter_panel_debug()` - Inferred from name: test encounter panel debug.

## test - `test/test_fighter_comprehensive.py`

- `__init__(self)` - Inferred from name: init.
- `_generate_recommendations(self)` - Generate recommendations based on test results.
- `_print_summary(self)` - Print validation summary.
- `_run_test_class(self, test_class, db_path)` - Run all tests in a test class and return results.
- `_validate_action_surge(self)` - Validate Action Surge mechanics.
- `_validate_champion_features(self)` - Validate Champion subclass features.
- `_validate_fighting_styles(self)` - Validate all Fighting Style effects.
- `_validate_indomitable(self)` - Validate Indomitable mechanics.
- `_validate_performance(self)` - Validate performance characteristics.
- `_validate_second_wind(self)` - Validate Second Wind mechanics.
- `_validate_ui_integration(self)` - Validate UI integration for Fighter features.
- `_validate_weapon_mastery(self)` - Validate weapon mastery mechanics.
- `save_report(self, filename: str='fighter_validation_report.json')` - Save detailed report to file.
- `validate_all_features(self)` - Run comprehensive validation of all Fighter features.
- `main()` - Main test runner function.
- `run_manual_feature_tests()` - Run specific manual tests for features that are hard to automate.

## test - `test/test_fighter_validation_demo.py`

- `demonstrate_testing_capabilities()` - Demonstrate the comprehensive testing capabilities.
- `show_usage_examples()` - Show examples of how to use the testing framework.
- `test_framework_setup()` - Test that the testing framework is properly set up.

## test - `test/test_full_action_economy.py`

- `_create_test_character(self, character_id='test_char', class_name='barbarian', level=20, subclass='berserker')` - Create a test character
- `_setup_test_database(self)` - Setup minimal database schema for testing
- `setup_method(self)` - Setup test database and enforcer
- `teardown_method(self)` - Cleanup test database
- `test_action_blocking_for_invalid_attempts(self)` - Test that invalid actions are blocked
- `test_available_actions_list(self)` - Test getting list of available actions
- `test_can_execute_action_check(self)` - Test non-destructive action checking
- `test_cannot_use_two_bonus_actions(self)` - Verify can't use two bonus actions
- `test_full_combat_with_all_rules_enforced(self)` - Full combat with all rules enforced
- `test_rage_consumes_bonus_action(self)` - Test Rage consumes bonus action
- `test_reaction_usage_and_reset(self)` - Check reaction usage and reset
- `test_resource_consumption(self)` - Validate resource consumption
- `test_full_action_economy()` - Main test function as specified in roadmap

## test - `test/test_galahad_smite.py`

- `test_galahad_smite()` - Inferred from name: test galahad smite.

## test - `test/test_level_1_paladin_fix.py`

- `main()` - Run all level 1 paladin tests.
- `test_divine_smite_availability()` - Test that level 1 paladins can potentially use Divine Smite (have spell slots).
- `test_level_1_paladin_spell_selection()` - Test that level 1 paladins can select 2 prepared spells during creation.
- `test_level_1_paladin_spell_slots()` - Test that level 1 paladins get 2 first-level spell slots (D&D 2024).

## test - `test/test_lucky_halo.py`

- `__init__(self)` - Inferred from name: init.
- `load_test_character_with_resources(self)` - Load a character with Lucky and Inspiration resources.
- `run_all_tests(self)` - Run all tests and report results.
- `setup(self)` - Setup the test environment.
- `test_halo_appearance(self)` - Test that halos appear when hovering over action cards.
- `test_halo_click(self)` - Test clicking the halo to use resources.
- `test_resource_priority(self)` - Test that Inspiration shows before Lucky.
- `main()` - Main test entry point.

## test - `test/test_monster_distribution.py`

- `setUp(self)` - Set up test fixtures
- `test_alignment_filtering(self)` - Test monster alignment filtering based on campaign frame rules
- `test_campaign_frame_serialization(self)` - Test that campaign frames can be serialized to/from JSON
- `test_cr_filtering(self)` - Test that monsters are filtered correctly by CR relative to party level
- `test_difficulty_distribution(self)` - Test that encounters are generated according to difficulty distribution
- `test_edge_cases(self)` - Test edge cases and error conditions
- `test_encounter_xp_accuracy(self)` - Test that encounter XP calculations are accurate
- `test_high_difficulty_encounter_structure(self)` - Test that high difficulty encounters follow single strong monster pattern
- `test_low_moderate_encounter_structure(self)` - Test that low/moderate encounters can have multiple monsters
- `test_monster_database_loading(self)` - Test that monsters are loaded correctly from database
- `test_monster_hp_calculation(self)` - Test monster HP rolling and average HP usage
- `test_monster_type_distribution(self)` - Test that monster types follow campaign frame weights over many encounters
- `test_random_bag_system(self)` - Test that RandomBag ensures variety in monster selection
- `test_xp_budget_calculation(self)` - Test XP budget calculations for different levels and difficulties
- `setUp(self)` - Set up integration test fixtures
- `test_full_campaign_simulation(self)` - Simulate a full campaign to test monster distribution over time
- `run_monster_distribution_tests()` - Run all monster distribution tests

## test - `test/test_paladin_comprehensive.py`

- `__init__(self)` - Inferred from name: init.
- `cleanup(self)` - Clean up test environment.
- `create_test_character(self, level=1)` - Create a test paladin character.
- `print_summary(self)` - Print test results summary.
- `run_all_tests(self)` - Run all paladin tests.
- `run_test(self, test_name, test_function)` - Run a single test and record results.
- `setup(self)` - Set up test environment with temporary database.
- `test_channel_divinity_uses(self)` - Test Channel Divinity use calculation.
- `test_database_tables_exist(self)` - Test that required database tables exist.
- `test_divine_smite_calculation(self)` - Test Divine Smite damage calculation.
- `test_divine_smite_vs_undead(self)` - Test Divine Smite bonus damage vs undead/fiends.
- `test_lay_on_hands_calculation(self)` - Test Lay on Hands pool calculation.
- `test_oath_spells_added(self)` - Test that oath spells are properly added.
- `test_paladin_character_creation(self)` - Test creating a paladin character.
- `test_paladin_class_exists(self)` - Test if paladin class is defined in database.
- `test_paladin_info_retrieval(self)` - Test getting comprehensive paladin information.
- `test_paladin_initialization(self)` - Test paladin character initialization.
- `test_paladin_service_creation(self)` - Test paladin service can be created.
- `test_paladin_spell_preparation(self)` - Test paladin spell preparation calculation.
- `main()` - Run the paladin test suite.

## test - `test/test_paladin_comprehensive_regression.py`

- `__init__(self)` - Inferred from name: init.
- `create_test_paladin_full(self, character_id: str, level: int, subclass: str='devotion')` - Create a complete test paladin with all required fields.
- `print_comprehensive_summary(self)` - Print comprehensive test results with feature coverage.
- `run_all_tests(self)` - Run the complete paladin regression test suite.
- `run_test(self, test_name: str, test_function, feature_category: str=None)` - Run a single test and record results.
- `setup(self)` - Set up comprehensive test environment.
- `test_action_panel_integration(self)` - Test action panel integration for paladin abilities.
- `test_cross_feature_interactions(self)` - Test interactions between different paladin features.
- `test_divine_smite_scaling(self)` - Test Divine Smite damage scaling.
- `test_level_10_aura_of_courage(self)` - Test level 10 Aura of Courage.
- `test_level_18_aura_expansion(self)` - Test level 18 aura range expansion.
- `test_level_1_basic_features(self)` - Test level 1 paladin features (Lay on Hands, Spellcasting, Weapon Mastery).
- `test_level_3_oath_features(self)` - Test level 3 paladin features (Channel Divinity, Sacred Oath).
- `test_level_6_aura_of_protection(self)` - Test level 6 Aura of Protection.
- `test_oath_variations(self)` - Test different sacred oath implementations.
- `test_resource_management(self)` - Test resource management (Lay on Hands pool, Channel Divinity uses).
- `test_ui_components(self)` - Test all UI components can be created.
- `main()` - Run the comprehensive paladin regression test suite.

## test - `test/test_paladin_simple.py`

- `run_all_tests()` - Run all simple paladin tests.
- `test_action_cards_exist()` - Test if paladin action card files exist.
- `test_devotion_subclass()` - Test if Devotion subclass exists.
- `test_divine_smite_calculation()` - Test Divine Smite damage calculation without database.
- `test_divine_smite_dialog()` - Test if Divine Smite dialog can be imported.
- `test_divine_smite_vs_undead()` - Test Divine Smite bonus damage vs undead/fiends.
- `test_paladin_class_exists()` - Test if paladin class is defined in database.
- `test_paladin_service_import()` - Test paladin service can be imported.
- `test_paladin_tables_needed()` - Test what paladin-specific tables exist.

## test - `test/test_paladin_subclasses.py`

- `test_subclass_features()` - Inferred from name: test subclass features.

## test - `test/test_parlay_system.py`

- `__init__(self)` - Inferred from name: init.
- `run_all_tests(self)` - Inferred from name: run all tests.
- `setup_test_character(self)` - Get a test character from the database.
- `test_encounter_parlay_check(self)` - Inferred from name: test encounter parlay check.
- `test_evil_monster_parlay(self)` - Inferred from name: test evil monster parlay.
- `test_good_monster_parlay(self)` - Inferred from name: test good monster parlay.
- `test_neutral_monster_parlay(self)` - Inferred from name: test neutral monster parlay.
- `test_parlay_skills(self)` - Inferred from name: test parlay skills.
- `test_xp_calculation(self)` - Inferred from name: test xp calculation.

## test - `test/test_rage_resistance.py`

- `_map_action_to_economy_type(self, action_type: ActionType)` - Copy of the mapping method for testing.
- `test_action_economy_integration()` - Test that rage action economy integration works.
- `test_rage_resistance_calculations()` - Test the mathematics of rage damage resistance.

## test - `test/test_rage_state_tracking.py`

- `test_damage_type_mapping()` - Test damage type recognition.
- `test_rage_state_conditions()` - Test the conditions for applying rage resistance.

## test - `test/test_rest_system.py`

- `__init__(self)` - Inferred from name: init.
- `cleanup_test_character(self)` - Inferred from name: cleanup test character.
- `run_all_tests(self)` - Inferred from name: run all tests.
- `setup_test_character(self)` - Inferred from name: setup test character.
- `test_no_rations_scenario(self)` - Inferred from name: test no rations scenario.
- `test_ration_check(self)` - Inferred from name: test ration check.
- `test_ration_consumption(self)` - Inferred from name: test ration consumption.

## test - `test/test_results_summary.py`

- `run_tests_and_summarize()` - Run tests and provide summary.

## test - `test/test_rogue_expertise_progression.py`

- `_create_rogue(self, level: int)` - Create a rogue character at specified level
- `_setup_test_database(self)` - Setup minimal database schema
- `setup_method(self)` - Setup test database
- `teardown_method(self)` - Cleanup test database
- `test_expertise_bonus_calculation(self)` - Test expertise doubles proficiency bonus
- `test_expertise_feature_granted_level_1(self)` - Test Expertise feature is granted at level 1
- `test_expertise_feature_upgraded_level_6(self)` - Test Expertise feature is upgraded at level 6
- `test_expertise_skills_increase_at_level_6(self)` - Test expertise skills increase to 4 at level 6
- `test_expertise_skills_stored_in_proficiencies(self)` - Test expertise skills are stored in character_proficiencies
- `test_level_up_service_grants_expertise(self)` - Test LevelUpService grants Expertise properly
- `test_proficiency_system_integration(self)` - Test proficiency system retrieves expertise correctly
- `test_rogue_features_table_expertise_count(self)` - Test rogue_features table tracks expertise count
- `main()` - Run all tests

## test - `test/test_rogue_level_progression.py`

- `__init__(self)` - Inferred from name: init.
- `run_full_test(self)` - Run complete level progression test.
- `setup(self)` - Create test database and character.
- `test_level(self, level: int)` - Test a specific level progression.
- `verify_level_features(self, level: int, result: Dict[str, Any])` - Verify expected features for a given level.

## test - `test/test_rogue_subclass_selection.py`

- `test_rogue_subclass_selection()` - Test that level 3 rogues can choose between Thief and Assassin subclasses.

## test - `test/test_rogue_ui_action_cards.py`

- `_calculate_sneak_attack_dice(self, level: int)` - Calculate sneak attack dice based on level
- `_create_test_rogue(self, level: int=1, character_id: str='test_rogue')` - Create a test rogue character
- `_get_character_context(self, character_id: str)` - Build character context dict
- `_setup_test_database(self)` - Setup minimal database schema for testing
- `setup_method(self)` - Setup test database
- `teardown_method(self)` - Cleanup test database
- `test_card_disappears_when_used(self)` - Test that Stroke of Luck card disappears after use
- `test_card_generation_all_levels(self)` - Test card generation for all key levels
- `test_cunning_action_cards_level_2(self)` - Test Cunning Action cards appear at level 2
- `test_cunning_action_usage_simulation(self)` - Test simulating Cunning Action usage
- `test_cunning_strike_cards_level_5(self)` - Test Cunning Strike cards appear at level 5
- `test_devious_strikes_cards_level_14(self)` - Test Devious Strikes cards appear at level 14
- `test_steady_aim_card_level_3(self)` - Test Steady Aim card appears at level 3
- `test_steady_aim_usage_simulation(self)` - Test simulating Steady Aim usage
- `test_stroke_of_luck_card_level_20(self)` - Test Stroke of Luck card appears at level 20
- `test_stroke_of_luck_usage_simulation(self)` - Test simulating Stroke of Luck usage
- `test_uncanny_dodge_card_level_5(self)` - Test Uncanny Dodge card appears at level 5
- `test_uncanny_dodge_usage_simulation(self)` - Test simulating Uncanny Dodge usage
- `main()` - Run all tests

## test - `test/test_rogue_ui_choice_cards.py`

- `_calculate_sneak_attack_dice(self, level: int)` - Calculate sneak attack dice based on level
- `_create_test_rogue(self, level: int=1, character_id: str='test_rogue')` - Create a test rogue character
- `_setup_test_database(self)` - Setup minimal database schema for testing
- `setup_method(self)` - Setup test database
- `teardown_method(self)` - Cleanup test database
- `test_card_cost_display_clarity(self)` - Test all Rogue cards clearly show action/resource costs
- `test_card_disabled_state_visual_feedback(self)` - Test disabled cards have clear visual distinction
- `test_cunning_action_choice_between_options(self)` - Test Cunning Action presents 3 distinct choices
- `test_cunning_strike_choice_availability(self)` - Test Cunning Strike cards show choice-based costs
- `test_cunning_strike_damage_calculation_preview(self)` - Test Cunning Strike cards show damage reduction preview
- `test_cunning_strike_disabled_without_sneak_attack(self)` - Test Cunning Strike cards are disabled when Sneak Attack is not available
- `test_cunning_strike_multiple_choices_level_11(self)` - Test level 11+ allows choosing TWO Cunning Strike effects
- `test_cunning_strike_poisoner_kit_requirement(self)` - Test Poison Strike requires Poisoner's Kit in inventory
- `test_devious_strikes_high_cost_choices(self)` - Test Devious Strikes show high die costs clearly
- `test_expertise_skill_selection_ui(self)` - Test Expertise selection at character creation and level 6
- `test_multiple_effect_stacking_ui_level_11(self)` - Test UI for selecting multiple Cunning Strike effects (level 11+)
- `test_reaction_timing_window_ui(self)` - Test UI for reaction-based cards (Uncanny Dodge, Stroke of Luck)
- `test_steady_aim_choice_vs_movement(self)` - Test Steady Aim card shows tradeoff clearly
- `test_stroke_of_luck_failed_roll_trigger(self)` - Test Stroke of Luck card appears after failed d20 roll
- `test_uncanny_dodge_choice_to_use(self)` - Test player can CHOOSE whether to use Uncanny Dodge
- `test_uncanny_dodge_reaction_timing(self)` - Test Uncanny Dodge card appears during enemy attack
- `main()` - Run all tests

## test - `test/test_rogue_validation.py`

- `main()` - Run all validation tests.
- `test_action_types_defined()` - Test that Rogue action types are defined.
- `test_feature_definitions()` - Test that Rogue feature definitions are complete.
- `test_rogue_service_import()` - Test that the RogueAbilitiesService can be imported.
- `test_sneak_attack_dice_calculation()` - Test Sneak Attack dice calculation logic.
- `test_weapon_attack_service_integration()` - Test that WeaponAttackService includes Sneak Attack integration.
- `test_weapon_eligibility()` - Test weapon eligibility for Sneak Attack.

## test - `test/test_scalable_subclass_architecture.py`

- `test_enhanced_manager_with_registry()` - Test that EnhancedSubclassManager works with the registry.
- `test_feature_type_compatibility()` - Test that different subclasses use feature types correctly.
- `test_registry_availability()` - Test registry availability queries.
- `test_registry_loads_berserker()` - Test that the registry can load the existing Berserker.
- `test_registry_loads_champion()` - Test that the registry can load the new Champion.

## test - `test/test_shop_integration.py`

- `__init__(self)` - Inferred from name: init.
- `run_all_tests(self)` - Inferred from name: run all tests.
- `test_shop_interface_signature(self)` - Test that ShopInterface can be instantiated with correct parameters
- `test_shop_size_enum_values(self)` - Test that all ShopSize enum values work
- `test_vendor_encounter_compatibility(self)` - Test that vendor encounter can create ShopInterface

## test - `test/test_shop_system.py`

- `__init__(self)` - Inferred from name: init.
- `run_all_tests(self)` - Inferred from name: run all tests.
- `test_fractional_currency(self)` - Inferred from name: test fractional currency.
- `test_large_shop_inventory(self)` - Inferred from name: test large shop inventory.
- `test_low_cost_items(self)` - Inferred from name: test low cost items.
- `test_medium_shop_inventory(self)` - Inferred from name: test medium shop inventory.
- `test_shop_markup(self)` - Inferred from name: test shop markup.
- `test_shop_sorting(self)` - Inferred from name: test shop sorting.
- `test_small_shop_inventory(self)` - Inferred from name: test small shop inventory.

## test - `test/test_simple.py`

- `test_character_creation()` - Inferred from name: test character creation.

## test - `test/test_simple_validation.py`

- `main()` - Inferred from name: main.

## test - `test/test_skill_challenge_system.py`

- `cleanup_test_data()` - Clean up test data from database.
- `main()` - Run all skill challenge system tests.
- `test_reward_system()` - Test reward and penalty application.
- `test_skill_attempt()` - Test making skill attempts.
- `test_skill_challenge_database()` - Test that skill challenge templates are loaded from database.
- `test_skill_challenge_session()` - Test creating and managing a skill challenge session.

## test - `test/test_skill_rewards.py`

- `__init__(self)` - Inferred from name: init.
- `get_inventory_count(self, item_name: str)` - Get quantity of an item in test character inventory.
- `run_all_tests(self)` - Inferred from name: run all tests.
- `setup_test_character(self)` - Create a test character in the database.
- `test_consumable_reward(self)` - Inferred from name: test consumable reward.
- `test_healing_potion_reward(self)` - Inferred from name: test healing potion reward.
- `test_item_reward(self)` - Inferred from name: test item reward.
- `test_rations_reward(self)` - Inferred from name: test rations reward.

## test - `test/test_skilled_feat.py`

- `setUp(self)` - Inferred from name: setUp.
- `tearDown(self)` - Inferred from name: tearDown.
- `test_skilled_feat_adds_three_skills(self)` - Inferred from name: test skilled feat adds three skills.
- `test_skilled_feat_can_be_taken_multiple_times(self)` - Inferred from name: test skilled feat can be taken multiple times.
- `test_skilled_feat_can_be_taken_twice_at_same_level(self)` - Inferred from name: test skilled feat can be taken twice at same level.
- `test_skilled_feat_excludes_existing_proficiencies(self)` - Inferred from name: test skilled feat excludes existing proficiencies.

## test - `test/test_sneak_attack_debug.py`

- `mock_get_context_weapon_properties(context)` - Inferred from name: mock get context weapon properties.
- `mock_has_class_feature(feature_name)` - Inferred from name: mock has class feature.
- `test_sneak_attack_debug()` - Debug sneak attack with various advantage states.

## test - `test/test_social_interactions.py`

- `__init__(self)` - Inferred from name: init.
- `_get_inventory_count(self, item_name: str)` - Get quantity of an item in inventory.
- `run_all_tests(self)` - Inferred from name: run all tests.
- `setup(self)` - Setup test character.
- `test_encounter_resolution_options(self)` - Test that encounters offer multiple resolution paths.
- `test_parlay_encounter_flow(self)` - Test complete parlay encounter flow.
- `test_skill_challenge_system_integration(self)` - Test skill challenge system integration with rewards.
- `test_skill_rewards_integration(self)` - Test that skill challenges properly reward items.
- `test_stealth_avoidance_flow(self)` - Test complete stealth avoidance flow.
- `test_xp_reward_balance(self)` - Test that different resolution methods have balanced XP rewards.

## test - `test/test_spell_action_cards.py`

- `main()` - Run all tests.
- `test_spell_action_cards_creation()` - Test that spell action cards are created for spellcasting characters.
- `test_spell_actions_consume_action_economy()` - Ensure spell action types integrate with action economy tracking.
- `test_spell_casting_context()` - Test that spell data is passed correctly in action context.
- `test_spell_icon_generation()` - Test that spell icons are generated correctly.

## test - `test/test_spell_cards_qt6.py`

- `test_spell_action_cards()` - Test that spell action cards appear for Nathlas.

## test - `test/test_spell_data_phase1.py`

- `main()` - Inferred from name: main.
- `test_cantrip_counts()` - Test that all classes have sufficient cantrips for character creation
- `test_essential_spells()` - Test that critical spells exist for each class
- `test_level1_spell_counts()` - Test that all classes have sufficient level 1 spells
- `test_total_spell_count()` - Test overall spell counts

## test - `test/test_spell_registry.py`

- `setUp(self)` - Set up test database.
- `tearDown(self)` - Clean up test database.
- `test_clear_cache(self)` - Test clearing the spell cache.
- `test_get_available_classes(self)` - Test getting all classes that have spells.
- `test_get_nonexistent_spell(self)` - Test retrieving a spell that doesn't exist.
- `test_get_ritual_spells(self)` - Test retrieving ritual spells.
- `test_get_ritual_spells_by_class(self)` - Test retrieving ritual spells for a specific class.
- `test_get_spell_by_id(self)` - Test retrieving a spell by ID.
- `test_get_spell_count_by_class(self)` - Test getting spell counts by level for a class.
- `test_get_spells_by_class(self)` - Test retrieving spells by class.
- `test_get_spells_by_class_and_level(self)` - Test retrieving spells by class and level.
- `test_search_spells_by_level(self)` - Test searching spells by level.
- `test_search_spells_by_name(self)` - Test searching spells by name.
- `test_search_spells_by_school(self)` - Test searching spells by school.
- `test_search_spells_concentration_only(self)` - Test searching for concentration spells only.
- `test_search_spells_ritual_only(self)` - Test searching for ritual spells only.
- `test_spell_caching(self)` - Test that spells are cached properly.

## test - `test/test_spell_saving_simple.py`

- `main()` - Inferred from name: main.
- `test_existing_character_spell_data()` - Inferred from name: test existing character spell data.
- `test_spell_data_available()` - Inferred from name: test spell data available.
- `test_spell_saving_logic_exists()` - Inferred from name: test spell saving logic exists.
- `test_spell_table_structure()` - Inferred from name: test spell table structure.

## test - `test/test_spell_selection_integration.py`

- `main()` - Inferred from name: main.
- `test_cleric_character_creation_no_spells()` - Inferred from name: test cleric character creation no spells.
- `test_warlock_character_creation_with_spells()` - Inferred from name: test warlock character creation with spells.
- `test_wizard_character_creation_with_spells()` - Inferred from name: test wizard character creation with spells.

## test - `test/test_spell_selection_ui.py`

- `main()` - Inferred from name: main.
- `test_cleric_selection()` - Inferred from name: test cleric selection.
- `test_fighter_no_selection()` - Inferred from name: test fighter no selection.
- `test_paladin_selection()` - Inferred from name: test paladin selection.
- `test_spell_data_availability()` - Inferred from name: test spell data availability.
- `test_warlock_selection()` - Inferred from name: test warlock selection.
- `test_wizard_selection()` - Inferred from name: test wizard selection.

## test - `test/test_spell_self_targeting.py`

- `_get_spell_buff_effects(spell_name, cast_level)` - Inferred from name: get spell buff effects.
- `_is_self_targeting_spell(spell_data)` - Inferred from name: is self targeting spell.
- `test_is_self_targeting_spell()` - Test that buff spells are correctly identified as self-targeting.
- `test_spell_buff_effects()` - Test that buff effects are correctly formatted.

## test - `test/test_spell_slots_qt6.py`

- `test_spell_slots()` - Test spell slot availability.

## test - `test/test_spellcasting_service.py`

- `setUp(self)` - Set up test database with minimal schema.
- `tearDown(self)` - Clean up test database.
- `test_concentration_mechanics(self)` - Test concentration spell mechanics.
- `test_initialize_cleric_spellcasting(self)` - Test initializing spellcasting for a cleric.
- `test_initialize_warlock_spellcasting(self)` - Test initializing spellcasting for a warlock.
- `test_initialize_wizard_spellcasting(self)` - Test initializing spellcasting for a wizard.
- `test_spell_slot_restoration(self)` - Test spell slot restoration on rest.
- `test_spell_slot_usage(self)` - Test using and restoring spell slots.
- `test_spell_validation(self)` - Test spell casting validation.
- `test_upcasting(self)` - Test casting spells at higher levels.
- `test_warlock_pact_magic_restoration(self)` - Test warlock pact magic slot restoration on short rest.

## test - `test/test_stage_1_3_ui.py`

- `log_callback(message)` - Inferred from name: log callback.
- `test_condition_badge_creation()` - Test creating individual condition badges.
- `test_condition_display_widget()` - Test the full condition display widget.
- `test_condition_logging()` - Test the condition logging system.
- `test_integration_with_existing_system()` - Test that our condition system doesn't break existing functionality.

## test - `test/test_stage_1_4_integration.py`

- `test_action_economy_restrictions()` - Test that conditions properly block actions.
- `test_condition_advantage_integration()` - Test that conditions properly integrate with advantage system.
- `test_condition_movement_restrictions()` - Test movement speed modifications from conditions.
- `test_danger_sense_full_integration()` - Test Danger Sense with full condition system integration.
- `test_exhaustion_comprehensive()` - Test comprehensive exhaustion effects across all systems.
- `test_saving_throw_integration()` - Test saving throw modifications from conditions.

## test - `test/test_stage_2_1_subclass_definitions.py`

- `test_berserker_definition()` - Test the Berserker subclass definition.
- `test_enhanced_subclass_manager()` - Test the enhanced subclass manager.
- `test_feature_type_handlers()` - Test different feature type handling.
- `test_subclass_feature_creation()` - Test creating individual subclass features.

## test - `test/test_stage_2_2_berserker_migration.py`

- `test_berserker_legacy_compatibility()` - Test that new system doesn't break existing Berserker functionality.
- `test_frenzy_damage_mechanics()` - Test Frenzy damage bonus mechanics.
- `test_intimidating_presence_mechanics()` - Test Intimidating Presence mechanics.
- `test_mindless_rage_integration()` - Test Mindless Rage with condition immunity system.
- `test_retaliation_mechanics()` - Test Retaliation reaction mechanics.

## test - `test/test_stage_2_3_ui_integration.py`

- `mock_handler(feature_name, character_id)` - Inferred from name: mock handler.
- `test_character_panel_integration()` - Test integration with character panel (mock-based).
- `test_feature_availability_logic()` - Test the feature availability checking logic.
- `test_feature_tooltips_and_styling()` - Test feature tooltips and visual styling information.
- `test_subclass_features_widget_backend()` - Test the backend functionality of SubclassFeaturesWidget.
- `test_ui_widget_creation()` - Test UI widget creation (if PyQt6 available).

## test - `test/test_stage_2_4_feature_activation.py`

- `test_action_card_integration()` - Test integration with action card system.
- `test_berserker_feature_activation()` - Test Berserker feature activation through action cards.
- `test_champion_feature_activation()` - Test Champion feature activation through automatic triggers.
- `test_resource_tracking_integration()` - Test resource tracking across the feature activation system.

## test - `test/test_stealth_mechanics.py`

- `add_equipment(self, db_path: str, character_id: str, item_data: Dict[str, Any])` - Add equipment to a character.
- `create_test_character(self, db_path: str, character_data: Dict[str, Any])` - Create a test character in the database.
- `setup_database(self, tmp_path)` - Create a test database with necessary schema.
- `test_assassin_features(self, setup_database)` - Test Assassin subclass features when attacking from hidden.
- `test_encounter_stealth_check(self, setup_database)` - Test full encounter stealth check with multiple monsters.
- `test_hidden_attack_bonuses(self, setup_database)` - Test attack bonuses when attacking from hidden.
- `test_monster_perception_check(self, setup_database)` - Test monster perception checks against stealth DC.
- `test_stealth_with_elven_cloak(self, setup_database)` - Test stealth with advantage from Elven Cloak.
- `test_stealth_with_heavy_armor(self, setup_database)` - Test stealth with disadvantage from heavy armor.
- `test_stealth_with_proficiency(self, setup_database)` - Test that character with stealth proficiency can attempt to hide.
- `test_stealth_without_proficiency(self, setup_database)` - Test that character without stealth proficiency cannot hide.

## test - `test/test_tab_styling.py`

- `get_tab_availability(status)` - Inferred from name: get tab availability.
- `test_css_generation()` - Test that CSS is generated correctly.
- `test_tab_availability_logic()` - Test the logic for determining tab availability.

## test - `test/test_ui_action_cards.py`

- `_create_test_character(self, character_id='test_char', class_name='barbarian', level=1, subclass='berserker', rage_uses=2)` - Create a test character
- `_setup_test_database(self)` - Setup minimal database schema for testing
- `setup_method(self)` - Setup test database and generator
- `teardown_method(self)` - Cleanup test database
- `test_action_card_generation(self)` - Test generating action cards from registry
- `test_disabled_states_with_reasons(self)` - Test disabled card states with detailed reasons
- `test_economy_state_awareness(self)` - Test that cards reflect action economy state
- `test_enhanced_description(self)` - Test enhanced descriptions with cost and availability info
- `test_grouped_by_economy_type(self)` - Test grouping cards by economy type
- `test_legacy_integration(self)` - Test integration with legacy ActionCard system
- `test_resource_cost_display(self)` - Test that resource costs are displayed correctly
- `test_resource_summary(self)` - Test resource summary generation
- `test_warning_badges(self)` - Test warning badge system
- `test_ui_action_cards()` - Main test function as specified in roadmap

## test - `test/test_unified_feature_system.py`

- `test_unified_feature_system()` - Test the new unified feature system with all 11 classes

## test - `test/test_weapon_hydration.py`

- `test_longsword_plus_one_exists()` - Inferred from name: test longsword plus one exists.
- `test_magic_weapon_variants()` - Inferred from name: test magic weapon variants.

## test - `test/testing_framework_character_creation.py`

- `__init__(self, framework: UIAutomationFramework)` - Inferred from name: init.
- `_finalize_character(self, name: str)` - Set character name and complete creation.
- `_handle_class_features(self, char_class: CharacterClass)` - Handle class-specific feature selection.
- `_handle_equipment(self)` - Handle equipment selection.
- `_handle_rogue_features(self)` - Handle Rogue-specific features.
- `_handle_spell_selection(self, char_class: CharacterClass)` - Handle spell selection for spellcasting classes.
- `_navigate_to_character_creation(self)` - Navigate to character creation interface.
- `_select_background_and_species(self)` - Select background and species.
- `_select_cantrips(self, recommended_cantrips: List[str], required_count: int)` - Select cantrips from available options.
- `_select_class(self, char_class: CharacterClass)` - Select character class.
- `_select_class_from_buttons(self, class_name: str)` - Select class from buttons.
- `_select_class_from_combo(self, class_name: str)` - Select class from combo box.
- `_select_class_from_list(self, class_name: str)` - Select class from QListWidget.
- `_select_fighting_style(self)` - Select fighting style for Fighter.
- `_select_from_list_or_combo(self, option_name: str, context_keywords: List[str])` - Select an option from list widget or combo box based on context.
- `_select_level1_spells(self, recommended_spells: List[str], required_count: int)` - Select level 1 spells.
- `_select_warlock_invocation(self)` - Select invocation for Warlock.
- `_set_ability_scores(self, char_class: CharacterClass)` - Set ability scores appropriate for the class.
- `_verify_character_created(self, name: str)` - Verify character was created in database.
- `create_complete_character(self, char_class: CharacterClass, name: str)` - Create a complete character with all steps.
- `__init__(self, framework: UIAutomationFramework)` - Inferred from name: init.
- `_find_spell_selection_ui(self)` - Check if spell selection UI elements are present.
- `validate_spell_selection_ui(self, char_class: CharacterClass)` - Validate that spell selection UI appears for spellcasting classes.
- `main()` - Main entry point for character creation testing.

## test - `test/testing_framework_combat_interactions.py`

- `__init__(self, framework: UIAutomationFramework)` - Inferred from name: init.
- `_check_concentration_indicator(self)` - Check if concentration indicator is shown.
- `_enter_combat_mode(self, character_id: str)` - Enter combat mode with the specified character.
- `_find_action_cards_by_type(self, action_type: str)` - Find action cards of a specific type.
- `_find_class_feature_cards(self)` - Find class feature action cards.
- `_find_concentration_spell_cards(self)` - Find spell cards that require concentration.
- `_find_spell_action_cards(self)` - Find spell action cards.
- `_find_weapon_attack_cards(self)` - Find weapon attack action cards.
- `_get_recent_combat_log(self)` - Get recent entries from combat log.
- `_get_spell_slot_counts(self)` - Get current spell slot counts.
- `_is_cantrip_card(self, card: QPushButton)` - Check if a card represents a cantrip.
- `_verify_slot_consumption(self, initial: Dict, final: Dict)` - Verify that a spell slot was consumed.
- `test_action_economy_enforcement(self, character_id: str)` - Test that action economy is properly enforced.
- `test_class_features(self, character_id: str)` - Test class feature activation.
- `test_concentration_mechanics(self, character_id: str)` - Test concentration spell mechanics.
- `test_spell_casting_in_combat(self, character_id: str)` - Test spell casting mechanics during combat.
- `test_weapon_attacks(self, character_id: str)` - Test weapon attack mechanics.
- `__init__(self, framework: UIAutomationFramework)` - Inferred from name: init.
- `create_combat_scenario(self, scenario: CombatScenario)` - Create and run a specific combat scenario.
- `run_all_combat_tests(self, character_id: str)` - Run all combat tests for a character.
- `main()` - Main entry point for combat testing.

## test - `test/testing_framework_master.py`

- `__init__(self)` - Inferred from name: init.
- `_get_test_character_with_spells(self)` - Get a character ID that has spells for testing.
- `cleanup(self)` - Clean up testing environment.
- `generate_comprehensive_report(self, results: List[TestResult])` - Generate a comprehensive test report.
- `quick_spell_test(self, character_id: Optional[str]=None)` - Run a quick spell action card validation.
- `run_character_creation_tests(self, spellcasters_only: bool=False)` - Run character creation tests.
- `run_combat_interaction_tests(self, character_id: Optional[str]=None)` - Run combat interaction tests.
- `run_full_test_suite(self)` - Run the complete test suite.
- `run_spell_action_card_tests(self, character_id: Optional[str]=None)` - Run comprehensive spell action card tests.
- `setup(self)` - Initialize the testing environment.
- `setup_test_data_and_run(self)` - Set up test data and run comprehensive tests.
- `main()` - Main entry point for the testing framework.

## test - `test/testing_framework_spell_actions.py`

- `__init__(self, framework: UIAutomationFramework)` - Inferred from name: init.
- `_enter_encounter_mode(self)` - Enter encounter mode to see action cards.
- `_find_all_action_cards(self)` - Find all action cards in the action panel.
- `_find_card_for_spell(self, spell: Dict, cards: List[QWidget])` - Find the action card for a specific spell.
- `_find_spell_cards_by_level(self, level: int)` - Find spell cards for a specific spell level.
- `_get_character_spell_slots(self, character_id: str)` - Get character's current spell slots.
- `_get_character_spells(self, character_id: str)` - Get character's spells from database.
- `_is_spell_card(self, card: QWidget)` - Check if an action card is a spell card.
- `_looks_like_action_card(self, widget: QWidget)` - Check if a widget looks like an action card.
- `_navigate_to_character(self, character_id: str)` - Navigate to and load a specific character.
- `test_cantrip_unlimited_casting(self, character_id: str)` - Test that cantrips can be cast unlimited times.
- `test_spell_card_generation(self, character_id: str)` - Test that spell cards are generated correctly for a character.
- `test_spell_slot_consumption(self, character_id: str)` - Test that casting spells consumes spell slots correctly.
- `__init__(self)` - Inferred from name: init.
- `cleanup_test_characters(self)` - Remove test characters from database.
- `create_test_wizard_with_spells(self, name: str='TestWizardSpells')` - Create a test wizard character with known spells.
- `main()` - Main entry point for spell action testing.

## test - `test/testing_framework_ui_automation.py`

- `__init__(self, framework: UIAutomationFramework)` - Inferred from name: init.
- `_complete_character_creation(self, name: str)` - Complete the character creation process.
- `_select_class(self, class_name: str)` - Select a character class.
- `_select_wizard_spells(self)` - Select spells for a wizard character.
- `_start_character_creation(self)` - Start character creation process.
- `create_test_wizard(self, name: str='TestWizard')` - Create a test wizard character with spells.
- `__init__(self, framework: UIAutomationFramework)` - Inferred from name: init.
- `_check_spell_cast_feedback(self)` - Check if spell casting produced expected feedback.
- `_find_spell_action_cards(self)` - Find spell action cards in the UI.
- `_load_character(self, character_id: str)` - Load a specific character.
- `_start_test_encounter(self)` - Start a test encounter to see action cards.
- `test_spell_cards_appear(self, character_id: str)` - Test that spell action cards appear for a spellcasting character.
- `test_spell_casting(self, character_id: str)` - Test actually casting a spell from action cards.
- `__init__(self)` - Inferred from name: init.
- `_generate_html_report(self)` - Generate HTML test report.
- `_get_test_character_with_spells(self)` - Get a character ID that has spells for testing.
- `cleanup(self)` - Clean up testing environment.
- `generate_report(self)` - Generate and save a test report.
- `run_character_creation_tests(self)` - Run character creation tests.
- `run_spell_action_card_tests(self)` - Run spell action card tests.
- `setup(self)` - Initialize the testing environment.
- `__init__(self, app: QApplication, main_window: MainWindow)` - Inferred from name: init.
- `_ensure_widget_visible(self, widget: QWidget)` - Ensure a widget is visible by scrolling its parent scroll area if needed.
- `check_checkbox(self, checkbox: QCheckBox, checked: bool=True)` - Check or uncheck a checkbox.
- `click_widget(self, widget: QWidget)` - Click a widget if it's clickable.
- `find_widget_by_object_name(self, object_name: str)` - Find a widget by its objectName.
- `find_widget_by_text(self, text: str, widget_type=None)` - Find a widget by its text content.
- `set_combo_box_value(self, combo_box: QComboBox, text: str)` - Set a combo box to a specific value.
- `set_spinbox_value(self, spinbox: QSpinBox, value: int)` - Set a spinbox to a specific value.
- `take_screenshot(self, name: str)` - Take a screenshot of the main window.
- `wait_for_widget(self, widget_finder, timeout_ms: int=5000)` - Wait for a widget to become available.
- `main()` - Main entry point for testing framework.

## test - `test/ui/test_action_panel_integration.py`

- `__init__(self, db_path)` - Inferred from name: init.
- `_force_reload_character(self)` - Mock character reload.
- `show_message(self, title, message)` - Mock message display.
- `test_improved_critical_range(self, action_panel)` - Test Champion's improved critical hit range (19-20).
- `test_dueling_damage_bonus_application(self, action_panel)` - Test Dueling fighting style adds +2 damage to one-handed weapons.
- `test_great_weapon_fighting_reroll_mechanics(self, action_panel)` - Test Great Weapon Fighting treats 1s and 2s as 3s per D&D 2024.
- `test_action_surge_activation_and_cooldown(self, action_panel)` - Test Action Surge usage and short rest recovery.
- `test_indomitable_save_reroll(self, action_panel)` - Test Indomitable save reroll functionality.
- `test_second_wind_activation_and_recovery(self, action_panel)` - Test Second Wind usage and short rest recovery.
- `test_tactical_master_substitution_at_level_9(self, action_panel)` - Test Tactical Master property substitution for level 9+ Fighters.
- `test_weapon_mastery_tooltip_display(self, action_panel)` - Test that weapon mastery tooltips show correct properties.
- `action_panel(qapp, temp_db, fighter_characters)` - Create ActionPanel with mocked main window.
- `fighter_characters(temp_db)` - Create Fighter characters at various levels for testing.
- `qapp()` - Create QApplication instance.
- `temp_db()` - Create temporary database with full Fighter test data.
- `test_ui_interaction_helpers()` - Test helper functions for UI interactions work correctly.

## test - `test/ui/test_rest_restrictions.py`

- `__init__(self, id, encounter_id, monster_id, monster_name, max_hit_points, current_hit_points, armor_class, initiative)` - Inferred from name: init.
- `is_alive(self)` - Inferred from name: is alive.
- `__init__(self)` - Inferred from name: init.
- `add_message(self, message)` - Inferred from name: add message.
- `clear(self)` - Inferred from name: clear.
- `contains(self, text)` - Inferred from name: contains.
- `log_combat(self, message)` - Inferred from name: log combat.
- `__init__(self, db_path)` - Inferred from name: init.
- `_force_reload_character(self)` - Inferred from name: force reload character.
- `show_message(self, title, message)` - Inferred from name: show message.
- `test_rest_blocked_with_active_hazard(self, action_panel_with_encounter)` - Test that rest is blocked when hazards are active.
- `test_long_rest_blocked_without_rations(self, action_panel_with_encounter)` - Test that long rest is blocked when character has no rations.
- `test_long_rest_consumes_ration(self, action_panel_with_encounter)` - Test that long rest consumes one ration.
- `test_rest_allowed_after_monsters_defeated(self, action_panel_with_encounter)` - Test that rest is allowed after all monsters are dead.
- `test_rest_blocked_with_active_monster(self, action_panel_with_encounter)` - Test that rest button is blocked when monsters are alive.
- `test_rest_blocked_with_multiple_monsters(self, action_panel_with_encounter)` - Test that rest is blocked when at least one monster is alive.
- `test_short_rest_does_not_consume_rations(self, action_panel_with_encounter)` - Test that short rest does NOT consume rations.
- `action_panel_with_encounter(qapp, temp_db, test_character)` - Create ActionPanel with mocked encounter panel for testing.
- `qapp()` - Create QApplication instance.
- `temp_db()` - Create temporary database with full schema and seed data.
- `test_character(temp_db)` - Get an existing test character and add rations.
- `test_monsters_present_detection()` - Unit test for _monsters_present() method.

## test - `test/validate_action_types.py`

- `_map_action_to_economy_type(self, action_type: ActionType)` - Copy of the mapping method for testing.
- `test_action_economy_mapping()` - Test that action economy mapping works without errors.
- `validate_action_types()` - Validate that all ActionType references exist in the enum.

## test - `test_hex_map.py`

- `test_hex_system()` - Inferred from name: test hex system.

## test - `test_monster_knowledge.py`

- `__init__(self)` - Inferred from name: init.
- `add_example_section(self, layout)` - Add an example showing different success levels.
- `init_ui(self)` - Initialize the user interface.
- `on_knowledge_checked(self, monster, knowledge)` - Handle knowledge check completion.
- `get_sample_monsters()` - Get some sample monsters from the database.
- `main()` - Run the demo application.

## test - `testing/debug_subclass_selection.py`

- `__init__(self)` - Inferred from name: init.
- `load_theron(self)` - Load Theron character
- `open_training_hall(self)` - Navigate to training hall
- `run_test(self)` - Run the complete test
- `setup(self)` - Initialize the application
- `test_subclass_selection(self)` - Test the subclass selection logic
- `wait(self, ms)` - Wait for specified milliseconds

## test - `tests/action_cards/test_action_panel_weapon_mastery.py`

- `mastery_db(tmp_path)` - Inferred from name: mastery db.
- `test_variant_weapon_hydrates_and_applies_mastery(qtbot, mastery_db)` - Inferred from name: test variant weapon hydrates and applies mastery.

## test - `tests/core/test_core_validation.py`

- `run_all_tests()` - Run all core validation tests.
- `test_character_classes_data()` - Test that character classes are properly loaded.
- `test_core_imports()` - Test that core modules can be imported.
- `test_database_exists()` - Test that the database exists and is accessible.
- `test_equipment_data()` - Test that equipment data is loaded.

## test - `tests/core/test_encounter_systems.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `log(self, message: str, status: str='INFO')` - Log test output.
- `print_summary(self)` - Print test results summary.
- `run_all_tests(self)` - Run all encounter system tests.
- `test_encounter_level_scaling(self)` - Test that encounters scale appropriately with character level.
- `test_hazard_gear_bonuses(self)` - Test that hazard gear bonuses work correctly.
- `test_hazard_system(self)` - Test hazard system and level-appropriate hazards.
- `test_monster_combat_data(self)` - Test that monsters have valid combat-related data.
- `test_monster_database_integrity(self)` - Test that monster database has valid entries with required fields.
- `test_skill_challenge_mechanics(self)` - Test skill challenge session creation and attempt mechanics.
- `test_skill_challenge_templates(self)` - Test that skill challenge templates are properly configured.
- `test_town_encounter_system(self)` - Test town encounter system (vendors, training hall, etc.).
- `main()` - Main entry point.

## test - `tests/core/test_features.py`

- `fighter_feature_db()` - Inferred from name: fighter feature db.
- `integration_db()` - Inferred from name: integration db.
- `qt_app()` - Inferred from name: qt app.
- `test_action_panel_uses_resource_service(qt_app, integration_db)` - Inferred from name: test action panel uses resource service.
- `test_feature_manager_loads_champion_features(fighter_feature_db)` - Inferred from name: test feature manager loads champion features.
- `test_feature_manager_loads_fighter_progression(fighter_feature_db)` - Inferred from name: test feature manager loads fighter progression.
- `test_initialize_character_features_seeds_resources(integration_db)` - Inferred from name: test initialize character features seeds resources.

## test - `tests/core/test_skill_allocation.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `create_test_character(self, class_id: str, background_id: str, race_id: str)` - Create a minimal test character.
- `get_class_skill_options(self, class_id: str)` - Get class skill selection parameters.
- `get_expected_background_skills(self, background_id: str)` - Get expected skills from background.
- `get_expected_species_skills(self, species_id: str)` - Get expected fixed skills from species.
- `get_skills_from_db(self, character_id: str)` - Retrieve skill proficiencies grouped by source.
- `log(self, message: str, status: str='INFO')` - Log test output.
- `print_summary(self)` - Print test results summary.
- `run_all_tests(self)` - Run all skill allocation tests.
- `setup(self)` - Setup test environment.
- `teardown(self)` - Cleanup test data.
- `test_background_skill_allocation(self)` - Test that background skills are properly allocated.
- `test_class_skill_allocation(self)` - Test that class skill selections are properly allocated.
- `test_no_duplicate_skills(self)` - Test that no duplicate skills are allocated across sources.
- `test_skill_count_validation(self)` - Test that characters receive the correct total number of skills.
- `test_species_skill_allocation(self)` - Test that species skills are properly allocated.
- `main()` - Main entry point.

## test - `tests/core_regression.py`

- `create_champion(self, db_path: str, level: int)` - Create test champion character
- `db_path(self, tmp_path)` - Inferred from name: db path.
- `test_level_10_heroic_warrior(self, db_path)` - Level 10: Heroic Warrior grants Inspiration at turn start
- `test_level_15_superior_critical(self, db_path)` - Level 15: Superior Critical sets crit range to 18-20
- `test_level_18_survivor(self, db_path)` - Level 18: Survivor heals 5+CON when bloodied at turn start
- `test_level_3_improved_critical(self, db_path)` - Level 3: Improved Critical sets crit range to 19-20
- `test_level_3_remarkable_athlete(self, db_path)` - Level 3: Remarkable Athlete grants bonus on Athletics checks
- `db_path(self, tmp_path)` - Inferred from name: db path.
- `test_champion_improved_crit_in_combat(self, db_path)` - Test Champion's improved crit range (19-20) is active
- `test_full_combat_round_with_abilities(self, db_path)` - Test complete combat round using Fighter abilities
- `db_path(self, tmp_path)` - Inferred from name: db path.
- `test_fighter_level_progression(self, db_path)` - Character can gain XP and level up
- `test_loot_drop_service_exists(self, db_path)` - Loot drop service can drop items
- `test_monster_has_xp(self, db_path)` - Monsters have experience points
- `create_fighter_level_19(self, db_path: str)` - Create level 19 fighter
- `db_path(self, tmp_path)` - Create test database
- `test_all_epic_boons_available(self, db_path)` - All 10 Epic Boons are available for selection
- `test_apply_epic_boon_to_character(self, db_path)` - Applying Epic Boon adds it to character_feats
- `test_can_select_epic_boon(self, db_path)` - Can select an Epic Boon feat at level 19
- `test_cannot_get_multiple_epic_boons(self, db_path)` - Character can only have one Epic Boon
- `test_level_19_triggers_epic_boon_choice(self, db_path)` - Level 19: Epic Boon feat becomes available
- `test_level_11_three_attacks(self)` - Level 11-19: 3 attacks (2 extra)
- `test_level_1_one_attack(self)` - Level 1-4: 1 attack
- `test_level_20_four_attacks(self)` - Level 20: 4 attacks (3 extra)
- `test_level_5_two_attacks(self)` - Level 5-10: 2 attacks (1 extra)
- `create_fighter(self, db_path: str, level: int, subclass: str=None)` - Create test fighter character
- `db_path(self, tmp_path)` - Inferred from name: db path.
- `test_level_10_second_wind_max(self, db_path)` - Level 10: Second Wind increases to 4 uses
- `test_level_13_indomitable_two_uses(self, db_path)` - Level 13: Indomitable increases to 2 uses
- `test_level_13_studied_attacks(self, db_path)` - Level 13: Studied Attacks grants advantage after miss
- `test_level_17_action_surge_two_uses(self, db_path)` - Level 17: Action Surge increases to 2 uses per rest
- `test_level_17_indomitable_three_uses(self, db_path)` - Level 17: Indomitable increases to 3 uses
- `test_level_1_second_wind_basic(self, db_path)` - Level 1: Second Wind heals 1d10 + level, 2 uses
- `test_level_2_action_surge(self, db_path)` - Level 2: Action Surge grants extra action, 1 use
- `test_level_2_tactical_mind(self, db_path)` - Level 2: Tactical Mind expends Second Wind for 1d10 boost
- `test_level_4_second_wind_scales(self, db_path)` - Level 4: Second Wind increases to 3 uses
- `test_level_9_indomitable(self, db_path)` - Level 9: Indomitable rerolls save with +level bonus, 1 use
- `test_long_rest_full_recovery(self, db_path)` - Long rest restores all Fighter resources
- `test_short_rest_recovery(self, db_path)` - Short rest restores 1 Second Wind use and all Action Surge
- `create_fighter(self, db_path: str, level: int)` - Create test fighter
- `db_path(self, tmp_path)` - Create test database
- `test_level_9_can_use_tactical_master(self, db_path)` - Level 9: Tactical Master becomes available
- `test_tactical_master_swap_to_push(self, db_path)` - Tactical Master: Can swap mastery to Push
- `test_tactical_master_swap_to_sap(self, db_path)` - Tactical Master: Can swap mastery to Sap
- `test_tactical_master_swap_to_slow(self, db_path)` - Tactical Master: Can swap mastery to Slow
- `db_path(self, tmp_path)` - Inferred from name: db path.
- `test_fighter_unlimited_masteries(self, db_path)` - Fighter has unlimited weapon masteries

## test - `tests/detailed/test_hero_mode_stats.py`

- `run_all_tests()` - Run all Hero Mode tests.
- `test_hero_mode_background_bonus()` - Test that background bonuses apply on top of 75 base points.
- `test_hero_mode_maximum_stats()` - Test edge case of maximizing stats within 75 points (max 18 per stat).
- `test_hero_mode_minimums()` - Test that Hero Mode enforces minimums correctly.
- `test_hero_mode_point_calculation()` - Test that Hero Mode uses 1-to-1 point calculation.
- `test_standard_vs_hero_mode()` - Compare standard point-buy vs Hero Mode for same stat array.

## test - `tests/features/test_champion_subclass.py`

- `combat_manager(self, fighter_db)` - Create CombatManager with test database.
- `fighter_db(self)` - Create Fighter test database.
- `test_champion_features_in_full_combat(self, combat_manager, fighter_db)` - Test Champion features work together in complete combat scenario.
- `test_remarkable_athlete_with_champion_combat(self, fighter_db)` - Test Remarkable Athlete enhances Champion's versatility.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `test_heroic_warrior_grants_inspiration(self, fighter_service)` - Test Heroic Warrior grants inspiration at start of turn.
- `test_heroic_warrior_level_requirement(self, fighter_service)` - Test Heroic Warrior requires Champion level 10.
- `test_heroic_warrior_no_duplicate_inspiration(self, fighter_service, fighter_db)` - Test Heroic Warrior doesn't grant inspiration if already at max.
- `fighter_db(self)` - Create Fighter test database.
- `test_improved_critical_19_20_range(self, weapon_service)` - Test Champion crits on 19-20 instead of just 20.
- `test_non_champion_normal_critical_range(self, weapon_service, fighter_db)` - Test non-Champions still crit only on 20.
- `test_superior_critical_18_19_20_range(self, weapon_service, fighter_db)` - Test Champion Superior Critical at level 15 (crits on 18-20).
- `weapon_service(self, fighter_db)` - Create WeaponAttackService with test database.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `test_remarkable_athlete_availability_level_3(self, fighter_service)` - Test Remarkable Athlete is available at Champion level 3.
- `test_remarkable_athlete_constitution_saves(self, fighter_service)` - Test Remarkable Athlete grants advantage on CON saving throws.
- `test_remarkable_athlete_dexterity_acrobatics(self, fighter_service)` - Test Remarkable Athlete grants advantage on DEX (Acrobatics) checks.
- `test_remarkable_athlete_initiative_rolls(self, fighter_service)` - Test Remarkable Athlete grants advantage on initiative.
- `test_remarkable_athlete_not_applied_to_other_skills(self, fighter_service)` - Test Remarkable Athlete doesn't apply to non-covered skills.
- `test_remarkable_athlete_strength_athletics(self, fighter_service)` - Test Remarkable Athlete grants advantage on STR (Athletics) checks.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `test_studied_attacks_advantage_after_miss(self, weapon_service, fighter_service, fighter_db)` - Test Studied Attacks grants advantage after missing same target.
- `test_studied_attacks_resets_on_hit(self, fighter_service)` - Test Studied Attacks advantage resets after hitting.
- `test_studied_attacks_target_specific(self, fighter_service)` - Test Studied Attacks advantage is specific to each target.
- `weapon_service(self, fighter_db)` - Create WeaponAttackService with test database.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `test_survivor_defy_death_at_zero_hp(self, fighter_service, fighter_db)` - Test Survivor prevents death at 0 HP.
- `test_survivor_healing_when_bloodied(self, fighter_service)` - Test Survivor heals when starting turn at half HP or less.
- `test_survivor_level_requirement(self, fighter_service)` - Test Survivor requires Champion level 18.
- `test_survivor_no_healing_when_healthy(self, fighter_service, fighter_db)` - Test Survivor doesn't heal when above half HP.

## test - `tests/features/test_fighter_action_surge.py`

- `fighter_db(self)` - Create Fighter test database.
- `test_action_surge_level_scaling_persistence(self, fighter_db)` - Test Action Surge max uses scale correctly with level.
- `test_action_surge_resource_tracking_persistence(self, fighter_db)` - Test Action Surge usage is properly tracked in database.
- `test_multiple_characters_independent_action_surge(self, fighter_db)` - Test Action Surge tracking is independent per character.
- `combat_setup(self, fighter_db)` - Set up combat scenario for testing.
- `fighter_db(self)` - Create Fighter test database.
- `test_action_surge_allows_multiple_attacks(self, combat_setup, fighter_db)` - Test Action Surge allows multiple Attack actions in one turn.
- `test_action_surge_dash_and_attack_combination(self, combat_setup, fighter_db)` - Test Action Surge allows Dash and Attack in same turn.
- `test_action_surge_spell_and_attack_combination(self, combat_setup, fighter_db)` - Test Action Surge allows casting spell and attacking (for Eldritch Knight).
- `combat_manager(self, fighter_db)` - Create CombatManager with test database.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `game_engine(self, fighter_db)` - Create GameEngine with test database.
- `test_action_surge_availability_at_level_2(self, fighter_service)` - Test Action Surge becomes available at Fighter level 2.
- `test_action_surge_combat_state_tracking(self, fighter_service, fighter_db)` - Test Action Surge state is tracked in combat.
- `test_action_surge_grants_additional_action(self, fighter_service, combat_manager)` - Test Action Surge grants one additional action on the current turn.
- `test_action_surge_multiclass_availability(self, fighter_service, fighter_db)` - Test Action Surge uses Fighter levels for multiclass characters.
- `test_action_surge_multiple_uses_at_high_level(self, fighter_service, fighter_db)` - Test Action Surge gets multiple uses at higher levels.
- `test_action_surge_no_additional_bonus_action(self, fighter_service)` - Test Action Surge does not grant additional bonus actions.
- `test_action_surge_no_additional_movement(self, fighter_service)` - Test Action Surge does not grant additional movement.
- `test_action_surge_resource_consumption(self, fighter_service)` - Test Action Surge consumes one use per short rest.
- `test_action_surge_rest_recovery(self, game_engine, fighter_service, fighter_db)` - Test Action Surge recovers on short and long rests.
- `test_action_surge_turn_end_cleanup(self, fighter_service, combat_manager)` - Test Action Surge effects end at the end of the turn.
- `test_action_surge_unconscious_character(self, fighter_service, fighter_db)` - Test Action Surge cannot be used when unconscious.

## test - `tests/features/test_fighter_combat_flow.py`

- `fighter_db(self)` - Create Fighter test database.
- `test_attack_roll_natural_1_always_misses(self, weapon_service)` - Test natural 1 always misses regardless of bonuses.
- `test_attack_roll_natural_20_always_hits(self, weapon_service)` - Test natural 20 always hits and crits regardless of AC.
- `test_attack_with_missing_weapon(self, weapon_service)` - Test attack calculation with weapon not in inventory.
- `test_attack_with_unequipped_weapon(self, weapon_service, fighter_db)` - Test attack with weapon in inventory but not equipped.
- `test_unconscious_character_cannot_attack(self, weapon_service, fighter_db)` - Test unconscious characters cannot make attacks.
- `weapon_service(self, fighter_db)` - Create WeaponAttackService with test database.
- `combat_manager(self, fighter_db)` - Create CombatManager with test database.
- `fighter_db(self)` - Create Fighter test database.
- `test_action_surge_doubles_attacks(self, combat_manager, weapon_service, fighter_db)` - Test Action Surge allows doubling attack actions.
- `test_critical_hit_damage_doubling(self, weapon_service)` - Test critical hits double damage dice correctly.
- `test_damage_resistance_interaction(self, weapon_service, fighter_db)` - Test Fighter damage vs resistant creatures.
- `test_fighting_style_and_mastery_combination(self, weapon_service)` - Test fighting style effects combine with weapon mastery.
- `test_full_attack_sequence_with_extra_attack(self, combat_manager, weapon_service)` - Test complete attack sequence with Extra Attack.
- `weapon_service(self, fighter_db)` - Create WeaponAttackService with test database.
- `fighter_db(self)` - Create Fighter test database.
- `test_archery_fighting_style_attack_bonus(self, weapon_service)` - Test Archery adds +2 to ranged weapon attack rolls.
- `test_archery_no_bonus_for_melee(self, weapon_service)` - Test Archery doesn't apply to melee attacks.
- `test_defense_fighting_style_ac_bonus(self, weapon_service, fighter_db)` - Test Defense fighting style adds +1 AC when wearing armor.
- `test_dueling_fighting_style_damage_bonus(self, weapon_service)` - Test Dueling adds +2 damage to one-handed weapon attacks.
- `test_dueling_no_bonus_with_shield_and_two_handed(self, weapon_service, fighter_db)` - Test Dueling doesn't apply with two-handed weapons.
- `test_great_weapon_fighting_no_effect_on_normal_rolls(self, weapon_service)` - Test Great Weapon Fighting doesn't affect rolls of 3 or higher.
- `test_great_weapon_fighting_treats_low_rolls_as_three(self, weapon_service)` - Test Great Weapon Fighting treats 1s and 2s as 3s per D&D 2024.
- `test_protection_fighting_style_reaction(self, weapon_service, fighter_db)` - Test Protection fighting style allows imposing disadvantage as reaction.
- `test_two_weapon_fighting_offhand_modifier(self, weapon_service, fighter_db)` - Test Two-Weapon Fighting adds ability modifier to off-hand damage.
- `weapon_service(self, fighter_db)` - Create WeaponAttackService with test database.

## test - `tests/features/test_fighter_indomitable.py`

- `fighter_db(self)` - Create Fighter test database.
- `test_indomitable_with_advantage(self, fighter_db)` - Test Indomitable interaction with advantage on saves.
- `test_indomitable_with_disadvantage(self, fighter_db)` - Test Indomitable interaction with disadvantage on saves.
- `fighter_db(self)` - Create Fighter test database.
- `test_indomitable_resource_tracking_persistence(self, fighter_db)` - Test Indomitable usage is properly tracked in database.
- `test_indomitable_save_history_tracking(self, fighter_db)` - Test saving throw history is tracked for analysis.
- `test_multiple_characters_independent_indomitable(self, fighter_db)` - Test Indomitable tracking is independent per character.
- `advantage_system(self, fighter_db)` - Create AdvantageSystem with test database.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `game_engine(self, fighter_db)` - Create GameEngine with test database.
- `test_indomitable_ability_modifier_application(self, fighter_service)` - Test Indomitable properly applies ability modifiers to saves.
- `test_indomitable_availability_at_level_9(self, fighter_service)` - Test Indomitable becomes available at Fighter level 9.
- `test_indomitable_death_save_interaction(self, fighter_service, fighter_db)` - Test Indomitable can be used on death saving throws.
- `test_indomitable_legendary_resistance_interaction(self, fighter_service)` - Test Indomitable doesn't stack with legendary resistance.
- `test_indomitable_level_17_three_uses(self, fighter_service, fighter_db)` - Test Indomitable gets 3 uses at level 17.
- `test_indomitable_long_rest_recovery(self, game_engine, fighter_service, fighter_db)` - Test Indomitable recovers on long rest only.
- `test_indomitable_multiclass_availability(self, fighter_service, fighter_db)` - Test Indomitable uses Fighter levels for multiclass characters.
- `test_indomitable_multiple_uses_at_high_level(self, fighter_service, fighter_db)` - Test Indomitable gets multiple uses at higher levels.
- `test_indomitable_must_use_reroll(self, fighter_service)` - Test that Indomitable forces you to use the reroll result.
- `test_indomitable_no_proficiency_bonus_for_non_proficient(self, fighter_service)` - Test Indomitable doesn't apply proficiency for non-proficient saves.
- `test_indomitable_proficiency_bonus_application(self, fighter_service)` - Test Indomitable applies proficiency bonus for proficient saves.
- `test_indomitable_reroll_mechanic(self, fighter_service)` - Test Indomitable allows rerolling a failed saving throw.
- `test_indomitable_resource_consumption(self, fighter_service)` - Test Indomitable consumes one use per long rest.

## test - `tests/features/test_fighter_second_wind.py`

- `fighter_db(self)` - Create Fighter test database.
- `test_multiple_characters_independent_tracking(self, fighter_db)` - Test Second Wind tracking is independent per character.
- `test_second_wind_resource_tracking_persistence(self, fighter_db)` - Test Second Wind usage is properly tracked in database.
- `test_second_wind_updates_character_hp(self, fighter_db)` - Test Second Wind properly updates character HP in database.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `game_engine(self, fighter_db)` - Create GameEngine with test database.
- `test_second_wind_healing_calculation(self, fighter_service, fighter_db)` - Test Second Wind healing: 1d10 + Fighter level.
- `test_second_wind_healing_cap_at_max_hp(self, fighter_service, fighter_db)` - Test Second Wind healing cannot exceed maximum HP.
- `test_second_wind_high_level_scaling(self, fighter_service, fighter_db)` - Test Second Wind scales with Fighter level.
- `test_second_wind_minimum_healing(self, fighter_service, fighter_db)` - Test Second Wind minimum healing (1 + level).
- `test_second_wind_multiclass_levels(self, fighter_service, fighter_db)` - Test Second Wind uses Fighter levels only for multiclass characters.
- `test_second_wind_resource_consumption(self, fighter_service, fighter_db)` - Test Second Wind consumes one use per short rest.
- `test_second_wind_rest_recovery(self, game_engine, fighter_db)` - Test Second Wind recovers on short and long rests.
- `test_second_wind_unconscious_character(self, fighter_service, fighter_db)` - Test Second Wind cannot be used when unconscious.
- `test_second_wind_wont_heal_at_max_hp(self, fighter_service)` - Test Second Wind cannot be used at maximum HP.

## test - `tests/features/test_fighter_weapon_mastery.py`

- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `test_tactical_master_level_requirement(self, fighter_service)` - Test Tactical Master only available at level 9+.
- `test_tactical_master_only_specific_masteries(self, fighter_service)` - Test Tactical Master only allows substituting Push, Sap, and Slow.
- `test_tactical_master_push_substitution(self, fighter_service, fighter_db)` - Test level 9+ Fighters can substitute Push mastery.
- `test_tactical_master_sap_substitution(self, fighter_service, fighter_db)` - Test level 9+ Fighters can substitute Sap mastery.
- `test_tactical_master_slow_substitution(self, fighter_service, fighter_db)` - Test level 9+ Fighters can substitute Slow mastery.
- `test_tactical_master_ui_interaction(self, fighter_service, fighter_db)` - Test UI shows substitution options for Tactical Master.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `test_fighter_weapon_mastery_availability(self, weapon_service)` - Test Fighters get weapon mastery from level 1.
- `test_graze_mastery_effect(self, weapon_service)` - Test Graze mastery deals damage on miss.
- `test_non_mastery_class_no_effects(self, weapon_service, fighter_db)` - Test non-mastery classes don't get mastery effects.
- `test_sap_mastery_effect(self, weapon_service)` - Test Sap mastery effect reduces target's next attack roll.
- `test_slow_mastery_effect(self, weapon_service)` - Test Slow mastery reduces target movement.
- `test_topple_mastery_effect(self, weapon_service)` - Test Topple mastery can knock target prone.
- `test_vex_mastery_effect(self, weapon_service)` - Test Vex mastery grants advantage on next attack against same target.
- `weapon_service(self, fighter_db)` - Create WeaponAttackService with test database.
- `fighter_db(self)` - Create Fighter test database.
- `test_mastery_multiclass_interaction(self, fighter_db)` - Test weapon mastery for multiclass characters.
- `test_mastery_with_improvised_weapons(self, fighter_db)` - Test mastery behavior with improvised weapons.
- `test_mastery_with_magical_weapons(self, fighter_db)` - Test weapon mastery works with magical weapon variants.
- `fighter_db(self)` - Create Fighter test database.
- `fighter_service(self, fighter_db)` - Create FighterAbilitiesService with test database.
- `game_engine(self, fighter_db)` - Create GameEngine with test database.
- `test_mastery_persistence_across_rests(self, game_engine, fighter_service)` - Test Fighter retains all weapon masteries after rest.
- `test_mastery_reordering_during_long_rest(self, game_engine, fighter_service)` - Test Fighters can reorder weapon masteries during long rest.
- `test_mastery_reordering_preserves_substitutions(self, fighter_service)` - Test reordering preserves Tactical Master substitutions.
- `test_no_mastery_slot_tracking(self, fighter_service)` - Test Fighters don't have limited mastery slots (per documentation).
- `fighter_db(self)` - Create Fighter test database.
- `test_mastery_reordering_ui_feedback(self, fighter_db)` - Test UI provides feedback during mastery reordering.
- `test_mastery_substitution_ui_indication(self, fighter_db)` - Test UI indicates when masteries are substituted.
- `test_mastery_tooltip_display(self, fighter_db)` - Test weapon tooltips show correct mastery information.

## test - `tests/features/test_paladin_action_integration.py`

- `__init__(self)` - Inferred from name: init.
- `print_summary(self)` - Print test results summary.
- `run_all_tests(self)` - Run all paladin action integration tests.
- `run_test(self, test_name: str, test_function)` - Run a single test and record results.
- `setup(self)` - Set up test environment.
- `test_action_type_mapping(self)` - Test that Lay on Hands action type is properly mapped.
- `test_apply_lay_on_hands_healing_method_exists(self)` - Test that _apply_lay_on_hands_healing method exists.
- `test_has_lay_on_hands_method_exists(self)` - Test that _has_lay_on_hands_uses method exists.
- `test_lay_on_hands_action_card_creation(self)` - Test that Lay on Hands action card can be created.
- `test_lay_on_hands_action_type_exists(self)` - Test that LAY_ON_HANDS action type is defined.
- `test_lay_on_hands_feature_check(self)` - Test checking for Lay on Hands feature.
- `test_lay_on_hands_import_in_action_panel(self)` - Test that LayOnHandsDialog is imported in action panel.
- `test_paladin_character_context_setup(self)` - Test setting up paladin character context.
- `test_use_lay_on_hands_method_exists(self)` - Test that _use_lay_on_hands method exists.
- `main()` - Run the paladin action integration test suite.

## test - `tests/features/test_paladin_auras.py`

- `__init__(self)` - Inferred from name: init.
- `create_test_paladin(self, character_id: str, level: int, charisma: int, subclass: str='devotion')` - Create a test paladin character in the database.
- `print_summary(self)` - Print test results summary.
- `run_all_tests(self)` - Run all paladin aura tests.
- `run_test(self, test_name: str, test_function)` - Run a single test and record results.
- `setup(self)` - Set up test environment.
- `test_aura_expansion_level_18(self)` - Test aura expansion at level 18.
- `test_aura_manager_creation(self)` - Test that aura manager can be created.
- `test_aura_of_courage(self)` - Test Aura of Courage (level 10, fear immunity).
- `test_aura_of_devotion(self)` - Test Aura of Devotion (level 7 Devotion oath, charm immunity).
- `test_aura_of_protection(self)` - Test Aura of Protection (level 6, +Cha mod to saves).
- `test_aura_range_calculation(self)` - Test aura range calculation by level.
- `test_different_oath_auras(self)` - Test auras from different oaths.
- `test_low_charisma_protection(self)` - Test Aura of Protection with low Charisma (minimum +1 bonus).
- `test_multiple_auras(self)` - Test character with multiple auras (high level).
- `test_non_paladin_no_auras(self)` - Test that non-paladins don't get auras.
- `main()` - Run the paladin aura test suite.

## test - `tests/features/test_paladin_channel_divinity.py`

- `__init__(self)` - Inferred from name: init.
- `print_summary(self)` - Print test results summary.
- `run_all_tests(self)` - Run all Channel Divinity tests.
- `run_test(self, test_name: str, test_function)` - Run a single test and record results.
- `setup(self)` - Set up test environment.
- `test_button_enable_disable(self)` - Test use button enable/disable logic.
- `test_channel_divinity_options_level_3_devotion(self)` - Test Channel Divinity options for level 3 Devotion paladin.
- `test_channel_divinity_options_level_9(self)` - Test Channel Divinity options for level 9 paladin.
- `test_dialog_creation(self)` - Test that Channel Divinity dialog can be created.
- `test_different_oaths(self)` - Test Channel Divinity options for different oaths.
- `test_option_data_structure(self)` - Test that option data has required fields.
- `test_option_selection(self)` - Test option selection functionality.
- `test_paladin_service_channel_divinity(self)` - Test Channel Divinity through paladin service.
- `test_uses_tracking(self)` - Test Channel Divinity uses tracking.
- `main()` - Run the Channel Divinity test suite.

## test - `tests/features/test_paladin_channel_divinity_integration.py`

- `__init__(self)` - Inferred from name: init.
- `print_summary(self)` - Print test results summary.
- `run_all_tests(self)` - Run all Channel Divinity action integration tests.
- `run_test(self, test_name: str, test_function)` - Run a single test and record results.
- `setup(self)` - Set up test environment.
- `test_action_type_mapping_channel_divinity(self)` - Test that Channel Divinity action type is properly mapped.
- `test_channel_divinity_action_card_creation(self)` - Test that Channel Divinity action card can be created.
- `test_channel_divinity_action_type_exists(self)` - Test that CHANNEL_DIVINITY action type is defined.
- `test_channel_divinity_feature_check(self)` - Test checking for Channel Divinity feature.
- `test_channel_divinity_import_in_action_panel(self)` - Test that ChannelDivinityDialog is imported in action panel.
- `test_channel_divinity_methods_exist(self)` - Test that Channel Divinity methods exist in action panel.
- `test_channel_divinity_options_generation(self)` - Test Channel Divinity options generation.
- `test_different_oath_options(self)` - Test Channel Divinity options for different oaths.
- `test_paladin_character_context_with_channel_divinity(self)` - Test setting up paladin character context for Channel Divinity.
- `main()` - Run the Channel Divinity action integration test suite.

## test - `tests/features/test_paladin_divine_smite.py`

- `action_panel(self, qapp, temp_db, paladin_character)` - Create ActionPanel with Paladin character.
- `capture_damage(monster_id, damage)` - Inferred from name: capture damage.
- `mock_exec(self)` - Inferred from name: mock exec.
- `mock_exec(self)` - Inferred from name: mock exec.
- `mock_exec(self)` - Inferred from name: mock exec.
- `mock_exec(self)` - Inferred from name: mock exec.
- `mock_exec(self)` - Inferred from name: mock exec.
- `paladin_character(self, temp_db)` - Create a test Paladin character with spell slots.
- `qapp(self)` - Create or get QApplication instance.
- `temp_db(self)` - Create temporary database with test data.
- `test_no_dialog_for_non_paladin(self, qapp, temp_db)` - Test that Divine Smite dialog doesn't appear for non-Paladin classes.
- `test_smite_damage_on_critical_hit(self, action_panel, temp_db)` - Test that Divine Smite damage is doubled on critical hits.
- `test_smite_dialog_appears_when_monster_survives(self, action_panel, temp_db)` - Test that Divine Smite dialog appears when monster would survive base damage.
- `test_smite_dialog_not_shown_when_monster_dies(self, action_panel, temp_db)` - Test that Divine Smite dialog doesn't appear when monster would die anyway.
- `test_spell_slot_consumption(self, action_panel, temp_db, paladin_character)` - Test that using Divine Smite properly consumes spell slots.

## test - `tests/features/test_paladin_lay_on_hands.py`

- `__init__(self)` - Inferred from name: init.
- `print_summary(self)` - Print test results summary.
- `run_all_tests(self)` - Run all Lay on Hands tests.
- `run_test(self, test_name: str, test_function)` - Run a single test and record results.
- `setup(self)` - Set up test environment.
- `test_dialog_creation(self)` - Test that Lay on Hands dialog can be created.
- `test_healing_info_retrieval(self)` - Test getting healing information from dialog.
- `test_healing_point_limits(self)` - Test healing point usage limits.
- `test_healing_pool_calculation(self)` - Test healing pool calculations.
- `test_low_pool_limits(self)` - Test behavior with low healing pool.
- `test_paladin_service_lay_on_hands(self)` - Test Lay on Hands through paladin service.
- `test_poison_curing_option(self)` - Test poison curing functionality.
- `main()` - Run the Lay on Hands test suite.

## test - `tests/fixtures/fighter_test_database.py`

- `__enter__(self)` - Context manager entry.
- `__exit__(self, exc_type, exc_val, exc_tb)` - Context manager exit with cleanup.
- `__init__(self, db_path=None)` - Initialize with optional database path.
- `_configure_fighting_styles(self)` - Assign fighting styles to test various combinations.
- `_create_fighter_characters(self)` - Create Fighter characters at various levels for comprehensive testing.
- `_setup_combat_state(self)` - Initialize combat state tables for testing.
- `_setup_fighter_equipment(self)` - Equip Fighter characters with appropriate weapons and armor.
- `cleanup(self)` - Clean up temporary database if needed.
- `get_character_ids(self)` - Get all Fighter character IDs for testing.
- `reset_resources(self, character_id)` - Reset all limited-use resources for testing.
- `setup_damaged_character(self, character_id, damage_amount)` - Damage a character for healing testing.
- `setup_database(self)` - Initialize database with full schema and Fighter test data.
- `create_fighter_test_db()` - Convenience function to create a Fighter test database.

## test - `tests/helpers/ui_test_helpers.py`

- `find_attack_buttons(action_panel)` - Find all weapon attack buttons in the action panel.
- `find_class_feature_buttons(action_panel)` - Find Fighter class feature buttons.
- `find_resource_buttons(action_panel)` - Find buttons that consume limited resources.
- `get_damage_roll_from_log(action_panel, attack_number: int=-1)` - Extract damage information from the most recent log entry.
- `simulate_combat_target_selection(action_panel, target_data: dict)` - Mock target selection for combat testing.
- `verify_resource_count_display(action_panel, feature_name: str, expected_current: int, expected_max: int)` - Verify resource count display shows correct values.
- `create_mock_character_data(character_id: str, level: int=1, class_id: str='fighter')` - Create mock character data for testing.
- `create_mock_target(ac: int=12, hp: int=10, name: str='Test Target')` - Create a mock combat target.
- `click_button_safe(button: QPushButton, wait_ms: int=50)` - Safely click a button with error handling.
- `count_enabled_buttons(buttons: List[QPushButton])` - Count how many buttons in a list are enabled.
- `drag_and_drop(source: QWidget, target: QWidget, source_pos: QPoint=None, target_pos: QPoint=None)` - Perform drag and drop operation between widgets.
- `enter_text_safe(line_edit: QLineEdit, text: str, clear_first: bool=True)` - Safely enter text into a line edit widget.
- `find_button_by_text(parent: QWidget, text: str, partial_match: bool=True)` - Find a button by its text content.
- `find_buttons_containing_text(parent: QWidget, text_fragments: List[str])` - Find all buttons containing any of the specified text fragments.
- `find_widget_by_object_name(parent: QWidget, object_name: str)` - Find a widget by its objectName property.
- `get_action_buttons_from_layout(parent: QWidget)` - Extract all action buttons from a layout.
- `get_label_text(parent: QWidget, object_name: str)` - Get text from a label widget by object name.
- `select_combobox_item(combo: QComboBox, text: str)` - Select an item in a combobox by text.
- `simulate_key_sequence(widget: QWidget, key_sequence: str)` - Simulate a key sequence on a widget.
- `trigger_context_menu_action(widget: QWidget, action_text: str)` - Trigger a context menu action on a widget.
- `verify_button_state(button: QPushButton, expected_enabled: bool, expected_text: str=None)` - Verify button state matches expectations.
- `verify_tooltip_contains(widget: QWidget, expected_text: str)` - Verify widget tooltip contains expected text.
- `wait_for_condition(condition: Callable[[], bool], timeout_ms: int=5000, check_interval_ms: int=100)` - Wait for a condition to become true within a timeout.
- `wait_for_ui_update(ms: int=100)` - Wait for UI to update and process events.

## test - `tests/integration/test_bag_of_holding_system.py`

- `_fetch_gold_rows(db_path: str, character_id: str)` - Inferred from name: fetch gold rows.
- `_give_bag_of_holding(db_path: str, character_id: str)` - Inferred from name: give bag of holding.
- `_insert_character(db_path: str)` - Inferred from name: insert character.
- `db_path(tmp_path)` - Create a fresh database and ensure schema upgrades run.
- `test_bag_capacity_redirects_excess_gold(db_path)` - Inferred from name: test bag capacity redirects excess gold.
- `test_gold_routes_to_bag_when_available(db_path)` - Inferred from name: test gold routes to bag when available.
- `test_inventory_sync_reports_bag_state_and_total_weight(db_path)` - Inferred from name: test inventory sync reports bag state and total weight.
- `test_rebalance_moves_existing_coin_into_bag(db_path)` - Inferred from name: test rebalance moves existing coin into bag.
- `test_schema_includes_bag_columns(db_path)` - Inferred from name: test schema includes bag columns.
- `test_treasure_exceeding_capacity_goes_to_inventory(db_path)` - Inferred from name: test treasure exceeding capacity goes to inventory.
- `test_treasure_generator_conversion_returns_tuple()` - Inferred from name: test treasure generator conversion returns tuple.

## test - `tests/integration/test_final_attack_morale.py`

- `test_final_attack_hit_and_miss()` - Test that final attack can hit or miss, with proper XP/loot distribution
- `test_group_morale_with_final_attack()` - Test morale with multiple enemies - some may be killed in final attack

## test - `tests/integration/test_morale_and_beast_loot.py`

- `test_beast_loot_drops()` - Test beast ration drops from wolves
- `test_mixed_combat()` - Test combat with both beasts and non-beasts
- `test_morale_system_with_goblins()` - Test morale system with multiple goblins

## test - `tests/integration/test_spell_effects_integration.py`

- `test_bless_attack_integration()` - Test that Bless bonus appears in attack rolls.
- `test_divine_favor_damage_integration()` - Test that Divine Favor adds radiant damage.
- `test_shield_of_faith_ac_integration()` - Test that Shield of Faith bonus appears in AC calculation.

## test - `tests/run_fighter_tests.py`

- `main()` - Main test execution function.
- `run_pytest_with_output(test_files, markers=None)` - Run pytest on specific test files and return results.

## test - `tests/run_regression_tests.py`

- `__init__(self, verbose=False)` - Inferred from name: init.
- `log(self, message, force=False)` - Log message with timestamp.
- `print_summary(self, total_duration, mode)` - Print test results summary.
- `run_command(self, cmd, cwd=None, description='')` - Run a command and capture results.
- `run_detailed_tests(self)` - Run detailed tests for additional features and edge cases.
- `run_full_tests(self)` - Run comprehensive test suite.
- `run_quick_tests(self)` - Run essential quick tests (< 30 seconds total).
- `run_tests(self, mode='quick')` - Run regression tests based on mode.
- `main()` - Main entry point.

## test - `tests/services/test_beast_loot_service.py`

- `setup_db()` - Setup test database
- `test_add_rations_to_inventory(setup_db)` - Test adding rations to character inventory
- `test_calculate_ration_drop(setup_db)` - Test ration quantity calculation
- `test_cr_to_treasure(setup_db)` - Test CR to individual treasure conversion
- `test_generate_beast_loot(setup_db)` - Test loot generation for beasts
- `test_get_monster_name(setup_db)` - Test getting monster name
- `test_is_beast(setup_db)` - Test beast detection
- `test_parse_cr(setup_db)` - Test CR parsing

## test - `tests/services/test_character_resources.py`

- `resource_db(tmp_path: Path)` - Inferred from name: resource db.
- `test_human_long_rest_grants_inspiration(resource_db: str)` - Inferred from name: test human long rest grants inspiration.
- `test_non_human_long_rest_does_not_grant_inspiration(resource_db: str)` - Inferred from name: test non human long rest does not grant inspiration.

## test - `tests/services/test_concentration_system.py`

- `setUp(self)` - Set up test database with minimal data.
- `tearDown(self)` - Clean up test database.
- `test_concentration_replaces_previous(self)` - Test that new concentration replaces previous concentration.
- `test_concentration_save_high_damage(self)` - Test concentration save with high damage.
- `test_concentration_save_success(self)` - Test successful concentration saving throw.
- `test_duration_parsing(self)` - Test spell duration parsing to rounds.
- `test_end_concentration_voluntary(self)` - Test voluntarily ending concentration.
- `test_get_all_concentrating_characters(self)` - Test getting all characters currently concentrating.
- `test_start_concentration_non_concentration_spell(self)` - Test trying to start concentration on a non-concentration spell.
- `test_start_concentration_success(self)` - Test successfully starting concentration on a spell.
- `test_update_concentration_duration(self)` - Test updating concentration duration during combat.

## test - `tests/services/test_condition_manager.py`

- `_create_test_schema(self)` - Create minimal schema for testing.
- `setUp(self)` - Create a test database and condition manager.
- `tearDown(self)` - Clean up test database.
- `test_add_simple_condition(self)` - Test adding a simple condition.
- `test_clear_all_conditions(self)` - Test clearing all conditions.
- `test_condition_caching(self)` - Test that condition caching works correctly.
- `test_condition_duration_tracking(self)` - Test duration countdown on turns.
- `test_condition_effects_lookup(self)` - Test looking up mechanical effects of conditions.
- `test_condition_immunity(self)` - Test condition immunity system.
- `test_condition_summary(self)` - Test readable condition summary.
- `test_condition_type_enum(self)` - Test that all D&D 2024 conditions are defined.
- `test_conditions_dont_stack(self)` - Test that conditions don't stack (except exhaustion).
- `test_exhaustion_death_at_level_6(self)` - Test exhaustion caps at level 6 (death).
- `test_exhaustion_stacking(self)` - Test that exhaustion levels stack.
- `test_incapacitating_conditions(self)` - Test detection of incapacitating conditions.
- `test_remove_condition_with_immunity(self)` - Test that gaining immunity removes existing condition.
- `test_save_ends_conditions(self)` - Test conditions that require saves.
- `test_unconscious_condition_effects(self)` - Test that unconscious has all correct nested conditions.
- `setUp(self)` - Set up for Danger Sense tests.
- `tearDown(self)` - Clean up.
- `test_danger_sense_blocked_by_incapacitated(self)` - Danger Sense should be blocked by incapacitated.
- `test_danger_sense_blocked_by_paralyzed(self)` - Danger Sense should be blocked by paralyzed (includes incapacitated).
- `test_danger_sense_not_blocked_by_frightened(self)` - Danger Sense should work when only frightened.
- `test_danger_sense_with_no_conditions(self)` - Danger Sense should work when not incapacitated.

## test - `tests/services/test_condition_stat_service.py`

- `_create_test_schema(self)` - Create minimal schema for testing.
- `setUp(self)` - Create a test database and services.
- `tearDown(self)` - Clean up test database.
- `test_ability_check_modifiers(self)` - Test ability check modifiers from conditions.
- `test_action_economy_restrictions(self)` - Test action economy restrictions from conditions.
- `test_attack_roll_modifiers(self)` - Test attack roll modifiers from conditions.
- `test_comprehensive_stat_modifiers(self)` - Test the comprehensive stat modifier function.
- `test_damage_resistances_and_immunities(self)` - Test damage resistance and immunity from conditions.
- `test_exhaustion_penalties(self)` - Test exhaustion level penalties across all systems.
- `test_movement_speed_modification(self)` - Test movement speed modifications from conditions.
- `test_saving_throw_modifiers(self)` - Test saving throw modifiers from conditions.

## test - `tests/services/test_fighter_champion.py`

- `_init_champion_schema(conn: sqlite3.Connection)` - Inferred from name: init champion schema.
- `temp_db_path(prefix: str)` - Inferred from name: temp db path.
- `test_combat_manager_applies_remarkable_athlete_to_initiative(monkeypatch)` - Inferred from name: test combat manager applies remarkable athlete to initiative.
- `test_heroic_warrior_awards_inspiration_and_sets_state()` - Inferred from name: test heroic warrior awards inspiration and sets state.
- `test_roll_skill_check_applies_remarkable_athlete(monkeypatch)` - Inferred from name: test roll skill check applies remarkable athlete.
- `test_survivor_heals_when_bloodied_and_tracks_defy_death()` - Inferred from name: test survivor heals when bloodied and tracks defy death.

## test - `tests/services/test_monster_ability_manager.py`

- `manager(test_db)` - Create a MonsterAbilityManager instance.
- `sample_character()` - Sample character data for testing saves.
- `test_condition_application(manager, sample_character)` - Test that failed saves apply conditions.
- `test_db()` - Create a temporary test database.
- `test_execute_ability_with_save(manager, sample_character)` - Test executing an ability that requires a saving throw.
- `test_execute_breath_weapon_damage(manager, sample_character)` - Test breath weapon execution with damage.
- `test_get_all_monster_abilities(manager)` - Test retrieving all abilities for a monster.
- `test_initialize_recharge_ability(manager)` - Test initializing a recharge ability like dragon breath.
- `test_limited_use_ability(manager)` - Test limited use ability like Aboleth's Dominate Mind (2/Day).
- `test_recharge_mechanics(manager)` - Test breath weapon recharge mechanics.
- `test_reset_daily_abilities(manager)` - Test resetting daily abilities on long rest.

## test - `tests/services/test_monster_attack_parser.py`

- `setUp(self)` - Set up database connection.
- `test_parse_database_monsters(self)` - Test parsing attacks from actual database monsters.
- `setUp(self)` - Set up test environment.
- `test_air_elemental_whirlwind(self)` - Test parsing Air Elemental's whirlwind with prone effect.
- `test_ankheg_bite_grapple(self)` - Test parsing Ankheg's bite with automatic grapple.
- `test_attack_summary(self)` - Test attack summary generation.
- `test_automatic_vs_save_distinction(self)` - Test that parser distinguishes automatic effects from save-based effects.
- `test_basilisk_bite_simple(self)` - Test parsing Basilisk's simple bite (no special effects).
- `test_charge_attack_with_save(self)` - Test parsing charge attacks that require saves to avoid prone.
- `test_complex_save_patterns(self)` - Test parsing various save patterns from real monster data.
- `test_condition_mapping(self)` - Test that condition names are mapped correctly.
- `test_damage_extraction_patterns(self)` - Test various damage format patterns.
- `test_ghast_claws_paralysis(self)` - Test parsing Ghast's claws with paralysis save.
- `test_giant_spider_bite(self)` - Test parsing Giant Spider's bite attack with poison save.
- `test_giant_spider_web(self)` - Test parsing Giant Spider's web attack with restrained condition.
- `test_multiattack_parsing(self)` - Test that multiattack entries are not parsed as attacks.
- `test_non_attack_actions_ignored(self)` - Test that non-attack actions are ignored.
- `test_parsing_errors_handled(self)` - Test that parsing errors are handled gracefully.
- `test_size_based_grapple(self)` - Test parsing size-based automatic grapple effects.
- `test_trample_attack_automatic_prone(self)` - Test parsing trample attacks that automatically knock prone.

## test - `tests/services/test_morale_manager.py`

- `setup_db()` - Setup test database
- `test_clear_encounter(setup_db)` - Test clearing encounter morale data
- `test_highest_wisdom_modifier(setup_db)` - Test getting highest WIS modifier from group
- `test_morale_check(setup_db)` - Test morale check rolling
- `test_morale_check_only_once(setup_db)` - Test that morale check only happens once
- `test_morale_trigger_group(setup_db)` - Test morale trigger for group (count-based)
- `test_morale_trigger_solo(setup_db)` - Test morale trigger for solo monster (HP-based)
- `test_track_combat_start(setup_db)` - Test initial morale tracking
- `test_wisdom_modifier(setup_db)` - Test Wisdom modifier calculation

## test - `tests/services/test_paladin_devotion.py`

- `_init_paladin_schema(conn: sqlite3.Connection)` - Inferred from name: init paladin schema.
- `temp_db_path(prefix: str)` - Inferred from name: temp db path.
- `test_channel_divinity()` - Test Channel Divinity usage.
- `test_devotion_oath_features()` - Test that Oath of Devotion features are properly applied.
- `test_divine_smite_calculation()` - Test Divine Smite damage calculation.
- `test_get_paladin_info()` - Test retrieving comprehensive paladin information.
- `test_half_caster_spell_progression()` - Test that paladins get appropriate spell slots as half-casters.
- `test_lay_on_hands()` - Test Lay on Hands healing feature.
- `test_lay_on_hands_empty_pool()` - Test Lay on Hands when pool is empty.
- `test_long_rest_recovery()` - Test long rest recovery for paladins.
- `test_paladin_initialization()` - Test basic paladin character initialization.

## test - `tests/services/test_ritual_casting.py`

- `setUp(self)` - Set up test database with minimal data.
- `tearDown(self)` - Clean up test database.
- `test_cannot_ritual_cast_non_ritual_spell(self)` - Test that non-ritual spells cannot be cast as rituals.
- `test_cast_ritual_spell_failure(self)` - Test failed ritual spell casting.
- `test_cast_ritual_spell_success(self)` - Test successful ritual spell casting.
- `test_cleric_can_ritual_cast_detect_magic(self)` - Test that cleric can ritual cast Detect Magic.
- `test_fighter_cannot_ritual_cast(self)` - Test that fighter cannot ritual cast.
- `test_get_ritual_spells_for_cleric(self)` - Test getting available ritual spells for cleric.
- `test_get_ritual_spells_for_wizard(self)` - Test getting available ritual spells for wizard.
- `test_ritual_casting_time_calculation(self)` - Test ritual casting time calculation.
- `test_wizard_can_ritual_cast_from_spellbook(self)` - Test that wizard can ritual cast spells from spellbook.

## test - `tests/services/test_rogue_abilities.py`

- `_create_test_database(self)` - Create minimal test database structure.
- `_create_test_rogue(self, level: int=1, character_id: str='test_rogue')` - Create a test rogue character.
- `setUp(self)` - Set up test database and service.
- `tearDown(self)` - Clean up test database.
- `test_calculate_sneak_attack_damage(self)` - Test Sneak Attack damage string calculation.
- `test_cunning_action(self)` - Test Cunning Action usage.
- `test_get_rogue_features(self)` - Test getting rogue features.
- `test_get_rogue_level(self)` - Test getting rogue level for characters.
- `test_reliable_talent(self)` - Test Reliable Talent application.
- `test_rest_rogue_resources(self)` - Test resource restoration on rest.
- `test_sneak_attack_dice_scaling(self)` - Test Sneak Attack dice scaling by level.
- `test_sneak_attack_eligibility(self)` - Test Sneak Attack eligibility checks.
- `test_steady_aim(self)` - Test Steady Aim usage.
- `test_stroke_of_luck(self)` - Test Stroke of Luck usage.
- `test_uncanny_dodge(self)` - Test Uncanny Dodge usage.
- `test_update_rogue_resources_for_level(self)` - Test resource updates for different levels.
- `test_weapon_eligibility_for_sneak_attack(self)` - Test weapon eligibility for Sneak Attack.

## test - `tests/services/test_warlock_fiend.py`

- `create_test_warlock(self, level=1, patron='Fiend')` - Helper to create a test warlock character.
- `setup_class(cls)` - Set up test database once for all tests.
- `setup_method(self)` - Clear character data before each test.
- `teardown_class(cls)` - Clean up test database.
- `test_can_cast_spell_with_pact_slot(self)` - Test checking if spell can be cast with pact slot.
- `test_dark_ones_own_luck(self)` - Test Dark One's Own Luck usage.
- `test_eldritch_invocations(self)` - Test learning and applying eldritch invocations.
- `test_eldritch_master(self)` - Test Eldritch Master feature at level 20.
- `test_fiend_level_progression(self)` - Test Fiend patron features at different levels.
- `test_fiend_patron_features(self)` - Test Fiend patron specific features.
- `test_fiendish_resilience(self)` - Test Fiendish Resilience damage type selection.
- `test_hurl_through_hell(self)` - Test Hurl Through Hell ability.
- `test_invocation_prerequisites(self)` - Test that invocations with prerequisites are properly filtered.
- `test_mystic_arcanum(self)` - Test Mystic Arcanum feature at high levels.
- `test_pact_boon_selection(self)` - Test selecting pact boons at level 3.
- `test_pact_magic_slots(self)` - Test pact magic slot progression.
- `test_pact_slot_usage_and_recovery(self)` - Test using and recovering pact slots.
- `test_spell_casting_integration(self)` - Test that Warlock integrates with spellcasting system.
- `test_warlock_initialization(self)` - Test basic Warlock initialization.

## test - `tests/services/test_weapon_attack_service.py`

- `_create_test_schema(self)` - Create minimal database schema for testing.
- `_insert_test_data(self)` - Insert test character data.
- `setUp(self)` - Set up test database and service.
- `tearDown(self)` - Clean up test database.
- `test_archery_attack_bonus(self)` - Test Archery fighting style attack bonus.
- `test_dueling_damage_bonus(self)` - Test Dueling fighting style damage bonus.
- `test_get_character_fighting_styles(self)` - Test retrieving character fighting styles.
- `test_great_weapon_fighting(self)` - Test Great Weapon Fighting style effects.
- `test_mastery_class_requires_mastery_property(self)` - Test that mastery classes require weapons to have mastery property.
- `test_non_mastery_class_no_errors(self)` - Test that non-mastery classes don't cause errors when weapons lack mastery.
- `test_parse_damage_dice(self)` - Test damage dice parsing.
- `test_parse_damage_dice_invalid_formats(self)` - Test that invalid damage dice formats raise ValueError.
- `test_savage_attacker_feat(self, mock_random)` - Test Savage Attacker feat application.
- `test_savage_attacker_first_roll_better(self, mock_random)` - Test Savage Attacker when first roll is better.
- `test_savage_attacker_not_first_attack(self)` - Test Savage Attacker doesn't apply if not first attack.
- `test_weapon_mastery_effects_cleave(self)` - Test Cleave weapon mastery effect.
- `test_weapon_mastery_effects_graze(self)` - Test Graze weapon mastery effect.
- `test_weapon_mastery_effects_topple(self)` - Test Topple weapon mastery save DC calculation.
- `test_weapon_mastery_unlimited_access(self)` - Test characters with unlimited weapon mastery access.

## test - `tests/services/test_wizard_evocation.py`

- `_init_wizard_schema(conn: sqlite3.Connection)` - Inferred from name: init wizard schema.
- `temp_db_path(prefix: str)` - Inferred from name: temp db path.
- `test_add_spell_to_spellbook()` - Test adding spells to wizard spellbook.
- `test_arcane_recovery_already_used()` - Test Arcane Recovery when already used.
- `test_arcane_recovery_basic()` - Test basic Arcane Recovery functionality.
- `test_arcane_recovery_higher_level()` - Test Arcane Recovery at higher levels with mixed slot usage.
- `test_evocation_subclass_features()` - Test that Evocation school features are properly applied.
- `test_get_wizard_info()` - Test retrieving comprehensive wizard information.
- `test_long_rest_recovery()` - Test long rest recovery for wizards.
- `test_wizard_initialization()` - Test basic wizard character initialization.
- `test_wizard_spell_preparation_limit()` - Test that wizard spell preparation respects Intelligence modifier + level.

## test - `tests/spells/test_buff_spells.py`

- `_create_test_database(cls)` - Inferred from name: create test database.
- `setUp(self)` - Inferred from name: setUp.
- `setUpClass(cls)` - Inferred from name: setUpClass.
- `tearDownClass(cls)` - Inferred from name: tearDownClass.
- `test_aid_healing(self)` - Inferred from name: test aid healing.
- `test_aid_hp_increase(self)` - Inferred from name: test aid hp increase.
- `test_bless_attack_save_bonus(self)` - Inferred from name: test bless attack save bonus.
- `test_concentration_breaks_previous_spell(self)` - Inferred from name: test concentration breaks previous spell.
- `test_divine_favor_damage_bonus(self)` - Inferred from name: test divine favor damage bonus.
- `test_multiple_buffs_stack(self)` - Inferred from name: test multiple buffs stack.
- `test_shield_of_faith_applies_buff(self)` - Inferred from name: test shield of faith applies buff.
- `test_shield_of_faith_concentration(self)` - Inferred from name: test shield of faith concentration.

## test - `tests/spells/test_healing_spells.py`

- `_create_test_database(cls)` - Inferred from name: create test database.
- `setUp(self)` - Inferred from name: setUp.
- `setUpClass(cls)` - Inferred from name: setUpClass.
- `tearDownClass(cls)` - Inferred from name: tearDownClass.
- `test_cure_wounds_healing_cap(self)` - Inferred from name: test cure wounds healing cap.
- `test_cure_wounds_healing_range(self)` - Inferred from name: test cure wounds healing range.
- `test_cure_wounds_level_1(self)` - Inferred from name: test cure wounds level 1.
- `test_cure_wounds_level_2(self)` - Inferred from name: test cure wounds level 2.
- `test_cure_wounds_level_3(self)` - Inferred from name: test cure wounds level 3.
- `test_prayer_of_healing_level_2(self)` - Inferred from name: test prayer of healing level 2.
- `test_prayer_of_healing_level_3(self)` - Inferred from name: test prayer of healing level 3.
- `test_prayer_of_healing_level_5(self)` - Inferred from name: test prayer of healing level 5.

## test - `tests/test_action_economy_enforcement.py`

- `test_action_economy_logic()` - Test the logic for action economy enforcement.
- `test_action_mapping()` - Test that actions are properly mapped to economy types.

## test - `tests/test_action_registry.py`

- `_create_test_character(self, character_id='test_char', class_name='barbarian', level=1, subclass='berserker')` - Create a test character
- `_setup_test_database(self)` - Setup minimal database schema for testing
- `setup_method(self)` - Setup test database and registry
- `teardown_method(self)` - Cleanup test database
- `test_action_definition_completeness(self)` - Test that action definitions have required fields
- `test_action_registration(self)` - Test registering and retrieving actions
- `test_barbarian_actions_registered(self)` - Test that all barbarian actions are registered
- `test_character_actions(self)` - Test getting actions for a specific character
- `test_class_actions_by_level(self)` - Test getting class actions filtered by level
- `test_combat_state_prerequisites(self)` - Test combat state prerequisite checking
- `test_economy_type_mapping(self)` - Test that actions have correct economy types
- `test_prerequisite_validation(self)` - Test prerequisite validation system
- `test_resource_checking(self)` - Test resource availability checking
- `test_subclass_actions(self)` - Test getting subclass-specific actions
- `test_trigger_types(self)` - Test that automatic triggers are properly set
- `test_action_registry()` - Test registry in isolation as specified in roadmap

## test - `tests/test_action_tracking.py`

- `setup_method(self)` - Setup test action economy
- `test_action_logging(self)` - Test that actions are properly logged
- `test_class_action_tracking(self)` - Test tracking of class-specific actions
- `test_duration_management(self)` - Test effect duration tracking and expiration
- `test_existing_economy_still_works(self)` - Test that existing action economy functionality is preserved
- `test_parallel_tracking(self)` - Test that class action tracking works alongside basic action economy
- `test_resource_consumption_tracking(self)` - Test resource consumption tracking across multiple actions
- `test_action_tracking()` - Main test function as specified in roadmap

## test - `tests/test_action_validation.py`

- `_create_test_character(self, character_id='test_char', class_name='barbarian', level=1, subclass='berserker', rage_uses=2)` - Create a test character
- `_setup_test_database(self)` - Setup minimal database schema for testing
- `setup_method(self)` - Setup test database and validator
- `teardown_method(self)` - Cleanup test database
- `test_action_availability_calculator(self)` - Test getting availability for all character actions
- `test_action_economy_blocking(self)` - Test validation respects action economy
- `test_detailed_feedback_system(self)` - Test the feedback system provides user-friendly messages
- `test_level_prerequisite_failure(self)` - Test validation fails appropriately for level requirements
- `test_resource_shortage_detection(self)` - Test validation detects resource shortages
- `test_user_friendly_messages(self)` - Test that error messages are user-friendly
- `test_valid_action_validation(self)` - Test validation of valid actions
- `test_warning_logs_without_blocking(self)` - Test that warnings are logged but actions aren't blocked
- `test_action_validation()` - Main test function as specified in roadmap

## test - `tests/test_alt_encounters.py`

- `controlled_choice(options)` - Inferred from name: controlled choice.
- `test_generate_skill_challenge_resource_swap_text()` - Inferred from name: test generate skill challenge resource swap text.
- `test_generate_skill_challenge_structure()` - Inferred from name: test generate skill challenge structure.

## test - `tests/test_barbarian_level_progression.py`

- `_calculate_brutal_critical_dice(level)` - Calculate brutal critical extra dice by level
- `_calculate_rage_uses(level)` - Calculate rage uses per long rest by level
- `_create_barbarian_character(db_path, character_id, level)` - Create a Barbarian character at the specified level
- `_setup_test_database(db_path)` - Setup minimal database schema for testing
- `_test_level_features(db_path, character_id, level)` - Test features available at specific level
- `test_barbarian_level_progression()` - Test Barbarian progression from level 1 to 20

## test - `tests/test_bis_loot_system.py`

- `clean_test_character(character_id)` - Inferred from name: clean test character.
- `create_test_character(class_name, strength=15, dexterity=10, constitution=14)` - Inferred from name: create test character.
- `test_bis_drops()` - Inferred from name: test bis drops.

## test - `tests/test_campaign_frame_simple.py`

- `test_campaign_frame()` - Inferred from name: test campaign frame.

## test - `tests/test_character_creation.py`

- `__init__(self)` - Inferred from name: init.
- `run(self)` - Run the test application
- `__init__(self)` - Inferred from name: init.
- `_setup_ui(self)` - Setup test interface
- `clear_results(self)` - Clear test results
- `log_test(self, test_name: str, success: bool, message: str='', error: Exception=None)` - Log test result
- `test_character_creation_mode(self)` - Test 3: Specifically test character creation mode activation
- `test_encounter_panel(self)` - Test 2: Create encounter panel with dummy data
- `test_full_creation_flow(self)` - Test 4: Full character creation flow
- `test_imports(self)` - Test 1: Basic imports

## test - `tests/test_character_creation_automated.py`

- `log_test(test_name: str, success: bool, message: str='', error: Exception=None)` - Log test result
- `run_automated_tests()` - Run all character creation tests automatically

## test - `tests/test_character_creation_fixed.py`

- `test_character_creation_fix()` - Inferred from name: test character creation fix.

## test - `tests/test_class_filtering.py`

- `test_class_filtering()` - Inferred from name: test class filtering.

## test - `tests/test_class_filtering_final.py`

- `test_class_filtering_final()` - Inferred from name: test class filtering final.

## test - `tests/test_cleric_life.py`

- `setUp(self)` - Set up test database with full schema.
- `tearDown(self)` - Clean up test database.
- `test_blessed_healer_bonus(self)` - Test Blessed Healer self-healing.
- `test_channel_divinity_initialization(self)` - Test Channel Divinity options are set up correctly.
- `test_channel_divinity_usage(self)` - Test using Channel Divinity abilities.
- `test_cleric_info_retrieval(self)` - Test getting complete cleric information.
- `test_cleric_initialization(self)` - Test basic cleric initialization.
- `test_disciple_of_life_bonus(self)` - Test Disciple of Life healing bonus calculation.
- `test_life_domain_spells(self)` - Test Life Domain spells are added correctly.
- `test_resource_restoration(self)` - Test cleric resource restoration on rest.
- `test_spell_slot_progression(self)` - Test cleric spell slot progression.
- `test_subclass_registry_integration(self)` - Test Life Domain is properly registered in subclass system.

## test - `tests/test_combat_log_parser.py`

- `setup_method(self)` - Inferred from name: setup method.
- `test_parse_attack_critical(self)` - Inferred from name: test parse attack critical.
- `test_parse_attack_hit_basic(self)` - Inferred from name: test parse attack hit basic.
- `test_parse_attack_miss(self)` - Inferred from name: test parse attack miss.
- `test_parse_attack_no_damage(self)` - Inferred from name: test parse attack no damage.
- `test_parse_attack_no_explicit_result(self)` - Inferred from name: test parse attack no explicit result.
- `test_parse_attack_with_weapon(self)` - Inferred from name: test parse attack with weapon.
- `test_parse_combat_round(self)` - Inferred from name: test parse combat round.
- `test_parse_condition_event(self)` - Inferred from name: test parse condition event.
- `test_parse_damage_event(self)` - Inferred from name: test parse damage event.
- `test_parse_death_event(self)` - Inferred from name: test parse death event.
- `test_parse_empty_log(self)` - Inferred from name: test parse empty log.
- `test_parse_event_auto_detect_attack(self)` - Inferred from name: test parse event auto detect attack.
- `test_parse_event_auto_detect_death(self)` - Inferred from name: test parse event auto detect death.
- `test_parse_event_auto_detect_healing(self)` - Inferred from name: test parse event auto detect healing.
- `test_parse_healing_event(self)` - Inferred from name: test parse healing event.
- `test_parse_none_log(self)` - Inferred from name: test parse none log.
- `test_parse_unparseable_log(self)` - Inferred from name: test parse unparseable log.

## test - `tests/test_condition_integration.py`

- `check_danger_sense_enhanced(character_id)` - Enhanced Danger Sense that checks for incapacitating conditions.
- `test_condition_system_standalone()` - Test that condition system works independently.
- `test_danger_sense_integration_prep()` - Test that we're ready for Danger Sense integration.

## test - `tests/test_cunning_strike_end_to_end.py`

- `_create_goblin(self, goblin_id: str='goblin1')` - Create test goblin target
- `_create_rogue(self, level: int=5, rogue_id: str='rogue1', dex: int=18)` - Create test rogue
- `_setup_test_database(self)` - Setup complete database schema
- `_store_cunning_strike_selection(self, character_id: str, effects: list)` - Store Cunning Strike selection
- `setup_method(self)` - Setup test database with full schema
- `teardown_method(self)` - Cleanup
- `test_knock_out_strike_high_cost(self)` - Test Knock Out Strike with 6d6 cost
- `test_multiple_effects_level_11(self)` - Test using 2 Cunning Strike effects at level 11+
- `test_poison_strike_requires_kit(self)` - Test Poison Strike requires Poisoner's Kit
- `test_trip_strike_combat_flow(self)` - Test Trip Strike: Select -> Attack -> Save -> Apply Prone
- `main()` - Run all end-to-end tests

## test - `tests/test_cunning_strike_integration.py`

- `_create_test_rogue(self, level: int=5, character_id: str='test_rogue', dexterity: int=18)` - Create a test rogue character
- `_setup_test_database(self)` - Setup minimal database schema
- `setup_method(self)` - Setup test database
- `teardown_method(self)` - Cleanup test database
- `test_apply_cunning_strike(self)` - Test applying Cunning Strike effects
- `test_available_options_level_14(self)` - Test available Cunning Strike options at level 14
- `test_available_options_level_5(self)` - Test available Cunning Strike options at level 5
- `test_can_use_multiple_effects_level_10(self)` - Test that level 10 rogue cannot use multiple effects
- `test_can_use_multiple_effects_level_11(self)` - Test that level 11+ rogue CAN use multiple effects
- `test_damage_calculation_high_cost(self)` - Test damage calculation with high-cost Devious Strike
- `test_damage_calculation_multiple_effects(self)` - Test damage calculation with multiple Cunning Strike effects
- `test_damage_calculation_single_effect(self)` - Test damage calculation with single Cunning Strike effect
- `test_poisoners_kit_requirement(self)` - Test Poison Strike requires Poisoner's Kit
- `test_preview_generation(self)` - Test Cunning Strike preview generation
- `test_save_dc_calculation(self)` - Test Cunning Strike save DC calculation (8 + DEX + prof)
- `test_sneak_attack_eligibility_non_finesse_weapon(self)` - Test Sneak Attack not eligible with non-finesse weapon
- `test_sneak_attack_eligibility_with_advantage(self)` - Test Sneak Attack eligibility with advantage
- `test_sneak_attack_eligibility_with_disadvantage(self)` - Test Sneak Attack NOT eligible with disadvantage
- `test_validation_allows_multiple_effects_level_11(self)` - Test validation allows multiple effects for level 11 rogue
- `test_validation_too_many_effects_level_5(self)` - Test validation rejects multiple effects for level 5 rogue
- `main()` - Run all integration tests

## test - `tests/test_danger_sense_integration.py`

- `test_backwards_compatibility()` - Test that existing code still works unchanged.
- `test_danger_sense_integration()` - Test that enhanced Danger Sense works with condition system.

## test - `tests/test_divine_smite_simple.py`

- `main()` - Run all simple tests.
- `test_critical_hit_indication()` - Test that critical hits are properly indicated in dialog.
- `test_hp_threshold_logic()` - Test the logic for when to show the smite dialog.
- `test_smite_damage_calculation()` - Test that smite damage is calculated correctly.

## test - `tests/test_dynamic_feature_system.py`

- `_setup_test_database(self)` - Setup test database with minimal schema and data
- `setUp(self)` - Inferred from name: setUp.
- `tearDown(self)` - Inferred from name: tearDown.
- `test_feature_progression_summary(self)` - Test getting feature progression summary
- `test_get_character_features(self)` - Test retrieving character features
- `test_grant_class_features_level_1(self)` - Test granting level 1 rogue features
- `test_grant_class_features_level_2(self)` - Test granting level 2 rogue features
- `test_grant_subclass_features(self)` - Test granting thief subclass features at level 3
- `test_level_up_integration(self)` - Test complete level up process
- `test_level_up_preview(self)` - Test level up preview functionality
- `test_subclass_selection_detection(self)` - Test detecting subclass selection level

## test - `tests/test_dynamic_system_validation.py`

- `test_dynamic_feature_system()` - Test the dynamic feature system with existing database

## test - `tests/test_encounter_avoidance.py`

- `__init__(self)` - Inferred from name: init.
- `run_all_tests(self)` - Inferred from name: run all tests.
- `setup_test_character(self)` - Get a test character from the database.
- `test_avoidance_attempt_simulation(self)` - Inferred from name: test avoidance attempt simulation.
- `test_avoidance_eligibility(self)` - Inferred from name: test avoidance eligibility.
- `test_encounter_difficulty(self)` - Inferred from name: test encounter difficulty.
- `test_multiple_avoidance_attempts(self)` - Inferred from name: test multiple avoidance attempts.
- `test_stealth_vs_perception(self)` - Inferred from name: test stealth vs perception.
- `test_xp_calculation(self)` - Inferred from name: test xp calculation.

## test - `tests/test_encounter_panel_debug.py`

- `test_encounter_panel_debug()` - Inferred from name: test encounter panel debug.

## test - `tests/test_fighter_comprehensive.py`

- `__init__(self)` - Inferred from name: init.
- `_generate_recommendations(self)` - Generate recommendations based on test results.
- `_print_summary(self)` - Print validation summary.
- `_run_test_class(self, test_class, db_path)` - Run all tests in a test class and return results.
- `_validate_action_surge(self)` - Validate Action Surge mechanics.
- `_validate_champion_features(self)` - Validate Champion subclass features.
- `_validate_fighting_styles(self)` - Validate all Fighting Style effects.
- `_validate_indomitable(self)` - Validate Indomitable mechanics.
- `_validate_performance(self)` - Validate performance characteristics.
- `_validate_second_wind(self)` - Validate Second Wind mechanics.
- `_validate_ui_integration(self)` - Validate UI integration for Fighter features.
- `_validate_weapon_mastery(self)` - Validate weapon mastery mechanics.
- `save_report(self, filename: str='fighter_validation_report.json')` - Save detailed report to file.
- `validate_all_features(self)` - Run comprehensive validation of all Fighter features.
- `main()` - Main test runner function.
- `run_manual_feature_tests()` - Run specific manual tests for features that are hard to automate.

## test - `tests/test_fighter_validation_demo.py`

- `demonstrate_testing_capabilities()` - Demonstrate the comprehensive testing capabilities.
- `show_usage_examples()` - Show examples of how to use the testing framework.
- `test_framework_setup()` - Test that the testing framework is properly set up.

## test - `tests/test_full_action_economy.py`

- `_create_test_character(self, character_id='test_char', class_name='barbarian', level=20, subclass='berserker')` - Create a test character
- `_setup_test_database(self)` - Setup minimal database schema for testing
- `setup_method(self)` - Setup test database and enforcer
- `teardown_method(self)` - Cleanup test database
- `test_action_blocking_for_invalid_attempts(self)` - Test that invalid actions are blocked
- `test_available_actions_list(self)` - Test getting list of available actions
- `test_can_execute_action_check(self)` - Test non-destructive action checking
- `test_cannot_use_two_bonus_actions(self)` - Verify can't use two bonus actions
- `test_full_combat_with_all_rules_enforced(self)` - Full combat with all rules enforced
- `test_rage_consumes_bonus_action(self)` - Test Rage consumes bonus action
- `test_reaction_usage_and_reset(self)` - Check reaction usage and reset
- `test_resource_consumption(self)` - Validate resource consumption
- `test_full_action_economy()` - Main test function as specified in roadmap

## test - `tests/test_galahad_smite.py`

- `test_galahad_smite()` - Inferred from name: test galahad smite.

## test - `tests/test_level_1_paladin_fix.py`

- `main()` - Run all level 1 paladin tests.
- `test_divine_smite_availability()` - Test that level 1 paladins can potentially use Divine Smite (have spell slots).
- `test_level_1_paladin_spell_selection()` - Test that level 1 paladins can select 2 prepared spells during creation.
- `test_level_1_paladin_spell_slots()` - Test that level 1 paladins get 2 first-level spell slots (D&D 2024).

## test - `tests/test_log_narration_pipeline.py`

- `__init__(self)` - Inferred from name: init.
- `synthesize(self, text, output_path: Path, voice_profile, *, style_overrides=None)` - Inferred from name: synthesize.
- `test_log_narration_event_from_payload()` - Inferred from name: test log narration event from payload.
- `test_narration_formatter_adds_details()` - Inferred from name: test narration formatter adds details.
- `test_pipeline_process_entries_sync(tmp_path: Path)` - Inferred from name: test pipeline process entries sync.

## test - `tests/test_lucky_halo.py`

- `__init__(self)` - Inferred from name: init.
- `load_test_character_with_resources(self)` - Load a character with Lucky and Inspiration resources.
- `run_all_tests(self)` - Run all tests and report results.
- `setup(self)` - Setup the test environment.
- `test_halo_appearance(self)` - Test that halos appear when hovering over action cards.
- `test_halo_click(self)` - Test clicking the halo to use resources.
- `test_resource_priority(self)` - Test that Inspiration shows before Lucky.
- `main()` - Main test entry point.

## test - `tests/test_monster_distribution.py`

- `setUp(self)` - Set up test fixtures
- `test_alignment_filtering(self)` - Test monster alignment filtering based on campaign frame rules
- `test_campaign_frame_serialization(self)` - Test that campaign frames can be serialized to/from JSON
- `test_cr_filtering(self)` - Test that monsters are filtered correctly by CR relative to party level
- `test_difficulty_distribution(self)` - Test that encounters are generated according to difficulty distribution
- `test_edge_cases(self)` - Test edge cases and error conditions
- `test_encounter_xp_accuracy(self)` - Test that encounter XP calculations are accurate
- `test_high_difficulty_encounter_structure(self)` - Test that high difficulty encounters follow single strong monster pattern
- `test_low_moderate_encounter_structure(self)` - Test that low/moderate encounters can have multiple monsters
- `test_monster_database_loading(self)` - Test that monsters are loaded correctly from database
- `test_monster_hp_calculation(self)` - Test monster HP rolling and average HP usage
- `test_monster_type_distribution(self)` - Test that monster types follow campaign frame weights over many encounters
- `test_random_bag_system(self)` - Test that RandomBag ensures variety in monster selection
- `test_xp_budget_calculation(self)` - Test XP budget calculations for different levels and difficulties
- `setUp(self)` - Set up integration test fixtures
- `test_full_campaign_simulation(self)` - Simulate a full campaign to test monster distribution over time
- `run_monster_distribution_tests()` - Run all monster distribution tests

## test - `tests/test_new_fighter_features.py`

- `create_champion(self, db_path: str, level: int)` - Inferred from name: create champion.
- `db_path(self, tmp_path)` - Inferred from name: db path.
- `test_defy_death_18_19_20_count_as_20(self, db_path)` - Defy Death: rolls of 18-20 count as nat 20
- `test_defy_death_grants_advantage(self, db_path)` - Defy Death grants advantage on death saves
- `test_level_17_no_defy_death(self, db_path)` - Level 17 Champion doesn't have Defy Death yet
- `test_level_18_has_defy_death(self, db_path)` - Level 18 Champion has Defy Death
- `test_no_defy_death_normal_roll(self, db_path)` - Without Defy Death, death save is normal
- `create_champion(self, db_path: str, level: int, strength: int=16)` - Inferred from name: create champion.
- `db_path(self, tmp_path)` - Inferred from name: db path.
- `test_jump_bonus_scales_with_strength(self, db_path)` - Jump bonus equals STR modifier
- `test_level_2_no_jump_bonus(self, db_path)` - Level 2 Champion doesn't have Remarkable Athlete yet
- `test_level_3_has_jump_bonus(self, db_path)` - Level 3 Champion gets jump distance bonus

## test - `tests/test_paladin_comprehensive.py`

- `__init__(self)` - Inferred from name: init.
- `cleanup(self)` - Clean up test environment.
- `create_test_character(self, level=1)` - Create a test paladin character.
- `print_summary(self)` - Print test results summary.
- `run_all_tests(self)` - Run all paladin tests.
- `run_test(self, test_name, test_function)` - Run a single test and record results.
- `setup(self)` - Set up test environment with temporary database.
- `test_channel_divinity_uses(self)` - Test Channel Divinity use calculation.
- `test_database_tables_exist(self)` - Test that required database tables exist.
- `test_divine_smite_calculation(self)` - Test Divine Smite damage calculation.
- `test_divine_smite_vs_undead(self)` - Test Divine Smite bonus damage vs undead/fiends.
- `test_lay_on_hands_calculation(self)` - Test Lay on Hands pool calculation.
- `test_oath_spells_added(self)` - Test that oath spells are properly added.
- `test_paladin_character_creation(self)` - Test creating a paladin character.
- `test_paladin_class_exists(self)` - Test if paladin class is defined in database.
- `test_paladin_info_retrieval(self)` - Test getting comprehensive paladin information.
- `test_paladin_initialization(self)` - Test paladin character initialization.
- `test_paladin_service_creation(self)` - Test paladin service can be created.
- `test_paladin_spell_preparation(self)` - Test paladin spell preparation calculation.
- `main()` - Run the paladin test suite.

## test - `tests/test_paladin_comprehensive_regression.py`

- `__init__(self)` - Inferred from name: init.
- `create_test_paladin_full(self, character_id: str, level: int, subclass: str='devotion')` - Create a complete test paladin with all required fields.
- `print_comprehensive_summary(self)` - Print comprehensive test results with feature coverage.
- `run_all_tests(self)` - Run the complete paladin regression test suite.
- `run_test(self, test_name: str, test_function, feature_category: str=None)` - Run a single test and record results.
- `setup(self)` - Set up comprehensive test environment.
- `test_action_panel_integration(self)` - Test action panel integration for paladin abilities.
- `test_cross_feature_interactions(self)` - Test interactions between different paladin features.
- `test_divine_smite_scaling(self)` - Test Divine Smite damage scaling.
- `test_level_10_aura_of_courage(self)` - Test level 10 Aura of Courage.
- `test_level_18_aura_expansion(self)` - Test level 18 aura range expansion.
- `test_level_1_basic_features(self)` - Test level 1 paladin features (Lay on Hands, Spellcasting, Weapon Mastery).
- `test_level_3_oath_features(self)` - Test level 3 paladin features (Channel Divinity, Sacred Oath).
- `test_level_6_aura_of_protection(self)` - Test level 6 Aura of Protection.
- `test_oath_variations(self)` - Test different sacred oath implementations.
- `test_resource_management(self)` - Test resource management (Lay on Hands pool, Channel Divinity uses).
- `test_ui_components(self)` - Test all UI components can be created.
- `main()` - Run the comprehensive paladin regression test suite.

## test - `tests/test_paladin_simple.py`

- `run_all_tests()` - Run all simple paladin tests.
- `test_action_cards_exist()` - Test if paladin action card files exist.
- `test_devotion_subclass()` - Test if Devotion subclass exists.
- `test_divine_smite_calculation()` - Test Divine Smite damage calculation without database.
- `test_divine_smite_dialog()` - Test if Divine Smite dialog can be imported.
- `test_divine_smite_vs_undead()` - Test Divine Smite bonus damage vs undead/fiends.
- `test_paladin_class_exists()` - Test if paladin class is defined in database.
- `test_paladin_service_import()` - Test paladin service can be imported.
- `test_paladin_tables_needed()` - Test what paladin-specific tables exist.

## test - `tests/test_paladin_subclasses.py`

- `test_subclass_features()` - Inferred from name: test subclass features.

## test - `tests/test_parlay_system.py`

- `__init__(self)` - Inferred from name: init.
- `run_all_tests(self)` - Inferred from name: run all tests.
- `setup_test_character(self)` - Get a test character from the database.
- `test_encounter_parlay_check(self)` - Inferred from name: test encounter parlay check.
- `test_evil_monster_parlay(self)` - Inferred from name: test evil monster parlay.
- `test_good_monster_parlay(self)` - Inferred from name: test good monster parlay.
- `test_neutral_monster_parlay(self)` - Inferred from name: test neutral monster parlay.
- `test_parlay_skills(self)` - Inferred from name: test parlay skills.
- `test_xp_calculation(self)` - Inferred from name: test xp calculation.

## test - `tests/test_potion_priority.py`

- `test_potion_priority()` - Test that the best healing potion is selected correctly.

## test - `tests/test_rage_resistance.py`

- `_map_action_to_economy_type(self, action_type: ActionType)` - Copy of the mapping method for testing.
- `test_action_economy_integration()` - Test that rage action economy integration works.
- `test_rage_resistance_calculations()` - Test the mathematics of rage damage resistance.

## test - `tests/test_rage_state_tracking.py`

- `test_damage_type_mapping()` - Test damage type recognition.
- `test_rage_state_conditions()` - Test the conditions for applying rage resistance.

## test - `tests/test_rest_system.py`

- `__init__(self)` - Inferred from name: init.
- `cleanup_test_character(self)` - Inferred from name: cleanup test character.
- `run_all_tests(self)` - Inferred from name: run all tests.
- `setup_test_character(self)` - Inferred from name: setup test character.
- `test_no_rations_scenario(self)` - Inferred from name: test no rations scenario.
- `test_ration_check(self)` - Inferred from name: test ration check.
- `test_ration_consumption(self)` - Inferred from name: test ration consumption.

## test - `tests/test_results_summary.py`

- `run_tests_and_summarize()` - Run tests and provide summary.

## test - `tests/test_rogue_expertise_progression.py`

- `_create_rogue(self, level: int)` - Create a rogue character at specified level
- `_setup_test_database(self)` - Setup minimal database schema
- `setup_method(self)` - Setup test database
- `teardown_method(self)` - Cleanup test database
- `test_expertise_bonus_calculation(self)` - Test expertise doubles proficiency bonus
- `test_expertise_feature_granted_level_1(self)` - Test Expertise feature is granted at level 1
- `test_expertise_feature_upgraded_level_6(self)` - Test Expertise feature is upgraded at level 6
- `test_expertise_skills_increase_at_level_6(self)` - Test expertise skills increase to 4 at level 6
- `test_expertise_skills_stored_in_proficiencies(self)` - Test expertise skills are stored in character_proficiencies
- `test_level_up_service_grants_expertise(self)` - Test LevelUpService grants Expertise properly
- `test_proficiency_system_integration(self)` - Test proficiency system retrieves expertise correctly
- `test_rogue_features_table_expertise_count(self)` - Test rogue_features table tracks expertise count
- `main()` - Run all tests

## test - `tests/test_rogue_level_progression.py`

- `__init__(self)` - Inferred from name: init.
- `run_full_test(self)` - Run complete level progression test.
- `setup(self)` - Create test database and character.
- `test_level(self, level: int)` - Test a specific level progression.
- `verify_level_features(self, level: int, result: Dict[str, Any])` - Verify expected features for a given level.

## test - `tests/test_rogue_subclass_selection.py`

- `test_rogue_subclass_selection()` - Test that level 3 rogues can choose between Thief and Assassin subclasses.

## test - `tests/test_rogue_ui_action_cards.py`

- `_calculate_sneak_attack_dice(self, level: int)` - Calculate sneak attack dice based on level
- `_create_test_rogue(self, level: int=1, character_id: str='test_rogue')` - Create a test rogue character
- `_get_character_context(self, character_id: str)` - Build character context dict
- `_setup_test_database(self)` - Setup minimal database schema for testing
- `setup_method(self)` - Setup test database
- `teardown_method(self)` - Cleanup test database
- `test_card_disappears_when_used(self)` - Test that Stroke of Luck card disappears after use
- `test_card_generation_all_levels(self)` - Test card generation for all key levels
- `test_cunning_action_cards_level_2(self)` - Test Cunning Action cards appear at level 2
- `test_cunning_action_usage_simulation(self)` - Test simulating Cunning Action usage
- `test_cunning_strike_cards_level_5(self)` - Test Cunning Strike cards appear at level 5
- `test_devious_strikes_cards_level_14(self)` - Test Devious Strikes cards appear at level 14
- `test_steady_aim_card_level_3(self)` - Test Steady Aim card appears at level 3
- `test_steady_aim_usage_simulation(self)` - Test simulating Steady Aim usage
- `test_stroke_of_luck_card_level_20(self)` - Test Stroke of Luck card appears at level 20
- `test_stroke_of_luck_usage_simulation(self)` - Test simulating Stroke of Luck usage
- `test_uncanny_dodge_card_level_5(self)` - Test Uncanny Dodge card appears at level 5
- `test_uncanny_dodge_usage_simulation(self)` - Test simulating Uncanny Dodge usage
- `main()` - Run all tests

## test - `tests/test_rogue_ui_choice_cards.py`

- `_calculate_sneak_attack_dice(self, level: int)` - Calculate sneak attack dice based on level
- `_create_test_rogue(self, level: int=1, character_id: str='test_rogue')` - Create a test rogue character
- `_setup_test_database(self)` - Setup minimal database schema for testing
- `setup_method(self)` - Setup test database
- `teardown_method(self)` - Cleanup test database
- `test_card_cost_display_clarity(self)` - Test all Rogue cards clearly show action/resource costs
- `test_card_disabled_state_visual_feedback(self)` - Test disabled cards have clear visual distinction
- `test_cunning_action_choice_between_options(self)` - Test Cunning Action presents 3 distinct choices
- `test_cunning_strike_choice_availability(self)` - Test Cunning Strike cards show choice-based costs
- `test_cunning_strike_damage_calculation_preview(self)` - Test Cunning Strike cards show damage reduction preview
- `test_cunning_strike_disabled_without_sneak_attack(self)` - Test Cunning Strike cards are disabled when Sneak Attack is not available
- `test_cunning_strike_multiple_choices_level_11(self)` - Test level 11+ allows choosing TWO Cunning Strike effects
- `test_cunning_strike_poisoner_kit_requirement(self)` - Test Poison Strike requires Poisoner's Kit in inventory
- `test_devious_strikes_high_cost_choices(self)` - Test Devious Strikes show high die costs clearly
- `test_expertise_skill_selection_ui(self)` - Test Expertise selection at character creation and level 6
- `test_multiple_effect_stacking_ui_level_11(self)` - Test UI for selecting multiple Cunning Strike effects (level 11+)
- `test_reaction_timing_window_ui(self)` - Test UI for reaction-based cards (Uncanny Dodge, Stroke of Luck)
- `test_steady_aim_choice_vs_movement(self)` - Test Steady Aim card shows tradeoff clearly
- `test_stroke_of_luck_failed_roll_trigger(self)` - Test Stroke of Luck card appears after failed d20 roll
- `test_uncanny_dodge_choice_to_use(self)` - Test player can CHOOSE whether to use Uncanny Dodge
- `test_uncanny_dodge_reaction_timing(self)` - Test Uncanny Dodge card appears during enemy attack
- `main()` - Run all tests

## test - `tests/test_rogue_validation.py`

- `main()` - Run all validation tests.
- `test_action_types_defined()` - Test that Rogue action types are defined.
- `test_feature_definitions()` - Test that Rogue feature definitions are complete.
- `test_rogue_service_import()` - Test that the RogueAbilitiesService can be imported.
- `test_sneak_attack_dice_calculation()` - Test Sneak Attack dice calculation logic.
- `test_weapon_attack_service_integration()` - Test that WeaponAttackService includes Sneak Attack integration.
- `test_weapon_eligibility()` - Test weapon eligibility for Sneak Attack.

## test - `tests/test_scalable_subclass_architecture.py`

- `test_enhanced_manager_with_registry()` - Test that EnhancedSubclassManager works with the registry.
- `test_feature_type_compatibility()` - Test that different subclasses use feature types correctly.
- `test_registry_availability()` - Test registry availability queries.
- `test_registry_loads_berserker()` - Test that the registry can load the existing Berserker.
- `test_registry_loads_champion()` - Test that the registry can load the new Champion.

## test - `tests/test_shop_integration.py`

- `__init__(self)` - Inferred from name: init.
- `run_all_tests(self)` - Inferred from name: run all tests.
- `test_shop_interface_signature(self)` - Test that ShopInterface can be instantiated with correct parameters
- `test_shop_size_enum_values(self)` - Test that all ShopSize enum values work
- `test_vendor_encounter_compatibility(self)` - Test that vendor encounter can create ShopInterface

## test - `tests/test_shop_system.py`

- `__init__(self)` - Inferred from name: init.
- `run_all_tests(self)` - Inferred from name: run all tests.
- `test_fractional_currency(self)` - Inferred from name: test fractional currency.
- `test_large_shop_inventory(self)` - Inferred from name: test large shop inventory.
- `test_low_cost_items(self)` - Inferred from name: test low cost items.
- `test_medium_shop_inventory(self)` - Inferred from name: test medium shop inventory.
- `test_shop_markup(self)` - Inferred from name: test shop markup.
- `test_shop_sorting(self)` - Inferred from name: test shop sorting.
- `test_small_shop_inventory(self)` - Inferred from name: test small shop inventory.

## test - `tests/test_simple.py`

- `test_character_creation()` - Inferred from name: test character creation.

## test - `tests/test_simple_validation.py`

- `main()` - Inferred from name: main.

## test - `tests/test_skill_challenge_system.py`

- `cleanup_test_data()` - Clean up test data from database.
- `main()` - Run all skill challenge system tests.
- `test_reward_system()` - Test reward and penalty application.
- `test_skill_attempt()` - Test making skill attempts.
- `test_skill_challenge_database()` - Test that skill challenge templates are loaded from database.
- `test_skill_challenge_session()` - Test creating and managing a skill challenge session.

## test - `tests/test_skill_rewards.py`

- `__init__(self)` - Inferred from name: init.
- `get_inventory_count(self, item_name: str)` - Get quantity of an item in test character inventory.
- `run_all_tests(self)` - Inferred from name: run all tests.
- `setup_test_character(self)` - Create a test character in the database.
- `test_consumable_reward(self)` - Inferred from name: test consumable reward.
- `test_healing_potion_reward(self)` - Inferred from name: test healing potion reward.
- `test_item_reward(self)` - Inferred from name: test item reward.
- `test_rations_reward(self)` - Inferred from name: test rations reward.

## test - `tests/test_skilled_feat.py`

- `setUp(self)` - Inferred from name: setUp.
- `tearDown(self)` - Inferred from name: tearDown.
- `test_skilled_feat_adds_three_skills(self)` - Inferred from name: test skilled feat adds three skills.
- `test_skilled_feat_can_be_taken_multiple_times(self)` - Inferred from name: test skilled feat can be taken multiple times.
- `test_skilled_feat_can_be_taken_twice_at_same_level(self)` - Inferred from name: test skilled feat can be taken twice at same level.
- `test_skilled_feat_excludes_existing_proficiencies(self)` - Inferred from name: test skilled feat excludes existing proficiencies.

## test - `tests/test_sneak_attack_debug.py`

- `mock_get_context_weapon_properties(context)` - Inferred from name: mock get context weapon properties.
- `mock_has_class_feature(feature_name)` - Inferred from name: mock has class feature.
- `test_sneak_attack_debug()` - Debug sneak attack with various advantage states.

## test - `tests/test_social_interactions.py`

- `__init__(self)` - Inferred from name: init.
- `_get_inventory_count(self, item_name: str)` - Get quantity of an item in inventory.
- `run_all_tests(self)` - Inferred from name: run all tests.
- `setup(self)` - Setup test character.
- `test_encounter_resolution_options(self)` - Test that encounters offer multiple resolution paths.
- `test_parlay_encounter_flow(self)` - Test complete parlay encounter flow.
- `test_skill_challenge_system_integration(self)` - Test skill challenge system integration with rewards.
- `test_skill_rewards_integration(self)` - Test that skill challenges properly reward items.
- `test_stealth_avoidance_flow(self)` - Test complete stealth avoidance flow.
- `test_xp_reward_balance(self)` - Test that different resolution methods have balanced XP rewards.

## test - `tests/test_spell_action_cards.py`

- `main()` - Run all tests.
- `test_spell_action_cards_creation()` - Test that spell action cards are created for spellcasting characters.
- `test_spell_actions_consume_action_economy()` - Ensure spell action types integrate with action economy tracking.
- `test_spell_casting_context()` - Test that spell data is passed correctly in action context.
- `test_spell_icon_generation()` - Test that spell icons are generated correctly.

## test - `tests/test_spell_cards_qt6.py`

- `test_spell_action_cards()` - Test that spell action cards appear for Nathlas.

## test - `tests/test_spell_data_phase1.py`

- `main()` - Inferred from name: main.
- `test_cantrip_counts()` - Test that all classes have sufficient cantrips for character creation
- `test_essential_spells()` - Test that critical spells exist for each class
- `test_level1_spell_counts()` - Test that all classes have sufficient level 1 spells
- `test_total_spell_count()` - Test overall spell counts

## test - `tests/test_spell_registry.py`

- `setUp(self)` - Set up test database.
- `tearDown(self)` - Clean up test database.
- `test_clear_cache(self)` - Test clearing the spell cache.
- `test_get_available_classes(self)` - Test getting all classes that have spells.
- `test_get_nonexistent_spell(self)` - Test retrieving a spell that doesn't exist.
- `test_get_ritual_spells(self)` - Test retrieving ritual spells.
- `test_get_ritual_spells_by_class(self)` - Test retrieving ritual spells for a specific class.
- `test_get_spell_by_id(self)` - Test retrieving a spell by ID.
- `test_get_spell_count_by_class(self)` - Test getting spell counts by level for a class.
- `test_get_spells_by_class(self)` - Test retrieving spells by class.
- `test_get_spells_by_class_and_level(self)` - Test retrieving spells by class and level.
- `test_search_spells_by_level(self)` - Test searching spells by level.
- `test_search_spells_by_name(self)` - Test searching spells by name.
- `test_search_spells_by_school(self)` - Test searching spells by school.
- `test_search_spells_concentration_only(self)` - Test searching for concentration spells only.
- `test_search_spells_ritual_only(self)` - Test searching for ritual spells only.
- `test_spell_caching(self)` - Test that spells are cached properly.

## test - `tests/test_spell_saving_simple.py`

- `main()` - Inferred from name: main.
- `test_existing_character_spell_data()` - Inferred from name: test existing character spell data.
- `test_spell_data_available()` - Inferred from name: test spell data available.
- `test_spell_saving_logic_exists()` - Inferred from name: test spell saving logic exists.
- `test_spell_table_structure()` - Inferred from name: test spell table structure.

## test - `tests/test_spell_selection_integration.py`

- `main()` - Inferred from name: main.
- `test_cleric_character_creation_no_spells()` - Inferred from name: test cleric character creation no spells.
- `test_warlock_character_creation_with_spells()` - Inferred from name: test warlock character creation with spells.
- `test_wizard_character_creation_with_spells()` - Inferred from name: test wizard character creation with spells.

## test - `tests/test_spell_selection_ui.py`

- `main()` - Inferred from name: main.
- `test_cleric_selection()` - Inferred from name: test cleric selection.
- `test_fighter_no_selection()` - Inferred from name: test fighter no selection.
- `test_paladin_selection()` - Inferred from name: test paladin selection.
- `test_spell_data_availability()` - Inferred from name: test spell data availability.
- `test_warlock_selection()` - Inferred from name: test warlock selection.
- `test_wizard_selection()` - Inferred from name: test wizard selection.

## test - `tests/test_spell_slots_qt6.py`

- `test_spell_slots()` - Test spell slot availability.

## test - `tests/test_spellcasting_service.py`

- `setUp(self)` - Set up test database with minimal schema.
- `tearDown(self)` - Clean up test database.
- `test_concentration_mechanics(self)` - Test concentration spell mechanics.
- `test_initialize_cleric_spellcasting(self)` - Test initializing spellcasting for a cleric.
- `test_initialize_warlock_spellcasting(self)` - Test initializing spellcasting for a warlock.
- `test_initialize_wizard_spellcasting(self)` - Test initializing spellcasting for a wizard.
- `test_spell_slot_restoration(self)` - Test spell slot restoration on rest.
- `test_spell_slot_usage(self)` - Test using and restoring spell slots.
- `test_spell_validation(self)` - Test spell casting validation.
- `test_upcasting(self)` - Test casting spells at higher levels.
- `test_warlock_pact_magic_restoration(self)` - Test warlock pact magic slot restoration on short rest.

## test - `tests/test_stage_1_3_ui.py`

- `log_callback(message)` - Inferred from name: log callback.
- `test_condition_badge_creation()` - Test creating individual condition badges.
- `test_condition_display_widget()` - Test the full condition display widget.
- `test_condition_logging()` - Test the condition logging system.
- `test_integration_with_existing_system()` - Test that our condition system doesn't break existing functionality.

## test - `tests/test_stage_1_4_integration.py`

- `test_action_economy_restrictions()` - Test that conditions properly block actions.
- `test_condition_advantage_integration()` - Test that conditions properly integrate with advantage system.
- `test_condition_movement_restrictions()` - Test movement speed modifications from conditions.
- `test_danger_sense_full_integration()` - Test Danger Sense with full condition system integration.
- `test_exhaustion_comprehensive()` - Test comprehensive exhaustion effects across all systems.
- `test_saving_throw_integration()` - Test saving throw modifications from conditions.

## test - `tests/test_stage_2_1_subclass_definitions.py`

- `test_berserker_definition()` - Test the Berserker subclass definition.
- `test_enhanced_subclass_manager()` - Test the enhanced subclass manager.
- `test_feature_type_handlers()` - Test different feature type handling.
- `test_subclass_feature_creation()` - Test creating individual subclass features.

## test - `tests/test_stage_2_2_berserker_migration.py`

- `test_berserker_legacy_compatibility()` - Test that new system doesn't break existing Berserker functionality.
- `test_frenzy_damage_mechanics()` - Test Frenzy damage bonus mechanics.
- `test_intimidating_presence_mechanics()` - Test Intimidating Presence mechanics.
- `test_mindless_rage_integration()` - Test Mindless Rage with condition immunity system.
- `test_retaliation_mechanics()` - Test Retaliation reaction mechanics.

## test - `tests/test_stage_2_3_ui_integration.py`

- `mock_handler(feature_name, character_id)` - Inferred from name: mock handler.
- `test_character_panel_integration()` - Test integration with character panel (mock-based).
- `test_feature_availability_logic()` - Test the feature availability checking logic.
- `test_feature_tooltips_and_styling()` - Test feature tooltips and visual styling information.
- `test_subclass_features_widget_backend()` - Test the backend functionality of SubclassFeaturesWidget.
- `test_ui_widget_creation()` - Test UI widget creation (if PyQt6 available).

## test - `tests/test_stage_2_4_feature_activation.py`

- `test_action_card_integration()` - Test integration with action card system.
- `test_berserker_feature_activation()` - Test Berserker feature activation through action cards.
- `test_champion_feature_activation()` - Test Champion feature activation through automatic triggers.
- `test_resource_tracking_integration()` - Test resource tracking across the feature activation system.

## test - `tests/test_stealth_mechanics.py`

- `add_equipment(self, db_path: str, character_id: str, item_data: Dict[str, Any])` - Add equipment to a character.
- `create_test_character(self, db_path: str, character_data: Dict[str, Any])` - Create a test character in the database.
- `setup_database(self, tmp_path)` - Create a test database with necessary schema.
- `test_assassin_features(self, setup_database)` - Test Assassin subclass features when attacking from hidden.
- `test_encounter_stealth_check(self, setup_database)` - Test full encounter stealth check with multiple monsters.
- `test_hidden_attack_bonuses(self, setup_database)` - Test attack bonuses when attacking from hidden.
- `test_monster_perception_check(self, setup_database)` - Test monster perception checks against stealth DC.
- `test_stealth_with_elven_cloak(self, setup_database)` - Test stealth with advantage from Elven Cloak.
- `test_stealth_with_heavy_armor(self, setup_database)` - Test stealth with disadvantage from heavy armor.
- `test_stealth_with_proficiency(self, setup_database)` - Test that character with stealth proficiency can attempt to hide.
- `test_stealth_without_proficiency(self, setup_database)` - Test that character without stealth proficiency cannot hide.

## test - `tests/test_tab_styling.py`

- `get_tab_availability(status)` - Inferred from name: get tab availability.
- `test_css_generation()` - Test that CSS is generated correctly.
- `test_tab_availability_logic()` - Test the logic for determining tab availability.

## test - `tests/test_tactical_master.py`

- `create_fighter(self, db_path: str, level: int)` - Create test fighter
- `db_path(self, tmp_path)` - Create test database
- `test_level_20_has_tactical_master(self, db_path)` - Level 20 Fighter can use Tactical Master
- `test_level_8_no_tactical_master(self, db_path)` - Level 8 Fighter cannot use Tactical Master
- `test_level_9_has_tactical_master(self, db_path)` - Level 9 Fighter can use Tactical Master
- `test_mastery_original_choice(self, db_path)` - Can choose to use original mastery
- `test_mastery_override_push(self, db_path)` - Can override mastery with Push
- `test_mastery_override_sap(self, db_path)` - Can override mastery with Sap
- `test_mastery_override_slow(self, db_path)` - Can override mastery with Slow
- `test_non_fighter_cannot_use_tactical_master(self, db_path)` - Non-Fighter cannot use Tactical Master
- `test_tactical_master_per_attack_flexibility(self, db_path)` - Tactical Master can be different on each attack
- `test_tactical_master_with_already_push_mastery(self, db_path)` - Can swap even if weapon already has Push

## test - `tests/test_tactical_shift.py`

- `create_fighter(self, db_path: str, level: int)` - Create test fighter
- `db_path(self, tmp_path)` - Create test database
- `test_level_20_tactical_shift(self, db_path)` - Level 20: Tactical Shift still works
- `test_level_4_no_tactical_shift(self, db_path)` - Level 4: Second Wind does not grant Tactical Shift
- `test_level_5_tactical_shift_activates(self, db_path)` - Level 5: Second Wind grants Tactical Shift movement
- `test_non_fighter_no_tactical_shift(self, db_path)` - Non-Fighter with Second Wind does not get Tactical Shift
- `test_tactical_shift_half_speed(self, db_path)` - Tactical Shift grants half speed movement
- `test_tactical_shift_stored_in_combat_state(self, db_path)` - Tactical Shift movement is stored in combat state

## test - `tests/test_ui_action_cards.py`

- `_create_test_character(self, character_id='test_char', class_name='barbarian', level=1, subclass='berserker', rage_uses=2)` - Create a test character
- `_setup_test_database(self)` - Setup minimal database schema for testing
- `setup_method(self)` - Setup test database and generator
- `teardown_method(self)` - Cleanup test database
- `test_action_card_generation(self)` - Test generating action cards from registry
- `test_disabled_states_with_reasons(self)` - Test disabled card states with detailed reasons
- `test_economy_state_awareness(self)` - Test that cards reflect action economy state
- `test_enhanced_description(self)` - Test enhanced descriptions with cost and availability info
- `test_grouped_by_economy_type(self)` - Test grouping cards by economy type
- `test_legacy_integration(self)` - Test integration with legacy ActionCard system
- `test_resource_cost_display(self)` - Test that resource costs are displayed correctly
- `test_resource_summary(self)` - Test resource summary generation
- `test_warning_badges(self)` - Test warning badge system
- `test_ui_action_cards()` - Main test function as specified in roadmap

## test - `tests/test_unified_class_abilities.py`

- `setup_test_database()` - Inferred from name: setup test database.
- `test_barbarian_rage_unified()` - Inferred from name: test barbarian rage unified.
- `test_fighter_second_wind_unified()` - Inferred from name: test fighter second wind unified.
- `test_unified_service_coverage()` - Inferred from name: test unified service coverage.

## test - `tests/test_unified_feature_system.py`

- `test_unified_feature_system()` - Test the new unified feature system with all 11 classes

## test - `tests/test_vendor_system.py`

- `_setup_test_database(cls)` - Inferred from name: setup test database.
- `setUp(self)` - Inferred from name: setUp.
- `setUpClass(cls)` - Inferred from name: setUpClass.
- `tearDownClass(cls)` - Inferred from name: tearDownClass.
- `test_calculate_ability_modifier(self)` - Inferred from name: test calculate ability modifier.
- `test_calculate_proficiency_bonus(self)` - Inferred from name: test calculate proficiency bonus.
- `test_calculate_sell_price_with_character(self)` - Inferred from name: test calculate sell price with character.
- `test_generate_hex_shop_inventory_pricing(self)` - Inferred from name: test generate hex shop inventory pricing.
- `test_generate_hex_shop_inventory_structure(self)` - Inferred from name: test generate hex shop inventory structure.
- `test_generate_hex_shop_inventory_with_crafter(self)` - Inferred from name: test generate hex shop inventory with crafter.
- `test_get_charisma_skill_roll_no_proficiency(self)` - Inferred from name: test get charisma skill roll no proficiency.
- `test_get_charisma_skill_roll_with_proficiency(self)` - Inferred from name: test get charisma skill roll with proficiency.
- `test_get_hex_settlement_method(self)` - Inferred from name: test get hex settlement method.
- `test_has_crafter_feat(self)` - Inferred from name: test has crafter feat.
- `test_settlement_generation_distribution(self)` - Inferred from name: test settlement generation distribution.
- `test_settlement_generation_in_hex(self)` - Inferred from name: test settlement generation in hex.
- `test_settlement_persistence(self)` - Inferred from name: test settlement persistence.
- `test_settlement_to_shop_size_mapping(self)` - Inferred from name: test settlement to shop size mapping.

## test - `tests/testing_framework_character_creation.py`

- `__init__(self, framework: UIAutomationFramework)` - Inferred from name: init.
- `_finalize_character(self, name: str)` - Set character name and complete creation.
- `_handle_class_features(self, char_class: CharacterClass)` - Handle class-specific feature selection.
- `_handle_equipment(self)` - Handle equipment selection.
- `_handle_rogue_features(self)` - Handle Rogue-specific features.
- `_handle_spell_selection(self, char_class: CharacterClass)` - Handle spell selection for spellcasting classes.
- `_navigate_to_character_creation(self)` - Navigate to character creation interface.
- `_select_background_and_species(self)` - Select background and species.
- `_select_cantrips(self, recommended_cantrips: List[str], required_count: int)` - Select cantrips from available options.
- `_select_class(self, char_class: CharacterClass)` - Select character class.
- `_select_class_from_buttons(self, class_name: str)` - Select class from buttons.
- `_select_class_from_combo(self, class_name: str)` - Select class from combo box.
- `_select_class_from_list(self, class_name: str)` - Select class from QListWidget.
- `_select_fighting_style(self)` - Select fighting style for Fighter.
- `_select_from_list_or_combo(self, option_name: str, context_keywords: List[str])` - Select an option from list widget or combo box based on context.
- `_select_level1_spells(self, recommended_spells: List[str], required_count: int)` - Select level 1 spells.
- `_select_warlock_invocation(self)` - Select invocation for Warlock.
- `_set_ability_scores(self, char_class: CharacterClass)` - Set ability scores appropriate for the class.
- `_verify_character_created(self, name: str)` - Verify character was created in database.
- `create_complete_character(self, char_class: CharacterClass, name: str)` - Create a complete character with all steps.
- `__init__(self, framework: UIAutomationFramework)` - Inferred from name: init.
- `_find_spell_selection_ui(self)` - Check if spell selection UI elements are present.
- `validate_spell_selection_ui(self, char_class: CharacterClass)` - Validate that spell selection UI appears for spellcasting classes.
- `main()` - Main entry point for character creation testing.

## test - `tests/testing_framework_combat_interactions.py`

- `__init__(self, framework: UIAutomationFramework)` - Inferred from name: init.
- `_check_concentration_indicator(self)` - Check if concentration indicator is shown.
- `_enter_combat_mode(self, character_id: str)` - Enter combat mode with the specified character.
- `_find_action_cards_by_type(self, action_type: str)` - Find action cards of a specific type.
- `_find_class_feature_cards(self)` - Find class feature action cards.
- `_find_concentration_spell_cards(self)` - Find spell cards that require concentration.
- `_find_spell_action_cards(self)` - Find spell action cards.
- `_find_weapon_attack_cards(self)` - Find weapon attack action cards.
- `_get_recent_combat_log(self)` - Get recent entries from combat log.
- `_get_spell_slot_counts(self)` - Get current spell slot counts.
- `_is_cantrip_card(self, card: QPushButton)` - Check if a card represents a cantrip.
- `_verify_slot_consumption(self, initial: Dict, final: Dict)` - Verify that a spell slot was consumed.
- `test_action_economy_enforcement(self, character_id: str)` - Test that action economy is properly enforced.
- `test_class_features(self, character_id: str)` - Test class feature activation.
- `test_concentration_mechanics(self, character_id: str)` - Test concentration spell mechanics.
- `test_spell_casting_in_combat(self, character_id: str)` - Test spell casting mechanics during combat.
- `test_weapon_attacks(self, character_id: str)` - Test weapon attack mechanics.
- `__init__(self, framework: UIAutomationFramework)` - Inferred from name: init.
- `create_combat_scenario(self, scenario: CombatScenario)` - Create and run a specific combat scenario.
- `run_all_combat_tests(self, character_id: str)` - Run all combat tests for a character.
- `main()` - Main entry point for combat testing.

## test - `tests/testing_framework_master.py`

- `__init__(self)` - Inferred from name: init.
- `_get_test_character_with_spells(self)` - Get a character ID that has spells for testing.
- `cleanup(self)` - Clean up testing environment.
- `generate_comprehensive_report(self, results: List[TestResult])` - Generate a comprehensive test report.
- `quick_spell_test(self, character_id: Optional[str]=None)` - Run a quick spell action card validation.
- `run_character_creation_tests(self, spellcasters_only: bool=False)` - Run character creation tests.
- `run_combat_interaction_tests(self, character_id: Optional[str]=None)` - Run combat interaction tests.
- `run_full_test_suite(self)` - Run the complete test suite.
- `run_spell_action_card_tests(self, character_id: Optional[str]=None)` - Run comprehensive spell action card tests.
- `setup(self)` - Initialize the testing environment.
- `setup_test_data_and_run(self)` - Set up test data and run comprehensive tests.
- `main()` - Main entry point for the testing framework.

## test - `tests/testing_framework_spell_actions.py`

- `__init__(self, framework: UIAutomationFramework)` - Inferred from name: init.
- `_enter_encounter_mode(self)` - Enter encounter mode to see action cards.
- `_find_all_action_cards(self)` - Find all action cards in the action panel.
- `_find_card_for_spell(self, spell: Dict, cards: List[QWidget])` - Find the action card for a specific spell.
- `_find_spell_cards_by_level(self, level: int)` - Find spell cards for a specific spell level.
- `_get_character_spell_slots(self, character_id: str)` - Get character's current spell slots.
- `_get_character_spells(self, character_id: str)` - Get character's spells from database.
- `_is_spell_card(self, card: QWidget)` - Check if an action card is a spell card.
- `_looks_like_action_card(self, widget: QWidget)` - Check if a widget looks like an action card.
- `_navigate_to_character(self, character_id: str)` - Navigate to and load a specific character.
- `test_cantrip_unlimited_casting(self, character_id: str)` - Test that cantrips can be cast unlimited times.
- `test_spell_card_generation(self, character_id: str)` - Test that spell cards are generated correctly for a character.
- `test_spell_slot_consumption(self, character_id: str)` - Test that casting spells consumes spell slots correctly.
- `__init__(self)` - Inferred from name: init.
- `cleanup_test_characters(self)` - Remove test characters from database.
- `create_test_wizard_with_spells(self, name: str='TestWizardSpells')` - Create a test wizard character with known spells.
- `main()` - Main entry point for spell action testing.

## test - `tests/testing_framework_ui_automation.py`

- `__init__(self, framework: UIAutomationFramework)` - Inferred from name: init.
- `_complete_character_creation(self, name: str)` - Complete the character creation process.
- `_select_class(self, class_name: str)` - Select a character class.
- `_select_wizard_spells(self)` - Select spells for a wizard character.
- `_start_character_creation(self)` - Start character creation process.
- `create_test_wizard(self, name: str='TestWizard')` - Create a test wizard character with spells.
- `__init__(self, framework: UIAutomationFramework)` - Inferred from name: init.
- `_check_spell_cast_feedback(self)` - Check if spell casting produced expected feedback.
- `_find_spell_action_cards(self)` - Find spell action cards in the UI.
- `_load_character(self, character_id: str)` - Load a specific character.
- `_start_test_encounter(self)` - Start a test encounter to see action cards.
- `test_spell_cards_appear(self, character_id: str)` - Test that spell action cards appear for a spellcasting character.
- `test_spell_casting(self, character_id: str)` - Test actually casting a spell from action cards.
- `__init__(self)` - Inferred from name: init.
- `_generate_html_report(self)` - Generate HTML test report.
- `_get_test_character_with_spells(self)` - Get a character ID that has spells for testing.
- `cleanup(self)` - Clean up testing environment.
- `generate_report(self)` - Generate and save a test report.
- `run_character_creation_tests(self)` - Run character creation tests.
- `run_spell_action_card_tests(self)` - Run spell action card tests.
- `setup(self)` - Initialize the testing environment.
- `__init__(self, app: QApplication, main_window: MainWindow)` - Inferred from name: init.
- `_ensure_widget_visible(self, widget: QWidget)` - Ensure a widget is visible by scrolling its parent scroll area if needed.
- `check_checkbox(self, checkbox: QCheckBox, checked: bool=True)` - Check or uncheck a checkbox.
- `click_widget(self, widget: QWidget)` - Click a widget if it's clickable.
- `find_widget_by_object_name(self, object_name: str)` - Find a widget by its objectName.
- `find_widget_by_text(self, text: str, widget_type=None)` - Find a widget by its text content.
- `set_combo_box_value(self, combo_box: QComboBox, text: str)` - Set a combo box to a specific value.
- `set_spinbox_value(self, spinbox: QSpinBox, value: int)` - Set a spinbox to a specific value.
- `take_screenshot(self, name: str)` - Take a screenshot of the main window.
- `wait_for_widget(self, widget_finder, timeout_ms: int=5000)` - Wait for a widget to become available.
- `main()` - Main entry point for testing framework.

## test - `tests/ui/test_action_panel_integration.py`

- `__init__(self, db_path)` - Inferred from name: init.
- `_force_reload_character(self)` - Mock character reload.
- `show_message(self, title, message)` - Mock message display.
- `test_improved_critical_range(self, action_panel)` - Test Champion's improved critical hit range (19-20).
- `test_dueling_damage_bonus_application(self, action_panel)` - Test Dueling fighting style adds +2 damage to one-handed weapons.
- `test_great_weapon_fighting_reroll_mechanics(self, action_panel)` - Test Great Weapon Fighting treats 1s and 2s as 3s per D&D 2024.
- `test_action_surge_activation_and_cooldown(self, action_panel)` - Test Action Surge usage and short rest recovery.
- `test_indomitable_save_reroll(self, action_panel)` - Test Indomitable save reroll functionality.
- `test_second_wind_activation_and_recovery(self, action_panel)` - Test Second Wind usage and short rest recovery.
- `test_tactical_master_substitution_at_level_9(self, action_panel)` - Test Tactical Master property substitution for level 9+ Fighters.
- `test_weapon_mastery_tooltip_display(self, action_panel)` - Test that weapon mastery tooltips show correct properties.
- `action_panel(qapp, temp_db, fighter_characters)` - Create ActionPanel with mocked main window.
- `fighter_characters(temp_db)` - Create Fighter characters at various levels for testing.
- `qapp()` - Create QApplication instance.
- `temp_db()` - Create temporary database with full Fighter test data.
- `test_ui_interaction_helpers()` - Test helper functions for UI interactions work correctly.

## test - `tests/ui/test_rest_restrictions.py`

- `__init__(self, id, encounter_id, monster_id, monster_name, max_hit_points, current_hit_points, armor_class, initiative)` - Inferred from name: init.
- `is_alive(self)` - Inferred from name: is alive.
- `__init__(self)` - Inferred from name: init.
- `add_message(self, message)` - Inferred from name: add message.
- `clear(self)` - Inferred from name: clear.
- `contains(self, text)` - Inferred from name: contains.
- `log_combat(self, message)` - Inferred from name: log combat.
- `__init__(self, db_path)` - Inferred from name: init.
- `_force_reload_character(self)` - Inferred from name: force reload character.
- `show_message(self, title, message)` - Inferred from name: show message.
- `test_rest_blocked_with_active_hazard(self, action_panel_with_encounter)` - Test that rest is blocked when hazards are active.
- `test_long_rest_blocked_without_rations(self, action_panel_with_encounter)` - Test that long rest is blocked when character has no rations.
- `test_long_rest_consumes_ration(self, action_panel_with_encounter)` - Test that long rest consumes one ration.
- `test_rest_allowed_after_monsters_defeated(self, action_panel_with_encounter)` - Test that rest is allowed after all monsters are dead.
- `test_rest_blocked_with_active_monster(self, action_panel_with_encounter)` - Test that rest button is blocked when monsters are alive.
- `test_rest_blocked_with_multiple_monsters(self, action_panel_with_encounter)` - Test that rest is blocked when at least one monster is alive.
- `test_short_rest_does_not_consume_rations(self, action_panel_with_encounter)` - Test that short rest does NOT consume rations.
- `action_panel_with_encounter(qapp, temp_db, test_character)` - Create ActionPanel with mocked encounter panel for testing.
- `qapp()` - Create QApplication instance.
- `temp_db()` - Create temporary database with full schema and seed data.
- `test_character(temp_db)` - Get an existing test character and add rations.
- `test_monsters_present_detection()` - Unit test for _monsters_present() method.

## test - `tests/unit/test_spell_effect_display.py`

- `_create_test_database(cls)` - Inferred from name: create test database.
- `setUpClass(cls)` - Inferred from name: setUpClass.
- `tearDownClass(cls)` - Inferred from name: tearDownClass.
- `test_condition_widget_displays_spell_effects(self)` - Inferred from name: test condition widget displays spell effects.
- `test_condition_widget_initialization(self)` - Inferred from name: test condition widget initialization.
- `test_condition_widget_no_effects(self)` - Inferred from name: test condition widget no effects.
- `test_spell_effect_badge_bless(self)` - Inferred from name: test spell effect badge bless.
- `test_spell_effect_badge_creation(self)` - Inferred from name: test spell effect badge creation.
- `test_spell_effect_badge_divine_favor(self)` - Inferred from name: test spell effect badge divine favor.

## test - `tests/unit/test_spell_effects_service.py`

- `_create_test_database(cls)` - Inferred from name: create test database.
- `setUp(self)` - Inferred from name: setUp.
- `setUpClass(cls)` - Inferred from name: setUpClass.
- `tearDownClass(cls)` - Inferred from name: tearDownClass.
- `test_apply_buff(self)` - Inferred from name: test apply buff.
- `test_apply_damage(self)` - Inferred from name: test apply damage.
- `test_apply_damage_overflow_temp_hp(self)` - Inferred from name: test apply damage overflow temp hp.
- `test_apply_damage_with_temp_hp(self)` - Inferred from name: test apply damage with temp hp.
- `test_apply_healing(self)` - Inferred from name: test apply healing.
- `test_apply_healing_max_cap(self)` - Inferred from name: test apply healing max cap.
- `test_apply_temp_hp(self)` - Inferred from name: test apply temp hp.
- `test_apply_temp_hp_higher_value_wins(self)` - Inferred from name: test apply temp hp higher value wins.
- `test_clear_temp_hp(self)` - Inferred from name: test clear temp hp.
- `test_decrement_effect_durations(self)` - Inferred from name: test decrement effect durations.
- `test_get_ac_modifier(self)` - Inferred from name: test get ac modifier.
- `test_get_active_buffs(self)` - Inferred from name: test get active buffs.
- `test_get_active_buffs_filtered(self)` - Inferred from name: test get active buffs filtered.
- `test_get_attack_bonus(self)` - Inferred from name: test get attack bonus.
- `test_get_buff(self)` - Inferred from name: test get buff.
- `test_get_set_temp_hp(self)` - Inferred from name: test get set temp hp.
- `test_has_buff(self)` - Inferred from name: test has buff.
- `test_remove_all_buffs(self)` - Inferred from name: test remove all buffs.
- `test_remove_buff(self)` - Inferred from name: test remove buff.

## test - `tests/unit/test_spell_handler_registry.py`

- `execute(self, caster_id, targets, slot_level, context)` - Inferred from name: execute.
- `_create_test_database(cls)` - Inferred from name: create test database.
- `setUp(self)` - Inferred from name: setUp.
- `setUpClass(cls)` - Inferred from name: setUpClass.
- `tearDownClass(cls)` - Inferred from name: tearDownClass.
- `test_execute_spell(self)` - Inferred from name: test execute spell.
- `test_execute_spell_not_registered(self)` - Inferred from name: test execute spell not registered.
- `test_get_handler_not_registered(self)` - Inferred from name: test get handler not registered.
- `test_handler_get_ability_mod(self)` - Inferred from name: test handler get ability mod.
- `test_handler_get_spell_save_dc(self)` - Inferred from name: test handler get spell save dc.
- `test_register_handler(self)` - Inferred from name: test register handler.

## test - `tests/validate_action_types.py`

- `_map_action_to_economy_type(self, action_type: ActionType)` - Copy of the mapping method for testing.
- `test_action_economy_mapping()` - Test that action economy mapping works without errors.
- `validate_action_types()` - Validate that all ActionType references exist in the enum.

## unsure - `add_categories.py`

- `add_category_comment(filepath, category)` - Inferred from name: add category comment.
- `main()` - Inferred from name: main.

## unsure - `add_encounter_pane_categories.py`

- `add_encounter_pane_categories()` - Inferred from name: add encounter pane categories.

## unsure - `add_init_categories.py`

- `add_category_to_init_files()` - Inferred from name: add category to init files.

## unsure - `add_legacy_root_categories.py`

- `add_legacy_root_categories()` - Inferred from name: add legacy root categories.

## unsure - `add_root_categories.py`

- `add_root_categories()` - Inferred from name: add root categories.

## unsure - `add_script_categories.py`

- `add_category_to_scripts()` - Inferred from name: add category to scripts.

## unsure - `agent.py`

- `__init__(self, api_key: str)` - Initializes the Agent.
- `execute_task(self, prompt: str)` - Sends a prompt to the LLM and gets a structured response.

## unsure - `check_monsters.py`

- `check_monster_exists(cursor: sqlite3.Cursor, monster_name: str)` - Inferred from name: check monster exists.
- `main()` - Inferred from name: main.

## unsure - `examples/add_potions_to_character.py`

- `add_potions_to_character(character_id: str, potion_type: str='all', quantity: int=1)` - Add healing potions to a character's inventory.
- `list_characters()` - List all characters in the database.
- `show_character_potions(character_id: str)` - Display all healing potions a character has.

## unsure - `examples/enhanced_systems_examples.py`

- `example_action_economy()` - Example: Using the action economy system
- `example_condition_system()` - Example: Using the condition system
- `example_configuration()` - Example: Using the configuration system
- `example_debug_commands()` - Example: Using debug commands
- `example_integration()` - Example: Integration between all systems
- `example_subclass_system()` - Example: Using the subclass system
- `main()` - Run all examples

## unsure - `examples/feature_usage_example.py`

- `__init__(self)` - Inferred from name: init.
- `attack_example(self, character_id: str, weapon_type: str='finesse')` - Example of attack resolution with features.
- `combat_example(self, character_id: str, target_ac: int=15)` - Example of using features during combat.
- `defense_example(self, character_id: str, incoming_damage: int=20)` - Example of using defensive features.
- `level_up_example(self, character_id: str, new_level: int)` - Example of handling level ups with new features.
- `rest_example(self, character_id: str)` - Example of rest processing.
- `run_all_examples()` - Run all examples with available characters.

## unsure - `examples/monster_abilities_demo.py`

- `demo_all_predefined()` - Show all predefined abilities.
- `demo_condition_application()` - Demonstrate automatic condition application on failed saves.
- `demo_dragon_breath()` - Demonstrate dragon breath weapon with recharge mechanics.
- `demo_limited_use()` - Demonstrate limited use ability (Aboleth's Dominate Mind).
- `demo_multiple_abilities()` - Show a monster with multiple special abilities.

## unsure - `examples/prepare_voice_from_audio.py`

- `main()` - Inferred from name: main.
- `split_audio_by_silence(audio_path: Path, output_dir: Path, min_silence_len: int=500, silence_thresh: int=-40, min_segment_len: int=1000, max_segment_len: int=10000)` - Split long audio into segments based on silence detection.
- `transcribe_audio_vosk(audio_path: Path, model_path: Optional[Path]=None)` - Transcribe audio using Vosk (offline, fast, free).
- `transcribe_audio_whisper(audio_path: Path)` - Transcribe audio using OpenAI Whisper (local, free).

## unsure - `examples/train_custom_voice.py`

- `main()` - Inferred from name: main.

## unsure - `file_system.py`

- `list_files(directory: str)` - Lists the contents of a directory recursively.
- `read_file(path: str)` - Reads the content of a file.
- `write_file(path: str, content: str)` - Writes content to a file, creating directories if necessary.

## unsure - `generate_categorization_report.py`

- `generate_report()` - Inferred from name: generate report.
- `get_category_from_file(filepath)` - Inferred from name: get category from file.

## unsure - `git.py`

- `git_commit(message: str)` - Commits changes with a given message.
- `git_diff()` - Gets the current git diff.

## unsure - `knowledge.py`

- `get_project_documentation(doc_name: str)` - Loads a specific project documentation file.
- `get_srd_document(topic: str)` - Loads a specific SRD document.
- `get_todo_list()` - Parses the ToDo list from the main readme.md.

## unsure - `main.py`

- `main(layout_profile: LayoutProfile | None=None)` - Inferred from name: main.
- `setup_logging()` - Inferred from name: setup logging.
- `start_ollama_server()` - Start Ollama server in background if not already running.

## unsure - `monster_srd_analysis.py`

- `main()` - Inferred from name: main.
- `search_srd(monster_name, srd_content)` - Inferred from name: search srd.

## unsure - `normalize_monster_actions.py`

- `__init__(self, db_path: str='talekeeper.db')` - Inferred from name: init.
- `_normalize_action(self, action: Dict[str, Any], monster_name: str)` - Normalize a single action entry.
- `_normalize_entry_text(self, text: str)` - Normalize action entry text from 5eTools format to D&D 2024 format.
- `capitalize_condition(match)` - Inferred from name: capitalize condition.
- `normalize_all_monsters(self, dry_run: bool=True)` - Normalize all monster actions in the database.
- `show_full_change(self, monster_name: str)` - Show full before/after for a specific monster.
- `show_sample_changes(self, limit: int=5)` - Show sample changes for review.
- `main()` - Run the normalization script.

## unsure - `shell.py`

- `run_shell_command(command: str)` - Executes a shell command and returns its output.

## unsure - `tools/annotate_and_document.py`

- `__init__(self, classification: str, file_path: Path, qualname: str, signature: str, summary: str, lineno: int)` - Inferred from name: init.
- `__init__(self)` - Inferred from name: init.
- `_handle_function(self, node: ast.AST)` - Inferred from name: handle function.
- `visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef)` - Inferred from name: visit AsyncFunctionDef.
- `visit_ClassDef(self, node: ast.ClassDef)` - Inferred from name: visit ClassDef.
- `visit_FunctionDef(self, node: ast.FunctionDef)` - Inferred from name: visit FunctionDef.
- `annotate_file(path: Path, classification: str)` - Inferred from name: annotate file.
- `classify(path: Path)` - Inferred from name: classify.
- `collect_functions(tree: ast.AST, classification: str, module_path: Path)` - Inferred from name: collect functions.
- `detect_existing_marker(body: str)` - Inferred from name: detect existing marker.
- `determine_newline(text: str)` - Inferred from name: determine newline.
- `ensure_docs_dir()` - Inferred from name: ensure docs dir.
- `format_signature(node: ast.AST)` - Inferred from name: format signature.
- `infer_summary(name: str, docstring: Optional[str])` - Inferred from name: infer summary.
- `main()` - Inferred from name: main.
- `rel_parts(path: Path)` - Inferred from name: rel parts.
- `remove_existing_marker(body: str)` - Inferred from name: remove existing marker.
- `should_skip(path: Path)` - Inferred from name: should skip.
- `write_catalog(functions: Sequence[FunctionRecord], parse_errors: Sequence[Tuple[Path, str]])` - Inferred from name: write catalog.

## unsure - `tools/compare_monsters.py`

- `compare_xml_to_db(xml_file='database/seeds/monsters_complete.xml', db_path='talekeeper.db')` - Inferred from name: compare xml to db.
- `show_monster_details(monster_name, db_path='talekeeper.db')` - Inferred from name: show monster details.

## unsure - `tools/load_monsters_to_db.py`

- `list_monsters_in_db(db_path='talekeeper.db')` - Inferred from name: list monsters in db.
- `load_monsters_from_xml(xml_file, db_path='talekeeper.db')` - Inferred from name: load monsters from xml.
- `parse_ability_scores(ability_scores_elem)` - Inferred from name: parse ability scores.
- `parse_actions(actions_elem)` - Inferred from name: parse actions.
- `parse_legendary_actions(legendary_actions_elem)` - Inferred from name: parse legendary actions.
- `parse_reactions(reactions_elem)` - Inferred from name: parse reactions.
- `parse_traits(traits_elem)` - Inferred from name: parse traits.

## unsure - `verify_categorization.py`

- `count_files(pattern, description)` - Inferred from name: count files.
- `run_grep_count(pattern, description)` - Inferred from name: run grep count.

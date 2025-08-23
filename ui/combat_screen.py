"""
File: ui/combat_screen.py
Path: /ui/combat_screen.py

Combat interface for TaleKeeper Desktop.
Handles turn-based D&D combat with monsters.

Pseudo Code:
1. Display combat participants and initiative order
2. Handle player action selection (attack, cast spell, etc.)
3. Process monster AI actions and responses
4. Update health, conditions, and combat state
5. Determine combat resolution (victory/defeat)

AI Agents: Combat UI and turn management system.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any, Optional
from loguru import logger

from core.game_engine import GameEngine
from models.character import Character
from models.monsters import Monster


class CombatScreen:
    """
    Combat interface for turn-based D&D combat.
    
    AI Agents: Add new combat actions and special abilities here.
    """
    
    def __init__(self, parent: ttk.Frame, game_engine: GameEngine, character: Character, monsters: List[Monster]):
        """Initialize combat screen."""
        self.parent = parent
        self.game_engine = game_engine
        self.character = character
        self.monsters = monsters
        
        # Combat state
        self.current_round = 1
        self.current_turn = 0
        self.initiative_order = []
        self.combat_active = True
        
        self._initialize_combat()
        self._create_interface()
        self._update_display()
        
        logger.info(f"Combat started: {character.name} vs {len(monsters)} monsters")
    
    def _initialize_combat(self):
        """Initialize combat state and roll initiative."""
        # Add character to initiative
        char_initiative = self.game_engine.dice_roller.roll_initiative(self.character.dexterity_modifier)
        self.initiative_order.append({
            "type": "character",
            "name": self.character.name,
            "initiative": char_initiative,
            "entity": self.character,
            "hp": self.character.hit_points_current,
            "max_hp": self.character.hit_points_max
        })
        
        # Add monsters to initiative
        for i, monster in enumerate(self.monsters):
            monster_initiative = self.game_engine.dice_roller.roll_initiative(monster.dexterity_modifier)
            self.initiative_order.append({
                "type": "monster",
                "name": f"{monster.name} {i+1}" if len(self.monsters) > 1 else monster.name,
                "initiative": monster_initiative,
                "entity": monster,
                "hp": monster.hit_points,
                "max_hp": monster.hit_points
            })
        
        # Sort by initiative (highest first)
        self.initiative_order.sort(key=lambda x: x["initiative"], reverse=True)
        
        # Format initiative order for logging
        init_list = [f"{c['name']}({c['initiative']})" for c in self.initiative_order]
        logger.info(f"Initiative order: {init_list}")
    
    def _create_interface(self):
        """Create the combat interface."""
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top: Initiative and current turn
        self._create_initiative_panel()
        
        # Middle: Combat participants
        self._create_participants_panel()
        
        # Bottom: Actions and combat log
        self._create_actions_panel()
    
    def _create_initiative_panel(self):
        """Create initiative order display."""
        init_frame = ttk.LabelFrame(self.main_frame, text="Initiative Order")
        init_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.initiative_text = tk.Text(init_frame, height=3, wrap=tk.WORD, state=tk.DISABLED)
        self.initiative_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Round and turn info
        info_frame = ttk.Frame(init_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        self.round_label = ttk.Label(info_frame, text=f"Round: {self.current_round}")
        self.round_label.pack(side=tk.LEFT)
        
        self.turn_label = ttk.Label(info_frame, text="")
        self.turn_label.pack(side=tk.RIGHT)
    
    def _create_participants_panel(self):
        """Create combat participants display."""
        participants_frame = ttk.LabelFrame(self.main_frame, text="Combatants")
        participants_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Character info
        char_frame = ttk.LabelFrame(participants_frame, text="Your Character")
        char_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 10), pady=5)
        
        self.char_hp_label = ttk.Label(char_frame, text="")
        self.char_hp_label.pack(pady=5)
        
        self.char_ac_label = ttk.Label(char_frame, text="")
        self.char_ac_label.pack()
        
        self.char_status_label = ttk.Label(char_frame, text="Ready")
        self.char_status_label.pack(pady=5)
        
        # Monsters info
        monsters_frame = ttk.LabelFrame(participants_frame, text="Enemies")
        monsters_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.monster_labels = []
        for combatant in self.initiative_order:
            if combatant["type"] == "monster":
                monster_frame = ttk.Frame(monsters_frame)
                monster_frame.pack(fill=tk.X, pady=2)
                
                name_label = ttk.Label(monster_frame, text=combatant["name"], font=('Arial', 10, 'bold'))
                name_label.pack(side=tk.LEFT)
                
                hp_label = ttk.Label(monster_frame, text="")
                hp_label.pack(side=tk.RIGHT)
                
                self.monster_labels.append({
                    "name": combatant["name"],
                    "hp_label": hp_label,
                    "combatant": combatant
                })
    
    def _create_actions_panel(self):
        """Create action selection and combat log."""
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.pack(fill=tk.X)
        
        # Actions (left side)
        actions_frame = ttk.LabelFrame(bottom_frame, text="Actions")
        actions_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Action buttons
        self.attack_btn = ttk.Button(actions_frame, text="Attack", command=self._attack_action)
        self.attack_btn.pack(fill=tk.X, pady=2)
        
        self.defend_btn = ttk.Button(actions_frame, text="Defend", command=self._defend_action)
        self.defend_btn.pack(fill=tk.X, pady=2)
        
        self.dash_btn = ttk.Button(actions_frame, text="Dash", command=self._dash_action)
        self.dash_btn.pack(fill=tk.X, pady=2)
        
        self.end_turn_btn = ttk.Button(actions_frame, text="End Turn", command=self._end_turn)
        self.end_turn_btn.pack(fill=tk.X, pady=(10, 2))
        
        # Combat log (right side)
        log_frame = ttk.LabelFrame(bottom_frame, text="Combat Log")
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.combat_log = tk.Text(log_container, wrap=tk.WORD, state=tk.DISABLED)
        log_scrollbar = ttk.Scrollbar(log_container, command=self.combat_log.yview)
        self.combat_log.config(yscrollcommand=log_scrollbar.set)
        
        self.combat_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add initial log entry
        self._add_combat_log("Combat begins!")
    
    def _update_display(self):
        """Update all combat displays."""
        # Initiative display
        init_text = f"Round {self.current_round} - Turn Order:\n"
        for i, combatant in enumerate(self.initiative_order):
            marker = " <-- CURRENT" if i == self.current_turn else ""
            status = "DEFEATED" if combatant["hp"] <= 0 else "ACTIVE"
            init_text += f"{combatant['name']} (Init: {combatant['initiative']}) - {status}{marker}\n"
        
        self.initiative_text.config(state=tk.NORMAL)
        self.initiative_text.delete(1.0, tk.END)
        self.initiative_text.insert(tk.END, init_text)
        self.initiative_text.config(state=tk.DISABLED)
        
        # Current turn label
        current_combatant = self.initiative_order[self.current_turn]
        self.turn_label.config(text=f"Current Turn: {current_combatant['name']}")
        
        # Character info
        self.char_hp_label.config(text=f"HP: {self.character.hit_points_current}/{self.character.hit_points_max}")
        self.char_ac_label.config(text=f"AC: {self.character.armor_class}")
        
        # Monster info
        for monster_label in self.monster_labels:
            combatant = monster_label["combatant"]
            hp_text = f"HP: {combatant['hp']}/{combatant['max_hp']}"
            if combatant["hp"] <= 0:
                hp_text += " (DEFEATED)"
            monster_label["hp_label"].config(text=hp_text)
        
        # Enable/disable action buttons based on current turn
        is_player_turn = self.initiative_order[self.current_turn]["type"] == "character"
        state = tk.NORMAL if is_player_turn and self.combat_active else tk.DISABLED
        
        self.attack_btn.config(state=state)
        self.defend_btn.config(state=state)
        self.dash_btn.config(state=state)
        self.end_turn_btn.config(state=tk.NORMAL if self.combat_active else tk.DISABLED)
        
        # If it's a monster turn, process automatically
        if not is_player_turn and self.combat_active:
            self.parent.after(1500, self._monster_turn)  # Delay for readability
    
    def _add_combat_log(self, message: str):
        """Add message to combat log."""
        self.combat_log.config(state=tk.NORMAL)
        self.combat_log.insert(tk.END, f"{message}\n")
        self.combat_log.see(tk.END)
        self.combat_log.config(state=tk.DISABLED)
        
        logger.info(f"Combat log: {message}")
    
    def _attack_action(self):
        """Player attacks a monster."""
        # Select target
        alive_monsters = [c for c in self.initiative_order if c["type"] == "monster" and c["hp"] > 0]
        if not alive_monsters:
            self._add_combat_log("No enemies to attack!")
            return
        
        # Simple targeting - attack first alive monster
        target = alive_monsters[0]
        
        # Make attack roll
        attack_bonus = self.character.proficiency_bonus + self.character.strength_modifier  # Simplified
        attack_roll, is_crit, is_fumble = self.game_engine.dice_roller.attack_roll(attack_bonus)
        
        target_ac = target["entity"].armor_class
        
        if attack_roll >= target_ac:
            # Hit!
            damage_dice = "1d8"  # Simplified weapon damage
            damage = self.game_engine.dice_roller.roll(damage_dice) + self.character.strength_modifier
            
            if is_crit:
                damage += self.game_engine.dice_roller.roll(damage_dice)  # Double weapon dice
                self._add_combat_log(f"Critical hit! You deal {damage} damage to {target['name']}!")
            else:
                self._add_combat_log(f"You hit {target['name']} for {damage} damage!")
            
            # Apply damage
            target["hp"] = max(0, target["hp"] - damage)
            
            if target["hp"] <= 0:
                self._add_combat_log(f"{target['name']} is defeated!")
        
        else:
            if is_fumble:
                self._add_combat_log(f"Fumble! You miss {target['name']} completely!")
            else:
                self._add_combat_log(f"You miss {target['name']} (rolled {attack_roll} vs AC {target_ac}).")
        
        self._check_combat_end()
        self._end_turn()
    
    def _defend_action(self):
        """Player takes defensive action."""
        self._add_combat_log("You take a defensive stance, gaining +2 AC until your next turn.")
        # TODO: Implement AC bonus tracking
        self._end_turn()
    
    def _dash_action(self):
        """Player dashes (gains extra movement)."""
        self._add_combat_log("You dash, doubling your movement speed this turn.")
        # TODO: Implement movement tracking
        self._end_turn()
    
    def _monster_turn(self):
        """Process monster AI turn."""
        current_combatant = self.initiative_order[self.current_turn]
        
        if current_combatant["hp"] <= 0:
            self._add_combat_log(f"{current_combatant['name']} is defeated and skips their turn.")
            self._end_turn()
            return
        
        monster = current_combatant["entity"]
        
        # Simple AI: attack if player is alive
        if self.character.hit_points_current > 0:
            # Make monster attack
            attack_bonus = monster.proficiency_bonus + monster.strength_modifier
            attack_roll, is_crit, is_fumble = self.game_engine.dice_roller.attack_roll(attack_bonus)
            
            target_ac = self.character.armor_class
            
            if attack_roll >= target_ac:
                # Monster hits
                # Find monster's attack (simplified)
                actions = monster.actions or []
                if actions:
                    action = actions[0]  # Use first attack
                    # Parse damage from description (simplified)
                    damage = self.game_engine.dice_roller.roll("1d6") + monster.strength_modifier
                    
                    if is_crit:
                        damage += self.game_engine.dice_roller.roll("1d6")
                        self._add_combat_log(f"Critical hit! {current_combatant['name']} deals {damage} damage to you!")
                    else:
                        self._add_combat_log(f"{current_combatant['name']} hits you for {damage} damage!")
                    
                    # Apply damage to character
                    self.character.hit_points_current = max(0, self.character.hit_points_current - damage)
                    
                    if self.character.hit_points_current <= 0:
                        self._add_combat_log("You have been defeated!")
                
            else:
                if is_fumble:
                    self._add_combat_log(f"{current_combatant['name']} fumbles their attack!")
                else:
                    self._add_combat_log(f"{current_combatant['name']} misses you!")
        
        self._check_combat_end()
        self._end_turn()
    
    def _end_turn(self):
        """End current turn and advance to next."""
        if not self.combat_active:
            return
        
        # Advance turn
        self.current_turn = (self.current_turn + 1) % len(self.initiative_order)
        
        # If we've cycled back to first combatant, advance round
        if self.current_turn == 0:
            self.current_round += 1
            self._add_combat_log(f"--- Round {self.current_round} begins ---")
        
        self._update_display()
    
    def _check_combat_end(self):
        """Check if combat should end."""
        # Check if all monsters are defeated
        alive_monsters = [c for c in self.initiative_order if c["type"] == "monster" and c["hp"] > 0]
        if not alive_monsters:
            self.combat_active = False
            self._add_combat_log("Victory! All enemies defeated!")
            self._end_combat(victory=True)
            return
        
        # Check if player is defeated
        if self.character.hit_points_current <= 0:
            self.combat_active = False
            self._add_combat_log("Defeat! You have been overcome...")
            self._end_combat(victory=False)
            return
    
    def _end_combat(self, victory: bool):
        """End combat and show results."""
        if victory:
            # Calculate XP reward
            total_xp = sum(m.xp_value or 0 for m in self.monsters)
            self.character.experience_points += total_xp
            
            messagebox.showinfo(
                "Victory!",
                f"Combat complete!\n\n"
                f"Experience gained: {total_xp} XP\n"
                f"Total XP: {self.character.experience_points}"
            )
        else:
            messagebox.showinfo(
                "Defeat",
                "You have been defeated in combat.\n\n"
                "In a real game, this might trigger death saving throws\n"
                "or other consequences."
            )
        
        # TODO: Return to exploration screen or handle aftermath
        logger.info(f"Combat ended - Victory: {victory}")
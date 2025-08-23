"""
File: ui/game_screen.py
Path: /ui/game_screen.py

Main game screen for exploration and adventure.
Handles location exploration, encounters, and character management.

Pseudo Code:
1. Display current location and available actions
2. Handle exploration actions (search, travel, rest)
3. Generate random encounters based on location
4. Show character status and quick actions
5. Navigate to combat screen when encounters begin

AI Agents: Main gameplay interface and exploration mechanics.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
from loguru import logger

from core.game_engine import GameEngine
from models.character import Character


class GameScreen:
    """
    Main game screen for exploration and adventure.
    
    AI Agents: Add new exploration mechanics and location types here.
    """
    
    def __init__(self, parent: ttk.Frame, game_engine: GameEngine, character: Character):
        """Initialize the game screen."""
        self.parent = parent
        self.game_engine = game_engine
        self.character = character
        
        self._create_interface()
        self._update_display()
        
        logger.info(f"Game screen initialized for {character.name}")
    
    def _create_interface(self):
        """Create the main game interface."""
        # Main layout
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top section: Character status
        self._create_character_status()
        
        # Middle section: Location and actions
        self._create_location_section()
        
        # Bottom section: Game log
        self._create_game_log()
    
    def _create_character_status(self):
        """Create character status display."""
        status_frame = ttk.LabelFrame(self.main_frame, text="Character Status")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Character info
        info_frame = ttk.Frame(status_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Left side: basic info
        left_info = ttk.Frame(info_frame)
        left_info.pack(side=tk.LEFT, fill=tk.Y)
        
        self.char_name_label = ttk.Label(left_info, text="", font=('Arial', 12, 'bold'))
        self.char_name_label.pack(anchor=tk.W)
        
        self.char_class_label = ttk.Label(left_info, text="")
        self.char_class_label.pack(anchor=tk.W)
        
        # Middle: health and resources
        middle_info = ttk.Frame(info_frame)
        middle_info.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 0))
        
        self.hp_label = ttk.Label(middle_info, text="")
        self.hp_label.pack(anchor=tk.W)
        
        self.ac_label = ttk.Label(middle_info, text="")
        self.ac_label.pack(anchor=tk.W)
        
        # Right side: quick actions
        right_info = ttk.Frame(info_frame)
        right_info.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(right_info, text="Rest", command=self._rest_character).pack(side=tk.TOP, pady=2)
        ttk.Button(right_info, text="Character Sheet", command=self._show_character_sheet).pack(side=tk.TOP, pady=2)
    
    def _create_location_section(self):
        """Create location display and actions."""
        location_frame = ttk.LabelFrame(self.main_frame, text="Current Location")
        location_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Location info
        self.location_label = ttk.Label(location_frame, text="Starting Town", font=('Arial', 14, 'bold'))
        self.location_label.pack(pady=10)
        
        self.location_desc_label = ttk.Label(location_frame, text="A peaceful town where adventurers begin their journeys.")
        self.location_desc_label.pack(pady=(0, 20))
        
        # Available actions
        actions_frame = ttk.Frame(location_frame)
        actions_frame.pack(expand=True)
        
        # Action buttons in grid
        actions = [
            ("Explore Area", self._explore_area),
            ("Search for Secrets", self._search_secrets),
            ("Random Encounter", self._random_encounter),
            ("Visit Town", self._visit_town),
            ("Travel", self._travel),
            ("Camp", self._make_camp)
        ]
        
        for i, (text, command) in enumerate(actions):
            row = i // 3
            col = i % 3
            btn = ttk.Button(actions_frame, text=text, command=command)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Configure grid
        for i in range(3):
            actions_frame.columnconfigure(i, weight=1)
    
    def _create_game_log(self):
        """Create game log display."""
        log_frame = ttk.LabelFrame(self.main_frame, text="Adventure Log")
        log_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Log text with scrollbar
        log_container = ttk.Frame(log_frame)
        log_container.pack(fill=tk.X, padx=5, pady=5)
        
        self.log_text = tk.Text(log_container, height=8, wrap=tk.WORD, state=tk.DISABLED)
        log_scrollbar = ttk.Scrollbar(log_container, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add welcome message
        self._add_log_entry("Welcome to TaleKeeper! Your adventure begins...")
    
    def _update_display(self):
        """Update all display elements."""
        # Character info
        race_name = self.character.race.name if self.character.race else "Unknown"
        class_name = self.character.character_class.name if self.character.character_class else "Unknown"
        
        self.char_name_label.config(text=self.character.name)
        self.char_class_label.config(text=f"Level {self.character.level} {race_name} {class_name}")
        self.hp_label.config(text=f"HP: {self.character.hit_points_current}/{self.character.hit_points_max}")
        self.ac_label.config(text=f"AC: {self.character.armor_class}")
        
        # Location info (from game state if available)
        if self.game_engine.game_state:
            location = self.game_engine.game_state.current_location
            self.location_label.config(text=location)
            
            # Update description based on location
            descriptions = {
                "Starting Town": "A peaceful town where adventurers begin their journeys.",
                "Dark Forest": "Ancient trees loom overhead, blocking out most sunlight.",
                "Abandoned Mine": "Old mining tunnels wind deep into the earth.",
                "Haunted Ruins": "Crumbling stones whisper of forgotten civilizations."
            }
            
            desc = descriptions.get(location, "An unknown location full of mystery.")
            self.location_desc_label.config(text=desc)
    
    def _add_log_entry(self, message: str):
        """Add entry to the game log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)  # Scroll to bottom
        self.log_text.config(state=tk.DISABLED)
        
        logger.info(f"Game log: {message}")
    
    def _explore_area(self):
        """Explore the current area."""
        roll = self.game_engine.roll_dice("1d20")
        
        if roll >= 15:
            self._add_log_entry("You discover something interesting while exploring!")
            # Could trigger treasure, encounter, or story event
            self._random_encounter()
        elif roll >= 8:
            self._add_log_entry("You explore the area but find nothing unusual.")
        else:
            self._add_log_entry("Your exploration reveals little of interest.")
    
    def _search_secrets(self):
        """Search for hidden secrets."""
        # Use character's perception/investigation
        investigation_bonus = self.character.intelligence_modifier  # Simplified
        roll = self.game_engine.roll_dice("1d20") + investigation_bonus
        
        if roll >= 18:
            self._add_log_entry("You discover a hidden treasure!")
            # TODO: Add treasure generation
        elif roll >= 12:
            self._add_log_entry("You find some interesting clues about this place.")
        else:
            self._add_log_entry("Despite your careful searching, you find nothing hidden.")
    
    def _random_encounter(self):
        """Generate a random encounter."""
        try:
            # Get fresh character data from database to avoid detached session issues
            from core.database import DatabaseSession
            with DatabaseSession() as db:
                character = db.query(Character).filter(Character.id == self.character.id).first()
                if not character:
                    self._add_log_entry("Error: Character data not found!")
                    return
                
                # Get monsters appropriate for character level
                max_cr = max(0.25, character.level * 0.5)  # Simple CR scaling
                monsters = self.game_engine.get_monsters_by_cr(0, max_cr)
            
            if not monsters:
                self._add_log_entry("The area seems strangely quiet...")
                return
            
            # Pick random monster
            import random
            monster = random.choice(monsters)
            
            # Show encounter dialog
            result = messagebox.askyesno(
                "Encounter!",
                f"You encounter a {monster.name}!\n\n"
                f"CR: {monster.challenge_rating}\n"
                f"HP: {monster.hit_points}\n"
                f"AC: {monster.armor_class}\n\n"
                f"Do you want to fight?"
            )
            
            if result:
                self._add_log_entry(f"You engage in combat with the {monster.name}!")
                self._start_combat([monster])
            else:
                flee_roll = self.game_engine.roll_dice("1d20") + self.character.dexterity_modifier
                if flee_roll >= 10:
                    self._add_log_entry(f"You successfully flee from the {monster.name}!")
                else:
                    self._add_log_entry(f"You fail to escape the {monster.name}!")
                    self._start_combat([monster])
        
        except Exception as e:
            logger.exception(f"Error in random encounter: {e}")
            self._add_log_entry("Something strange happens, but nothing comes of it.")
    
    def _visit_town(self):
        """Visit town services."""
        if self.game_engine.game_state and self.game_engine.game_state.location_type == "town":
            options = ["Rest at Inn", "Visit Shop", "Gather Information", "Leave Town"]
            # TODO: Implement town interface
            self._add_log_entry("You visit the town center.")
        else:
            self._add_log_entry("There's no town here to visit.")
    
    def _travel(self):
        """Travel to different location."""
        locations = ["Starting Town", "Dark Forest", "Abandoned Mine", "Haunted Ruins"]
        current = self.game_engine.game_state.current_location if self.game_engine.game_state else "Starting Town"
        
        # Simple travel - just change location
        available = [loc for loc in locations if loc != current]
        
        if available:
            import random
            new_location = random.choice(available)
            
            if self.game_engine.game_state:
                self.game_engine.game_state.current_location = new_location
            
            self._add_log_entry(f"You travel to {new_location}.")
            self._update_display()
        else:
            self._add_log_entry("You have nowhere new to travel.")
    
    def _make_camp(self):
        """Make camp (short rest)."""
        self._add_log_entry("You make camp and take a short rest.")
        
        # Restore some HP and resources
        if self.character.hit_points_current < self.character.hit_points_max:
            healing = self.game_engine.roll_dice("1d4") + max(1, self.character.constitution_modifier)
            old_hp = self.character.hit_points_current
            self.character.hit_points_current = min(
                self.character.hit_points_max,
                self.character.hit_points_current + healing
            )
            healed = self.character.hit_points_current - old_hp
            
            if healed > 0:
                self._add_log_entry(f"You recover {healed} hit points.")
            
            self._update_display()
    
    def _rest_character(self):
        """Handle character rest."""
        rest_type = messagebox.askyesno("Rest", "Take a long rest? (Yes = Long Rest, No = Short Rest)")
        
        if rest_type:  # Long rest
            self.character.hit_points_current = self.character.hit_points_max
            self.character.hit_dice_current = self.character.hit_dice_max
            self._add_log_entry("You take a long rest and fully recover.")
        else:  # Short rest
            if self.character.hit_dice_current > 0:
                # Use hit die for healing
                healing = self.game_engine.roll_dice(f"1d{self.character.character_class.hit_die if self.character.character_class else 8}")
                healing += self.character.constitution_modifier
                
                old_hp = self.character.hit_points_current
                self.character.hit_points_current = min(
                    self.character.hit_points_max,
                    self.character.hit_points_current + healing
                )
                
                self.character.hit_dice_current -= 1
                healed = self.character.hit_points_current - old_hp
                
                self._add_log_entry(f"You take a short rest and recover {healed} hit points.")
            else:
                self._add_log_entry("You have no hit dice remaining for a short rest.")
        
        self._update_display()
    
    def _show_character_sheet(self):
        """Show detailed character sheet."""
        # TODO: Implement character sheet window
        char_info = self.character.to_dict()
        messagebox.showinfo("Character Sheet", f"Name: {char_info['name']}\nLevel: {char_info['level']}")
    
    def _start_combat(self, monsters):
        """Start combat with given monsters."""
        # TODO: Implement combat screen navigation
        self._add_log_entry("Combat system not yet implemented!")
        messagebox.showinfo("Combat", "Combat system coming soon!")
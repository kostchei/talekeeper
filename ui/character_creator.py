"""
File: ui/character_creator.py
Path: /ui/character_creator.py

Character creation window for TaleKeeper Desktop.
Handles D&D character creation with race, class, background selection.

Pseudo Code:
1. Create character creation wizard with multiple steps
2. Handle race selection with ability score previews
3. Manage class and subclass selection
4. Process background selection and proficiencies
5. Generate ability scores and calculate derived stats
6. Create character in database and return to main window

AI Agents: Character creation UI and D&D rules application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, List, Callable
from loguru import logger

from core.game_engine import GameEngine


class CharacterCreatorWindow:
    """
    Character creation window with step-by-step wizard.
    
    AI Agents: Extend with additional character options and validation.
    """
    
    def __init__(self, parent: tk.Tk, game_engine: GameEngine, save_slot: Optional[int], callback: Callable):
        """
        Initialize character creator.
        
        Args:
            parent: Parent window
            game_engine: Game engine instance
            save_slot: Target save slot (optional)
            callback: Function to call when character is created
        """
        self.game_engine = game_engine
        self.save_slot = save_slot
        self.callback = callback
        
        # Character data
        self.character_data = {
            "name": "",
            "race_id": "",
            "class_id": "",
            "subclass_id": "",
            "background_id": "",
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10,
            "notes": ""
        }
        
        # Available options
        self.races = game_engine.get_available_races()
        self.classes = game_engine.get_available_classes()
        self.backgrounds = game_engine.get_available_backgrounds()
        
        # Current selections
        self.selected_race = None
        self.selected_class = None
        self.selected_subclass = None
        self.selected_background = None
        
        # Create window
        self._create_window(parent)
        self._create_interface()
        self._setup_step1_basic_info()
        
        logger.info("Character creator opened")
    
    def _create_window(self, parent: tk.Tk):
        """Create the character creator window."""
        self.window = tk.Toplevel(parent)
        self.window.title("Create New Character")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Make modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center on parent
        self.window.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (800 // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (600 // 2)
        self.window.geometry(f"800x600+{x}+{y}")
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_interface(self):
        """Create the main interface."""
        # Main container
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="Create New Character", style='Heading.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Notebook for steps
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create step frames
        self.step1_frame = ttk.Frame(self.notebook)
        self.step2_frame = ttk.Frame(self.notebook) 
        self.step3_frame = ttk.Frame(self.notebook)
        self.step4_frame = ttk.Frame(self.notebook)
        self.step5_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.step1_frame, text="Basic Info")
        self.notebook.add(self.step2_frame, text="Race")
        self.notebook.add(self.step3_frame, text="Class")
        self.notebook.add(self.step4_frame, text="Background")
        self.notebook.add(self.step5_frame, text="Abilities")
        
        # Button frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X)
        
        self.prev_button = ttk.Button(self.button_frame, text="Previous", command=self._prev_step)
        self.prev_button.pack(side=tk.LEFT)
        
        self.next_button = ttk.Button(self.button_frame, text="Next", command=self._next_step)
        self.next_button.pack(side=tk.RIGHT)
        
        self.create_button = ttk.Button(self.button_frame, text="Create Character", command=self._create_character)
        self.create_button.pack(side=tk.RIGHT, padx=(0, 10))
        self.create_button.pack_forget()  # Hide initially
        
        # Bind tab change
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _setup_step1_basic_info(self):
        """Setup basic character information step."""
        # Character name
        ttk.Label(self.step1_frame, text="Character Name:").pack(anchor=tk.W, pady=(10, 5))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(self.step1_frame, textvariable=self.name_var, font=('Arial', 12))
        name_entry.pack(fill=tk.X, pady=(0, 20))
        name_entry.focus()
        
        # Save slot info
        if self.save_slot:
            ttk.Label(self.step1_frame, text=f"Save Slot: {self.save_slot}").pack(anchor=tk.W, pady=(0, 10))
        
        # Notes
        ttk.Label(self.step1_frame, text="Character Notes (optional):").pack(anchor=tk.W, pady=(10, 5))
        self.notes_text = tk.Text(self.step1_frame, height=6, wrap=tk.WORD)
        self.notes_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for notes
        notes_scrollbar = ttk.Scrollbar(self.step1_frame, command=self.notes_text.yview)
        self.notes_text.config(yscrollcommand=notes_scrollbar.set)
    
    def _setup_step2_race(self):
        """Setup race selection step."""
        # Clear frame
        for widget in self.step2_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.step2_frame, text="Choose your character's race:").pack(anchor=tk.W, pady=(10, 10))
        
        # Race list
        race_frame = ttk.Frame(self.step2_frame)
        race_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side: race list
        list_frame = ttk.Frame(race_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.race_listbox = tk.Listbox(list_frame, height=10)
        self.race_listbox.pack(fill=tk.Y, expand=True)
        self.race_listbox.bind("<<ListboxSelect>>", self._on_race_select)
        
        for race in self.races:
            self.race_listbox.insert(tk.END, race["name"])
        
        # Right side: race details
        self.race_details_frame = ttk.Frame(race_frame)
        self.race_details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.race_details_text = tk.Text(self.race_details_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.race_details_text.pack(fill=tk.BOTH, expand=True)
    
    def _setup_step3_class(self):
        """Setup class selection step."""
        # Clear frame
        for widget in self.step3_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.step3_frame, text="Choose your character's class:").pack(anchor=tk.W, pady=(10, 10))
        
        # Class layout
        class_frame = ttk.Frame(self.step3_frame)
        class_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side: class list
        list_frame = ttk.Frame(class_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.class_listbox = tk.Listbox(list_frame, height=8)
        self.class_listbox.pack(fill=tk.Y)
        self.class_listbox.bind("<<ListboxSelect>>", self._on_class_select)
        
        for cls in self.classes:
            self.class_listbox.insert(tk.END, cls["name"])
        
        # Right side: class details
        details_frame = ttk.Frame(class_frame)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.class_details_text = tk.Text(details_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.class_details_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Subclass selection
        ttk.Label(details_frame, text="Subclass (choose at level 3):").pack(anchor=tk.W)
        self.subclass_var = tk.StringVar()
        self.subclass_combo = ttk.Combobox(details_frame, textvariable=self.subclass_var, state="readonly")
        self.subclass_combo.pack(fill=tk.X)
    
    def _setup_step4_background(self):
        """Setup background selection step.""" 
        # Clear frame
        for widget in self.step4_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.step4_frame, text="Choose your character's background:").pack(anchor=tk.W, pady=(10, 10))
        
        # Background layout
        bg_frame = ttk.Frame(self.step4_frame)
        bg_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side: background list
        list_frame = ttk.Frame(bg_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.background_listbox = tk.Listbox(list_frame, height=8)
        self.background_listbox.pack(fill=tk.Y)
        self.background_listbox.bind("<<ListboxSelect>>", self._on_background_select)
        
        for bg in self.backgrounds:
            self.background_listbox.insert(tk.END, bg["name"])
        
        # Right side: background details
        self.background_details_frame = ttk.Frame(bg_frame)
        self.background_details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.background_details_text = tk.Text(self.background_details_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.background_details_text.pack(fill=tk.BOTH, expand=True)
    
    def _setup_step5_abilities(self):
        """Setup ability score generation step."""
        # Clear frame
        for widget in self.step5_frame.winfo_children():
            widget.destroy()
        
        ttk.Label(self.step5_frame, text="Generate Ability Scores:").pack(anchor=tk.W, pady=(10, 10))
        
        # Generation method
        method_frame = ttk.Frame(self.step5_frame)
        method_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(method_frame, text="Method:").pack(side=tk.LEFT)
        self.method_var = tk.StringVar(value="standard")
        method_combo = ttk.Combobox(method_frame, textvariable=self.method_var, values=["standard", "classic", "heroic"], state="readonly")
        method_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Generate button
        generate_btn = ttk.Button(method_frame, text="Generate", command=self._generate_abilities)
        generate_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Ability scores display
        self.abilities_frame = ttk.Frame(self.step5_frame)
        self.abilities_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.ability_vars = {}
        abilities = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        
        for i, ability in enumerate(abilities):
            row = i // 2
            col = i % 2
            
            ability_frame = ttk.Frame(self.abilities_frame)
            ability_frame.grid(row=row, column=col, padx=10, pady=5, sticky=tk.W+tk.E)
            
            ttk.Label(ability_frame, text=f"{ability}:").pack(side=tk.LEFT)
            
            var = tk.StringVar(value="10")
            self.ability_vars[ability.lower()] = var
            score_label = ttk.Label(ability_frame, textvariable=var, font=('Arial', 12, 'bold'))
            score_label.pack(side=tk.RIGHT)
        
        # Configure grid weights
        self.abilities_frame.columnconfigure(0, weight=1)
        self.abilities_frame.columnconfigure(1, weight=1)
        
        # Summary
        self.summary_text = tk.Text(self.step5_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.summary_text.pack(fill=tk.BOTH, expand=True)
    
    def _generate_abilities(self):
        """Generate ability scores using selected method."""
        method = self.method_var.get()
        scores = self.game_engine.dice_roller.roll_stats(method)
        
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for i, ability in enumerate(abilities):
            self.ability_vars[ability].set(str(scores[i]))
            self.character_data[ability] = scores[i]
        
        self._update_character_summary()
    
    def _update_character_summary(self):
        """Update the character summary display."""
        if not all([self.selected_race, self.selected_class, self.selected_background]):
            return
        
        summary = "Character Summary:\n\n"
        summary += f"Name: {self.name_var.get() or 'Unnamed'}\n"
        summary += f"Race: {self.selected_race['name']}\n"
        summary += f"Class: {self.selected_class['name']}\n"
        if self.selected_subclass:
            summary += f"Subclass: {self.selected_subclass['name']}\n"
        summary += f"Background: {self.selected_background['name']}\n\n"
        
        summary += "Ability Scores (with racial bonuses):\n"
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            base_score = self.character_data[ability]
            racial_bonus = self.selected_race.get('ability_score_increases', {}).get(ability, 0)
            final_score = base_score + racial_bonus
            modifier = (final_score - 10) // 2
            modifier_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            summary += f"{ability.title()}: {final_score} ({modifier_str})\n"
        
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary)
        self.summary_text.config(state=tk.DISABLED)
    
    def _on_race_select(self, event):
        """Handle race selection."""
        selection = self.race_listbox.curselection()
        if not selection:
            return
        
        race_index = selection[0]
        self.selected_race = self.races[race_index]
        self.character_data["race_id"] = self.selected_race["id"]
        
        # Update details display
        race_text = f"{self.selected_race['name']}\n\n"
        race_text += f"Size: {self.selected_race['size']}\n"
        race_text += f"Speed: {self.selected_race['speed']} feet\n\n"
        race_text += f"Description:\n{self.selected_race['description']}\n\n"
        
        if self.selected_race['ability_score_increases']:
            race_text += "Ability Score Increases:\n"
            for ability, bonus in self.selected_race['ability_score_increases'].items():
                race_text += f"  {ability.title()}: +{bonus}\n"
            race_text += "\n"
        
        if self.selected_race['traits']:
            race_text += "Racial Traits:\n"
            for trait, description in self.selected_race['traits'].items():
                race_text += f"  {trait.replace('_', ' ').title()}: {description}\n"
        
        self.race_details_text.config(state=tk.NORMAL)
        self.race_details_text.delete(1.0, tk.END)
        self.race_details_text.insert(tk.END, race_text)
        self.race_details_text.config(state=tk.DISABLED)
        
        self._update_character_summary()
    
    def _on_class_select(self, event):
        """Handle class selection."""
        selection = self.class_listbox.curselection()
        if not selection:
            return
        
        class_index = selection[0]
        self.selected_class = self.classes[class_index]
        self.character_data["class_id"] = self.selected_class["id"]
        
        # Update subclass options
        subclasses = self.selected_class.get('subclasses', [])
        self.subclass_combo['values'] = [sub['name'] for sub in subclasses]
        if subclasses:
            self.subclass_combo.set(subclasses[0]['name'])
            self.selected_subclass = subclasses[0]
            self.character_data["subclass_id"] = subclasses[0]["id"]
        
        # Update details display
        class_text = f"{self.selected_class['name']}\n\n"
        class_text += f"Hit Die: d{self.selected_class['hit_die']}\n"
        class_text += f"Primary Ability: {self.selected_class['primary_ability']}\n\n"
        class_text += f"Description:\n{self.selected_class['description']}\n\n"
        
        class_text += "Proficiencies:\n"
        if self.selected_class['armor_proficiencies']:
            class_text += f"  Armor: {', '.join(self.selected_class['armor_proficiencies'])}\n"
        if self.selected_class['weapon_proficiencies']:
            class_text += f"  Weapons: {', '.join(self.selected_class['weapon_proficiencies'])}\n"
        if self.selected_class['saving_throw_proficiencies']:
            class_text += f"  Saving Throws: {', '.join(self.selected_class['saving_throw_proficiencies'])}\n"
        
        self.class_details_text.config(state=tk.NORMAL)
        self.class_details_text.delete(1.0, tk.END)
        self.class_details_text.insert(tk.END, class_text)
        self.class_details_text.config(state=tk.DISABLED)
        
        self._update_character_summary()
    
    def _on_background_select(self, event):
        """Handle background selection."""
        selection = self.background_listbox.curselection()
        if not selection:
            return
        
        bg_index = selection[0]
        self.selected_background = self.backgrounds[bg_index]
        self.character_data["background_id"] = self.selected_background["id"]
        
        # Update details display
        bg_text = f"{self.selected_background['name']}\n\n"
        bg_text += f"Description:\n{self.selected_background['description']}\n\n"
        
        if self.selected_background['skill_proficiencies']:
            bg_text += f"Skill Proficiencies: {', '.join(self.selected_background['skill_proficiencies'])}\n"
        if self.selected_background['tool_proficiencies']:
            bg_text += f"Tool Proficiencies: {', '.join(self.selected_background['tool_proficiencies'])}\n"
        
        bg_text += f"\nFeature: {self.selected_background['feature_name']}\n"
        bg_text += f"{self.selected_background['feature_description']}"
        
        self.background_details_text.config(state=tk.NORMAL)
        self.background_details_text.delete(1.0, tk.END)
        self.background_details_text.insert(tk.END, bg_text)
        self.background_details_text.config(state=tk.DISABLED)
        
        self._update_character_summary()
    
    def _on_tab_changed(self, event):
        """Handle tab changes."""
        current_tab = self.notebook.index("current")
        
        # Setup tabs as they're accessed
        if current_tab == 1:  # Race
            self._setup_step2_race()
        elif current_tab == 2:  # Class
            self._setup_step3_class()
        elif current_tab == 3:  # Background
            self._setup_step4_background()
        elif current_tab == 4:  # Abilities
            self._setup_step5_abilities()
            self._generate_abilities()  # Auto-generate on first view
        
        # Show/hide buttons
        if current_tab == 0:
            self.prev_button.config(state=tk.DISABLED)
        else:
            self.prev_button.config(state=tk.NORMAL)
        
        if current_tab == 4:  # Last tab
            self.next_button.pack_forget()
            self.create_button.pack(side=tk.RIGHT, padx=(0, 10))
        else:
            self.create_button.pack_forget()
            self.next_button.pack(side=tk.RIGHT)
    
    def _prev_step(self):
        """Go to previous step."""
        current = self.notebook.index("current")
        if current > 0:
            self.notebook.select(current - 1)
    
    def _next_step(self):
        """Go to next step."""
        current = self.notebook.index("current")
        if current < self.notebook.index("end") - 1:
            # Validate current step
            if self._validate_step(current):
                self.notebook.select(current + 1)
    
    def _validate_step(self, step: int) -> bool:
        """Validate current step before proceeding."""
        if step == 0:  # Basic info
            if not self.name_var.get().strip():
                messagebox.showerror("Error", "Please enter a character name.")
                return False
            self.character_data["name"] = self.name_var.get().strip()
            self.character_data["notes"] = self.notes_text.get(1.0, tk.END).strip()
        
        elif step == 1:  # Race
            if not self.selected_race:
                messagebox.showerror("Error", "Please select a race.")
                return False
        
        elif step == 2:  # Class
            if not self.selected_class:
                messagebox.showerror("Error", "Please select a class.")
                return False
        
        elif step == 3:  # Background
            if not self.selected_background:
                messagebox.showerror("Error", "Please select a background.")
                return False
        
        return True
    
    def _create_character(self):
        """Create the character and close the window."""
        # Final validation
        if not self._validate_step(self.notebook.index("current")):
            return
        
        try:
            # Update ability scores with current values
            for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
                self.character_data[ability] = int(self.ability_vars[ability].get())
            
            # Create character
            character = self.game_engine.create_new_character(self.character_data, self.save_slot or 1)
            
            messagebox.showinfo("Success", f"Character '{character.name}' created successfully!")
            
            # Call callback and close
            if self.callback:
                self.callback(character)
            
            self._close()
            
        except Exception as e:
            logger.exception(f"Error creating character: {e}")
            messagebox.showerror("Error", f"Failed to create character: {str(e)}")
    
    def _on_close(self):
        """Handle window close."""
        self._close()
    
    def _close(self):
        """Close the character creator window."""
        self.window.grab_release()
        self.window.destroy()
        logger.info("Character creator closed")
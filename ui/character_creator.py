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
from tkinter import ttk, messagebox, font
from typing import Optional, Dict, Any, List, Callable
from loguru import logger
from pathlib import Path
import os
import sys

try:
    import pyglet
    PYGLET_AVAILABLE = True
except ImportError:
    PYGLET_AVAILABLE = False
    logger.warning("pyglet not available, using fallback fonts")

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
        
        # Setup custom fonts
        self._setup_fonts()
        
        # Create window
        self._create_window(parent)
        self._create_interface()
        self._setup_step1_basic_info()
        
        logger.info("Character creator opened")
    
    def _setup_fonts(self):
        """Setup custom Caslon Antique fonts from assets folder using pyglet."""
        # Default font family name
        caslon_family = "Georgia"
        
        try:
            # Get assets directory
            assets_dir = Path("assets")
            font_files = [
                "CaslonAntique.ttf",
                "CaslonAntique-Bold.ttf", 
                "CaslonAntique-Italic.ttf",
                "CaslonAntique-BoldItalic.ttf"
            ]
            
            # Load fonts using pyglet if available
            if PYGLET_AVAILABLE:
                fonts_loaded = 0
                for font_file in font_files:
                    font_path = assets_dir / font_file
                    if font_path.exists():
                        try:
                            pyglet.font.add_file(str(font_path.absolute()))
                            fonts_loaded += 1
                        except Exception as e:
                            logger.warning(f"Failed to load font {font_file}: {e}")
                
                if fonts_loaded > 0:
                    caslon_family = "Caslon Antique"
                    logger.info(f"Loaded {fonts_loaded} Caslon Antique font files using pyglet")
                else:
                    logger.warning("No Caslon Antique fonts could be loaded, using Georgia fallback")
            else:
                logger.info("pyglet not available, using Georgia fonts")
            
            # Create font objects with the determined family
            self.caslon_font = font.Font(family=caslon_family, size=14)
            self.caslon_large_font = font.Font(family=caslon_family, size=20)
            self.caslon_title_font = font.Font(family=caslon_family, size=28, weight="bold")
            self.caslon_button_font = font.Font(family=caslon_family, size=16)
            
        except Exception as e:
            logger.warning(f"Font setup failed: {e}, using default fonts")
            # Safe fallback
            self.caslon_font = font.Font(size=14)
            self.caslon_large_font = font.Font(size=20)
            self.caslon_title_font = font.Font(size=28, weight="bold")
            self.caslon_button_font = font.Font(size=16)
    
    def _create_window(self, parent: tk.Tk):
        """Create the character creator window."""
        self.window = tk.Toplevel(parent)
        self.window.title("Create New Character")
        
        # Get screen dimensions first
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Calculate appropriate window size (ensure buttons are visible)
        desired_width, desired_height = 1000, 850  # Increased height for button visibility
        
        # Ensure window fits on screen (max 90% of screen size)
        final_width = min(desired_width, int(screen_width * 0.9))
        final_height = min(desired_height, int(screen_height * 0.9))
        
        # Set minimum size that guarantees button visibility
        min_width = max(800, final_width)  # Absolute minimum width
        min_height = max(700, final_height)  # Absolute minimum height (increased for buttons)
        
        # Set window geometry and constraints
        self.window.geometry(f"{final_width}x{final_height}")
        self.window.minsize(min_width, min_height)
        self.window.resizable(True, True)
        
        # Make modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center on parent
        parent_x = parent.winfo_x() if parent.winfo_x() > 0 else 100
        parent_y = parent.winfo_y() if parent.winfo_y() > 0 else 100
        parent_width = parent.winfo_width() if parent.winfo_width() > 1 else 800
        parent_height = parent.winfo_height() if parent.winfo_height() > 1 else 600
        
        x = parent_x + (parent_width // 2) - (final_width // 2)
        y = parent_y + (parent_height // 2) - (final_height // 2)
        
        # Ensure window is not positioned off-screen
        x = max(0, min(x, screen_width - final_width))
        y = max(0, min(y, screen_height - final_height))
        
        # Apply final geometry
        self.window.geometry(f"{final_width}x{final_height}+{x}+{y}")
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_interface(self):
        """Create the main interface using 3x3 grid layout."""
        # Set window background color
        self.window.configure(bg="#E8E8E8")  # Light grey background for margins
        
        # Configure window grid - 3x3 layout
        self.window.columnconfigure(0, weight=15, minsize=50)   # Left margin - 15%
        self.window.columnconfigure(1, weight=70, minsize=200)  # Center content - 70% 
        self.window.columnconfigure(2, weight=15, minsize=50)   # Right margin - 15%
        
        self.window.rowconfigure(0, weight=15, minsize=50)      # Top margin - 15%
        self.window.rowconfigure(1, weight=70, minsize=200)     # Center content - 70%
        self.window.rowconfigure(2, weight=15, minsize=60)      # Bottom margin - 15% (increased for buttons)
        
        # Create center content frame (row=1, col=1)
        self.main_frame = ttk.Frame(self.window, style="Content.TFrame")
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # Configure frame style for better appearance
        try:
            style = ttk.Style()
            style.configure('Content.TFrame', background='#FFFFFF', relief='raised', borderwidth=1)
        except:
            pass
        
        # Configure main frame grid for title, content, and button areas
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0)  # Title area - fixed height
        self.main_frame.rowconfigure(1, weight=1)  # Content area - expandable
        self.main_frame.rowconfigure(2, weight=0)  # Button area - fixed height
        
        # Title with custom font
        title_label = ttk.Label(self.main_frame, text="Create New Character", font=self.caslon_title_font)
        title_label.grid(row=0, column=0, pady=(15, 20), sticky="ew")
        
        # Content container for the notebook
        content_container = ttk.Frame(self.main_frame)
        content_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # Configure content container
        content_container.columnconfigure(0, weight=1)
        content_container.rowconfigure(0, weight=1)
        
        # Notebook for steps
        self.notebook = ttk.Notebook(content_container)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        
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
        
        # Create button frames in bottom left and right grid cells
        button_width = 15  # Standard button width in characters
        
        # Previous button in bottom left (row=2, col=0) - centered in cell
        prev_frame = ttk.Frame(self.window)
        prev_frame.grid(row=2, column=0, sticky="nsew")
        prev_frame.grid_rowconfigure(0, weight=1)
        prev_frame.grid_columnconfigure(0, weight=1)
        
        self.prev_button = ttk.Button(prev_frame, text="Previous", command=self._prev_step, width=button_width)
        self.prev_button.configure(style="Custom.TButton")
        self.prev_button.grid(row=0, column=0)
        
        # Next/Create button in bottom right (row=2, col=2) - centered in cell
        next_frame = ttk.Frame(self.window)
        next_frame.grid(row=2, column=2, sticky="nsew")
        next_frame.grid_rowconfigure(0, weight=1)
        next_frame.grid_columnconfigure(0, weight=1)
        
        self.next_button = ttk.Button(next_frame, text="Next", command=self._next_step, width=button_width)
        self.next_button.configure(style="Custom.TButton")
        self.next_button.grid(row=0, column=0)
        
        self.create_button = ttk.Button(next_frame, text="Create Character", command=self._create_character, width=button_width)
        self.create_button.configure(style="Custom.TButton")
        # Don't grid initially - will be managed by tab changes
        
        # Initial button state (first tab)
        self.prev_button.config(state=tk.DISABLED)
        
        # Configure button style
        self._setup_button_style()
        
        # Bind tab change events
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _setup_button_style(self):
        """Setup custom button styling."""
        try:
            style = ttk.Style()
            style.configure('Custom.TButton', 
                          font=self.caslon_button_font,
                          padding=(15, 8))
        except Exception as e:
            logger.warning(f"Button style setup failed: {e}")
    
    def _update_button_layout(self):
        """Update button layout based on current tab."""
        current_tab = self.notebook.index("current")
        
        # Update Previous button state
        if current_tab > 0:
            self.prev_button.config(state=tk.NORMAL)
        else:
            self.prev_button.config(state=tk.DISABLED)
        
        # Switch between Next and Create button in right frame
        if current_tab == 4:  # Last tab
            self.next_button.grid_forget()
            self.create_button.grid(row=0, column=0)
        else:
            self.create_button.grid_forget()
            self.next_button.grid(row=0, column=0)
    
    def _setup_step1_basic_info(self):
        """Setup basic character information step."""
        # Container with proper spacing
        content_frame = ttk.Frame(self.step1_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Character name
        ttk.Label(content_frame, text="Character Name:", font=self.caslon_large_font).pack(anchor=tk.W, pady=(5, 5))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(content_frame, textvariable=self.name_var, font=self.caslon_font, width=50)
        name_entry.pack(fill=tk.X, pady=(0, 15))
        name_entry.focus()
        
        # Save slot info
        if self.save_slot:
            ttk.Label(content_frame, text=f"Save Slot: {self.save_slot}", font=self.caslon_font).pack(anchor=tk.W, pady=(0, 10))
        
        # Notes
        ttk.Label(content_frame, text="Character Notes (optional):", font=self.caslon_large_font).pack(anchor=tk.W, pady=(10, 5))
        self.notes_text = tk.Text(content_frame, height=12, wrap=tk.WORD, font=self.caslon_font)
        self.notes_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for notes
        notes_scrollbar = ttk.Scrollbar(self.step1_frame, command=self.notes_text.yview)
        self.notes_text.config(yscrollcommand=notes_scrollbar.set)
    
    def _setup_step2_race(self):
        """Setup race selection step."""
        # Clear frame
        for widget in self.step2_frame.winfo_children():
            widget.destroy()
        
        # Container with proper spacing
        content_frame = ttk.Frame(self.step2_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        ttk.Label(content_frame, text="Choose your character's race:", font=self.caslon_large_font).pack(anchor=tk.W, pady=(5, 10))
        
        # Race list
        race_frame = ttk.Frame(content_frame)
        race_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side: race list
        list_frame = ttk.Frame(race_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 15))
        
        ttk.Label(list_frame, text="Races:", font=self.caslon_font).pack(anchor=tk.W, pady=(0, 5))
        self.race_listbox = tk.Listbox(list_frame, font=self.caslon_font, selectmode=tk.SINGLE, width=25)
        self.race_listbox.pack(fill=tk.BOTH, expand=True)
        self.race_listbox.bind("<<ListboxSelect>>", self._on_race_select)
        
        for race in self.races:
            self.race_listbox.insert(tk.END, race.name)
        
        # Right side: race details
        self.race_details_frame = ttk.Frame(race_frame)
        self.race_details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(self.race_details_frame, text="Race Details:", font=self.caslon_font).pack(anchor=tk.W, pady=(0, 5))
        self.race_details_text = tk.Text(self.race_details_frame, wrap=tk.WORD, state=tk.DISABLED, 
                                        font=self.caslon_font, bg='#f8f8f8')
        self.race_details_text.pack(fill=tk.BOTH, expand=True)
    
    def _setup_step3_class(self):
        """Setup class selection step."""
        # Clear frame
        for widget in self.step3_frame.winfo_children():
            widget.destroy()
        
        # Container with proper spacing
        content_frame = ttk.Frame(self.step3_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        ttk.Label(content_frame, text="Choose your character's class:", font=self.caslon_large_font).pack(anchor=tk.W, pady=(5, 10))
        
        # Class layout
        class_frame = ttk.Frame(content_frame)
        class_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side: class list
        list_frame = ttk.Frame(class_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 15))
        
        ttk.Label(list_frame, text="Classes:", font=self.caslon_font).pack(anchor=tk.W, pady=(0, 5))
        self.class_listbox = tk.Listbox(list_frame, font=self.caslon_font, selectmode=tk.SINGLE, width=25)
        self.class_listbox.pack(fill=tk.BOTH, expand=True)
        self.class_listbox.bind("<<ListboxSelect>>", self._on_class_select)
        
        for cls in self.classes:
            self.class_listbox.insert(tk.END, cls.name)
        
        # Right side: class details
        details_frame = ttk.Frame(class_frame)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(details_frame, text="Class Details:", font=self.caslon_font).pack(anchor=tk.W, pady=(0, 5))
        self.class_details_text = tk.Text(details_frame, wrap=tk.WORD, state=tk.DISABLED, 
                                         font=self.caslon_font, bg='#f8f8f8')
        self.class_details_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Subclass selection
        ttk.Label(details_frame, text="Subclass (choose at level 3):", font=self.caslon_font).pack(anchor=tk.W, pady=(0, 5))
        self.subclass_var = tk.StringVar()
        self.subclass_combo = ttk.Combobox(details_frame, textvariable=self.subclass_var, state="readonly", font=self.caslon_font)
        self.subclass_combo.pack(fill=tk.X)
    
    def _setup_step4_background(self):
        """Setup background selection step.""" 
        # Clear frame
        for widget in self.step4_frame.winfo_children():
            widget.destroy()
        
        # Container with proper spacing
        content_frame = ttk.Frame(self.step4_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        ttk.Label(content_frame, text="Choose your character's background:", font=self.caslon_large_font).pack(anchor=tk.W, pady=(5, 10))
        
        # Background layout
        bg_frame = ttk.Frame(content_frame)
        bg_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side: background list
        list_frame = ttk.Frame(bg_frame)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 15))
        
        ttk.Label(list_frame, text="Backgrounds:", font=self.caslon_font).pack(anchor=tk.W, pady=(0, 5))
        self.background_listbox = tk.Listbox(list_frame, font=self.caslon_font, selectmode=tk.SINGLE, width=25)
        self.background_listbox.pack(fill=tk.BOTH, expand=True)
        self.background_listbox.bind("<<ListboxSelect>>", self._on_background_select)
        
        for bg in self.backgrounds:
            self.background_listbox.insert(tk.END, bg.name)
        
        # Right side: background details
        self.background_details_frame = ttk.Frame(bg_frame)
        self.background_details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(self.background_details_frame, text="Background Details:", font=self.caslon_font).pack(anchor=tk.W, pady=(0, 5))
        self.background_details_text = tk.Text(self.background_details_frame, wrap=tk.WORD, state=tk.DISABLED, 
                                              font=self.caslon_font, bg='#f8f8f8')
        self.background_details_text.pack(fill=tk.BOTH, expand=True)
    
    def _setup_step5_abilities(self):
        """Setup ability score generation step."""
        # Clear frame
        for widget in self.step5_frame.winfo_children():
            widget.destroy()
        
        # Container with proper spacing
        content_frame = ttk.Frame(self.step5_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        ttk.Label(content_frame, text="Generate Ability Scores:", font=self.caslon_large_font).pack(anchor=tk.W, pady=(5, 10))
        
        # Generation method
        method_frame = ttk.Frame(content_frame)
        method_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(method_frame, text="Method:", font=self.caslon_font).pack(side=tk.LEFT)
        self.method_var = tk.StringVar(value="standard")
        method_combo = ttk.Combobox(method_frame, textvariable=self.method_var, 
                                  values=["standard", "classic", "heroic"], 
                                  state="readonly", font=self.caslon_font)
        method_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Generate button
        generate_btn = ttk.Button(method_frame, text="Generate", command=self._generate_abilities)
        generate_btn.configure(style="Custom.TButton")
        generate_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Ability scores display
        self.abilities_frame = ttk.Frame(content_frame)
        self.abilities_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.ability_vars = {}
        abilities = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        
        for i, ability in enumerate(abilities):
            row = i // 3
            col = i % 3
            
            ability_frame = ttk.Frame(self.abilities_frame)
            ability_frame.grid(row=row, column=col, padx=15, pady=8, sticky=tk.W+tk.E)
            
            ttk.Label(ability_frame, text=f"{ability}:", font=self.caslon_font).pack(side=tk.LEFT)
            
            var = tk.StringVar(value="10")
            self.ability_vars[ability.lower()] = var
            score_label = ttk.Label(ability_frame, textvariable=var, font=self.caslon_large_font)
            score_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Configure grid weights
        self.abilities_frame.columnconfigure(0, weight=1)
        self.abilities_frame.columnconfigure(1, weight=1)
        self.abilities_frame.columnconfigure(2, weight=1)
        
        # Summary
        summary_label = ttk.Label(content_frame, text="Character Summary:", font=self.caslon_large_font)
        summary_label.pack(anchor=tk.W, pady=(15, 5))
        
        self.summary_text = tk.Text(content_frame, wrap=tk.WORD, state=tk.DISABLED, 
                                   font=self.caslon_font, bg='#f8f8f8')
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
        # Check if UI is fully initialized
        if not hasattr(self, 'summary_text'):
            return
        if not all([self.selected_race, self.selected_class, self.selected_background]):
            return
        
        summary = "Character Summary:\n\n"
        summary += f"Name: {self.name_var.get() or 'Unnamed'}\n"
        summary += f"Race: {self.selected_race.name}\n"
        summary += f"Class: {self.selected_class.name}\n"
        if self.selected_subclass:
            summary += f"Subclass: {self.selected_subclass['name']}\n"
        summary += f"Background: {self.selected_background.name}\n\n"
        
        summary += "Ability Scores (with racial bonuses):\n"
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            base_score = self.character_data[ability]
            racial_bonus = self.selected_race.ability_score_increases.get(ability, 0) if self.selected_race.ability_score_increases else 0
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
        self.character_data["race_id"] = self.selected_race.id
        
        # Update details display
        race_text = f"{self.selected_race.name}\n\n"
        race_text += f"Size: {self.selected_race.size}\n"
        race_text += f"Speed: {self.selected_race.speed} feet\n\n"
        race_text += f"Description:\n{self.selected_race.description}\n\n"
        
        if self.selected_race.ability_score_increases:
            race_text += "Ability Score Increases:\n"
            for ability, bonus in self.selected_race.ability_score_increases.items():
                race_text += f"  {ability.title()}: +{bonus}\n"
            race_text += "\n"
        
        if self.selected_race.traits:
            race_text += "Racial Traits:\n"
            for trait, description in self.selected_race.traits.items():
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
        self.character_data["class_id"] = self.selected_class.id
        
        # Update subclass options
        subclasses = self.selected_class.subclasses or []
        self.subclass_combo['values'] = [sub['name'] for sub in subclasses]
        if subclasses:
            self.subclass_combo.set(subclasses[0]['name'])
            self.selected_subclass = subclasses[0]
            self.character_data["subclass_id"] = subclasses[0]["id"]
        
        # Update details display
        class_text = f"{self.selected_class.name}\n\n"
        class_text += f"Hit Die: d{self.selected_class.hit_die}\n"
        class_text += f"Primary Ability: {self.selected_class.primary_ability}\n\n"
        class_text += f"Description:\n{self.selected_class.description}\n\n"
        
        class_text += "Proficiencies:\n"
        if self.selected_class.armor_proficiencies:
            class_text += f"  Armor: {', '.join(self.selected_class.armor_proficiencies)}\n"
        if self.selected_class.weapon_proficiencies:
            class_text += f"  Weapons: {', '.join(self.selected_class.weapon_proficiencies)}\n"
        if self.selected_class.saving_throw_proficiencies:
            class_text += f"  Saving Throws: {', '.join(self.selected_class.saving_throw_proficiencies)}\n"
        
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
        self.character_data["background_id"] = self.selected_background.id
        
        # Update details display
        bg_text = f"{self.selected_background.name}\n\n"
        bg_text += f"Description:\n{self.selected_background.description}\n\n"
        
        if self.selected_background.skill_proficiencies:
            bg_text += f"Skill Proficiencies: {', '.join(self.selected_background.skill_proficiencies)}\n"
        if self.selected_background.tool_proficiencies:
            bg_text += f"Tool Proficiencies: {', '.join(self.selected_background.tool_proficiencies)}\n"
        
        bg_text += f"\nFeature: {self.selected_background.feature_name}\n"
        bg_text += f"{self.selected_background.feature_description}"
        
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
        
        # Update button layout
        self._update_button_layout()
    
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
            character_name = self.character_data['name']  # Store name before creation
            character = self.game_engine.create_new_character(self.character_data, self.save_slot or 1)
            
            messagebox.showinfo("Success", f"Character '{character_name}' created successfully!")
            
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
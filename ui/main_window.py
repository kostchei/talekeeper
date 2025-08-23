"""
File: ui/main_window.py
Path: /ui/main_window.py

Main application window for TaleKeeper Desktop.
Manages the primary UI layout and navigation between screens.

Pseudo Code:
1. Initialize main window with menu bar and status bar
2. Create notebook widget for tabbed interface
3. Initialize different game screens (character, exploration, combat)
4. Handle window events and navigation
5. Manage save/load operations and settings

AI Agents: Main UI controller and navigation hub.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any
from loguru import logger

from core.game_engine import GameEngine
from core.dtos import SaveSlotDTO
from ui.character_creator import CharacterCreatorWindow
from ui.game_screen import GameScreen
from ui.combat_screen import CombatScreen


class MainWindow:
    """
    Main application window managing all UI screens.
    
    AI Agents: Add new screens and navigation options here.
    """
    
    def __init__(self, root: tk.Tk, game_engine: GameEngine):
        """Initialize the main window."""
        self.root = root
        self.game_engine = game_engine
        
        # Apply theme
        self.style = ttk.Style()
        self._setup_theme()
        
        # Setup main window
        self._setup_window()
        self._create_menu()
        self._create_main_interface()
        self._create_status_bar()
        
        # Initialize screens
        self.character_creator: Optional[CharacterCreatorWindow] = None
        self.game_screen: Optional[GameScreen] = None
        self.combat_screen: Optional[CombatScreen] = None
        
        # Show start screen
        self._show_start_screen()
        
        logger.info("Main window initialized")
    
    def _setup_theme(self):
        """Setup the application theme."""
        # Configure ttk styles for dark theme
        self.style.theme_use('clam')
        
        # Dark theme colors
        bg_color = '#2b2b2b'
        fg_color = '#ffffff'
        select_color = '#404040'
        accent_color = '#4a90e2'
        
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, foreground=fg_color)
        self.style.configure('TButton', background=select_color, foreground=fg_color)
        self.style.configure('TNotebook', background=bg_color, tabposition='n')
        self.style.configure('TNotebook.Tab', background=select_color, foreground=fg_color, padding=[8, 4])
        self.style.configure('Heading.TLabel', font=('Arial', 12, 'bold'))
        
        # Configure root window
        self.root.configure(bg=bg_color)
    
    def _setup_window(self):
        """Setup main window properties."""
        self.root.title("TaleKeeper - D&D 2024 Adventure")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Center the window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Character", command=self._new_character)
        game_menu.add_command(label="Load Character", command=self._load_character)
        game_menu.add_separator()
        game_menu.add_command(label="Save Game", command=self._save_game)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self._exit_application)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Dice Roller", command=self._open_dice_roller)
        tools_menu.add_command(label="Settings", command=self._open_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_main_interface(self):
        """Create the main interface with notebook tabs."""
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Start screen (shown initially)
        self.start_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.start_frame, text="Start")
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=5)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        # Character info (shown when character is loaded)
        self.character_info = ttk.Label(self.status_bar, text="")
        self.character_info.pack(side=tk.RIGHT)
    
    def _show_start_screen(self):
        """Display the start screen with save slot options."""
        # Clear the start frame
        for widget in self.start_frame.winfo_children():
            widget.destroy()
        
        # Title
        title_label = ttk.Label(self.start_frame, text="TaleKeeper", style='Heading.TLabel')
        title_label.pack(pady=20)
        
        subtitle_label = ttk.Label(self.start_frame, text="D&D 2024 Adventure")
        subtitle_label.pack(pady=(0, 30))
        
        # Save slots frame
        slots_frame = ttk.Frame(self.start_frame)
        slots_frame.pack(expand=True)
        
        # Get save slots from game engine
        save_slots = self.game_engine.get_save_slots()
        
        for i in range(1, 11):  # 10 save slots
            slot_data = next((slot for slot in save_slots if slot.slot_number == i), None)
            self._create_save_slot_button(slots_frame, i, slot_data)
    
    def _create_save_slot_button(self, parent: ttk.Frame, slot_number: int, slot_data: Optional[SaveSlotDTO]):
        """Create a save slot button."""
        slot_frame = ttk.Frame(parent)
        slot_frame.pack(fill=tk.X, padx=20, pady=2)
        
        if slot_data and slot_data.is_occupied:
            # Occupied slot
            text = f"Slot {slot_number}: {slot_data.character_name} (Level {slot_data.character_level})"
            if slot_data.last_played:
                text += f" - Last played: {str(slot_data.last_played)[:10]}"
            
            button = ttk.Button(
                slot_frame, 
                text=text,
                command=lambda s=slot_number: self._load_character_from_slot(s)
            )
            button.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Delete button
            delete_btn = ttk.Button(
                slot_frame,
                text="Delete",
                command=lambda s=slot_number: self._delete_save_slot(s)
            )
            delete_btn.pack(side=tk.RIGHT, padx=(5, 0))
        else:
            # Empty slot
            text = f"Slot {slot_number}: Empty"
            button = ttk.Button(
                slot_frame,
                text=text,
                command=lambda s=slot_number: self._create_new_character_in_slot(s)
            )
            button.pack(fill=tk.X)
    
    def _new_character(self):
        """Start new character creation."""
        self._show_character_creator()
    
    def _load_character(self):
        """Load existing character."""
        # This could open a dialog to select save slot
        pass
    
    def _load_character_from_slot(self, slot_number: int):
        """Load character from specific save slot."""
        character = self.game_engine.load_character(slot_number)
        if character:
            self._show_game_interface(character)
        else:
            messagebox.showerror("Error", f"Failed to load character from slot {slot_number}")
    
    def _create_new_character_in_slot(self, slot_number: int):
        """Create new character in specific save slot."""
        self._show_character_creator(slot_number)
    
    def _delete_save_slot(self, slot_number: int):
        """Delete a save slot after confirmation."""
        result = messagebox.askyesno(
            "Delete Save",
            f"Are you sure you want to delete save slot {slot_number}? This cannot be undone."
        )
        if result:
            # TODO: Implement delete functionality
            self._show_start_screen()  # Refresh the screen
    
    def _show_character_creator(self, save_slot: Optional[int] = None):
        """Show character creation window."""
        if self.character_creator:
            self.character_creator.window.lift()
            return
        
        self.character_creator = CharacterCreatorWindow(
            self.root, 
            self.game_engine, 
            save_slot,
            self._on_character_created
        )
    
    def _on_character_created(self, character):
        """Called when character creation is complete."""
        self.character_creator = None
        self._show_game_interface(character)
    
    def _show_game_interface(self, character):
        """Show the main game interface with character loaded."""
        # Remove start tab
        if "Start" in [self.notebook.tab(i, "text") for i in range(self.notebook.index("end"))]:
            for i in range(self.notebook.index("end")):
                if self.notebook.tab(i, "text") == "Start":
                    self.notebook.forget(i)
                    break
        
        # Create game screen tab
        if not hasattr(self, 'game_tab'):
            self.game_tab = ttk.Frame(self.notebook)
            self.notebook.add(self.game_tab, text="Adventure")
            
            self.game_screen = GameScreen(self.game_tab, self.game_engine, character)
        
        # Update status bar
        self.character_info.config(
            text=f"{character.name} - Level {character.level} {character.race_name if character.race_name else ''} {character.class_name if character.class_name else ''}"
        )
        
        # Select the game tab
        self.notebook.select(self.game_tab)
        
        logger.info(f"Game interface shown for character: {character.name}")
    
    def _save_game(self):
        """Save the current game."""
        if self.game_engine.current_character:
            self.game_engine.save_game()
            self.status_label.config(text="Game saved")
            self.root.after(3000, lambda: self.status_label.config(text="Ready"))
        else:
            messagebox.showwarning("No Game", "No character loaded to save.")
    
    def _open_dice_roller(self):
        """Open dice roller tool."""
        # TODO: Implement dice roller window
        pass
    
    def _open_settings(self):
        """Open settings window."""
        # TODO: Implement settings window
        pass
    
    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About TaleKeeper",
            "TaleKeeper Desktop v1.0\n\n"
            "A single-player D&D 2024 adventure game.\n\n"
            "Created with Python and Tkinter."
        )
    
    def _exit_application(self):
        """Exit the application."""
        if self.game_engine.current_character:
            result = messagebox.askyesno("Exit", "Do you want to save before exiting?")
            if result:
                self.game_engine.save_game()
        
        self.game_engine.shutdown()
        self.root.quit()
    
    def update_status(self, message: str):
        """Update the status bar message."""
        self.status_label.config(text=message)
        logger.info(f"Status: {message}")
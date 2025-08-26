# TaleKeeper PyQt6 Migration Plan

## Overview
This document outlines the strategy for migrating TaleKeeper from Tkinter to PyQt6, implementing the animated game layout specified in `ui_plan.md`. The migration will maintain compatibility with existing game systems while introducing modern UI capabilities.

## Current Architecture Analysis

### Existing Structure
```
TaleKeeper/
├── core/
│   ├── game_engine.py      # Central coordinator - NO CHANGES NEEDED
│   ├── database.py         # SQLAlchemy ORM - NO CHANGES NEEDED  
│   └── dtos.py            # Data transfer objects - NO CHANGES NEEDED
├── models/                # SQLAlchemy models - NO CHANGES NEEDED
├── services/              # Business logic - NO CHANGES NEEDED
├── data/                  # JSON game data - NO CHANGES NEEDED
└── ui/                    # UI layer - REQUIRES COMPLETE REWRITE
    ├── main_window.py     # Tkinter main window
    ├── character_creator.py
    ├── game_screen.py
    └── combat_screen.py
```

### Integration Points
- **GameEngine**: Core business logic coordinator (unchanged)
- **Database Layer**: SQLAlchemy models and session management (unchanged)
- **Services**: Dice rolling, combat mechanics (unchanged)
- **Models**: Character, Monster, Item classes (unchanged)

## Migration Strategy

### Phase 1: Foundation Setup
**Files to Create:**
- `ui/pyqt_main_window.py` - PyQt6 replacement for main_window.py
- `ui/pyqt_game_page.py` - Animated game layout from ui_plan.md
- `requirements_pyqt6.txt` - PyQt6 dependencies

**Dependencies to Add:**
```python
# Add to requirements.txt
PyQt6>=6.5.0
PyQt6-tools>=6.5.0  # For designer tools if needed
```

### Phase 2: Core UI Components

#### 2.1 Main Window Migration (`ui/main_window.py` → `ui/pyqt_main_window.py`)

**Current Tkinter Components → PyQt6 Equivalents:**

| Tkinter Component | PyQt6 Equivalent | Notes |
|------------------|------------------|-------|
| `tk.Tk()` | `QMainWindow` | Main application window |
| `ttk.Notebook` | `QTabWidget` | Tab management |
| `ttk.Frame` | `QWidget`/`QFrame` | Container widgets |
| `ttk.Label` | `QLabel` | Text display |
| `ttk.Button` | `QPushButton` | Clickable buttons |
| `ttk.Style` | `setStyleSheet()` | Theming system |
| `tk.Menu` | `QMenuBar` | Menu system |

**Key Methods to Migrate:**
```python
# Tkinter → PyQt6 Method Mapping
MainWindow.__init__() → PyQtMainWindow.__init__()
_setup_theme() → _apply_stylesheet()
_create_menu() → _create_menubar()
_show_start_screen() → _show_start_page()
_show_game_interface() → _show_game_page()
```

#### 2.2 Animated Game Layout (`ui_plan.md` → `ui/pyqt_game_page.py`)

**Layout Specifications:**
- **Window Size**: 1920x1080 minimum
- **Margins**: 5% (96px horizontal, 54px vertical)
- **Usable Space**: 1728x972

**Component Breakdown:**

```python
# Main Layout Structure
QMainWindow
├── Central QWidget
    ├── QVBoxLayout (main_layout)
        ├── Menu Section (648x200)
        │   ├── Menu Frame
        │   └── Dropdown Menu (648x300, hidden)
        ├── QSplitter (horizontal, main_splitter)
        │   ├── Character Frame (648→1296 x 972) [ANIMATED]
        │   ├── Encounter Frame (648 x 972)
        │   └── QSplitter (vertical, right_splitter)
        │       ├── Log Frame (432 x 486)
        │       └── Equipment Frame (432→1080 x 486) [ANIMATED]
        └── Action Cards Frame (1728 x 300)
```

**Animation Implementation:**
```python
# Character Sheet Animation (648px ↔ 1296px)
QPropertyAnimation(character_frame, b"geometry")
- Duration: 400ms
- Easing: QEasingCurve.Type.OutCubic
- Property: Frame width

# Equipment Panel Animation (432px ↔ 1080px)  
QPropertyAnimation(equipment_frame, b"geometry")
- Duration: 400ms
- Easing: QEasingCurve.Type.OutCubic
- Property: Frame width
```

### Phase 3: Screen-Specific Migrations

#### 3.1 Character Creator (`ui/character_creator.py`)

**Migration Strategy:**
- Replace Tkinter form widgets with PyQt6 equivalents
- Maintain existing GameEngine integration
- Preserve character creation workflow

**Component Mapping:**
```python
# Tkinter → PyQt6
ttk.Combobox → QComboBox
ttk.Entry → QLineEdit
ttk.Spinbox → QSpinBox
ttk.Scrolledtext → QTextEdit
ttk.Treeview → QTreeWidget/QTableWidget
```

#### 3.2 Combat Screen (`ui/combat_screen.py`)

**Integration with Animated Layout:**
- Combat interface becomes part of Encounter Pane
- Initiative tracker in Equipment Panel (expanded)
- Action buttons in Action Cards area
- Combat log in Log Pane

#### 3.3 Game Screen (`ui/game_screen.py`)

**Integration Strategy:**
- Exploration/story content in Encounter Pane
- Character status in Character Sheet
- Inventory in Equipment Panel
- Action options in Action Cards

### Phase 4: Integration Architecture

#### 4.1 GameEngine Integration

**No Changes Required to Core Logic:**
```python
# Existing GameEngine methods work unchanged
game_engine.load_character(slot_number)
game_engine.save_game()
game_engine.get_save_slots()
game_engine.current_character
```

**PyQt6 Signal/Slot Integration:**
```python
class PyQtGamePage(QMainWindow):
    def __init__(self, game_engine: GameEngine):
        self.game_engine = game_engine
        
    def _save_game(self):
        """Connected to Save button signal"""
        self.game_engine.save_game()
        self.log_text.append("Game saved")
        
    def _load_character(self, slot: int):
        """Connected to character selection signal"""
        char = self.game_engine.load_character(slot)
        self._update_character_display(char)
```

#### 4.2 Data Flow Architecture

```
User Input → PyQt6 Widgets → Signal/Slot → GameEngine Methods → Database
                ↓
            UI Updates ← Data Updates ← GameEngine State ← Database Response
```

### Phase 5: Styling and Theming

#### 5.1 Dark Theme Implementation

**PyQt6 Stylesheet:**
```css
QMainWindow {
    background-color: #1a1a1a;
    color: #ffffff;
}

QFrame {
    background-color: #2d2d2d;
    border: 2px solid #444444;
    border-radius: 8px;
}

QPushButton {
    background-color: #404040;
    color: #ffffff;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 8px;
}

QPushButton:hover {
    background-color: #505050;
}
```

#### 5.2 Font Integration

**Custom Font Loading:**
```python
from PyQt6.QtGui import QFontDatabase

# Load custom fonts from assets/
QFontDatabase.addApplicationFont("assets/CaslonAntique.ttf")
QFontDatabase.addApplicationFont("assets/CaslonAntique-Bold.ttf")
```

## Implementation Phases

### Phase 1: Setup (Day 1)
1. Add PyQt6 dependencies to requirements.txt
2. Create basic PyQt6 main window structure
3. Test PyQt6 integration with GameEngine

### Phase 2: Core Layout (Days 2-3)
1. Implement animated game layout from ui_plan.md
2. Create sliding panels with QPropertyAnimation
3. Integrate menu system and basic navigation

### Phase 3: Game Integration (Days 4-5)
1. Connect character data to character panel
2. Implement combat interface integration
3. Add game log and equipment displays

### Phase 4: Feature Parity (Days 6-7)
1. Migrate character creator to PyQt6
2. Implement save/load functionality
3. Add settings and preferences

### Phase 5: Polish (Day 8)
1. Apply consistent theming
2. Add animations and transitions
3. Performance optimization and testing

## File Structure After Migration

```
TaleKeeper/
├── core/                  # Unchanged
├── models/                # Unchanged  
├── services/              # Unchanged
├── data/                  # Unchanged
├── ui/
│   ├── tkinter/           # Legacy Tkinter UI (moved)
│   │   ├── main_window.py
│   │   ├── character_creator.py
│   │   ├── game_screen.py
│   │   └── combat_screen.py
│   └── pyqt6/            # New PyQt6 UI
│       ├── main_window.py
│       ├── game_page.py   # Animated layout
│       ├── character_creator.py
│       └── dialogs/
├── main.py               # Modified to choose UI framework
└── main_pyqt6.py        # PyQt6 entry point
```

## Entry Point Strategy

### Dual UI Support
```python
# main.py - Modified to support both UIs
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ui', choices=['tkinter', 'pyqt6'], 
                       default='pyqt6', help='UI framework to use')
    args = parser.parse_args()
    
    if args.ui == 'tkinter':
        from ui.tkinter.main_window import MainWindow as TkMainWindow
        # Launch Tkinter version
    else:
        from ui.pyqt6.main_window import MainWindow as PyQtMainWindow  
        # Launch PyQt6 version
```

## Compatibility and Testing

### Backwards Compatibility
- Existing save files remain compatible
- Character data unchanged
- Game mechanics preserved

### Testing Strategy
1. Unit tests for PyQt6 components
2. Integration tests with GameEngine
3. UI automation tests for animations
4. Performance benchmarking

## Migration Benefits

### Immediate Advantages
- Modern, responsive UI with animations
- Better scaling and DPI support
- Professional appearance
- Improved user experience

### Technical Benefits  
- More flexible layout system
- Better styling capabilities
- Rich widget ecosystem
- Cross-platform consistency

### Future Possibilities
- Custom widgets and controls
- Advanced graphics and effects
- Plugin architecture
- Theme customization system

## Risk Mitigation

### Potential Issues
1. **Animation Performance**: Test on lower-end hardware
2. **Memory Usage**: Monitor PyQt6 memory footprint vs Tkinter
3. **Learning Curve**: PyQt6 signal/slot system different from Tkinter
4. **Dependencies**: PyQt6 larger than Tkinter (built-in)

### Mitigation Strategies
1. Keep Tkinter version available as fallback
2. Gradual migration with feature flags
3. Performance testing on target hardware
4. Documentation and code comments for PyQt6 patterns

## Conclusion

This migration plan preserves the existing TaleKeeper architecture while introducing a modern, animated UI. The GameEngine and business logic remain unchanged, ensuring stability while dramatically improving the user experience through PyQt6's advanced capabilities.
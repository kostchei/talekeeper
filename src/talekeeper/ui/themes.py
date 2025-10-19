# core
# category: core
"""UI theme definitions for TaleKeeper.

Provides light and dark palettes inspired by the watercolor palette in art/pallette.jpg.
Each theme contains colors for background, text, and accents extracted from the
medieval fantasy watercolor palette to create immersive D&D-appropriate theming.
"""

from __future__ import annotations

# Light theme based on Light_.JPG color palette
LIGHT_THEME = {
    # Base colors from Light_.JPG - warm, bright tones with higher contrast
    "background": "#faf2e7",          # Brighter warm cream background
    "surface": "#f4e5d4",             # Light warm beige for panels
    "text": "#2b211c",                # Deep brown text for stronger contrast
    "text_secondary": "#4c3d35",      # Muted brown-gray for secondary text

    # Accent colors from Light_.JPG swatches
    "accent_primary": "#7c4f32",      # Rich reddish-brown from palette
    "accent_secondary": "#a45f38",    # Warm orange-brown accent
    "accent_tertiary": "#3f7663",     # Blue-teal accent used for selections
    "accent_quaternary": "#cf8a5b",   # Light orange tone

    # UI element colors
    "button": "#a45f38",              # Warm orange-brown for buttons
    "button_hover": "#bb7346",        # Lighter on hover
    "button_pressed": "#7c4f32",      # Darker when pressed
    "border": "#c9b59c",              # Soft but pronounced border
    "selection": "#3f7663",           # Blue-teal for selections, links, active states
    "highlight": "#fff9f1",           # Even lighter warm highlight
}

# Dark theme based on Dark.JPG color palette
DARK_THEME = {
    # Base colors from Dark.JPG - deep, rich tones with elevated contrast
    "background": "#1f150d",          # Deeper brown-black for strong contrast
    "surface": "#2d2116",             # Slightly lighter dark brown for panels
    "text": "#f2e6cf",                # Bright warm cream text for readability
    "text_secondary": "#d6c6ac",      # Muted cream for secondary text

    # Accent colors from Dark.JPG swatches
    "accent_primary": "#5b4633",      # Medium brown from palette
    "accent_secondary": "#74543c",    # Warm brown accent
    "accent_tertiary": "#3d6d5a",     # Blue-teal from palette (use for all blue elements)
    "accent_quaternary": "#8a6748",   # Warm brown-gray tone

    # UI element colors for dark theme
    "button": "#5b4633",              # Medium brown for buttons
    "button_hover": "#74543c",        # Lighter brown on hover
    "button_pressed": "#3d2d20",      # Darker when pressed
    "border": "#4c3a2a",              # Pronounced dark brown border
    "selection": "#3d6d5a",           # Blue-teal for selections, links, active states
    "highlight": "#302217",           # Subtle dark highlight
}

def build_stylesheet(palette: dict[str, str]) -> str:
    """Return a comprehensive PyQt6 stylesheet for the provided color palette.
    
    Args:
        palette: Dictionary containing color definitions for the theme
        
    Returns:
        Complete CSS stylesheet string for PyQt6 widgets
    """
    return f"""
    /* Main Window and Base Styling */
    QMainWindow {{
        background-color: {palette['background']};
        color: {palette['text']};
        font-family: 'IM FELL Great Primer Roman', 'Times New Roman', serif;
        font-size: 12pt;
    }}
    
    QWidget {{
        background-color: {palette['background']};
        color: {palette['text']};
        font-family: 'IM FELL Great Primer Roman', 'Times New Roman', serif;
    }}
    
    /* Panels and Containers */
    QFrame {{
        background-color: {palette['surface']};
        border: 1px solid {palette['border']};
        border-radius: 4px;
        padding: 1px;
    }}
    
    QScrollArea {{
        background-color: {palette['surface']};
        border: 1px solid {palette['border']};
        border-radius: 4px;
    }}
    
    /* Splitter Handles */
    QSplitter::handle {{
        background-color: {palette['accent_primary']};
        border: 1px solid {palette['border']};
    }}
    
    QSplitter::handle:horizontal {{
        width: 6px;
    }}
    
    QSplitter::handle:vertical {{
        height: 6px;
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {palette['button']};
        color: {palette['text']};
        border: 2px solid {palette['border']};
        border-radius: 6px;
        padding: 1px 2px;
        font-weight: bold;
        font-size: 11pt;
    }}
    
    QPushButton:hover {{
        background-color: {palette['button_hover']};
        border-color: {palette['accent_primary']};
    }}
    
    QPushButton:pressed {{
        background-color: {palette['button_pressed']};
        border-color: {palette['accent_secondary']};
    }}
    
    QPushButton:disabled {{
        background-color: {palette['surface']};
        color: {palette['text_secondary']};
        border-color: {palette['border']};
    }}
    
    /* Text Input Fields */
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {palette['surface']};
        color: {palette['text']};
        border: 2px solid {palette['border']};
        border-radius: 4px;
        padding: 1px;
        selection-background-color: {palette['selection']};
    }}
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {palette['accent_tertiary']};  /* Blue-teal for focus states */
    }}
    
    /* Labels and Text */
    QLabel {{
        color: {palette['text']};
        background-color: transparent;
    }}
    
    QLabel[heading="true"] {{
        font-size: 14pt;
        font-weight: bold;
        color: {palette['accent_primary']};
        margin: 1px 0px;
    }}
    
    /* Lists and Tables */
    QListWidget, QTreeWidget, QTableWidget {{
        background-color: {palette['surface']};
        color: {palette['text']};
        border: 1px solid {palette['border']};
        alternate-background-color: {palette['highlight']};
        selection-background-color: {palette['selection']};
        selection-color: {palette['text']};
    }}
    
    QListWidget::item, QTreeWidget::item, QTableWidget::item {{
        padding: 1px;
        border-bottom: 1px solid {palette['border']};
    }}
    
    QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {{
        background-color: {palette['selection']};
        color: {palette['text']};
    }}
    
    QHeaderView::section {{
        background-color: {palette['accent_primary']};
        color: {palette['text']};
        padding: 1px;
        border: 1px solid {palette['border']};
        font-weight: bold;
    }}
    
    /* Combo Boxes */
    QComboBox {{
        background-color: {palette['surface']};
        color: {palette['text']};
        border: 2px solid {palette['border']};
        border-radius: 4px;
        padding: 1px 2px;
    }}
    
    QComboBox:hover {{
        border-color: {palette['accent_tertiary']};  /* Blue-teal for hover states */
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 8px solid {palette['text']};
        margin-right: 5px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {palette['surface']};
        color: {palette['text']};
        border: 1px solid {palette['border']};
        selection-background-color: {palette['selection']};
    }}
    
    /* Spin Boxes */
    QSpinBox, QDoubleSpinBox {{
        background-color: {palette['surface']};
        color: {palette['text']};
        border: 2px solid {palette['border']};
        border-radius: 4px;
        padding: 1px;
    }}
    
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {palette['accent_tertiary']};
    }}
    
    /* Check Boxes and Radio Buttons */
    QCheckBox, QRadioButton {{
        color: {palette['text']};
        spacing: 5px;
    }}
    
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 16px;
        height: 16px;
        border: 2px solid {palette['border']};
        background-color: {palette['surface']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {palette['accent_tertiary']};
        border-color: {palette['accent_primary']};
    }}
    
    QRadioButton::indicator {{
        border-radius: 8px;
    }}
    
    QRadioButton::indicator:checked {{
        background-color: {palette['accent_tertiary']};
        border-color: {palette['accent_primary']};
    }}
    
    /* Progress Bars */
    QProgressBar {{
        background-color: {palette['surface']};
        border: 2px solid {palette['border']};
        border-radius: 4px;
        text-align: center;
        color: {palette['text']};
    }}
    
    QProgressBar::chunk {{
        background-color: {palette['accent_tertiary']};
        border-radius: 2px;
    }}
    
    /* Sliders */
    QSlider::groove:horizontal {{
        border: 1px solid {palette['border']};
        height: 6px;
        background-color: {palette['surface']};
        border-radius: 3px;
    }}
    
    QSlider::handle:horizontal {{
        background-color: {palette['accent_primary']};
        border: 2px solid {palette['border']};
        width: 16px;
        margin: -6px 0;
        border-radius: 8px;
    }}
    
    QSlider::handle:horizontal:hover {{
        background-color: {palette['accent_secondary']};
    }}
    
    /* Tab Widgets */
    QTabWidget::pane {{
        border: 2px solid {palette['border']};
        background-color: {palette['surface']};
    }}
    
    QTabBar::tab {{
        background-color: {palette['accent_primary']};
        color: {palette['text']};
        padding: 1px 2px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {palette['accent_secondary']};
        border-bottom: 2px solid {palette['accent_secondary']};
    }}
    
    QTabBar::tab:hover {{
        background-color: {palette['accent_tertiary']};
    }}
    
    /* Scroll Bars */
    QScrollBar:vertical {{
        background-color: {palette['surface']};
        width: 16px;
        border: 1px solid {palette['border']};
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {palette['accent_primary']};
        border: 1px solid {palette['border']};
        border-radius: 4px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {palette['accent_secondary']};
    }}
    
    QScrollBar:horizontal {{
        background-color: {palette['surface']};
        height: 16px;
        border: 1px solid {palette['border']};
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {palette['accent_primary']};
        border: 1px solid {palette['border']};
        border-radius: 4px;
        min-width: 20px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {palette['accent_secondary']};
    }}
    
    QScrollBar::add-line, QScrollBar::sub-line {{
        background-color: {palette['surface']};
        border: 1px solid {palette['border']};
    }}
    
    QScrollBar::add-line:hover, QScrollBar::sub-line:hover {{
        background-color: {palette['accent_primary']};
    }}
    
    /* Menu Bar and Menus */
    QMenuBar {{
        background-color: {palette['accent_primary']};
        color: {palette['text']};
        border-bottom: 1px solid {palette['border']};
    }}
    
    QMenuBar::item {{
        padding: 1px 2px;
        background-color: transparent;
    }}
    
    QMenuBar::item:selected {{
        background-color: {palette['accent_secondary']};
    }}
    
    QMenu {{
        background-color: {palette['surface']};
        color: {palette['text']};
        border: 1px solid {palette['border']};
    }}
    
    QMenu::item {{
        padding: 1px 2px;
    }}
    
    QMenu::item:selected {{
        background-color: {palette['selection']};
    }}
    
    /* Tool Tips */
    QToolTip {{
        background-color: {palette['accent_primary']};
        color: {palette['text']};
        border: 1px solid {palette['border']};
        border-radius: 4px;
        padding: 1px;
    }}
    
    /* Status Bar */
    QStatusBar {{
        background-color: {palette['surface']};
        color: {palette['text']};
        border-top: 1px solid {palette['border']};
    }}
    
    /* Character Sheet Skill Styling - No borders, smaller font for tight spaces */
    QFrame#skillEntry {{
        background-color: {palette['surface']};
        border: 1px solid {palette['border']};
        border-radius: 0px;  /* Remove border radius completely */
        margin: 1px 0px;
        padding: 0px;
    }}
    
    QLabel#skillName {{
        color: {palette['text']};
        font-size: 10px;  /* Smaller font for tight spaces */
        font-weight: normal;
        padding: 1px 2px;
        margin: 0px;
    }}
    
    QLabel#skillBonus {{
        color: {palette['accent_tertiary']};  /* Use blue-teal for skill bonuses */
        font-size: 10px;  /* Smaller font to match */
        font-weight: bold;
        padding: 1px 2px;
        margin: 0px;
        min-width: 20px;   /* Even smaller width */
        text-align: center;
    }}
    
    QFrame#skillWidget {{
        background-color: {palette['surface']};
        border: 1px solid {palette['border']};
        border-radius: 0px;  /* Remove border radius */
        margin: 1px;
        padding: 0px;     /* Remove padding */
    }}
    
    QLabel#proficiencyIndicator {{
        color: {palette['accent_tertiary']};  /* Use blue-teal for proficiency indicators */
        font-size: 10px;  /* Smaller font to match */
        font-weight: bold;
        padding: 1px 2px;
    }}
    
    /* Saving Throw Widgets - Fix visibility issues */
    QFrame#savingThrowWidget {{
        background-color: {palette['surface']};
        border: 1px solid {palette['border']};
        border-radius: 0px;  /* No border radius */
        margin: 1px;
        padding: 0px;
    }}
    
    QLabel#savingThrowIndicator {{
        color: {palette['accent_tertiary']};  /* Use blue-teal for visibility */
        font-size: 10px;
        font-weight: bold;
        padding: 1px;
    }}
    
    QLabel#savingThrowLabel {{
        color: {palette['text']};  /* Use main text color for readability */
        font-size: 9px;   /* Small but readable */
        font-weight: bold;
        padding: 1px 2px;
    }}
    
    QLabel#savingThrowBonus {{
        color: {palette['accent_tertiary']};  /* Blue-teal for bonuses */
        font-size: 10px;
        font-weight: bold;
        padding: 1px;
        min-width: 20px;
        text-align: center;
    }}
    
    /* Character Panel - Override all hardcoded colors with theme-responsive ones */
    CharacterPanel {{
        background-color: {palette['background']};
        color: {palette['text']};
    }}
    
    QFrame#headerFrame {{
        background-color: {palette['surface']};
        border: 1px solid {palette['border']};
    }}
    
    QFrame#abilitiesFrame, QFrame#secondaryFrame, QFrame#skillsFrame,
    QFrame#featuresFrame, QFrame#spellsFrame {{
        background-color: {palette['surface']};
        border: 1px solid {palette['border']};
        border-radius: 0px;
    }}
    
    QFrame#abilityWidget {{
        background-color: {palette['surface']};
        border: 1px solid {palette['border']};
        border-radius: 0px;
    }}
    
    QLabel#abilityName {{
        color: {palette['text']};
        font-size: 10px;
        font-weight: bold;
    }}
    
    QLabel#abilityModifier {{
        color: {palette['accent_tertiary']};  /* Blue-teal for modifiers */
        font-size: 18px;
        font-weight: bold;
    }}
    
    QLabel#abilityScore {{
        color: {palette['text_secondary']};
        font-size: 14px;
    }}
    
    QFrame#statWidget {{
        background-color: {palette['surface']};
        border: 1px solid {palette['border']};
        border-radius: 0px;
    }}
    
    QLabel#statName {{
        color: {palette['text']};
        font-size: 9px;
        font-weight: bold;
    }}
    
    QLabel#statValue {{
        color: {palette['accent_tertiary']};  /* Blue-teal for values */
        font-size: 14px;
        font-weight: bold;
    }}
    
    QFrame#abilityRow {{
        background-color: transparent;
        border-bottom: 1px solid {palette['border']};
        margin: 1px 0px;
    }}
    
    QFrame#detailHeader {{
        background-color: {palette['surface']};
        border: 1px solid {palette['border']};
    }}
    
    QLabel#sectionTitle {{
        color: {palette['text']};
        font-size: 14px;
        font-weight: bold;
        padding: 1px;
    }}
    
    QTextEdit#featuresText, QTextEdit#proficienciesText, QTextEdit#spellsText {{
        background-color: {palette['surface']};
        color: {palette['text']};
        border: 1px solid {palette['border']};
        border-radius: 0px;
        padding: 1px;
        font-size: 12pt;
    }}
    
    QLabel#charTitle {{
        color: {palette['text']};
        font-size: 12px;
        font-weight: normal;
    }}
    
    QLabel#charNameLabel {{
        color: {palette['text']};
        font-size: 18px;
        font-weight: bold;
        padding: 1px;
    }}
    
    QLabel#charDetailsLabel {{
        color: {palette['text_secondary']};
        font-size: 12px;
        padding: 1px;
    }}
    
    QLabel#hpLabel {{
        color: {palette['text']};
        font-size: 12px;
        min-width: 60px;
    }}
    
    QLabel#abilityValue {{
        color: {palette['text_secondary']};
        font-size: 11px;
        padding: 1px;
    }}
    
    QPushButton#expandButton {{
        background-color: {palette['button']};
        color: {palette['text']};
        border: 1px solid {palette['border']};
        border-radius: 0px;
        padding: 1px 2px;
        font-weight: bold;
    }}
    
    QPushButton#expandButton:hover {{
        background-color: {palette['button_hover']};
    }}
    """

# POTENTIAL_DEAD_CODE: Function 'get_theme_names' appears unused
def get_theme_names() -> list[str]:
    """Return list of available theme names."""
    return ["light", "dark"]

def get_theme_palette(theme_name: str) -> dict[str, str]:
    """Get color palette for the specified theme.
    
    Args:
        theme_name: Name of the theme ("light" or "dark")
        
    Returns:
        Dictionary containing color definitions for the theme
        
    Raises:
        ValueError: If theme_name is not valid
    """
    themes = {
        "light": LIGHT_THEME,
        "dark": DARK_THEME
    }
    
    if theme_name not in themes:
        raise ValueError(f"Unknown theme: {theme_name}. Available themes: {list(themes.keys())}")
    
    return themes[theme_name]
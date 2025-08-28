"""UI theme definitions for TaleKeeper.

Provides light and dark palettes inspired by the project's art cards.
Each theme contains colors for background, text and accents which are
used to build a simple stylesheet applied to the PyQt6 widgets."""

from __future__ import annotations

LIGHT_THEME = {
    "background": "#e6d5b8",
    "text": "#4b3f36",
    "accent1": "#7a5c4d",
    "accent2": "#a05a3c",
    "accent3": "#2f6e64",
}

DARK_THEME = {
    "background": "#223047",
    "text": "#c19b6b",
    "accent1": "#3f5c4b",
    "accent2": "#1d4c56",
    "accent3": "#a67c52",
}

def build_stylesheet(palette: dict[str, str]) -> str:
    """Return a stylesheet string for the provided color palette."""
    return f"""
    QMainWindow {{
        background-color: {palette['background']};
        color: {palette['text']};
        font-family: 'IM FELL Great Primer Roman';
    }}
    QSplitter::handle {{
        background-color: {palette['accent1']};
    }}
    QPushButton {{
        background-color: {palette['accent2']};
        color: {palette['text']};
    }}
    QPushButton:hover {{
        background-color: {palette['accent3']};
    }}
    """

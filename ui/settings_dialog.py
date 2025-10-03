from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QCheckBox, QGroupBox, QTabWidget,
                            QWidget, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional

from core.config import get_config


class NarrativeSettingsWidget(QWidget):
    """Widget for narrative generation settings."""

    settings_changed = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.config = get_config()
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the narrative settings UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel("Narrative Generation Settings")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel(
            "Control how narrative text is generated and displayed in combat logs.\n"
            "Narratives use campaign-specific AI prompts to create atmospheric descriptions."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(desc)

        self.enable_combat_narratives_cb = QCheckBox("Enable Combat Narratives")
        self.enable_combat_narratives_cb.setChecked(self.config.narrative.enable_combat_narratives)
        self.enable_combat_narratives_cb.setToolTip(
            "Generate narrative descriptions for combat actions (attacks, spells, etc.)"
        )
        self.enable_combat_narratives_cb.stateChanged.connect(self._on_settings_changed)
        layout.addWidget(self.enable_combat_narratives_cb)

        self.enable_round_summaries_cb = QCheckBox("Show Round Summaries")
        self.enable_round_summaries_cb.setChecked(self.config.narrative.enable_round_summaries)
        self.enable_round_summaries_cb.setToolTip(
            "Generate narrative summaries at the end of each combat round"
        )
        self.enable_round_summaries_cb.stateChanged.connect(self._on_settings_changed)
        layout.addWidget(self.enable_round_summaries_cb)

        self.enable_victory_narratives_cb = QCheckBox("Show Victory Descriptions")
        self.enable_victory_narratives_cb.setChecked(self.config.narrative.enable_victory_narratives)
        self.enable_victory_narratives_cb.setToolTip(
            "Generate narrative descriptions when combat ends victoriously"
        )
        self.enable_victory_narratives_cb.stateChanged.connect(self._on_settings_changed)
        layout.addWidget(self.enable_victory_narratives_cb)

        self.show_only_narratives_cb = QCheckBox("Show Only Narratives (hide mechanics)")
        self.show_only_narratives_cb.setChecked(self.config.narrative.show_only_narratives)
        self.show_only_narratives_cb.setToolTip(
            "Hide mechanical details (rolls, damage) and show only narrative text"
        )
        self.show_only_narratives_cb.stateChanged.connect(self._on_settings_changed)
        layout.addWidget(self.show_only_narratives_cb)

        layout.addStretch()

        info = QLabel(
            "Note: Narrative generation requires Ollama to be running.\n"
            "If unavailable, mechanical descriptions will be shown instead."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
        layout.addWidget(info)

    def _on_settings_changed(self):
        """Handle settings change."""
        self.settings_changed.emit()

    def apply_settings(self):
        """Apply current settings to config."""
        self.config.narrative.enable_combat_narratives = self.enable_combat_narratives_cb.isChecked()
        self.config.narrative.enable_round_summaries = self.enable_round_summaries_cb.isChecked()
        self.config.narrative.enable_victory_narratives = self.enable_victory_narratives_cb.isChecked()
        self.config.narrative.show_only_narratives = self.show_only_narratives_cb.isChecked()
        self.config.save_config()


class SettingsDialog(QDialog):
    """Settings dialog for TaleKeeper application."""

    settings_changed = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("TaleKeeper Settings")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the settings dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("settingsTabs")

        self.narrative_widget = NarrativeSettingsWidget()
        self.narrative_widget.settings_changed.connect(self._on_settings_changed)
        self.tabs.addTab(self.narrative_widget, "Narrative Generation")

        layout.addWidget(self.tabs)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self._apply_settings)
        button_layout.addWidget(self.apply_btn)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self._ok_clicked)
        button_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        self._apply_theme()

    def _apply_theme(self):
        """Apply theme styling to dialog."""
        try:
            from ui.themes import get_theme_palette
            theme_name = 'dark'
            parent = self.parent()
            if parent and hasattr(parent, 'current_theme'):
                theme_name = getattr(parent, 'current_theme', 'dark')

            palette = get_theme_palette(theme_name)

            style_sheet = f"""
            SettingsDialog {{
                background-color: {palette['background']};
                color: {palette['text']};
            }}

            QTabWidget::pane {{
                border: 1px solid {palette['border']};
                background-color: {palette['surface']};
            }}

            QTabBar::tab {{
                background-color: {palette['surface']};
                color: {palette['text']};
                border: 1px solid {palette['border']};
                padding: 8px 16px;
                margin-right: 2px;
            }}

            QTabBar::tab:selected {{
                background-color: {palette['accent_primary']};
                color: {palette['text']};
            }}

            QCheckBox {{
                color: {palette['text']};
                spacing: 8px;
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {palette['border']};
                border-radius: 3px;
                background-color: {palette['surface']};
            }}

            QCheckBox::indicator:checked {{
                background-color: {palette['accent_primary']};
                border-color: {palette['accent_primary']};
            }}

            QPushButton {{
                background-color: {palette['button']};
                color: {palette['text']};
                border: 1px solid {palette['border']};
                border-radius: 4px;
                padding: 6px 16px;
                min-width: 80px;
            }}

            QPushButton:hover {{
                background-color: {palette['button_hover']};
            }}

            QPushButton:pressed {{
                background-color: {palette['button_pressed']};
            }}

            QLabel {{
                color: {palette['text']};
            }}
            """
            self.setStyleSheet(style_sheet)
        except Exception:
            pass

    def _on_settings_changed(self):
        """Handle settings changed signal."""
        pass

    def _apply_settings(self):
        """Apply all settings."""
        self.narrative_widget.apply_settings()
        self.settings_changed.emit()

    def _ok_clicked(self):
        """Handle OK button click."""
        self._apply_settings()
        self.accept()

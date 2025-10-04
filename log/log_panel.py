"""
Log Panel Widget - Game activity and message display

PyQt6 widget that provides game logging functionality:
- Real-time game event display
- Different message types (info, warning, error, combat)
- Auto-scrolling and message filtering
- Save log to file capability

Designed to match ui_plan.md specifications:
- Fixed size: 432x486 (top half of right column)
- Auto-scroll to newest messages
- Dark theme styling
- Color-coded message types
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QFrame, QTextEdit, QComboBox,
                            QCheckBox, QScrollArea, QSlider)
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime, QTimer
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont
from typing import Optional, List, Dict, Any
from enum import Enum
import json
from datetime import datetime

from ui.layout_profiles import BASELINE_PROFILE, LayoutProfile


class LogLevel(Enum):
    """Message severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    COMBAT = "combat"
    DICE = "dice"
    SYSTEM = "system"
    NARRATIVE = "narrative"


class LogPanel(QWidget):
    """
    Game log display widget with filtering and export capabilities.
    
    Signals:
        log_exported: Emitted when log is exported to file
        filter_changed: Emitted when log filter is changed
    """
    
    log_exported = pyqtSignal(str)  # file path
    filter_changed = pyqtSignal(list)  # enabled levels
    log_message_added = pyqtSignal(dict)
    narration_enabled_changed = pyqtSignal(bool)
    narration_volume_changed = pyqtSignal(float)
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        layout_profile: Optional[LayoutProfile] = None,
    ):
        super().__init__(parent)
        self.layout_profile = layout_profile or BASELINE_PROFILE
        self.log_entries = []
        self.enabled_levels = set(LogLevel)  # All levels enabled by default
        self.max_entries = 1000  # Limit to prevent memory issues

        # Load narrative config
        try:
            from core.config import get_config
            self.config = get_config()
        except Exception:
            self.config = None

        # Set fixed size
        self.setFixedSize(
            self.layout_profile.log_panel_width,
            self.layout_profile.log_panel_height,
        )
        self._setup_ui()
        self._apply_styles()

        # Auto-scroll timer
        self.scroll_timer = QTimer()
        self.scroll_timer.setSingleShot(True)
        self.scroll_timer.timeout.connect(self._scroll_to_bottom)

        # Add welcome message
        self.add_log_message("Game session started", LogLevel.SYSTEM)
    
    def _setup_ui(self):
        """Initialize the log panel UI components."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(3)
        
        # === HEADER SECTION ===
        self.header_frame = QFrame()
        self.header_frame.setObjectName("headerFrame")
        self.header_frame.setFixedHeight(40)
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(5, 2, 5, 2)
        
        # Title
        self.title_label = QLabel("Game Log")
        self.title_label.setObjectName("titleLabel")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Narration toggle button
        self.narration_toggle = QPushButton("TTS")
        self.narration_toggle.setObjectName("narrationToggle")
        self.narration_toggle.setCheckable(True)
        self.narration_toggle.setChecked(True)
        self.narration_toggle.setFixedWidth(40)
        self.narration_toggle.setToolTip("Toggle narration on/off")
        self.narration_toggle.toggled.connect(self._on_narration_toggled)
        header_layout.addWidget(self.narration_toggle)

        # Queue indicator
        self.queue_label = QLabel("Q:0")
        self.queue_label.setObjectName("queueLabel")
        self.queue_label.setFixedWidth(30)
        self.queue_label.setToolTip("Narration queue size")
        header_layout.addWidget(self.queue_label)

        # Volume slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setObjectName("volumeSlider")
        self.volume_slider.setFixedWidth(60)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.setToolTip("Narration volume")
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        header_layout.addWidget(self.volume_slider)

        header_layout.addStretch()

        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.setObjectName("filterCombo")
        self.filter_combo.addItems(["All Messages", "Combat Only", "System Only", "Dice Rolls"])
        self.filter_combo.currentTextChanged.connect(self._apply_filter)
        header_layout.addWidget(self.filter_combo)
        
        # === LOG DISPLAY ===
        self.log_text = QTextEdit()
        self.log_text.setObjectName("logText")
        self.log_text.setReadOnly(True)
        self.log_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.log_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # === CONTROLS SECTION ===
        self.controls_frame = QFrame()
        self.controls_frame.setObjectName("controlsFrame")
        self.controls_frame.setFixedHeight(35)
        
        controls_layout = QHBoxLayout(self.controls_frame)
        controls_layout.setContentsMargins(5, 2, 5, 2)
        
        # Auto-scroll checkbox
        self.auto_scroll_cb = QCheckBox("Auto-scroll")
        self.auto_scroll_cb.setObjectName("autoScrollCheckBox")
        self.auto_scroll_cb.setChecked(True)
        controls_layout.addWidget(self.auto_scroll_cb)
        
        controls_layout.addStretch()
        
        # Action buttons
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("smallButton")
        self.clear_btn.clicked.connect(self.clear_log)
        controls_layout.addWidget(self.clear_btn)
        
        self.export_btn = QPushButton("Export")
        self.export_btn.setObjectName("smallButton")
        self.export_btn.clicked.connect(self._export_log)
        controls_layout.addWidget(self.export_btn)
        
        # Add components to main layout
        self.main_layout.addWidget(self.header_frame)
        self.main_layout.addWidget(self.log_text, 1)  # Take most space
        self.main_layout.addWidget(self.controls_frame)
    
    def _apply_styles(self):
        """Apply initial styling based on the active theme."""
        theme_name = 'light'
        parent = self.parent()
        if parent and hasattr(parent, 'current_theme'):
            theme_name = getattr(parent, 'current_theme', 'light')
        self.update_theme(theme_name)
    
    def update_theme(self, theme_name: str):
        """Update styling based on theme."""
        from ui.themes import get_theme_palette
        palette = get_theme_palette(theme_name)
        
        style_sheet = f"""
        LogPanel {{
            background-color: {palette['background']};
            border: 2px solid {palette['border']};
            border-radius: 8px;
        }}
        
        QFrame#headerFrame {{
            background-color: {palette['surface']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
        }}
        
        QFrame#filtersFrame {{
            background-color: {palette['surface']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
        }}
        
        QLabel#titleLabel {{
            color: {palette['text']};
            font-size: 14px;
            font-weight: bold;
        }}
        
        QLabel#levelLabel {{
            color: {palette['text_secondary']};
            font-size: 11px;
            font-weight: bold;
        }}
        
        QTextEdit#logDisplay {{
            background-color: {palette['background']};
            color: {palette['text']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            selection-background-color: {palette['selection']};
            selection-color: {palette['text']};
        }}
        
        QComboBox#levelFilter {{
            background-color: {palette['surface']};
            color: {palette['text']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
            padding: 2px 6px;
        }}
        
        QPushButton#clearButton {{
            background-color: {palette['button']};
            color: {palette['text']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 10px;
            font-weight: bold;
        }}
        
        QPushButton#clearButton:hover {{
            background-color: {palette['button_hover']};
        }}
        
        QPushButton#clearButton:pressed {{
            background-color: {palette['button_pressed']};
        }}
        
        QPushButton#autoScrollButton {{
            background-color: {palette['surface']};
            color: {palette['text']};
            border: 1px solid {palette['border']};
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 10px;
        }}
        
        QPushButton#smallButton {{
            background-color: {palette['button']};
            color: {palette['text']};
            border: 1px solid {palette['border']};
            border-radius: 3px;
            padding: 4px 8px;
            font-size: 8px;
            font-weight: bold;
            min-width: 50px;
        }}
        
        QPushButton#smallButton:hover {{
            background-color: {palette['button_hover']};
        }}
        
        QPushButton#smallButton:pressed {{
            background-color: {palette['button_pressed']};
        }}
        
        QScrollBar:vertical {{
            background-color: {palette['surface']};
            width: 12px;
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
        """
        self.setStyleSheet(style_sheet)
        
        # Reformat all existing log entries with new theme colors
        self._reformat_existing_entries(theme_name)
    
    def _reformat_existing_entries(self, theme_name: str):
        """Reformat all existing log entries with new theme colors."""
        # Clear the current log display
        self.log_text.clear()
        
        # Re-add all entries with current theme formatting
        for entry in self.log_entries:
            if entry['level'] in self.enabled_levels:
                self._format_and_display_entry(entry)
        
        # Scroll to bottom
        self._scroll_to_bottom()
    
    def _format_and_display_entry(self, entry: Dict[str, Any]):
        """Format and display a single log entry."""
        # Get entry data
        timestamp = entry['timestamp']
        message = entry['message']
        level = entry['level']
        
        # Move cursor to end
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Set format based on level
        format = QTextCharFormat()
        
        # Get current theme colors
        try:
            from ui.themes import get_theme_palette
            theme_name = getattr(self.parent(), 'current_theme', 'dark')
            palette = get_theme_palette(theme_name)
            
            # For light theme, use dark text; for dark theme, use light text
            if theme_name == 'light':
                text_color = palette['text']  # Dark text for light theme
                secondary_color = palette['text_secondary']
            else:
                text_color = "#ffffff"  # White text for dark theme
                secondary_color = "#888888"  # Gray for dark theme
        except Exception as e:
            # Fallback colors for dark theme
            text_color = "#ffffff"
            secondary_color = "#888888"
        
        if level == LogLevel.INFO:
            format.setForeground(QColor(text_color))  # Use theme text color
        elif level == LogLevel.WARNING:
            format.setForeground(QColor("#ff9500"))
        elif level == LogLevel.ERROR:
            format.setForeground(QColor("#ff4444"))
        elif level == LogLevel.COMBAT:
            format.setForeground(QColor("#ff6b6b"))
            format.setFontWeight(QFont.Weight.Bold)
        elif level == LogLevel.DICE:
            format.setForeground(QColor("#4a9"))
        elif level == LogLevel.SYSTEM:
            format.setForeground(QColor(secondary_color))  # Use theme secondary color
            format.setFontItalic(True)
        elif level == LogLevel.NARRATIVE:
            format.setForeground(QColor("#a0d0ff"))  # Light blue for narratives
            format.setFontItalic(True)
        
        # Format the message
        level_prefix = {
            LogLevel.INFO: "",
            LogLevel.WARNING: "[WARN] ",
            LogLevel.ERROR: "[FAIL] ",
            LogLevel.COMBAT: "[COMBAT] ",
            LogLevel.DICE: "[DICE] ",
            LogLevel.SYSTEM: "[SYSTEM] ",
            LogLevel.NARRATIVE: ">> "
        }

        # Check if we should show this message based on narrative config
        if level == LogLevel.NARRATIVE and self.config:
            if not self.config.narrative.enable_combat_narratives:
                return  # Skip narrative messages if disabled

        formatted_message = f"[{timestamp.strftime('%H:%M:%S')}] {level_prefix.get(level, '')}{message}\n"
        
        # Insert with formatting
        cursor.setCharFormat(format)
        cursor.insertText(formatted_message)
        
        # Reset format
        format.setForeground(QColor(text_color))  # Use theme text color
        format.setFontWeight(QFont.Weight.Normal)
        format.setFontItalic(False)
        cursor.setCharFormat(format)
    
    def add_log_message(self, message: str, level: LogLevel = LogLevel.INFO,
                       details: Optional[Dict[str, Any]] = None):
        """Add a new message to the log."""
        timestamp = datetime.now()

        # Create log entry
        entry = {
            'timestamp': timestamp,
            'message': message,
            'level': level,
            'details': details or {}
        }
        
        # Add to entries list
        self.log_entries.append(entry)
        
        # Limit entries to prevent memory issues
        if len(self.log_entries) > self.max_entries:
            self.log_entries.pop(0)
        
        # Update display if this level is enabled
        if level in self.enabled_levels:
            self._add_message_to_display(entry)

        # Auto-scroll if enabled
        if self.auto_scroll_cb.isChecked():
            self.scroll_timer.start(50)  # Small delay for smooth scrolling

        # Emit signal for downstream automation (audio narration, analytics, etc.)
        try:
            self.log_message_added.emit(self._serialize_entry(entry))
        except Exception as exc:  # pragma: no cover - defensive
            print(f"Failed to emit log_message_added: {exc}")

    def _serialize_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Convert internal entry representation into signal-friendly payload."""
        level = entry.get('level')
        if isinstance(level, LogLevel):
            level_value = level.value
        else:
            level_value = str(level)
        timestamp = entry.get('timestamp')
        if isinstance(timestamp, datetime):
            timestamp_value = timestamp.isoformat()
        else:
            timestamp_value = str(timestamp)
        return {
            'timestamp': timestamp_value,
            'message': entry.get('message', ''),
            'level': level_value,
            'details': entry.get('details', {}),
        }
    
    def _add_message_to_display(self, entry: Dict[str, Any]):
        """Add a message entry to the text display."""
        timestamp = entry['timestamp'].strftime("%H:%M:%S")
        message = entry['message']
        level = entry['level']
        
        # Move cursor to end
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Set format based on level
        format = QTextCharFormat()
        
        # Get current theme colors
        try:
            from ui.themes import get_theme_palette
            theme_name = getattr(self.parent(), 'current_theme', 'dark')
            palette = get_theme_palette(theme_name)
            
            # For light theme, use dark text; for dark theme, use light text
            if theme_name == 'light':
                text_color = palette['text']  # Dark text for light theme
                secondary_color = palette['text_secondary']
            else:
                text_color = "#ffffff"  # White text for dark theme
                secondary_color = "#888888"  # Gray for dark theme
        except Exception as e:
            # Fallback colors for dark theme
            text_color = "#ffffff"
            secondary_color = "#888888"
        
        if level == LogLevel.INFO:
            format.setForeground(QColor(text_color))  # Use theme text color instead of white
        elif level == LogLevel.WARNING:
            format.setForeground(QColor("#ff9500"))
        elif level == LogLevel.ERROR:
            format.setForeground(QColor("#ff4444"))
        elif level == LogLevel.COMBAT:
            format.setForeground(QColor("#ff6b6b"))
            format.setFontWeight(QFont.Weight.Bold)
        elif level == LogLevel.DICE:
            format.setForeground(QColor("#4a9"))
        elif level == LogLevel.SYSTEM:
            format.setForeground(QColor(secondary_color))  # Use theme secondary color
            format.setFontItalic(True)
        elif level == LogLevel.NARRATIVE:
            format.setForeground(QColor("#a0d0ff"))  # Light blue for narratives
            format.setFontItalic(True)

        # Format the message
        level_prefix = {
            LogLevel.INFO: "",
            LogLevel.WARNING: "[WARN] ",
            LogLevel.ERROR: "[FAIL] ",
            LogLevel.COMBAT: "[COMBAT] ",
            LogLevel.DICE: "[DICE] ",
            LogLevel.SYSTEM: "[SYSTEM] ",
            LogLevel.NARRATIVE: ">> "
        }

        # Check if we should show this message based on narrative config
        if level == LogLevel.NARRATIVE and self.config:
            if not self.config.narrative.enable_combat_narratives:
                return  # Skip narrative messages if disabled

        formatted_message = f"[{timestamp}] {level_prefix.get(level, '')}{message}\n"
        
        # Insert with formatting
        cursor.setCharFormat(format)
        cursor.insertText(formatted_message)
        
        # Reset format
        format.setForeground(QColor(text_color))  # Use theme text color instead of white
        format.setFontWeight(QFont.Weight.Normal)
        format.setFontItalic(False)
        cursor.setCharFormat(format)
    
    def _scroll_to_bottom(self):
        """Scroll the log view to the bottom."""
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _apply_filter(self, filter_text: str):
        """Apply message filtering based on selection."""
        # Update enabled levels based on filter
        if filter_text == "All Messages":
            self.enabled_levels = set(LogLevel)
        elif filter_text == "Combat Only":
            self.enabled_levels = {LogLevel.COMBAT, LogLevel.DICE}
        elif filter_text == "System Only":
            self.enabled_levels = {LogLevel.SYSTEM, LogLevel.ERROR}
        elif filter_text == "Dice Rolls":
            self.enabled_levels = {LogLevel.DICE}
        
        # Rebuild display
        self._rebuild_display()
        
        # Emit signal
        self.filter_changed.emit(list(self.enabled_levels))
    
    def _rebuild_display(self):
        """Rebuild the log display with current filter."""
        self.log_text.clear()
        
        for entry in self.log_entries:
            if entry['level'] in self.enabled_levels:
                self._add_message_to_display(entry)
        
        if self.auto_scroll_cb.isChecked():
            self._scroll_to_bottom()
    
    def clear_log(self):
        """Clear all log messages."""
        self.log_entries.clear()
        self.log_text.clear()
        self.add_log_message("Log cleared", LogLevel.SYSTEM)
    
    def _export_log(self):
        """Export log messages to file."""
        from PyQt6.QtWidgets import QFileDialog
        
        # Get save file path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Game Log",
            f"game_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;JSON Files (*.json)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    # Export as JSON
                    export_data = []
                    for entry in self.log_entries:
                        export_data.append({
                            'timestamp': entry['timestamp'].isoformat(),
                            'message': entry['message'],
                            'level': entry['level'].value,
                            'details': entry['details']
                        })
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2, ensure_ascii=False)
                else:
                    # Export as plain text
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write("TaleKeeper Game Log\n")
                        f.write("=" * 50 + "\n\n")
                        
                        for entry in self.log_entries:
                            timestamp = entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
                            level_name = entry['level'].value.upper()
                            message = entry['message']
                            f.write(f"[{timestamp}] {level_name}: {message}\n")
                
                self.add_log_message(f"Log exported to {file_path}", LogLevel.SYSTEM)
                self.log_exported.emit(file_path)
                
            except Exception as e:
                self.add_log_message(f"Export failed: {str(e)}", LogLevel.ERROR)
    
    def set_auto_scroll(self, enabled: bool):
        """Enable or disable auto-scrolling."""
        self.auto_scroll_cb.setChecked(enabled)
    
    def get_log_entries(self) -> List[Dict[str, Any]]:
        """Get all log entries."""
        return self.log_entries.copy()
    
    def get_enabled_levels(self) -> List[LogLevel]:
        """Get currently enabled log levels."""
        return list(self.enabled_levels)
    
    # Convenience methods for different log types
    def log_info(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Log an info message."""
        self.add_log_message(message, LogLevel.INFO, details)
    
    def log_warning(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Log a warning message."""
        self.add_log_message(message, LogLevel.WARNING, details)
    
    def log_error(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Log an error message."""
        self.add_log_message(message, LogLevel.ERROR, details)
    
    def log_combat(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Log a combat message."""
        self.add_log_message(message, LogLevel.COMBAT, details)
    
    def log_dice(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Log a dice roll message."""
        self.add_log_message(message, LogLevel.DICE, details)
    
    def log_system(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Log a system message."""
        self.add_log_message(message, LogLevel.SYSTEM, details)

    def log_narrative(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Log a narrative message."""
        self.add_log_message(message, LogLevel.NARRATIVE, details)

    def update_narration_queue(self, queue_size: int) -> None:
        """Update the narration queue display."""
        self.queue_label.setText(f"Q:{queue_size}")

    def _on_narration_toggled(self, enabled: bool) -> None:
        """Handle narration toggle button."""
        self.narration_enabled_changed.emit(enabled)
        if enabled:
            self.narration_toggle.setStyleSheet("background-color: #2a9d2a;")
        else:
            self.narration_toggle.setStyleSheet("background-color: #9d2a2a;")

    def _on_volume_changed(self, value: int) -> None:
        """Handle volume slider change."""
        volume = value / 100.0
        self.narration_volume_changed.emit(volume)
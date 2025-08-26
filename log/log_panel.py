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
                            QCheckBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime, QTimer
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont
from typing import Optional, List, Dict, Any
from enum import Enum
import json
from datetime import datetime


class LogLevel(Enum):
    """Message severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error" 
    COMBAT = "combat"
    DICE = "dice"
    SYSTEM = "system"


class LogPanel(QWidget):
    """
    Game log display widget with filtering and export capabilities.
    
    Signals:
        log_exported: Emitted when log is exported to file
        filter_changed: Emitted when log filter is changed
    """
    
    log_exported = pyqtSignal(str)  # file path
    filter_changed = pyqtSignal(list)  # enabled levels
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.log_entries = []
        self.enabled_levels = set(LogLevel)  # All levels enabled by default
        self.max_entries = 1000  # Limit to prevent memory issues
        
        # Set fixed size
        self.setFixedSize(432, 486)
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
        self.main_layout.setContentsMargins(5, 5, 5, 5)
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
        """Apply dark theme styling to log panel components."""
        style_sheet = """
        LogPanel {
            background-color: #181818;
            border: 2px solid #555555;
            border-radius: 8px;
        }
        
        QFrame#headerFrame {
            background-color: #222222;
            border: 1px solid #444444;
            border-radius: 4px;
        }
        
        QFrame#controlsFrame {
            background-color: #222222;
            border: 1px solid #444444;
            border-radius: 4px;
        }
        
        QLabel#titleLabel {
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
        }
        
        QTextEdit#logText {
            background-color: #151515;
            color: #ffffff;
            border: 1px solid #444444;
            border-radius: 4px;
            padding: 5px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 11px;
        }
        
        QComboBox#filterCombo {
            background-color: #2a2a2a;
            color: #ffffff;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 3px 6px;
            min-width: 100px;
        }
        
        QComboBox#filterCombo::drop-down {
            border: none;
        }
        
        QComboBox#filterCombo::down-arrow {
            width: 12px;
            height: 12px;
        }
        
        QComboBox#filterCombo QAbstractItemView {
            background-color: #2a2a2a;
            color: #ffffff;
            border: 1px solid #555555;
            selection-background-color: #4a90e2;
        }
        
        QCheckBox#autoScrollCheckBox {
            color: #ffffff;
            font-size: 11px;
        }
        
        QCheckBox#autoScrollCheckBox::indicator {
            width: 16px;
            height: 16px;
            background-color: #2a2a2a;
            border: 1px solid #555555;
            border-radius: 3px;
        }
        
        QCheckBox#autoScrollCheckBox::indicator:checked {
            background-color: #4a90e2;
            border-color: #4a90e2;
        }
        
        QPushButton#smallButton {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #666666;
            border-radius: 3px;
            padding: 4px 8px;
            font-size: 10px;
            font-weight: bold;
            min-width: 50px;
        }
        
        QPushButton#smallButton:hover {
            background-color: #505050;
        }
        
        QPushButton#smallButton:pressed {
            background-color: #303030;
        }
        
        QScrollBar:vertical {
            background-color: #2a2a2a;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #555555;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #666666;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        """
        self.setStyleSheet(style_sheet)
    
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
        
        if level == LogLevel.INFO:
            format.setForeground(QColor("#ffffff"))
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
            format.setForeground(QColor("#888888"))
            format.setFontItalic(True)
        
        # Format the message
        level_prefix = {
            LogLevel.INFO: "",
            LogLevel.WARNING: "⚠ ",
            LogLevel.ERROR: "❌ ",
            LogLevel.COMBAT: "⚔ ",
            LogLevel.DICE: "🎲 ",
            LogLevel.SYSTEM: "⚙ "
        }
        
        formatted_message = f"[{timestamp}] {level_prefix.get(level, '')}{message}\n"
        
        # Insert with formatting
        cursor.setCharFormat(format)
        cursor.insertText(formatted_message)
        
        # Reset format
        format.setForeground(QColor("#ffffff"))
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
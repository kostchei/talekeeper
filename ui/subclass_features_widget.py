"""
Subclass Features Widget for TaleKeeper

Displays subclass features with availability indicators, resource tracking,
and tooltips in the character sheet's detail panel.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QFrame, QScrollArea, QPushButton, QProgressBar,
                            QToolTip, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
from typing import Dict, List, Optional, Any
import sqlite3

from services.enhanced_subclass_manager import (
    EnhancedSubclassManager, SubclassFeature, FeatureType, ActionCost
)


class SubclassFeatureWidget(QFrame):
    """Widget representing a single subclass feature."""

    feature_activated = pyqtSignal(str, str)  # feature_name, character_id

    def __init__(self, feature: SubclassFeature, character_id: str, parent=None):
        super().__init__(parent)
        self.feature = feature
        self.character_id = character_id
        self.manager = EnhancedSubclassManager()

        self.setObjectName("subclassFeatureWidget")
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        self.setFixedHeight(120)

        self._setup_ui()
        self._update_availability()

        # Install event filter for hover tooltips
        self.setMouseTracking(True)
        self.installEventFilter(self)

    def _setup_ui(self):
        """Setup the feature widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # Header with name and level
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Feature name
        self.name_label = QLabel(self.feature.name)
        self.name_label.setObjectName("featureName")
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        self.name_label.setFont(font)
        header_layout.addWidget(self.name_label)

        header_layout.addStretch()

        # Level indicator
        level_label = QLabel(f"Level {self.feature.level}")
        level_label.setObjectName("featureLevel")
        level_label.setStyleSheet("color: #666; font-size: 10px;")
        header_layout.addWidget(level_label)

        layout.addLayout(header_layout)

        # Feature type and action cost indicators
        indicators_layout = QHBoxLayout()
        indicators_layout.setContentsMargins(0, 0, 0, 0)

        # Feature type badge
        type_badge = QLabel(self._get_type_display(self.feature.feature_type))
        type_badge.setObjectName("featureTypeBadge")
        type_badge.setStyleSheet(self._get_type_style(self.feature.feature_type))
        indicators_layout.addWidget(type_badge)

        # Action cost badge (if applicable)
        if self.feature.action_cost != ActionCost.NONE:
            action_badge = QLabel(self._get_action_display(self.feature.action_cost))
            action_badge.setObjectName("featureActionBadge")
            action_badge.setStyleSheet(self._get_action_style(self.feature.action_cost))
            indicators_layout.addWidget(action_badge)

        indicators_layout.addStretch()

        # Availability indicator
        self.availability_label = QLabel()
        self.availability_label.setObjectName("featureAvailability")
        indicators_layout.addWidget(self.availability_label)

        layout.addLayout(indicators_layout)

        # Resource tracking (if applicable)
        if self.feature.uses_per_rest:
            self._setup_resource_tracking(layout)

        # Description (truncated)
        description = self.feature.description
        if len(description) > 100:
            description = description[:97] + "..."

        self.description_label = QLabel(description)
        self.description_label.setObjectName("featureDescription")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #555; font-size: 10px;")
        layout.addWidget(self.description_label)

        # Activation button (for activated features)
        if self.feature.feature_type == FeatureType.ACTIVATED:
            self.activation_button = QPushButton(f"Use {self.feature.name}")
            self.activation_button.setObjectName("featureActivationButton")
            self.activation_button.clicked.connect(self._on_activation_clicked)
            layout.addWidget(self.activation_button)

    def _setup_resource_tracking(self, layout: QVBoxLayout):
        """Setup resource tracking display."""
        resource_layout = QHBoxLayout()
        resource_layout.setContentsMargins(0, 0, 0, 0)

        # Resource name and current/max uses
        self.resource_label = QLabel()
        self.resource_label.setObjectName("featureResourceLabel")
        resource_layout.addWidget(self.resource_label)

        # Progress bar for visual representation
        self.resource_progress = QProgressBar()
        self.resource_progress.setObjectName("featureResourceProgress")
        self.resource_progress.setFixedHeight(8)
        self.resource_progress.setTextVisible(False)
        resource_layout.addWidget(self.resource_progress)

        layout.addLayout(resource_layout)

        # Update resource display
        self._update_resource_display()

    def _update_resource_display(self):
        """Update the resource tracking display."""
        if not self.feature.uses_per_rest:
            return

        # Get current resource usage
        with sqlite3.connect(self.manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT current_uses, max_uses FROM subclass_resources
                WHERE character_id = ? AND resource_name = ?
            """, (self.character_id, self.feature.name))

            row = cursor.fetchone()
            if row:
                current_uses, max_uses = row
            else:
                current_uses = 0
                max_uses = self.feature.uses_per_rest

        remaining = max_uses - current_uses

        # Update labels
        self.resource_label.setText(f"{remaining}/{max_uses} uses")

        # Update progress bar
        if hasattr(self, 'resource_progress'):
            self.resource_progress.setMaximum(max_uses)
            self.resource_progress.setValue(remaining)

    def _update_availability(self):
        """Update the feature availability indicator."""
        available = self._check_feature_availability()

        if available:
            self.availability_label.setText("✓ Available")
            self.availability_label.setStyleSheet("color: #28a745; font-weight: bold; font-size: 10px;")
            if hasattr(self, 'activation_button'):
                self.activation_button.setEnabled(True)
        else:
            reason = self._get_unavailability_reason()
            self.availability_label.setText(f"✗ {reason}")
            self.availability_label.setStyleSheet("color: #dc3545; font-weight: bold; font-size: 10px;")
            if hasattr(self, 'activation_button'):
                self.activation_button.setEnabled(False)

    def _check_feature_availability(self) -> bool:
        """Check if the feature is currently available to use."""
        # Check resource limitations
        if self.feature.uses_per_rest:
            with sqlite3.connect(self.manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT current_uses, max_uses FROM subclass_resources
                    WHERE character_id = ? AND resource_name = ?
                """, (self.character_id, self.feature.name))

                row = cursor.fetchone()
                if row:
                    current_uses, max_uses = row
                    if current_uses >= max_uses:
                        return False

        # Check prerequisites (basic implementation)
        if self.feature.prerequisites:
            # For now, assume features are available if no specific checks implemented
            pass

        return True

    def _get_unavailability_reason(self) -> str:
        """Get the reason why the feature is unavailable."""
        if self.feature.uses_per_rest:
            with sqlite3.connect(self.manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT current_uses, max_uses FROM subclass_resources
                    WHERE character_id = ? AND resource_name = ?
                """, (self.character_id, self.feature.name))

                row = cursor.fetchone()
                if row:
                    current_uses, max_uses = row
                    if current_uses >= max_uses:
                        return f"No uses ({self.feature.rest_type} rest)"

        return "Prerequisites not met"

    def _get_type_display(self, feature_type: FeatureType) -> str:
        """Get display text for feature type."""
        return {
            FeatureType.PASSIVE: "Passive",
            FeatureType.ACTIVATED: "Active",
            FeatureType.TRIGGERED: "Triggered",
            FeatureType.REACTION: "Reaction",
            FeatureType.RESOURCE: "Resource"
        }.get(feature_type, "Unknown")

    def _get_type_style(self, feature_type: FeatureType) -> str:
        """Get CSS style for feature type badge."""
        colors = {
            FeatureType.PASSIVE: "background-color: #6c757d; color: white;",
            FeatureType.ACTIVATED: "background-color: #007bff; color: white;",
            FeatureType.TRIGGERED: "background-color: #ffc107; color: black;",
            FeatureType.REACTION: "background-color: #dc3545; color: white;",
            FeatureType.RESOURCE: "background-color: #28a745; color: white;"
        }
        base_style = "padding: 2px 6px; border-radius: 3px; font-size: 9px; font-weight: bold;"
        return base_style + colors.get(feature_type, "background-color: #666; color: white;")

    def _get_action_display(self, action_cost: ActionCost) -> str:
        """Get display text for action cost."""
        return {
            ActionCost.ACTION: "Action",
            ActionCost.BONUS_ACTION: "Bonus",
            ActionCost.REACTION: "Reaction",
            ActionCost.FREE: "Free"
        }.get(action_cost, "")

    def _get_action_style(self, action_cost: ActionCost) -> str:
        """Get CSS style for action cost badge."""
        colors = {
            ActionCost.ACTION: "background-color: #fd7e14; color: white;",
            ActionCost.BONUS_ACTION: "background-color: #6610f2; color: white;",
            ActionCost.REACTION: "background-color: #e83e8c; color: white;",
            ActionCost.FREE: "background-color: #20c997; color: white;"
        }
        base_style = "padding: 2px 6px; border-radius: 3px; font-size: 9px; font-weight: bold; margin-left: 4px;"
        return base_style + colors.get(action_cost, "")

    def _on_activation_clicked(self):
        """Handle feature activation button click."""
        self.feature_activated.emit(self.feature.name, self.character_id)

        # Update availability after activation
        QTimer.singleShot(100, self._update_availability)
        QTimer.singleShot(100, self._update_resource_display)

    def eventFilter(self, obj, event):
        """Handle mouse events for tooltips."""
        if event.type() == event.Type.Enter:
            # Show tooltip with full description
            tooltip_text = f"<b>{self.feature.name}</b><br/><br/>{self.feature.description}"
            if self.feature.tooltip_extended:
                tooltip_text += f"<br/><br/><i>{self.feature.tooltip_extended}</i>"
            QToolTip.showText(event.globalPos(), tooltip_text, self)
        elif event.type() == event.Type.Leave:
            QToolTip.hideText()

        return super().eventFilter(obj, event)


class SubclassFeaturesWidget(QWidget):
    """Widget displaying all subclass features for a character."""

    feature_activated = pyqtSignal(str, str)  # feature_name, character_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.character_id = None
        self.manager = EnhancedSubclassManager()
        self.feature_widgets: List[SubclassFeatureWidget] = []

        self.setObjectName("subclassFeaturesWidget")
        self._setup_ui()

    def _setup_ui(self):
        """Setup the main features widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("Subclass Features")
        title_label.setObjectName("sectionTitle")
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        title_label.setFont(font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Refresh button
        self.refresh_button = QPushButton("↻")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.setFixedSize(24, 24)
        self.refresh_button.setToolTip("Refresh feature availability")
        self.refresh_button.clicked.connect(self.refresh_features)
        header_layout.addWidget(self.refresh_button)

        layout.addLayout(header_layout)

        # Scroll area for features
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("featuresScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Container for feature widgets
        self.features_container = QWidget()
        self.features_layout = QVBoxLayout(self.features_container)
        self.features_layout.setContentsMargins(0, 0, 0, 0)
        self.features_layout.setSpacing(8)

        self.scroll_area.setWidget(self.features_container)
        layout.addWidget(self.scroll_area)

        # Placeholder text
        self.placeholder_label = QLabel("No subclass features available")
        self.placeholder_label.setObjectName("placeholderText")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.placeholder_label)

        # Initially hide placeholder
        self.placeholder_label.hide()

    def set_character(self, character_id: str, character_level: int):
        """Set the character to display features for."""
        self.character_id = character_id
        self.character_level = character_level
        self.refresh_features()

    def refresh_features(self):
        """Refresh the display of subclass features."""
        if not self.character_id:
            return

        # Clear existing widgets
        for widget in self.feature_widgets:
            widget.deleteLater()
        self.feature_widgets.clear()

        # Get character's subclass features
        features = self.manager.get_character_subclass_features(self.character_id, self.character_level)

        if not features:
            self.scroll_area.hide()
            self.placeholder_label.show()
            return

        self.placeholder_label.hide()
        self.scroll_area.show()

        # Create widgets for each feature
        for feature in features:
            feature_widget = SubclassFeatureWidget(feature, self.character_id, self)
            feature_widget.feature_activated.connect(self.feature_activated.emit)

            self.features_layout.addWidget(feature_widget)
            self.feature_widgets.append(feature_widget)

        # Add stretch at the end
        self.features_layout.addStretch()

    def update_feature_availability(self):
        """Update availability indicators for all features."""
        for widget in self.feature_widgets:
            widget._update_availability()
            widget._update_resource_display()
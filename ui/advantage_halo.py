"""
Advantage Halo Component
Displays Lucky/Inspiration usage options as a small halo card overlay
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPainter, QPainterPath, QBrush, QColor


class AdvantageHalo(QWidget):
    """
    Small halo card that appears over action/monster cards to offer Lucky/Inspiration usage.
    Shows Inspiration first, then Lucky when Inspiration is exhausted.
    """
    
    resource_used = pyqtSignal(str)  # Emits 'inspiration' or 'lucky'
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)  # Small triangle size
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Current resource state
        self.resource_type = None
        self.resource_count = 0
        self.resource_max = 0
        self.resource_consumed = False  # Prevent double-clicking
        
        # No UI setup needed - just a triangle overlay
        
        # Auto-hide timer for defensive usage
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.hide)
        self.hide_timer.setSingleShot(True)
        
        # Make clickable
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def update_resources(self, lucky_current, lucky_max, inspiration_current, inspiration_max):
        """Update the triangle based on available resources (Inspiration priority)."""
        self.resource_consumed = False  # Reset consumption flag
        print(f"[DEBUG] Halo update_resources: inspiration={inspiration_current}/{inspiration_max}, lucky={lucky_current}/{lucky_max}")
        
        if inspiration_current > 0:
            self.resource_type = "inspiration"
            self.resource_count = inspiration_current
            self.resource_max = inspiration_max
            self.triangle_color = "rgba(70, 130, 200, 180)"  # Blue for inspiration
            self.setToolTip(f"Click to use Inspiration ({inspiration_current}/{inspiration_max})")
            print(f"[DEBUG] Halo showing for inspiration, visible: {self.isVisible()}")
            self.show()
            print(f"[DEBUG] Halo after show(), visible: {self.isVisible()}")
        elif lucky_current > 0:
            self.resource_type = "lucky"
            self.resource_count = lucky_current
            self.resource_max = lucky_max
            self.triangle_color = "rgba(220, 180, 50, 180)"  # Gold for lucky
            self.setToolTip(f"Click to use Lucky ({lucky_current}/{lucky_max})")
            print(f"[DEBUG] Halo showing for lucky, visible: {self.isVisible()}")
            self.show()
            print(f"[DEBUG] Halo after show(), visible: {self.isVisible()}")
        else:
            print(f"[DEBUG] Halo hiding - no resources")
            self.hide()
        self.update()  # Trigger repaint
            
    def position_over_card(self, card_widget):
        """Position the halo in the top-right quarter of the given card."""
        if not card_widget:
            return
            
        # Get card dimensions and position
        card_rect = card_widget.geometry()
        parent_widget = card_widget.parent()
        
        if parent_widget:
            # Convert card position to parent coordinates
            global_pos = card_widget.mapToGlobal(card_widget.rect().topLeft())
            parent_pos = parent_widget.mapFromGlobal(global_pos)
            
            # Position completely outside card bounds for clickability
            halo_x = parent_pos.x() + card_rect.width() - 20  # Overlap slightly but stay clickable
            halo_y = parent_pos.y() - 10  # Move above the card
            
            self.move(halo_x, halo_y)
            self.raise_()  # Bring to front
            self.setWindowFlags(Qt.WindowType.Widget | Qt.WindowType.WindowStaysOnTopHint)
            self.show()
            
    def show_with_timeout(self, timeout_ms=3000):
        """Show the halo and auto-hide after timeout (for defensive usage)."""
        self.show()
        self.hide_timer.start(timeout_ms)
        
    def mousePressEvent(self, event):
        """Handle clicks to use the resource."""
        if event.button() == Qt.MouseButton.LeftButton and self.resource_type and not self.resource_consumed:
            print(f"[DEBUG] Halo clicked: using {self.resource_type}")
            self.resource_consumed = True  # Prevent further clicks
            self.resource_used.emit(self.resource_type)
            # Hide immediately after use
            self.hide()
            self.hide_timer.stop()
        event.accept()
        
    def mouseReleaseEvent(self, event):
        """Ensure mouse release is handled properly."""
        if event.button() == Qt.MouseButton.LeftButton and self.resource_type:
            print(f"[DEBUG] Halo mouse release: {self.resource_type}")
        event.accept()
            
    def paintEvent(self, event):
        """Draw a triangle in the top-right corner."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if hasattr(self, 'triangle_color') and self.triangle_color:
            # Draw filled triangle
            painter.setBrush(QBrush(QColor(self.triangle_color)))
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Triangle points (top-right corner)
            points = [
                self.rect().topRight(),  # Top right
                self.rect().bottomRight(),  # Bottom right  
                self.rect().topLeft() + self.rect().topRight() - self.rect().topLeft()  # Top left of triangle area
            ]
            
            path = QPainterPath()
            path.moveTo(0, 0)  # Top left
            path.lineTo(30, 0)  # Top right
            path.lineTo(30, 30)  # Bottom right
            path.closeSubpath()
            
            painter.fillPath(path, QBrush(QColor(self.triangle_color)))
        
        super().paintEvent(event)


class AdvantageResourceManager:
    """
    Manages Lucky and Inspiration resources for a character.
    Handles priority (Inspiration first) and resource consumption.
    """
    
    def __init__(self, character_data):
        self.character_data = character_data
        self.update_from_character(character_data)
        
        # Track pending advantage for next attack
        self.pending_inspiration_advantage = False
        self.pending_lucky_advantage = False
        
    def update_from_character(self, character_data):
        """Update resource counts from character data."""
        self.lucky_current = character_data.get('lucky_uses_current', 0)
        self.lucky_max = character_data.get('lucky_uses_max', 0)
        self.inspiration_current = character_data.get('inspiration_uses_current', 0)
        self.inspiration_max = character_data.get('inspiration_uses_max', 0)
        
        
    def has_resources(self):
        """Check if any advantage resources are available."""
        return self.inspiration_current > 0 or self.lucky_current > 0
        
    def get_primary_resource(self):
        """Get the primary resource to display (Inspiration priority)."""
        if self.inspiration_current > 0:
            return "inspiration"
        elif self.lucky_current > 0:
            return "lucky"
        return None
        
    def consume_resource(self, resource_type):
        """Consume a resource and return updated counts."""
        if resource_type == "inspiration" and self.inspiration_current > 0:
            self.inspiration_current -= 1
            self.pending_inspiration_advantage = True  # Set advantage flag
            print(f"[DEBUG] AdvantageResourceManager: Set pending_inspiration_advantage = True")
            return True
        elif resource_type == "lucky" and self.lucky_current > 0:
            self.lucky_current -= 1
            self.pending_lucky_advantage = True  # Set advantage flag
            print(f"[DEBUG] AdvantageResourceManager: Set pending_lucky_advantage = True")
            return True
        return False
        
    def consume_pending_advantage(self):
        """Consume pending advantage and return which type was used."""
        if self.pending_inspiration_advantage:
            self.pending_inspiration_advantage = False
            print(f"[DEBUG] AdvantageResourceManager: Consumed pending inspiration advantage")
            return "inspiration"
        elif self.pending_lucky_advantage:
            self.pending_lucky_advantage = False
            print(f"[DEBUG] AdvantageResourceManager: Consumed pending lucky advantage")
            return "lucky"
        return None
        
    def has_pending_advantage(self):
        """Check if there's pending advantage for next attack."""
        return self.pending_inspiration_advantage or self.pending_lucky_advantage
    
    def get_resource_counts(self):
        """Get all current resource counts."""
        return {
            'lucky_current': self.lucky_current,
            'lucky_max': self.lucky_max,
            'inspiration_current': self.inspiration_current,
            'inspiration_max': self.inspiration_max
        }
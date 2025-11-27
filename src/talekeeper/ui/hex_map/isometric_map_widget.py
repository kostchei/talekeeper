# core
# category: ui
"""
Isometric Map Widget for TaleKeeper.

This widget renders the hex map using an isometric projection.
It is designed to be decoupled from the game logic, only receiving data to render.
"""

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtGui import QColor, QPolygonF, QPen, QBrush, QPainter
import math
from typing import Dict, List, Tuple, Optional

from talekeeper.services.hex_map_service import HexMapService
from talekeeper.services.hex_coordinate_system import HexCoordinateSystem

class IsometricMapWidget(QGraphicsView):
    """
    A QGraphicsView that renders hex data in an isometric projection.
    """
    
    hex_clicked = pyqtSignal(int, int)  # Emits (q, r)
    
    def __init__(self, db_path: str, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.hex_service = HexMapService(db_path)
        self.coord_system = HexCoordinateSystem()
        
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        
        # Isometric projection constants
        self.tile_width = 64
        self.tile_height = 32  # 2:1 ratio for standard isometric
        
        self.character_id = None
        self.current_hexes = []
        
    def set_character(self, character_id: str):
        """Set the character context for the map."""
        self.character_id = character_id
        self.refresh_map()
        
    def refresh_map(self):
        """Reload data and redraw the map."""
        if not self.character_id:
            return
            
        self.scene.clear()
        
        # Get current position
        current_q, current_r = self.hex_service.get_character_position(self.character_id)
        
        # Get visible hexes (radius 5 for now)
        self.current_hexes = self.hex_service.get_visible_hexes(self.character_id, current_q, current_r, radius=5)
        
        # Draw hexes in painter's algorithm order (back to front)
        # For isometric, we sort by (r + q) usually, or just Y coordinate
        # But for hexes, it's a bit more complex. Let's try simple sorting first.
        
        # Sort by r then q is a simple approximation for 2D grids, 
        # but for hexes converted to iso, we need to be careful.
        # Let's just draw them and see.
        
        for hex_data in self.current_hexes:
            self._draw_iso_hex(hex_data, current_q, current_r)
            
    def _draw_iso_hex(self, hex_data: Dict, current_q: int, current_r: int):
        q = hex_data['q']
        r = hex_data['r']
        
        # 1. Convert Hex (q, r) to Cartesian (x, y)
        # Using flat-topped hex conversion
        hex_size = 40 # Logical size for spacing
        cart_x, cart_y = self.coord_system.hex_to_pixel(q, r, hex_size)
        
        # 2. Convert Cartesian (x, y) to Isometric (iso_x, iso_y)
        # Simple isometric projection:
        # iso_x = x - y
        # iso_y = (x + y) / 2
        
        iso_x = cart_x - cart_y
        iso_y = (cart_x + cart_y) / 2
        
        # Center the map roughly
        iso_x += 400
        iso_y += 300
        
        # Draw the tile
        self._draw_tile(iso_x, iso_y, hex_data, q == current_q and r == current_r)
        
    def _draw_tile(self, x: float, y: float, hex_data: Dict, is_current: bool):
        """Draw a single isometric tile."""
        
        # Create a diamond shape for the base
        w = self.tile_width
        h = self.tile_height
        
        points = [
            QPointF(x, y - h/2),      # Top
            QPointF(x + w/2, y),      # Right
            QPointF(x, y + h/2),      # Bottom
            QPointF(x - w/2, y)       # Left
        ]
        polygon = QPolygonF(points)
        
        # Color based on terrain
        color = self._get_terrain_color(hex_data.get('terrain_type', 'unknown'))
        
        if not hex_data.get('revealed'):
            color = QColor(50, 50, 50)
        elif not hex_data.get('visited'):
            color = color.darker(130)
            
        brush = QBrush(color)
        pen = QPen(QColor(0, 0, 0), 1)
        
        if is_current:
            pen = QPen(QColor(255, 255, 0), 2)
            
        # Add "thickness" (fake 3D)
        thickness = 10
        if hex_data.get('terrain_type') == 'mountain':
            thickness = 30
        elif hex_data.get('terrain_type') == 'hills':
            thickness = 20
            
        # Draw sides (darker)
        side_color = color.darker(150)
        
        # Left side
        left_side = QPolygonF([
            QPointF(x - w/2, y),
            QPointF(x, y + h/2),
            QPointF(x, y + h/2 + thickness),
            QPointF(x - w/2, y + thickness)
        ])
        self.scene.addPolygon(left_side, QPen(Qt.PenStyle.NoPen), QBrush(side_color))
        
        # Right side
        right_side = QPolygonF([
            QPointF(x, y + h/2),
            QPointF(x + w/2, y),
            QPointF(x + w/2, y + thickness),
            QPointF(x, y + h/2 + thickness)
        ])
        self.scene.addPolygon(right_side, QPen(Qt.PenStyle.NoPen), QBrush(side_color.darker(110)))
        
        # Draw top
        # Shift top up by thickness to make it look like a block
        top_polygon = QPolygonF([
            QPointF(p.x(), p.y() - thickness) for p in points
        ])
        
        item = self.scene.addPolygon(top_polygon, pen, brush)
        
        # Store data for click handling
        item.setData(0, hex_data['q'])
        item.setData(1, hex_data['r'])
        
    def _get_terrain_color(self, terrain: str) -> QColor:
        colors = {
            'plains': QColor(100, 200, 100),
            'forest': QColor(34, 139, 34),
            'mountain': QColor(169, 169, 169),
            'hills': QColor(210, 180, 140),
            'swamp': QColor(47, 79, 79),
            'desert': QColor(244, 164, 96),
            'water': QColor(65, 105, 225),
            'unknown': QColor(100, 100, 100)
        }
        return colors.get(terrain, colors['unknown'])

    def mousePressEvent(self, event):
        """Handle mouse clicks."""
        scene_pos = self.mapToScene(event.pos())
        item = self.scene.itemAt(scene_pos, self.transform())
        
        if item and hasattr(item, 'data'):
            q = item.data(0)
            r = item.data(1)
            if q is not None and r is not None:
                self.hex_clicked.emit(int(q), int(r))
                
        super().mousePressEvent(event)

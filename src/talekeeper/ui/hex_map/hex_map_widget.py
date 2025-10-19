# core
# category: core
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt6.QtGui import QColor, QPainter, QPolygonF, QPen, QBrush, QFont
import math
from typing import Optional, Dict, List

from talekeeper.services.hex_map_service import HexMapService
from talekeeper.services.hex_coordinate_system import HexCoordinateSystem
from talekeeper.services.hex_scouting_service import HexScoutingService

class HexMapWidget(QWidget):

    travel_requested = pyqtSignal(int, int)
    closed = pyqtSignal()
    hex_shop_requested = pyqtSignal(int, int, str)

    def __init__(self, db_path: str, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.hex_service = HexMapService(db_path)
        self.coord_system = HexCoordinateSystem()
        self.scouting_service = HexScoutingService(db_path)
        self.character_id = None
        self.current_hex_data = None

        self.hex_size = 40
        self.selected_hex = None

        self.setWindowTitle("Hex Map Explorer")
        self.setMinimumSize(1200, 800)

        self._setup_ui()
        self._setup_theme()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        header = QHBoxLayout()
        self.title_label = QLabel("Hex Map - Explorer")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header.addWidget(self.title_label)

        header.addStretch()

        close_button = QPushButton("Close [ESC]")
        close_button.clicked.connect(self.close_map)
        header.addWidget(close_button)

        layout.addLayout(header)

        main_area = QHBoxLayout()

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.mousePressEvent = self._on_view_click

        main_area.addWidget(self.view, stretch=3)

        info_panel = QVBoxLayout()

        self.hex_info_label = QLabel("Select a hex")
        self.hex_info_label.setWordWrap(True)
        self.hex_info_label.setStyleSheet("padding: 10px; border: 1px solid #555;")
        self.hex_info_label.setMinimumWidth(250)
        info_panel.addWidget(self.hex_info_label)

        self.vendor_button = QPushButton("Visit Vendor")
        self.vendor_button.clicked.connect(self._on_vendor_button_clicked)
        self.vendor_button.hide()
        info_panel.addWidget(self.vendor_button)

        self.stats_label = QLabel("Exploration Stats")
        self.stats_label.setWordWrap(True)
        self.stats_label.setStyleSheet("padding: 10px; border: 1px solid #555; margin-top: 10px;")
        info_panel.addWidget(self.stats_label)

        info_panel.addStretch()

        main_area.addLayout(info_panel)

        layout.addLayout(main_area)

        footer = QHBoxLayout()
        footer.addWidget(QLabel("Click adjacent hex to travel | ESC to close"))
        footer.addStretch()
        layout.addLayout(footer)

        self.setLayout(layout)

    def _setup_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #555;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QGraphicsView {
                border: 1px solid #555;
                background-color: #2a2a2a;
            }
        """)

    def set_character(self, character_id: str, character_name: str):
        self.character_id = character_id
        self.title_label.setText(f"Hex Map - {character_name}")

        self.hex_service.initialize_character_position(character_id)
        self.refresh_map()

    def refresh_map(self):
        if not self.character_id:
            return

        self.scene.clear()

        current_q, current_r = self.hex_service.get_character_position(self.character_id)
        hexes = self.hex_service.get_visible_hexes(self.character_id, current_q, current_r, radius=5)

        for hex_data in hexes:
            self._draw_hex(hex_data)

        self.view.centerOn(0, 0)
        self._update_stats()

    def _draw_hex(self, hex_data: Dict):
        q = hex_data['q']
        r = hex_data['r']

        x, y = self.coord_system.hex_to_pixel(q, r, self.hex_size)

        polygon = self._create_hex_polygon(x, y)

        color = self._get_hex_color(hex_data)
        pen = QPen(QColor(100, 100, 100), 2)

        current_q, current_r = self.hex_service.get_character_position(self.character_id)
        if q == current_q and r == current_r:
            pen = QPen(QColor(255, 255, 0), 4)

        brush = QBrush(color)

        hex_item = self.scene.addPolygon(polygon, pen, brush)
        hex_item.setData(0, q)
        hex_item.setData(1, r)

        if hex_data.get('revealed') or hex_data.get('visited'):
            text = self.scene.addText(f"{q},{r}", QFont("Arial", 8))
            text.setPos(x - 15, y - 10)
            text.setDefaultTextColor(QColor(200, 200, 200))

    def _create_hex_polygon(self, center_x: float, center_y: float) -> QPolygonF:
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.pi / 180 * angle_deg
            x = center_x + self.hex_size * math.cos(angle_rad)
            y = center_y + self.hex_size * math.sin(angle_rad)
            points.append(QPointF(x, y))
        return QPolygonF(points)

    def _get_hex_color(self, hex_data: Dict) -> QColor:
        if not hex_data.get('revealed'):
            return QColor(40, 40, 40)

        terrain_colors = {
            'plains': QColor(144, 168, 96),
            'forest': QColor(76, 153, 76),
            'mountain': QColor(128, 128, 128),
            'hills': QColor(153, 153, 102),
            'swamp': QColor(102, 102, 76),
            'desert': QColor(204, 183, 122),
            'unknown': QColor(60, 60, 60)
        }

        color = terrain_colors.get(hex_data.get('terrain_type', 'unknown'), QColor(60, 60, 60))

        if not hex_data.get('visited'):
            color = color.darker(150)

        return color

    def _on_view_click(self, event):
        scene_pos = self.view.mapToScene(event.pos())
        item = self.scene.itemAt(scene_pos, self.view.transform())

        if item and hasattr(item, 'data'):
            q = item.data(0)
            r = item.data(1)

            if q is not None and r is not None:
                self._select_hex(int(q), int(r))

        QGraphicsView.mousePressEvent(self.view, event)

    def _select_hex(self, q: int, r: int):
        self.selected_hex = (q, r)
        hex_data = self.hex_service.get_hex(self.character_id, q, r)
        self.current_hex_data = hex_data

        if not hex_data:
            self.hex_info_label.setText(f"Hex ({q}, {r})\nUnexplored")
            self.vendor_button.hide()
            return

        current_q, current_r = self.hex_service.get_character_position(self.character_id)
        distance = self.coord_system.get_distance(current_q, current_r, q, r)

        settlement_type = hex_data.get('settlement_type')
        show_vendor = (distance == 0 and settlement_type and settlement_type != 'empty')

        if distance == 1 and hex_data.get('revealed'):
            scouting_info = self.scouting_service.scout_hex(self.character_id, q, r, hex_data)
            html = self.scouting_service.format_scouting_html(scouting_info)
            html += "<br/><br/><b>[Click again to travel here]</b>"
            self.hex_info_label.setText(html)
            self.hex_info_label.setTextFormat(Qt.TextFormat.RichText)
            self.vendor_button.hide()

            if q != current_q or r != current_r:
                self._travel_to_hex(q, r)
        elif distance == 0:
            info_parts = [
                f"<b>Hex ({q}, {r})</b>",
                f"Terrain: {hex_data['terrain_type'].title()}",
            ]

            if settlement_type:
                settlement_names = {
                    'empty': 'No Settlement',
                    'hamlet': 'Hamlet',
                    'village': 'Village',
                    'town_small': 'Small Town',
                    'town_medium': 'Medium Town',
                    'town_large': 'Large Town'
                }
                settlement_name = settlement_names.get(settlement_type, 'Unknown')
                info_parts.append(f"Settlement: {settlement_name}")

            info_parts.append("")
            info_parts.append("<b>[Current Location]</b>")

            self.hex_info_label.setText("<br/>".join(info_parts))
            self.hex_info_label.setTextFormat(Qt.TextFormat.RichText)

            if show_vendor:
                self.vendor_button.show()
            else:
                self.vendor_button.hide()
        else:
            info_parts = [
                f"<b>Hex ({q}, {r})</b>",
                f"Terrain: {hex_data['terrain_type'].title()}",
            ]

            if hex_data['visited']:
                info_parts.append(f"Visited: {hex_data['visit_count']} time(s)")
                if hex_data.get('cleared'):
                    info_parts.append("Status: Cleared")
            elif hex_data['revealed']:
                info_parts.append("Status: Visible (not visited)")

            if distance > 1:
                info_parts.append(f"<br/>Distance: {distance} hexes away")

            self.hex_info_label.setText("<br/>".join(info_parts))
            self.hex_info_label.setTextFormat(Qt.TextFormat.RichText)
            self.vendor_button.hide()

    def _on_vendor_button_clicked(self):
        if not self.selected_hex or not self.current_hex_data:
            return

        q, r = self.selected_hex
        settlement_type = self.current_hex_data.get('settlement_type')

        if settlement_type and settlement_type != 'empty':
            self.hex_shop_requested.emit(q, r, settlement_type)

    def _travel_to_hex(self, q: int, r: int):
        try:
            hex_data = self.hex_service.travel_to_hex(self.character_id, q, r)
            self.refresh_map()
            self.travel_requested.emit(q, r)
        except ValueError as e:
            print(f"Cannot travel: {e}")

    def _update_stats(self):
        if not self.character_id:
            return

        stats = self.hex_service.get_exploration_stats(self.character_id)

        stats_text = [
            "Exploration Statistics",
            "",
            f"Hexes Discovered: {stats.get('total_hexes', 0)}",
            f"Hexes Visited: {stats.get('visited_hexes', 0)}",
            f"Hexes Cleared: {stats.get('cleared_hexes', 0)}",
            f"Total Events: {stats.get('total_events', 0)}",
        ]

        self.stats_label.setText("\n".join(stats_text))

    def close_map(self):
        self.closed.emit()
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape or event.key() == Qt.Key.Key_M:
            self.close_map()
        else:
            super().keyPressEvent(event)

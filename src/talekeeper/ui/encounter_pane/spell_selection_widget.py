# core
# category: core
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QComboBox, QCheckBox, QTextEdit, QScrollArea, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
import sqlite3
import json
from typing import Dict, List, Optional, Set


class SpellSelectionWidget(QWidget):

    spells_changed = pyqtSignal()

    def __init__(self, parent=None, db_path='talekeeper.db'):
        super().__init__(parent)
        self.db_path = db_path

        self.selected_cantrips: List[str] = []
        self.selected_spells: List[str] = []

        self.cantrip_combos: List[QComboBox] = []
        self.spell_checkboxes: Dict[str, QCheckBox] = {}

        self.spell_requirements = {
            'wizard': {
                'cantrips': 3,
                'known_spells': 6,
                'prepare_spells': False,
            },
            'cleric': {
                'cantrips': 3,
                'known_spells': 0,
                'prepare_spells': True,
            },
            'warlock': {
                'cantrips': 2,
                'known_spells': 2,
                'prepare_spells': False,
            },
            'paladin': {
                'cantrips': 0,
                'known_spells': 2,  # Level 1 paladins prepare 2 spells at creation
                'prepare_spells': True,
            }
        }

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        self.cantrip_container = QWidget()
        self.cantrip_layout = QVBoxLayout(self.cantrip_container)
        self.cantrip_layout.setContentsMargins(0, 0, 0, 0)
        self.cantrip_layout.setSpacing(1)
        layout.addWidget(self.cantrip_container)

        self.spell_container = QWidget()
        self.spell_layout = QVBoxLayout(self.spell_container)
        self.spell_layout.setContentsMargins(0, 0, 0, 0)
        self.spell_layout.setSpacing(1)
        layout.addWidget(self.spell_container)

        self.spell_description = QTextEdit()
        self.spell_description.setObjectName("spellDescription")
        self.spell_description.setMaximumHeight(100)
        self.spell_description.setReadOnly(True)
        self.spell_description.setPlaceholderText("Hover over a spell to see its description")
        layout.addWidget(self.spell_description)

    def setup_for_class(self, class_name: str):
        class_id = class_name.lower()

        if class_id not in self.spell_requirements:
            self.hide()
            return

        self.show()
        self._clear_widgets()

        reqs = self.spell_requirements[class_id]

        if reqs['cantrips'] > 0:
            self._setup_cantrip_selection(class_id, reqs['cantrips'])

        if reqs['known_spells'] > 0:
            self._setup_spell_selection(class_id, reqs['known_spells'])
        elif reqs['prepare_spells']:
            self._setup_preparation_info(class_id)

    def _clear_widgets(self):
        for i in reversed(range(self.cantrip_layout.count())):
            widget = self.cantrip_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for i in reversed(range(self.spell_layout.count())):
            widget = self.spell_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.cantrip_combos.clear()
        self.spell_checkboxes.clear()
        self.selected_cantrips.clear()
        self.selected_spells.clear()

    def _setup_cantrip_selection(self, class_id: str, count: int):
        group = QGroupBox(f"Cantrips - Choose {count}")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(1)

        cantrips = self._load_spells_for_class(class_id, level=0)

        for i in range(count):
            combo_layout = QHBoxLayout()
            combo_layout.setSpacing(5)

            label = QLabel(f"Cantrip {i+1}:")
            combo_layout.addWidget(label)

            combo = QComboBox()
            combo.addItem("Select a cantrip...", None)

            for spell in cantrips:
                combo.addItem(spell['name'], spell['id'])

            combo.currentIndexChanged.connect(lambda idx, c=combo: self._on_cantrip_selected(c))
            combo.setProperty('spell_data', cantrips)

            combo_layout.addWidget(combo)
            layout.addLayout(combo_layout)

            self.cantrip_combos.append(combo)

        self.cantrip_layout.addWidget(group)

    def _setup_spell_selection(self, class_id: str, count: int):
        group = QGroupBox(f"Level 1 Spells - Choose {count}")
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(5, 5, 5, 5)
        group_layout.setSpacing(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(200)

        content = QWidget()
        grid = QGridLayout(content)
        grid.setSpacing(1)

        spells = self._load_spells_for_class(class_id, level=1)

        self.spell_count_label = QLabel(f"Selected: 0/{count}")
        grid.addWidget(self.spell_count_label, 0, 0, 1, 2)

        row = 1
        col = 0
        for spell in spells:
            cb = QCheckBox(spell['name'])
            cb.setProperty('spell_id', spell['id'])
            cb.setProperty('spell_data', spell)
            cb.toggled.connect(lambda checked, s=spell['id']: self._on_spell_toggled(s, checked, count))

            grid.addWidget(cb, row, col)
            self.spell_checkboxes[spell['id']] = cb

            col += 1
            if col > 1:
                col = 0
                row += 1

        scroll.setWidget(content)
        group_layout.addWidget(scroll)

        self.spell_layout.addWidget(group)

    def _setup_preparation_info(self, class_id: str):
        if class_id == 'cleric':
            info_text = "Clerics prepare spells from their full spell list. After character creation, you can prepare a number of spells equal to your Wisdom modifier + your level (minimum 1)."
        elif class_id == 'paladin':
            info_text = "Paladins prepare spells from their spell list. After character creation, you can prepare a number of spells equal to your Charisma modifier + half your level (minimum 1)."
        else:
            info_text = "You will prepare spells after character creation."

        label = QLabel(info_text)
        label.setWordWrap(True)
        label.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
        self.spell_layout.addWidget(label)

    def _on_cantrip_selected(self, combo: QComboBox):
        cantrip_id = combo.currentData()

        self.selected_cantrips = []
        for c in self.cantrip_combos:
            spell_id = c.currentData()
            if spell_id:
                self.selected_cantrips.append(spell_id)

        spell_data = combo.property('spell_data')
        if spell_data and cantrip_id:
            spell = next((s for s in spell_data if s['id'] == cantrip_id), None)
            if spell:
                self._show_spell_description(spell)

        self.spells_changed.emit()

    def _on_spell_toggled(self, spell_id: str, checked: bool, max_spells: int):
        selected_count = sum(1 for cb in self.spell_checkboxes.values() if cb.isChecked())

        if checked and selected_count > max_spells:
            sender_cb = self.spell_checkboxes.get(spell_id)
            if sender_cb:
                sender_cb.blockSignals(True)
                sender_cb.setChecked(False)
                sender_cb.blockSignals(False)
            return

        for spell_id_iter, cb in self.spell_checkboxes.items():
            if not cb.isChecked():
                cb.setEnabled(selected_count < max_spells)

        self.selected_spells = [sid for sid, cb in self.spell_checkboxes.items() if cb.isChecked()]

        if hasattr(self, 'spell_count_label'):
            self.spell_count_label.setText(f"Selected: {selected_count}/{max_spells}")

        if checked:
            cb = self.spell_checkboxes.get(spell_id)
            if cb:
                spell_data = cb.property('spell_data')
                if spell_data:
                    self._show_spell_description(spell_data)

        self.spells_changed.emit()

    def _show_spell_description(self, spell: Dict):
        html = f"<h3>{spell['name']}</h3>"
        html += f"<p><b>Level:</b> {spell['level']} | <b>School:</b> {spell['school']}</p>"
        html += f"<p><b>Casting Time:</b> {spell['casting_time']} | <b>Range:</b> {spell['range_value']}</p>"
        html += f"<p><b>Components:</b> {spell['components']} | <b>Duration:</b> {spell['duration']}</p>"
        html += f"<p>{spell['description']}</p>"
        if spell.get('higher_levels'):
            html += f"<p><i>At Higher Levels: {spell['higher_levels']}</i></p>"
        self.spell_description.setHtml(html)

    def _load_spells_for_class(self, class_id: str, level: int) -> List[Dict]:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, level, school, casting_time, range_value,
                       components, duration, concentration, ritual,
                       description, higher_levels, source, classes
                FROM spells
                WHERE level = ?
                ORDER BY name
            """, (level,))

            spells = []
            for row in cursor.fetchall():
                spell_classes = json.loads(row[13]) if row[13] else []

                if class_id in spell_classes:
                    spells.append({
                        'id': row[0],
                        'name': row[1],
                        'level': row[2],
                        'school': row[3],
                        'casting_time': row[4],
                        'range_value': row[5],
                        'components': row[6],
                        'duration': row[7],
                        'concentration': row[8],
                        'ritual': row[9],
                        'description': row[10],
                        'higher_levels': row[11],
                        'source': row[12],
                        'classes': spell_classes
                    })

            conn.close()
            return spells

        except Exception as e:
            print(f"Error loading spells: {e}")
            return []

    def get_selected_cantrips(self) -> List[str]:
        return self.selected_cantrips

    def get_selected_spells(self) -> List[str]:
        return self.selected_spells

    def is_selection_complete(self, class_name: str) -> bool:
        class_id = class_name.lower()

        if class_id not in self.spell_requirements:
            return True

        reqs = self.spell_requirements[class_id]

        if reqs['cantrips'] > 0:
            if len(self.selected_cantrips) < reqs['cantrips']:
                return False

        if reqs['known_spells'] > 0:
            if len(self.selected_spells) < reqs['known_spells']:
                return False

        return True
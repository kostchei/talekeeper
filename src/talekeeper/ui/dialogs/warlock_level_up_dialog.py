# core
# category: core
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
import sqlite3
import json
from typing import List, Tuple, Optional


class WarlockLevelUpDialog(QDialog):
    def __init__(self, character_id: str, character_name: str, level: int,
                 invocations_to_learn: int, spells_to_learn: int = 0,
                 cantrips_to_learn: int = 0,
                 db_path: str = 'talekeeper.db', parent=None):
        super().__init__(parent)
        self.character_id = character_id
        self.character_name = character_name
        self.level = level
        self.invocations_to_learn = invocations_to_learn
        self.spells_to_learn = spells_to_learn
        self.cantrips_to_learn = cantrips_to_learn
        self.db_path = db_path

        self.selected_invocations: List[str] = []
        self.selected_spells: List[str] = []
        self.selected_cantrips: List[str] = []

        self.setWindowTitle(f"Warlock Level {level} - {character_name}")
        self.setMinimumSize(800, 600)

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel(f"<h2>Level {self.level} Warlock Advancement</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        if self.invocations_to_learn > 0:
            inv_group = QGroupBox(f"Select {self.invocations_to_learn} Eldritch Invocation(s)")
            inv_layout = QVBoxLayout(inv_group)

            self.invocation_list = QListWidget()
            self.invocation_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
            self.invocation_list.itemClicked.connect(self._on_invocation_clicked)
            inv_layout.addWidget(self.invocation_list)

            self.invocation_desc = QTextEdit()
            self.invocation_desc.setReadOnly(True)
            self.invocation_desc.setMaximumHeight(100)
            self.invocation_desc.setPlaceholderText("Select an invocation to see its description")
            inv_layout.addWidget(self.invocation_desc)

            layout.addWidget(inv_group)

        # Cantrip selection
        if self.cantrips_to_learn > 0:
            cantrip_group = QGroupBox(f"Select {self.cantrips_to_learn} Cantrip(s)")
            cantrip_layout = QVBoxLayout(cantrip_group)

            cantrip_info_text = f"Select {self.cantrips_to_learn} cantrip(s):"
            cantrip_info = QLabel(cantrip_info_text)
            cantrip_layout.addWidget(cantrip_info)

            self.cantrip_list = QListWidget()
            if self.cantrips_to_learn > 1:
                self.cantrip_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
            else:
                self.cantrip_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
            self.cantrip_list.itemClicked.connect(self._on_cantrip_clicked)
            cantrip_layout.addWidget(self.cantrip_list)

            self.cantrip_desc = QTextEdit()
            self.cantrip_desc.setReadOnly(True)
            self.cantrip_desc.setMaximumHeight(100)
            self.cantrip_desc.setPlaceholderText("Select a cantrip to see its description")
            cantrip_layout.addWidget(self.cantrip_desc)

            layout.addWidget(cantrip_group)
        else:
            self.cantrip_list = None
            self.cantrip_desc = None

        # Only show spell selection if spells need to be learned
        if self.spells_to_learn > 0:
            spell_group = QGroupBox(f"Select {self.spells_to_learn} Additional Spell(s)")
            spell_layout = QVBoxLayout(spell_group)

            spell_info_text = "Warlocks learn new spells when leveling up. "
            if self.spells_to_learn == 1:
                spell_info_text += "Select 1 additional spell:"
            else:
                spell_info_text += f"Select {self.spells_to_learn} additional spells:"
            spell_info = QLabel(spell_info_text)
            spell_layout.addWidget(spell_info)

            self.spell_list = QListWidget()
            # Use multi-selection if learning multiple spells
            if self.spells_to_learn > 1:
                self.spell_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
            else:
                self.spell_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
            self.spell_list.itemClicked.connect(self._on_spell_clicked)
            spell_layout.addWidget(self.spell_list)
        else:
            # Create empty group to maintain layout
            spell_group = QGroupBox("No new spells this level")
            spell_layout = QVBoxLayout(spell_group)
            spell_info = QLabel("You don't learn additional spells at this level.")
            spell_layout.addWidget(spell_info)

            self.spell_list = None

        self.spell_desc = QTextEdit()
        self.spell_desc.setReadOnly(True)
        self.spell_desc.setMaximumHeight(100)
        self.spell_desc.setPlaceholderText("Select a spell to see its description")
        spell_layout.addWidget(self.spell_desc)

        layout.addWidget(spell_group)

        button_layout = QHBoxLayout()

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self._on_confirm)
        button_layout.addWidget(self.confirm_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def _load_data(self):
        self._load_invocations()
        self._load_cantrips()
        self._load_spells()

    def _load_invocations(self):
        if self.invocations_to_learn <= 0:
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT wf.pact_boon FROM warlock_features wf
                    WHERE wf.character_id = ?
                """, (self.character_id,))
                pact_boon_row = cursor.fetchone()
                pact_boon = pact_boon_row[0] if pact_boon_row and pact_boon_row[0] else None

                cursor.execute("""
                    SELECT wi.invocation_id FROM warlock_invocations wi
                    WHERE wi.character_id = ?
                """, (self.character_id,))
                known_invocations = [row[0] for row in cursor.fetchall()]

                cursor.execute("""
                    SELECT id, name, description, prerequisites
                    FROM invocations
                    ORDER BY name
                """)

                for row in cursor.fetchall():
                    inv_id, name, description, prereqs_json = row

                    if inv_id in known_invocations:
                        continue

                    prereqs = json.loads(prereqs_json) if prereqs_json else {}

                    if not self._meets_invocation_prerequisites(prereqs, pact_boon):
                        continue

                    item = QListWidgetItem(name)
                    item.setData(Qt.ItemDataRole.UserRole, {
                        'id': inv_id,
                        'name': name,
                        'description': description
                    })
                    self.invocation_list.addItem(item)

        except Exception as e:
            print(f"Error loading invocations: {e}")
            import traceback
            traceback.print_exc()

    def _meets_invocation_prerequisites(self, prereqs: dict, pact_boon: Optional[str]) -> bool:
        if 'level' in prereqs and self.level < prereqs['level']:
            return False

        if 'pact' in prereqs:
            if not pact_boon or pact_boon != prereqs['pact']:
                return False

        return True

    def _load_cantrips(self):
        # Skip if no cantrip list widget (no cantrips to learn)
        if self.cantrip_list is None:
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get known cantrips
                cursor.execute("""
                    SELECT spell_id FROM character_spells
                    WHERE character_id = ?
                """, (self.character_id,))
                known_spell_ids = [row[0] for row in cursor.fetchall()]

                # Get available warlock cantrips
                cursor.execute("""
                    SELECT s.id, s.name, s.school, s.casting_time,
                           s.range_value, s.components, s.duration, s.description
                    FROM spells s
                    JOIN spell_class_availability sca ON s.id = sca.spell_id
                    WHERE sca.class_id = 'warlock'
                      AND s.level = 0
                    ORDER BY s.name
                """)

                for row in cursor.fetchall():
                    spell_id, name, school, casting_time, spell_range, components, duration, description = row

                    if spell_id in known_spell_ids:
                        continue

                    item = QListWidgetItem(name)
                    item.setData(Qt.ItemDataRole.UserRole, {
                        'id': spell_id,
                        'name': name,
                        'level': 0,
                        'school': school,
                        'casting_time': casting_time,
                        'range': spell_range,
                        'components': components,
                        'duration': duration,
                        'description': description
                    })
                    self.cantrip_list.addItem(item)

        except Exception as e:
            print(f"Error loading cantrips: {e}")
            import traceback
            traceback.print_exc()

    def _load_spells(self):
        # Skip if no spell list widget (no spells to learn)
        if self.spell_list is None:
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT spell_id FROM character_spells
                    WHERE character_id = ?
                """, (self.character_id,))
                known_spell_ids = [row[0] for row in cursor.fetchall()]

                max_spell_level = min(5, (self.level + 1) // 2)

                cursor.execute("""
                    SELECT s.id, s.name, s.level, s.school, s.casting_time,
                           s.range_value, s.components, s.duration, s.description
                    FROM spells s
                    JOIN spell_class_availability sca ON s.id = sca.spell_id
                    WHERE sca.class_id = 'warlock'
                      AND s.level > 0
                      AND s.level <= ?
                    ORDER BY s.level, s.name
                """, (max_spell_level,))

                for row in cursor.fetchall():
                    spell_id, name, level, school, casting_time, spell_range, components, duration, description = row

                    if spell_id in known_spell_ids:
                        continue

                    display_name = f"{name} (Lv {level})"
                    item = QListWidgetItem(display_name)
                    item.setData(Qt.ItemDataRole.UserRole, {
                        'id': spell_id,
                        'name': name,
                        'level': level,
                        'school': school,
                        'casting_time': casting_time,
                        'range': spell_range,
                        'components': components,
                        'duration': duration,
                        'description': description
                    })
                    self.spell_list.addItem(item)

        except Exception as e:
            print(f"Error loading spells: {e}")
            import traceback
            traceback.print_exc()

    def _on_invocation_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.invocation_desc.setPlainText(data['description'])

    def _on_cantrip_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data and self.cantrip_desc:
            desc_text = f"{data['name']} (Cantrip {data['school']})\n\n"
            desc_text += f"Casting Time: {data['casting_time']}\n"
            desc_text += f"Range: {data['range']}\n"
            desc_text += f"Components: {data['components']}\n"
            desc_text += f"Duration: {data['duration']}\n\n"
            desc_text += data['description']
            self.cantrip_desc.setPlainText(desc_text)

    def _on_spell_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            desc_text = f"{data['name']} (Level {data['level']} {data['school']})\n\n"
            desc_text += f"Casting Time: {data['casting_time']}\n"
            desc_text += f"Range: {data['range']}\n"
            desc_text += f"Components: {data['components']}\n"
            desc_text += f"Duration: {data['duration']}\n\n"
            desc_text += data['description']
            self.spell_desc.setPlainText(desc_text)

    def _on_confirm(self):
        if self.invocations_to_learn > 0:
            selected_inv_items = self.invocation_list.selectedItems()
            if len(selected_inv_items) != self.invocations_to_learn:
                QMessageBox.warning(self, "Incomplete Selection",
                                  f"Please select exactly {self.invocations_to_learn} invocation(s).")
                return

            self.selected_invocations = [
                item.data(Qt.ItemDataRole.UserRole)['id']
                for item in selected_inv_items
            ]

        # Check cantrip selection if cantrips need to be learned
        if self.cantrips_to_learn > 0 and self.cantrip_list is not None:
            selected_cantrip_items = self.cantrip_list.selectedItems()
            if len(selected_cantrip_items) != self.cantrips_to_learn:
                if len(selected_cantrip_items) == 0:
                    reply = QMessageBox.question(self, "No Cantrip Selected",
                                                f"You haven't selected any cantrips. You need to select {self.cantrips_to_learn}. Continue without selecting?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.No:
                        return
                else:
                    QMessageBox.warning(self, "Incorrect Selection",
                                      f"Please select exactly {self.cantrips_to_learn} cantrip(s). You selected {len(selected_cantrip_items)}.")
                    return
            else:
                self.selected_cantrips = [
                    item.data(Qt.ItemDataRole.UserRole)['id']
                    for item in selected_cantrip_items
                ]

        # Check spell selection if spells need to be learned
        if self.spells_to_learn > 0 and self.spell_list is not None:
            selected_spell_items = self.spell_list.selectedItems()
            if len(selected_spell_items) != self.spells_to_learn:
                if len(selected_spell_items) == 0:
                    reply = QMessageBox.question(self, "No Spell Selected",
                                                f"You haven't selected any spells. You need to select {self.spells_to_learn}. Continue without selecting?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.No:
                        return
                else:
                    QMessageBox.warning(self, "Incorrect Selection",
                                      f"Please select exactly {self.spells_to_learn} spell(s). You selected {len(selected_spell_items)}.")
                    return
            else:
                self.selected_spells = [
                    item.data(Qt.ItemDataRole.UserRole)['id']
                    for item in selected_spell_items
                ]

        self.accept()

    def get_selections(self) -> Tuple[List[str], List[str], List[str]]:
        """Returns (invocations, spells, cantrips)"""
        return self.selected_invocations, self.selected_spells, self.selected_cantrips

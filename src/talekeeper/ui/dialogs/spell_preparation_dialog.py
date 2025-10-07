from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QScrollArea, QWidget, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt
import sqlite3
from typing import List, Dict, Any


class SpellPreparationDialog(QDialog):

    def __init__(self, character_id: str, character_name: str, db_path: str = 'talekeeper.db', parent=None):
        super().__init__(parent)
        self.character_id = character_id
        self.character_name = character_name
        self.db_path = db_path
        self.prepared_spells = set()
        self.always_prepared_spells = set()
        self.spell_checkboxes = {}

        self._load_character_data()
        self._setup_ui()
        self._load_spells()

    def _load_character_data(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT c.class_id, c.level, c.charisma, c.wisdom, c.intelligence,
                       cs.spellcasting_ability
                FROM characters c
                LEFT JOIN character_spellcasting cs ON c.id = cs.character_id
                WHERE c.id = ?
            """, (self.character_id,))

            row = cursor.fetchone()
            if row:
                self.class_id = row['class_id']
                self.level = row['level']
                self.spellcasting_ability = row['spellcasting_ability'] or 'charisma'

                # D&D 2024: Fixed prepared spells by class and level
                if self.class_id == 'paladin':
                    # Paladin prepared spells from SRD table
                    paladin_prepared = {
                        1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 6, 7: 7, 8: 7, 9: 9, 10: 9,
                        11: 10, 12: 10, 13: 11, 14: 11, 15: 12, 16: 12, 17: 14, 18: 14, 19: 15, 20: 15
                    }
                    self.max_prepared = paladin_prepared.get(self.level, 2)
                elif self.class_id == 'cleric':
                    # Cleric prepared spells from SRD table
                    cleric_prepared = {
                        1: 4, 2: 5, 3: 6, 4: 7, 5: 9, 6: 9, 7: 10, 8: 10, 9: 12, 10: 12,
                        11: 13, 12: 13, 13: 14, 14: 14, 15: 15, 16: 15, 17: 16, 18: 17, 19: 18, 20: 19
                    }
                    self.max_prepared = cleric_prepared.get(self.level, 4)
                elif self.class_id == 'wizard':
                    # Wizard prepared spells from SRD table
                    wizard_prepared = {
                        1: 4, 2: 5, 3: 6, 4: 7, 5: 9, 6: 9, 7: 10, 8: 10, 9: 12, 10: 12,
                        11: 13, 12: 13, 13: 14, 14: 14, 15: 15, 16: 15, 17: 16, 18: 17, 19: 18, 20: 19
                    }
                    self.max_prepared = wizard_prepared.get(self.level, 4)
                elif self.class_id == 'warlock':
                    # Warlock prepared spells from SRD table
                    warlock_prepared = {
                        1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 10,
                        11: 11, 12: 11, 13: 12, 14: 12, 15: 13, 16: 13, 17: 14, 18: 14, 19: 15, 20: 15
                    }
                    self.max_prepared = warlock_prepared.get(self.level, 2)
                elif self.class_id == 'bard':
                    # Bard prepared spells from SRD table
                    bard_prepared = {
                        1: 4, 2: 5, 3: 6, 4: 7, 5: 9, 6: 10, 7: 11, 8: 12, 9: 14, 10: 15,
                        11: 16, 12: 16, 13: 17, 14: 17, 15: 18, 16: 18, 17: 19, 18: 20, 19: 21, 20: 22
                    }
                    self.max_prepared = bard_prepared.get(self.level, 4)
                elif self.class_id == 'druid':
                    # Druid prepared spells from SRD table
                    druid_prepared = {
                        1: 4, 2: 5, 3: 6, 4: 7, 5: 9, 6: 10, 7: 11, 8: 12, 9: 14, 10: 15,
                        11: 16, 12: 16, 13: 17, 14: 17, 15: 18, 16: 18, 17: 19, 18: 20, 19: 21, 20: 22
                    }
                    self.max_prepared = druid_prepared.get(self.level, 4)
                elif self.class_id == 'ranger':
                    # Ranger prepared spells from SRD table
                    ranger_prepared = {
                        1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 6, 7: 7, 8: 7, 9: 9, 10: 9,
                        11: 10, 12: 10, 13: 11, 14: 11, 15: 12, 16: 12, 17: 14, 18: 14, 19: 15, 20: 15
                    }
                    self.max_prepared = ranger_prepared.get(self.level, 2)
                elif self.class_id == 'sorcerer':
                    # Sorcerer prepared spells from SRD table
                    sorcerer_prepared = {
                        1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11,
                        11: 12, 12: 12, 13: 13, 14: 13, 15: 14, 16: 14, 17: 15, 18: 15, 19: 16, 20: 17
                    }
                    self.max_prepared = sorcerer_prepared.get(self.level, 2)
                else:
                    # Fallback - shouldn't reach here in D&D 2024
                    self.max_prepared = 2

            cursor.execute("""
                SELECT spell_id, is_prepared, always_prepared
                FROM character_spells
                WHERE character_id = ?
            """, (self.character_id,))

            for row in cursor.fetchall():
                if row['always_prepared']:
                    self.always_prepared_spells.add(row['spell_id'])
                if row['is_prepared'] or row['always_prepared']:
                    self.prepared_spells.add(row['spell_id'])

    def _setup_ui(self):
        self.setWindowTitle(f"Prepare Spells - {self.character_name}")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        layout = QVBoxLayout(self)

        info_text = f"<b>{self.character_name}</b> ({self.class_id.title()} {self.level})<br>"
        info_text += f"You can prepare <b>{self.max_prepared}</b> spells from your spell list.<br>"
        info_text += f"Oath/Domain spells (if any) are always prepared and don't count toward this limit."

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        self.count_label = QLabel("")
        self.count_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.count_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(350)

        scroll_content = QWidget()
        self.spell_layout = QVBoxLayout(scroll_content)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.confirm_btn = QPushButton("Confirm Preparation")
        self.confirm_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.confirm_btn)

        layout.addLayout(button_layout)

    def _load_spells(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT cs.spell_id, s.name, s.level, s.school, s.description,
                       cs.is_prepared, cs.always_prepared, cs.source
                FROM character_spells cs
                JOIN spells s ON cs.spell_id = s.id
                WHERE cs.character_id = ?
                ORDER BY s.level, s.name
            """, (self.character_id,))

            spells = [dict(row) for row in cursor.fetchall()]

        spells_by_level = {}
        for spell in spells:
            level = spell['level']
            if level not in spells_by_level:
                spells_by_level[level] = []
            spells_by_level[level].append(spell)

        for level in sorted(spells_by_level.keys()):
            if level == 0:
                continue

            group = QGroupBox(f"Level {level} Spells")
            grid = QGridLayout(group)

            row = 0
            col = 0
            for spell in spells_by_level[level]:
                cb = QCheckBox(spell['name'])
                cb.setProperty('spell_data', spell)

                if spell['always_prepared']:
                    cb.setChecked(True)
                    cb.setEnabled(False)
                    cb.setToolTip(f"{spell['description'][:100]}...\n\n[Always Prepared from {spell['source']}]")
                else:
                    cb.setChecked(spell['spell_id'] in self.prepared_spells)
                    cb.setToolTip(f"{spell['description'][:100]}...")
                    cb.toggled.connect(lambda checked, sid=spell['spell_id']: self._on_spell_toggled(sid, checked))

                grid.addWidget(cb, row, col)
                self.spell_checkboxes[spell['spell_id']] = cb

                col += 1
                if col > 1:
                    col = 0
                    row += 1

            self.spell_layout.addWidget(group)

        self._update_count()

    def _on_spell_toggled(self, spell_id: str, checked: bool):
        if checked:
            self.prepared_spells.add(spell_id)
        else:
            self.prepared_spells.discard(spell_id)

        self._update_count()

        non_always_prepared = len(self.prepared_spells - self.always_prepared_spells)

        if non_always_prepared > self.max_prepared:
            for sid, cb in self.spell_checkboxes.items():
                if not cb.isChecked() and sid not in self.always_prepared_spells:
                    cb.setEnabled(False)
        else:
            for sid, cb in self.spell_checkboxes.items():
                if sid not in self.always_prepared_spells:
                    cb.setEnabled(True)

    def _update_count(self):
        non_always_prepared = len(self.prepared_spells - self.always_prepared_spells)
        always_count = len(self.always_prepared_spells)

        self.count_label.setText(
            f"Prepared: {non_always_prepared}/{self.max_prepared} "
            f"(+{always_count} always prepared)"
        )

        if non_always_prepared > self.max_prepared:
            self.count_label.setStyleSheet("font-weight: bold; font-size: 14px; color: red;")
            self.confirm_btn.setEnabled(False)
        elif non_always_prepared < self.max_prepared:
            self.count_label.setStyleSheet("font-weight: bold; font-size: 14px; color: orange;")
            self.confirm_btn.setEnabled(True)
        else:
            self.count_label.setStyleSheet("font-weight: bold; font-size: 14px; color: green;")
            self.confirm_btn.setEnabled(True)

    def get_prepared_spells(self) -> List[str]:
        return list(self.prepared_spells)

    def save_prepared_spells(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE character_spells
                SET is_prepared = 0
                WHERE character_id = ? AND always_prepared = 0
            """, (self.character_id,))

            for spell_id in self.prepared_spells:
                cursor.execute("""
                    UPDATE character_spells
                    SET is_prepared = 1
                    WHERE character_id = ? AND spell_id = ?
                """, (self.character_id, spell_id))

            conn.commit()

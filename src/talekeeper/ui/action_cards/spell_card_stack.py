from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Dict, Any


class SpellCardStack(QFrame):

    spell_cast = pyqtSignal(dict)

    def __init__(self, spell_level: int, cast_type: str, spells: List[Dict[str, Any]],
                 available_slots: int, max_slots: int, parent=None):
        super().__init__(parent)
        self.spell_level = spell_level
        self.cast_type = cast_type
        self.spells = sorted(spells, key=lambda s: s['name'])
        self.available_slots = available_slots
        self.max_slots = max_slots
        self.current_index = 0

        self.setObjectName("spellCardStack")
        self.setFixedSize(140, 180)

        self._setup_ui()
        self._update_display()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        self.header_label = QLabel()
        self.header_label.setObjectName("spellCardHeader")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.header_label)

        self.name_label = QLabel()
        self.name_label.setObjectName("spellCardName")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)

        self.effect_label = QLabel()
        self.effect_label.setObjectName("spellCardEffect")
        self.effect_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.effect_label.setWordWrap(True)
        layout.addWidget(self.effect_label, 1)

        layout.addStretch()

        self.cast_button = QPushButton("Cast")
        self.cast_button.setObjectName("spellCastButton")
        self.cast_button.clicked.connect(self._on_cast_clicked)
        layout.addWidget(self.cast_button)

        if len(self.spells) > 1:
            self.mousePressEvent = self._on_card_clicked

    def _update_display(self):
        if self.spell_level == 0:
            header = "Cantrips"
        else:
            header = f"Lv {self.spell_level} {self.available_slots}/{self.max_slots}"

        if len(self.spells) > 1:
            header += f" ({self.current_index + 1}/{len(self.spells)})"

        self.header_label.setText(header)

        if not self.spells:
            self.name_label.setText("No spells")
            self.effect_label.setText("")
            self.cast_button.setEnabled(False)
            return

        current_spell = self.spells[self.current_index]
        self.name_label.setText(current_spell['name'])

        effect = self._get_spell_effect(current_spell)
        self.effect_label.setText(effect)

        can_cast = self.spell_level == 0 or self.available_slots > 0
        self.cast_button.setEnabled(can_cast)

    def _get_spell_effect(self, spell: Dict[str, Any]) -> str:
        desc = spell.get('description', '')
        range_val = spell.get('range_value', 'Self')

        effects = []

        if 'extra 1d4 radiant' in desc.lower() or '1d4 radiant damage' in desc.lower():
            effects.append("1d4 radiant per strike")

        if '+2 bonus to AC' in desc:
            effects.append(f"+2 AC ({range_val})")

        if 'immune to.*frightened' in desc.lower():
            effects.append("Immune Frightened")

        if 'temporary hit points' in desc.lower():
            effects.append(f"Temp HP ({range_val})")

        if not effects:
            first_sentence = desc.split('.')[0]
            if len(first_sentence) > 60:
                first_sentence = first_sentence[:57] + "..."
            effects.append(first_sentence)

        if range_val.lower() not in ['self', 'touch'] and not any(range_val in e for e in effects):
            effects.insert(0, range_val)
        elif range_val.lower() == 'touch' and not any('Touch' in e for e in effects):
            effects.insert(0, "Touch")
        elif range_val.lower() == 'self' and not any('Self' in e for e in effects):
            effects.insert(0, "Self")

        return " | ".join(effects)

    def _on_card_clicked(self, event):
        if len(self.spells) <= 1:
            print(f"[SPELL STACK] Card clicked but only {len(self.spells)} spell(s)")
            return

        old_spell = self.spells[self.current_index]['name']
        self.current_index = (self.current_index + 1) % len(self.spells)
        new_spell = self.spells[self.current_index]['name']
        print(f"[SPELL STACK] Flipped from {old_spell} to {new_spell} ({self.current_index + 1}/{len(self.spells)})")
        self._update_display()

    def _on_cast_clicked(self):
        if not self.spells:
            return

        current_spell = self.spells[self.current_index]

        if self.spell_level > 0 and self.available_slots <= 0:
            return

        self.spell_cast.emit(current_spell)

    def update_slots(self, available: int, max_slots: int):
        self.available_slots = available
        self.max_slots = max_slots
        self._update_display()

    def update_theme_styles(self, theme: str):
        if theme == "light":
            self.setStyleSheet("""
                QFrame#spellCardStack {
                    background-color: #f4e5d4;
                    border: 2px solid #a45f38;
                    border-radius: 6px;
                }
                QLabel#spellCardHeader {
                    color: #000000;
                    font-weight: bold;
                    font-size: 10pt;
                }
                QLabel#spellCardName {
                    color: #000000;
                    font-weight: bold;
                    font-size: 9pt;
                }
                QLabel#spellCardEffect {
                    color: #000000;
                    font-size: 8pt;
                }
                QPushButton#spellCastButton {
                    background-color: #7c4f32;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    font-weight: bold;
                    font-size: 9pt;
                }
                QPushButton#spellCastButton:hover {
                    background-color: #2d8659;
                }
                QPushButton#spellCastButton:disabled {
                    background-color: #ddc3a7;
                    color: #83644b;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame#spellCardStack {
                    background-color: #2d2116;
                    border: 2px solid #4c3a2a;
                    border-radius: 6px;
                }
                QLabel#spellCardHeader {
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 10pt;
                }
                QLabel#spellCardName {
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 9pt;
                }
                QLabel#spellCardEffect {
                    color: #d4c4b0;
                    font-size: 8pt;
                }
                QPushButton#spellCastButton {
                    background-color: #4c3a2a;
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    font-weight: bold;
                    font-size: 9pt;
                }
                QPushButton#spellCastButton:hover {
                    background-color: #5f4934;
                }
                QPushButton#spellCastButton:disabled {
                    background-color: #3a2d20;
                    color: #6b5a47;
                }
            """)

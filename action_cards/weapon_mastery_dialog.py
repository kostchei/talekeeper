"""Weapon Mastery selection dialog for TaleKeeper."""

from typing import Dict, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QLabel,
)


class WeaponMasteryDialog(QDialog):
    """Allow the user to choose weapon mastery assignments."""

    def __init__(
        self,
        options: List[Dict[str, str]],
        selected: List[str],
        max_selections: Optional[int] = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Weapon Mastery Selection")
        self.resize(440, 520)

        self._options = options
        self._selected_names = {name.lower() for name in (selected or [])}
        self._max = max_selections if max_selections is not None else -1

        layout = QVBoxLayout(self)

        intro = QLabel(
            "Prepare the weapons whose mastery properties you want at your fingertips.\n"
            "Fighters never lose access to mastery techniques--swapping favorites after a rest just changes which ones are spotlighted."
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        self.list_widget = QListWidget(self)
        self.list_widget.itemChanged.connect(self._enforce_limit)
        layout.addWidget(self.list_widget)

        for option in options:
            weapon_name = option.get("weapon_name", "Unknown Weapon")
            mastery_type = option.get("mastery_type", "?")
            description = option.get("description", "")
            equipped = option.get("equipped", False)

            display = f"{weapon_name} - {mastery_type}"
            if equipped:
                display = f"[E] {display} (equipped)"
            if description:
                display += f"\n{description}"

            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, option)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if weapon_name.lower() in self._selected_names:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
            self.list_widget.addItem(item)

        self._enforce_limit()  # Apply limit immediately

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, parent=self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    # ------------------------------------------------------------------
    def _checked_items(self) -> List[QListWidgetItem]:
        return [
            self.list_widget.item(i)
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).checkState() == Qt.CheckState.Checked
        ]

    def _enforce_limit(self) -> None:
        if self._max is None or self._max < 0:
            return

        checked = self._checked_items()
        over_limit = len(checked) >= self._max >= 0

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                continue
            item.setFlags(
                (item.flags() | Qt.ItemFlag.ItemIsEnabled)
                if not over_limit
                else (item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            )

    # ------------------------------------------------------------------
    def selected_options(self) -> List[Dict[str, str]]:
        """Return the currently checked weapon mastery assignments."""
        selections: List[Dict[str, str]] = []
        for item in self._checked_items():
            option = item.data(Qt.ItemDataRole.UserRole) or {}
            weapon_name = option.get("weapon_name")
            mastery_type = option.get("mastery_type")
            if weapon_name and mastery_type:
                selections.append(
                    {
                        "weapon_name": weapon_name,
                        "mastery_type": mastery_type,
                    }
                )
        return selections


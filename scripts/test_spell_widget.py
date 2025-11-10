"""Test spell selection widget cantrip selection"""
import sys
sys.path.insert(0, 'src')

# Mock PyQt6 to avoid GUI requirements
from unittest.mock import MagicMock, Mock
sys.modules['PyQt6'] = MagicMock()
sys.modules['PyQt6.QtWidgets'] = MagicMock()
sys.modules['PyQt6.QtCore'] = MagicMock()

# Now import the widget
from talekeeper.ui.encounter_pane.spell_selection_widget import SpellSelectionWidget

# Create widget
widget = SpellSelectionWidget(db_path='talekeeper.db')

print("Testing spell widget cantrip selection:")
print(f"Initial selected_cantrips: {widget.selected_cantrips}")
print(f"Initial selected_spells: {widget.selected_spells}")

# Simulate what happens when widget is setup for warlock
print("\nCalling setup_for_class('warlock')...")
try:
    widget.setup_for_class('warlock')
    print(f"After setup - cantrip_combos created: {len(widget.cantrip_combos)}")
    print(f"After setup - selected_cantrips: {widget.selected_cantrips}")
except Exception as e:
    print(f"Setup failed: {e}")

# Simulate user selecting cantrips by directly calling _on_cantrip_selected
print("\nSimulating cantrip selections...")

# Create mock combos that return spell IDs
mock_combo1 = Mock()
mock_combo1.currentData.return_value = 'eldritch_blast'
mock_combo2 = Mock()
mock_combo2.currentData.return_value = 'chill_touch'

# Replace the cantrip_combos with our mocks
widget.cantrip_combos = [mock_combo1, mock_combo2]

# Call _on_cantrip_selected to rebuild the list
print("Calling _on_cantrip_selected...")
try:
    widget._on_cantrip_selected(mock_combo1)
    print(f"After _on_cantrip_selected: {widget.selected_cantrips}")
    print(f"get_selected_cantrips() returns: {widget.get_selected_cantrips()}")
except Exception as e:
    print(f"_on_cantrip_selected failed: {e}")
    import traceback
    traceback.print_exc()

# Test what happens if combo returns None
print("\nTesting with None (default selection):")
mock_combo1.currentData.return_value = None
mock_combo2.currentData.return_value = None
widget.cantrip_combos = [mock_combo1, mock_combo2]

try:
    widget._on_cantrip_selected(mock_combo1)
    print(f"After selecting None: {widget.selected_cantrips}")
    print(f"get_selected_cantrips() returns: {widget.get_selected_cantrips()}")
except Exception as e:
    print(f"Failed: {e}")

# test
#utility
# test
import sys
from PyQt6.QtWidgets import QApplication
from log.log_panel import LogPanel, LogLevel
from core.config import get_config

def test_narrative_log():
    app = QApplication(sys.argv)

    config = get_config()

    print(f"Narrative config loaded:")
    print(f"  enable_combat_narratives: {config.narrative.enable_combat_narratives}")
    print(f"  enable_round_summaries: {config.narrative.enable_round_summaries}")
    print(f"  enable_victory_narratives: {config.narrative.enable_victory_narratives}")
    print(f"  show_only_narratives: {config.narrative.show_only_narratives}")
    print()

    log_panel = LogPanel()
    log_panel.show()

    log_panel.log_combat("Fighter attacks Goblin")
    log_panel.log_dice("Roll: 18+5=23 vs AC 15 - HIT!")
    log_panel.log_combat("Damage: 1d8+3 = 11")
    log_panel.log_narrative("Your blade carves through goblin flesh with savage precision.\nThe creature shrieks as steel bites deep.")

    log_panel.log_combat("\nGoblin attacks Fighter")
    log_panel.log_dice("Roll: 12+4=16 vs AC 18 - MISS!")
    log_panel.log_narrative("The goblin's crude blade clangs uselessly against your shield.")

    log_panel.log_system("\n--- Round 1 Complete ---")

    print("\nTest completed. Check the log panel window.")
    print("Narrative messages should appear with >> prefix in light blue italic.")

    sys.exit(app.exec())

if __name__ == "__main__":
    test_narrative_log()

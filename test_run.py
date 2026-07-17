import sys
from PySide6.QtWidgets import QApplication
from main import DynastyApp

app = QApplication(sys.argv)
window = DynastyApp()

# Stub out the blocking end-game dialog so this can run headless.
window.show_end_game_dialog = lambda: None

window.dynasty_input.setText("唐")
window.emperor_input.setText("李世民")
window.year_number_input.setText("贞观")
window.start_game_from_ui()

# Run until the dynasty ends, or a safety limit is reached.
for _ in range(5000):
    if not window.ongame:
        break
    window.gamemin()

# Spot-check: chronicle rows carry emperor honorific when present
events = [e for e in window.event_happened[1:] if e.get("event")]
assert events, "expected chronicle events"
assert any(e.get("emperor") for e in events), "chronicle should record emperor (尊号)"

print(f"Passed: ran to year {window.year}, dynasty "
      f"{'ended' if window.dynasty_die else 'still standing'}, "
      f"{len(window.listjson)} emperors recorded, "
      f"{len(events)} chronicle rows")
sys.exit(0)

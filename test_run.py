import sys
from PySide6.QtWidgets import QApplication
from main import DynastyApp

app = QApplication(sys.argv)
window = DynastyApp()

# Stub out the blocking GUI dialogs so this can run as a headless smoke test.
window.show_new_emp_dialog = lambda: window.new_emp_confirm()
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

print(f"Passed: ran to year {window.year}, dynasty "
      f"{'ended' if window.dynasty_die else 'still standing'}, "
      f"{len(window.listjson)} emperors recorded")
sys.exit(0)

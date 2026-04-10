import sys
from PySide6.QtWidgets import QApplication
from main import DynastyApp

app = QApplication(sys.argv)
window = DynastyApp()

window.dynasty_input.setText("唐")
window.emperor_input.setText("李世民")
window.year_number_input.setText("贞观")
window.start_game_from_ui()

# Simulate a full loop with possible die scenario
for i in range(10):
    window.gamemin()
    if not window.ongame:
        # Emperor died
        window.new_emp_confirm()

print("Passed")
sys.exit(0)

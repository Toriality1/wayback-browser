from PyQt6.QtWidgets import QApplication
import sys
from browser.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


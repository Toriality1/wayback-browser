from PyQt6.QtWidgets import QToolBar, QLineEdit
from PyQt6.QtGui import QAction

class NavigationToolbar(QToolBar):
    def __init__(self, main_window):
        super().__init__("Navigation")
        self.main_window = main_window

        # --- Navigation Buttons ---
        back_btn = QAction("Back", main_window)
        back_btn.triggered.connect(main_window.view.back)
        self.addAction(back_btn)

        forward_btn = QAction("Forward", main_window)
        forward_btn.triggered.connect(main_window.view.forward)
        self.addAction(forward_btn)

        reload_btn = QAction("Reload", main_window)
        reload_btn.triggered.connect(main_window.view.reload)
        self.addAction(reload_btn)

        home_btn = QAction("Home", main_window)
        home_btn.triggered.connect(main_window.go_home)
        self.addAction(home_btn)

        # --- URL bar ---
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL...")
        self.url_bar.returnPressed.connect(main_window.navigate_to_url)
        self.url_bar.setMaximumWidth(800)
        self.addWidget(self.url_bar)


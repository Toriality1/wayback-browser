from PyQt6.QtWidgets import QMainWindow, QStatusBar, QProgressBar
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import sys
from .web_page import CustomWebPage
from .toolbar import NavigationToolbar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Web view ---
        self.view = QWebEngineView()
        self.page = CustomWebPage(self.view)
        self.view.setPage(self.page)
        self.setCentralWidget(self.view)

        # --- Navigation toolbar (top) ---
        self.nav_bar = NavigationToolbar(self)
        self.addToolBar(self.nav_bar)

        # --- Status bar (bottom) ---
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Add progress bar inside status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # --- Connect browser signals ---
        self.view.urlChanged.connect(self.update_url_bar)
        self.view.loadStarted.connect(self.on_load_started)
        self.view.loadProgress.connect(self.on_load_progress)
        self.view.loadFinished.connect(self.on_load_finished)

        # --- Window setup ---
        self.setWindowTitle("Wayback Browser")
        self.resize(1280, 720)

        # Load homepage
        self.go_home()

    # --- Page navigation ---
    def go_home(self):
        with open("home.html", "r") as f:
            home_html = f.read()
        self.view.setHtml(home_html, QUrl("file://" + sys.path[0] + "/home.html"))

    def navigate_to_url(self):
        url = self.nav_bar.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.view.setUrl(QUrl(url))

    def update_url_bar(self, url):
        self.nav_bar.url_bar.setText(url.toString())

    # --- Loading status handlers ---
    def on_load_started(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Loading page...")

    def on_load_progress(self, progress):
        self.progress_bar.setValue(progress)
        self.status_bar.showMessage(f"Loading... {progress}%")

    def on_load_finished(self, ok):
        self.progress_bar.setVisible(False)
        if ok:
            self.status_bar.showMessage("Page loaded successfully", 3000)
        else:
            self.status_bar.showMessage("Failed to load page", 3000)


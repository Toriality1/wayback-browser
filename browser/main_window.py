from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWidgets import QDockWidget, QMainWindow, QStatusBar, QProgressBar
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt
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

        # --- DevTools ---
        self.dev_tools = QWebEngineView()
        self.dev_tools_page = QWebEnginePage()
        self.dev_tools.setPage(self.dev_tools_page)
        self.dev_tools.show()
        self.page.setDevToolsPage(self.dev_tools_page)
        self.dev_dock = QDockWidget("Developer Tools", self)
        self.dev_dock.setWidget(self.dev_tools)
        self.dev_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dev_dock)
        self.resizeDocks([self.dev_dock], [400], Qt.Orientation.Horizontal)
        self.dev_dock.hide()


        # --- Keyboard shortcuts ---
        QShortcut(Qt.Key.Key_F5, self, self.view.reload)
        QShortcut(Qt.Key.Key_F11, self, self.toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+R"), self, self.view.reload)
        QShortcut(QKeySequence("Ctrl+L"), self, self.focus_url_bar)
        QShortcut(QKeySequence("Alt+Left"), self, self.view.back)
        QShortcut(QKeySequence("Alt+Right"), self, self.view.forward)
        QShortcut(QKeySequence("Alt+Home"), self, self.go_home)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Ctrl+Shift+I"), self, self.toggle_devtools)

        # --- Window setup ---
        self.setWindowTitle("Wayback Browser")
        self.resize(1280, 720)


        # Load homepage
        self.go_home()

    # --- Shortcut handlers ---
    def toggle_devtools(self):
        self.dev_dock.setVisible(not self.dev_dock.isVisible())

    def focus_url_bar(self):
        self.nav_bar.url_bar.setFocus()
        self.nav_bar.url_bar.selectAll()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

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


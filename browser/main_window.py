from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWidgets import QMainWindow, QStatusBar, QProgressBar
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from pathlib import Path

from .web_page import CustomWebPage
from .toolbar import NavigationToolbar
from .shortcuts import register_shortcuts
from .devtools import create_devtools
from .web_page import WaybackWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._connect_signals()
        self.dev_dock, self.dev_page = create_devtools(self)
        self.page.setDevToolsPage(self.dev_page)
        register_shortcuts(self)
        self.setWindowTitle("Wayback Browser")
        self.resize(1280, 720)
        self.go_home()

        self._wayyback_fetch_in_progress = False

    # ==========================================================
    # UI Setup
    # ==========================================================
    def _setup_ui(self):
        # Web view
        self.view = QWebEngineView()
        self.page = CustomWebPage(self.view)
        self.view.setPage(self.page)
        self.setCentralWidget(self.view)

        # Navigation toolbar
        self.nav_bar = NavigationToolbar(self)
        self.addToolBar(self.nav_bar)

        # Status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Progress bar inside status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setFixedHeight(14)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

    # ==========================================================
    # Signal Connections
    # ==========================================================
    def _connect_signals(self):
        self.view.urlChanged.connect(self.update_url_bar)
        self.view.loadStarted.connect(self.on_load_started)
        self.view.loadProgress.connect(self.on_load_progress)
        self.view.loadFinished.connect(self.on_load_finished)

    # ==========================================================
    # Navigation
    # ==========================================================
    def go_home(self):
        home_path = Path(__file__).resolve().parent / "resources" / "home.html"
        if home_path.exists():
            html = home_path.read_text(encoding="utf-8")
            self.view.setHtml(html, QUrl.fromLocalFile(str(home_path)))
        else:
            self.view.setHtml("<h1>Home page not found</h1>")


    def navigate_to_url(self):
        url = self.nav_bar.url_bar.text().strip()
        if not url:
            return
        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        self._wayback_fetch_in_progress = True
        self.nav_bar.url_bar.setEnabled(False)
        self.status_bar.showMessage("Fetching Wayback snapshot...")

        worker = WaybackWorker(url)
        # Connect to CustomWebPage._load_wayback_url
        worker.signals.finished.connect(
            lambda wayback_url: self.page._load_wayback_url(wayback_url, url)
        )
        # Connect MainWindow signal to reset state
        self.page.wayback_ready.connect(self._on_wayback_ready)
        self.page.thread_pool.start(worker)

    def _on_wayback_ready(self):
        self._wayback_fetch_in_progress = False
        self.nav_bar.url_bar.setEnabled(True)
        self.status_bar.showMessage("Snapshot loaded", 2000)
        # Disconnect to avoid multiple triggers
        self.page.wayback_ready.disconnect(self._on_wayback_ready)


    def update_url_bar(self, url: QUrl):
        if hasattr(self.page, "current_display_url") and self.page.current_display_url:
            self.nav_bar.url_bar.setText(self.page.current_display_url)
        else:
            self.nav_bar.url_bar.setText(url.toString())

    # ==========================================================
    # Loading Status
    # ==========================================================
    def on_load_started(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Loading page...")

    def on_load_progress(self, progress: int):
        self.progress_bar.setValue(progress)
        self.status_bar.showMessage(f"Loading... {progress}%")

    def on_load_finished(self, ok: bool):
        if self._wayyback_fetch_in_progress:
            # Ignore intermediate failures while fetching wayback
            return
        self.progress_bar.setVisible(False)
        if ok:
            self.status_bar.showMessage("Page loaded successfully", 3000)
        else:
            self.status_bar.showMessage("Failed to load page", 3000)

    # ==========================================================
    # Keyboard Shortcut Handlers
    # ==========================================================
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


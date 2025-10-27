from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QStatusBar, QToolBar, QLineEdit
from PyQt6.QtGui import QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl
import sys

class CustomWebPage(QWebEnginePage):
    def acceptNavigationRequest(self, url: QUrl, type, isMainFrame):
        if type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            print("Clicked URL:", url.toString())
            return False
        return True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.view = QWebEngineView()
        self.page = CustomWebPage(self.view)
        self.view.setPage(self.page)
        self.setCentralWidget(self.view)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.nav_bar = QToolBar("Navigation")
        self.addToolBar(self.nav_bar)

        back_btn = QAction("Back", self)
        back_btn.triggered.connect(self.view.back)
        self.nav_bar.addAction(back_btn)

        forward_btn = QAction("Forward", self)
        forward_btn.triggered.connect(self.view.forward)
        self.addAction(forward_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.view.reload)
        self.addAction(reload_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.view.reload)
        self.nav_bar.addAction(reload_btn)

        home_btn = QAction("Home", self)
        home_btn.triggered.connect(self.go_home)
        self.nav_bar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.nav_bar.addWidget(self.url_bar)

        self.loading_label = QLabel("Ready")
        self.nav_bar.addWidget(self.loading_label)

        self.view.urlChanged.connect(self.update_url_bar)
        self.view.loadStarted.connect(self.on_load_started)
        self.view.loadProgress.connect(self.on_load_progress)
        self.view.loadFinished.connect(self.on_load_finished)

        self.setWindowTitle("Wayback Browser")
        self.resize(1280, 720)

        self.go_home()

    def go_home(self):
        with (open("home.html", "r")) as f:
            home_html = f.read()
        self.view.setHtml(home_html, QUrl("file://" + sys.path[0] + "/home.html"))

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.view.setUrl(QUrl(url))

    def update_url_bar(self, url):
        self.url_bar.setText(url.toString())

    def on_load_started(self):
        self.loading_label.setText("Loading...")
        self.status_bar.showMessage("Loading page...")

    def on_load_progress(self, progress):
        self.loading_label.setText(f"Loading... {progress}%")
        self.status_bar.showMessage(f"Loading page... {progress}%")

    def on_load_finished(self, ok):
        if ok:
            self.loading_label.setText("Done")
            self.status_bar.showMessage("Page loaded.", 5000)
        else:
            self.loading_label.setText("Failed")
            self.status_bar.showMessage("Failed to load page.", 5000)

app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())


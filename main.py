import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QStatusBar
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineScript, QWebEnginePage
from PyQt5.QtGui import QDesktopServices

# class CustomWebEnginePage(QWebEnginePage):
#     """ Custom WebEnginePage to customize how we handle link navigation """
#     # Store external windows.
#     external_windows = []
#
#     def acceptNavigationRequest(self, url,  type, isMainFrame):
#         w = QWebEngineView()
#         w.setUrl(url)
#         w.show()
#
#         # Keep reference to external window, so it isn't cleared up.
#         self.external_windows.append(w)
#         # return super().acceptNavigationRequest(url,  _type, isMainFrame)

class MainWindow(QMainWindow):
    display_url: str = ""

    def __init__(self):
        super(MainWindow, self).__init__()
        self.browser = QWebEngineView()
        self.browser.setPage(CustomWebEnginePage())
        self.browser.setUrl(QUrl('https://www.google.com'))
        self.setCentralWidget(self.browser)
        self.showMaximized()
        navbar = QToolBar()
        self.addToolBar(navbar)
        back_btn = QAction('Back', self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)
        forward_btn = QAction('Forward', self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)
        reload_btn = QAction('Reload', self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)
        home_btn = QAction('Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)
        self.browser.urlChanged.connect(self.update_url)
        self.browser.loadStarted.connect(self.update_status_loading)
        self.browser.loadFinished.connect(self.load_finished)
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def navigate_home(self):
        self.display_url = 'https://www.google.com'
        self.browser.setUrl(QUrl(self.display_url))

    def get_wayback_snapshot_url(self, original_url):
        if not original_url.startswith(('http://', 'https://')):
            original_url = 'http://' + original_url
        mock_timestamp = "20000101000000"
        return f"http://web.archive.org/web/{mock_timestamp}id_/{original_url}"

    def navigate_to_url(self):
        original_url = self.url_bar.text().strip()
        is_wayback_request = True
        if is_wayback_request:
            wayback_snapshot_url = self.get_wayback_snapshot_url(original_url)
            self.display_url = original_url
            self.browser.setUrl(QUrl(wayback_snapshot_url))
            self.url_bar.setText(self.display_url)
        else:
            if not original_url.startswith(('http://', 'https://')):
                original_url = 'http://' + original_url
            self.browser.setUrl(QUrl(original_url))
            self.display_url = original_url


    def update_url(self, q):
        current_loaded_url = q.toString()
        wayback_prefix = "http://web.archive.org/web/"

        if current_loaded_url.startswith(wayback_prefix) and self.display_url:
            pass
        else:
            self.display_url = current_loaded_url
            self.url_bar.setText(current_loaded_url)

    def update_status_loading(self):
        self.status_bar.showMessage("Loading...")

    def load_finished(self, ok):
        if ok:
            self.status_bar.showMessage("Done", 2000)
        else:
            self.status_bar.showMessage("Load Failed. Check URL and connectivity.", 5000)
        if ok:
            if not self.url_bar.text():
                 self.url_bar.setText(self.browser.url().toString())
            current_loaded_url = self.browser.url().toString()
            wayback_prefix = "http://web.archive.org/web/"
            if current_loaded_url.startswith(wayback_prefix):
                pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName('Wayback Browser')
    window = MainWindow()
    sys.exit(app.exec_())


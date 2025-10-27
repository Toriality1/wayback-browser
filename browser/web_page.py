from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl

class CustomWebPage(QWebEnginePage):
    def acceptNavigationRequest(self, url: QUrl, type, isMainFrame):
        if type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            print("Clicked URL:", url.toString())
            return False  # Block link clicks (or True to allow)
        return True


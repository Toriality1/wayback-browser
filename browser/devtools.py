from PyQt6.QtWidgets import QDockWidget, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import Qt

def create_devtools(main_window: QMainWindow):
    dev_view = QWebEngineView()
    dev_page = QWebEnginePage()
    dev_view.setPage(dev_page)

    dock = QDockWidget("Developer Tools", main_window)
    dock.setWidget(dev_view)
    dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
    main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
    main_window.resizeDocks([dock], [400], Qt.Orientation.Horizontal)
    dock.hide()

    return dock, dev_page

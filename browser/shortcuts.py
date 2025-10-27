from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt

def register_shortcuts(win):
    QShortcut(Qt.Key.Key_F5, win, win.view.reload)
    QShortcut(Qt.Key.Key_F11, win, win.toggle_fullscreen)
    QShortcut(QKeySequence("Ctrl+R"), win, win.view.reload)
    QShortcut(QKeySequence("Ctrl+L"), win, win.focus_url_bar)
    QShortcut(QKeySequence("Alt+Left"), win, win.view.back)
    QShortcut(QKeySequence("Alt+Right"), win, win.view.forward)
    QShortcut(QKeySequence("Alt+Home"), win, win.go_home)
    QShortcut(QKeySequence("Ctrl+Q"), win, win.close)
    QShortcut(QKeySequence("Ctrl+Shift+I"), win, win.toggle_devtools)


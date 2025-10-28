from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl, QRunnable, QThreadPool, pyqtSignal, QObject
from pathlib import Path
import json
import urllib.request

WAYBACK_DOMAIN = "web.archive.org"

class WaybackWorkerSignals(QObject):
    finished = pyqtSignal(str)  # emits the resolved Wayback URL


class WaybackWorker(QRunnable):
    def __init__(self, url, is_checking_existing=False):
        super().__init__()
        self.url = url
        self.is_checking_existing = is_checking_existing
        self.signals = WaybackWorkerSignals()


    def run(self):
        if self.is_checking_existing:
            print(f"[WaybackWorker] Checking if Wayback URL exists: {self.url}")
            exists = self.check_wayback_url_exists(self.url)
            print(f"[WaybackWorker] Wayback URL exists: {exists}")
            self.signals.finished.emit(self.url if exists else None)
        else:
            print(f"[WaybackWorker] Fetching Wayback URL for: {self.url}")
            resolved_url = self.get_wayback_url(self.url)
            print(f"[WaybackWorker] Resolved Wayback URL: {resolved_url}")
            self.signals.finished.emit(resolved_url)

    @staticmethod
    def check_wayback_url_exists(url):
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.getcode() == 200
        except Exception as e:
            print(f"[WaybackWorker] Error checking Wayback URL: {e}")
            return False


    @staticmethod
    def get_wayback_url(url):
        try:
            # Only try snapshot closest to Jan 1, 2009
            timestamp = "2009"
            api_url = f"https://archive.org/wayback/available?url={url}&timestamp={timestamp}"
            print(f"[WaybackWorker] Querying API: {api_url}")

            with urllib.request.urlopen(api_url, timeout=10) as response:
                data = json.loads(response.read().decode())
                snapshot = data.get("archived_snapshots", {}).get("closest")
                print(data)
                if snapshot:
                        return WaybackWorker._add_id_to_snapshot_url(snapshot["url"])
                else:
                    print(f"[WaybackWorker] No snapshot found for {url}")

        except Exception as e:
            print(f"[WaybackWorker] Error fetching Wayback URL: {e}")

        # Return None if no 2009 snapshot is found
        print(f"[WaybackWorker] No 2009 snapshot found for {url}")
        return None


    @staticmethod
    def _add_id_to_snapshot_url(url):
        import re
        match = re.search(r'/web/(\d{14})/', url)
        if match:
            timestamp = match.group(1)
            return url.replace(f'/web/{timestamp}/', f'/web/{timestamp}id_/')
        return url

class CustomWebPage(QWebEnginePage):
    wayback_ready = pyqtSignal() # emitted when snapshot is ready

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread_pool = QThreadPool()
        self.current_display_url = None
        self.loading_url = None  # Track the URL we're currently loading

    def acceptNavigationRequest(self, url: QUrl, type, isMainFrame):
        url_str = url.toString()
        print(f"[CustomWebPage] Navigation requested: {url_str} (type={type})")

        # Skip non-HTTP URLs
        if not url_str.startswith(("http://", "https://")):
            print(f"[CustomWebPage] Skipping non-HTTP URL: {url_str}")
            return super().acceptNavigationRequest(url, type, isMainFrame)

        # If we're already loading this URL, allow it to proceed
        if self.loading_url == url_str:
            print(f"[CustomWebPage] Already loading URL, allowing navigation: {url_str}")
            self.loading_url = None  # Reset after allowing navigation
            return super().acceptNavigationRequest(url, type, isMainFrame)

        if WAYBACK_DOMAIN in url.host():
            print(f"[CustomWebPage] URL is already a Wayback snapshot, checking if it exists")
            worker = WaybackWorker(url_str, is_checking_existing=True)
            worker.signals.finished.connect(
                lambda wayback_url: self._load_wayback_url(wayback_url, url_str)
            )
            self.thread_pool.start(worker)
            return False

        # Intercept link clicks or typed URLs
        if type in (QWebEnginePage.NavigationType.NavigationTypeLinkClicked,
                    QWebEnginePage.NavigationType.NavigationTypeTyped,
                    QWebEnginePage.NavigationType.NavigationTypeFormSubmitted):
            print(f"[CustomWebPage] Launching WaybackWorker for URL: {url_str}")

            worker = WaybackWorker(url_str)
            worker.signals.finished.connect(
                lambda wayback_url: self._load_wayback_url(wayback_url)
            )
            self.thread_pool.start(worker)

            # Cancel current navigation; the worker will handle it
            return False

        # Other navigation types proceed normally
        return super().acceptNavigationRequest(url, type, isMainFrame)

    def _load_wayback_url(self, wayback_url, display_url=None):
        if not wayback_url:
            # wayback_url is None → load local 404
            print("true")
            home_path = Path(__file__).resolve().parent / "resources" / "404.html"
            html = "<h1>404 - 2009 snapshot not found</h1>"  # fallback
            if home_path.exists():
                html = home_path.read_text(encoding="utf-8")
                print(f"[CustomWebPage] Loading local 404 page")
            self.current_display_url = "Page not found (2009 snapshot missing)"
            self.setHtml(html, QUrl.fromLocalFile(str(home_path)) if home_path.exists() else QUrl())
            self.wayback_ready.emit()
            return

        # Normal Wayback snapshot
        if display_url is None:
            display_url = wayback_url
        self.current_display_url = display_url
        self.loading_url = wayback_url  # Track the URL we're about to load
        print(f"[CustomWebPage] Loading Wayback URL: {wayback_url} (display as {display_url})")
        self.load(QUrl(wayback_url))
        self.wayback_ready.emit()

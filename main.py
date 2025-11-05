"""
PyBrowser   a tiny, beginner‑friendly web browser in one file.

What you get:
- A window with Back / Forward / Reload / Home buttons
- An address bar (press Enter or click Go)
- A status strip that shows DNS results (the IPs the hostname resolves to)

Requirements (pick ONE line depending on what you prefer):
    pip install PyQt6 PyQt6-WebEngine
  # or
    pip install PyQt5 PyQtWebEngine

Run it:
    python simple_browser.py

Notes for learners:
- We keep everything short and clear, with plain names and comments.
- If you only have PyQt5 installed, see the two import lines near the top
  switch the "PyQt6" imports to the PyQt5 ones (they're provided and commented).
"""

from __future__ import annotations

import sys
import socket
from urllib.parse import urlparse

# --- Choose ONE set of imports. PyQt6 by default (easier to install today). ---
# PyQt6 imports:
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

# If you prefer PyQt5 instead, comment the PyQt6 block above and uncomment below:
# from PyQt5.QtWidgets import (
#     QApplication, QWidget, QVBoxLayout, QHBoxLayout,
#     QLineEdit, QPushButton, QLabel
# )
# from PyQt5.QtWebEngineWidgets import QWebEngineView
# from PyQt5.QtCore import QUrl


def normalize_url(text: str) -> str:
    """Add http:// if the user forgot it.
    We also keep it very forgiving for beginners.
    """
    text = text.strip()
    if not text:
        return "http://example.com"  # safe default
    # If there is no scheme, assume http
    if "://" not in text:
        text = "http://" + text
    return text


def resolve_dns(hostname: str) -> list[str]:
    """Return a list of IP addresses for the hostname.
    We use the system resolver via socket.getaddrinfo.
    """
    try:
        infos = socket.getaddrinfo(hostname, None)
        ips = []
        for fam, stype, proto, canon, sockaddr in infos:
            ip = sockaddr[0]
            if ip not in ips:
                ips.append(ip)
        return ips
    except Exception:
        return []


class PyBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyBrowser")
        self.resize(1000, 700)

        # --- Top bar: nav buttons + address field + Go ---
        self.back_btn = QPushButton("Back")
        self.fwd_btn = QPushButton("Forward")
        self.reload_btn = QPushButton("Reload")
        self.home_btn = QPushButton("Home")
        self.address = QLineEdit()
        self.go_btn = QPushButton("Go")

        top = QHBoxLayout()
        top.addWidget(self.back_btn)
        top.addWidget(self.fwd_btn)
        top.addWidget(self.reload_btn)
        top.addWidget(self.home_btn)
        top.addWidget(self.address, 1)
        top.addWidget(self.go_btn)

        # --- Web view ---
        self.view = QWebEngineView()

        # --- Bottom strip: simple status with DNS output ---
        self.status = QLabel("Ready")

        # --- Main layout ---
        root = QVBoxLayout()
        root.addLayout(top)
        root.addWidget(self.view, 1)
        root.addWidget(self.status)
        self.setLayout(root)

        # --- Wire up actions ---
        self.back_btn.clicked.connect(self.view.back)
        self.fwd_btn.clicked.connect(self.view.forward)
        self.reload_btn.clicked.connect(self.view.reload)
        self.home_btn.clicked.connect(self.go_home)
        self.go_btn.clicked.connect(self.load_from_address)
        self.address.returnPressed.connect(self.load_from_address)

        # Update the address bar when navigation happens
        self.view.urlChanged.connect(self.on_url_changed)
        # Nice touch: show loading progress in the window title
        self.view.loadProgress.connect(self.on_load_progress)

        # Start on a friendly page
        self.address.setText("https://example.com")
        self.load_from_address()

    # --- Slots (handlers) ---
    def go_home(self):
        self.address.setText("https://example.com")
        self.load_from_address()

    def on_url_changed(self, qurl: QUrl):
        # Keep the address bar in sync with where we navigated to
        self.address.setText(qurl.toString())

    def on_load_progress(self, percent: int):
        self.setWindowTitle(f"PyBrowser   {percent}%")
        if percent == 100:
            self.setWindowTitle("PyBrowser")

    def load_from_address(self):
        """Called when the user presses Go or hits Enter in the address bar."""
        url_text = normalize_url(self.address.text())

        # Show DNS info for learning
        try:
            hostname = urlparse(url_text).hostname or ""
            ips = resolve_dns(hostname)
            if ips:
                self.status.setText(f"DNS: {hostname} → {', '.join(ips)}")
            else:
                self.status.setText(f"DNS: {hostname} → (no result)")
        except Exception as e:
            self.status.setText(f"DNS error: {e}")

        # Tell the web view to navigate
        self.view.load(QUrl(url_text))


def main():
    app = QApplication(sys.argv)
    w = PyBrowser()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

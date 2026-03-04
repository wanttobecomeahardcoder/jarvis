import sys
import os

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QUrl, Qt, QObject, Slot, Signal

from jarvis_core import JarvisCore


class Bridge(QObject):

    log_signal        = Signal(str, str)
    transcript_signal = Signal(str)
    status_signal     = Signal(bool)

    def __init__(self):
        super().__init__()
        self.core = JarvisCore(
            on_log        = lambda text, kind: self.log_signal.emit(text, kind),
            on_transcript = lambda text:       self.transcript_signal.emit(text),
            on_status     = lambda active:     self.status_signal.emit(active),
        )

    @Slot()
    def toggle_listen(self):
        self.core.toggle()

    @Slot(str)
    def run_command(self, text):
        self.core.run_command(text)


class JarvisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JARVIS")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        self.browser = QWebEngineView()

        self.channel = QWebChannel()
        self.bridge  = Bridge()
        self.channel.registerObject("bridge", self.bridge)
        self.browser.page().setWebChannel(self.channel)

        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jarvis.html")
        self.browser.setUrl(QUrl.fromLocalFile(html_path))
        self.setCentralWidget(self.browser)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_F11:
            self.showNormal() if self.isFullScreen() else self.showFullScreen()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = JarvisWindow()
    sys.exit(app.exec())

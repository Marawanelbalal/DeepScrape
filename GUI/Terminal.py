from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer, pyqtSlot
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtGui import QFont, QTextCursor
import sys


class CustomStream(QObject):
    text_written = pyqtSignal(str)

    def write(self, message):

        if isinstance(message, bytes):
            try:
                message = message.decode('utf-8')
            except UnicodeDecodeError:
                message = str(message)

        self.text_written.emit(message)

    def flush(self):
        pass


class Terminal(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.text_edit.setStyleSheet("""
                    QTextEdit {
                        background-color: #000000;
                        color: #FFFFFF;
                        border: 1px solid #333333;
                        border-radius: 4px;
                        padding: 5px;
                        selection-background-color: #555555;
                    }
                    QScrollBar:vertical {
                        background: #1a1a1a;
                        width: 12px;
                        margin: 0px;
                    }
                    QScrollBar::handle:vertical {
                        background: #444444;
                        min-height: 20px;
                        border-radius: 4px;
                    }
                    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                        background: none;
                    }
                """)
        self.text_edit.setFont(QFont("Menlo", 11))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.text_edit)

        self.stdout_stream = CustomStream()
        self.stderr_stream = CustomStream()

        self.stdout_stream.text_written.connect(self.handle_output, Qt.ConnectionType.QueuedConnection)
        self.stderr_stream.text_written.connect(self.handle_output, Qt.ConnectionType.QueuedConnection)

        QTimer.singleShot(0, self.redirect_stdout_to_terminal)

    def redirect_stdout_to_terminal(self):
        sys.stdout = self.stdout_stream
        sys.stderr = self.stderr_stream

    @pyqtSlot(str)
    def handle_output(self, text):

        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self.text_edit.setTextCursor(cursor)

        # Only scroll if we're at bottom
        scrollbar = self.text_edit.verticalScrollBar()
        if scrollbar.value() == scrollbar.maximum():
            scrollbar.setValue(scrollbar.maximum())

    def closeEvent(self, event):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        super().closeEvent(event)

    def write(self, text: str):
        pass

    def flush(self):
        pass
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sys
import time

# Worker thread to run your long task without blocking the UI
class Worker(QThread):
    finished = pyqtSignal()

    def run(self):
        # Simulate long-running task
        time.sleep(5)
        self.finished.emit()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.button = QPushButton("Analyze")
        self.button.clicked.connect(self.start_task)

        self.spinner_label = QLabel()
        self.spinner_label.setFixedSize(192, 192)
        self.spinner_label.setVisible(False)

        self.movie = QMovie(r"/resources/spinner.gif")
        self.spinner_label.setMovie(self.movie)

        layout = QHBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.spinner_label)
        layout.addStretch()
        self.setLayout(layout)

        self.worker = Worker()
        self.worker.finished.connect(self.task_finished)

    def start_task(self):
        self.spinner_label.setVisible(True)
        self.movie.start()
        self.button.setEnabled(False)  # Optional: disable button while running

        self.worker.start()

    def task_finished(self):
        self.movie.stop()
        self.spinner_label.setVisible(False)
        self.button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

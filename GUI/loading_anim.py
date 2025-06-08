from . import QFrame,QLabel,Qt,QMovie,QWidget,os
import resources_rc

class LoadingAnimation(QLabel):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setVisible(False)
        self.setFixedSize(192,192)  # Size of spinner resources
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setStyleSheet("""
            background: rgba(0, 0, 0, 150);
            border-radius: 15px;
        """)

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysStackOnTop)

    def adjustPosition(self):
        if self.parent():
            self.move(
                self.parent().width() // 2 - self.width() // 2,
                self.parent().height() // 2 - self.height() // 2
            )

    def initMovie(self):
        try:
            self.movie = QMovie(r":/images/resources/spinner.gif")
            if not self.movie.isValid():
                print("Error: Invalid GIF file")
            self.setMovie(self.movie)
        except Exception as e:
            print(f"Error loading spinner GIF: {e}")

    def showGIF(self):

        if self.movie and self.movie.isValid():
            self.adjustPosition()
            self.setVisible(True)
            self.movie.start()
            self.raise_()

    def hideGIF(self):
        self.setVisible(False)
        if self.movie:
            self.movie.stop()




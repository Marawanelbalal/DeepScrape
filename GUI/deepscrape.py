from . import QMainWindow,QApplication,QIcon,QPalette,QColor,Qt
from common_imports import sys
from .main_menu import MainMenu
from .intro import Intro
from .scraper_screen import ScraperScreen
import resources_rc

class DeepScrape:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setWindowIcon(QIcon(":/resources/DEEPSCRAPE_IMPROVED.ico"))
        self.app.setStyle("Fusion")

        palette = self.app.palette()
        #Give the application a dark purple palette
        palette.setColor(QPalette.ColorRole.Window, QColor("#1a1a2e"))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor("#2c2c3a"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#3a3a4a"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor("#3a3a4a"))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#7719d4"))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        self.app.setPalette(palette)
        self.intro = Intro()
        self.main_menu = MainMenu()
        self.intro.finished_signal.connect(lambda: (self.intro.close(), self.main_menu.showFullScreen()))
    def run(self):
        self.intro.show()
        sys.exit(self.app.exec())
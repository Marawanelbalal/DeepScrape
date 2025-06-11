from common_imports import time,json,os,pd,matplotlib
import threading
import io

from plotly.graph_objs import FigureWidget
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QScrollArea, QFrame,QGraphicsOpacityEffect,
                             QMainWindow,QRadioButton,QButtonGroup,QComboBox,QProgressBar,QMessageBox,
                             QFileDialog,QPlainTextEdit,QTextEdit,QSizePolicy,QGridLayout)

from PyQt6.QtGui import QIcon,QFont, QPixmap,QTextCursor,QPalette, QBrush, QColor, QLinearGradient,QMovie
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal, QParallelAnimationGroup,\
    QCoreApplication,QRect,QPoint,QObject,pyqtSlot,QFile


from PyQt6.QtWebEngineWidgets import QWebEngineView
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
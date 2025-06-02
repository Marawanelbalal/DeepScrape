import sys
import threading
import time
import matplotlib
import os
import json
import pandas as pd
from plotly.graph_objs import FigureWidget
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QScrollArea, QFrame,QGraphicsOpacityEffect,
                             QMainWindow,QRadioButton,QButtonGroup,QComboBox,QProgressBar,QMessageBox,
                             QFileDialog,QPlainTextEdit,QTextEdit)

from PyQt6.QtGui import QIcon,QFont, QPixmap, QPalette, QBrush, QColor, QLinearGradient,QMovie
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal, QParallelAnimationGroup,\
    QCoreApplication,QRect,QPoint,QObject

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
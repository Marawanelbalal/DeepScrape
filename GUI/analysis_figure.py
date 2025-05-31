from . import QMainWindow,FigureCanvas,NavigationToolbar,QWidget,QVBoxLayout

class AnalysisFigure(QMainWindow):
    def __init__(self,fig):
        super().__init__()
        self.setWindowTitle("Analysis Result")
        self.canvas = FigureCanvas(fig)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas, self)
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setCentralWidget(central_widget)
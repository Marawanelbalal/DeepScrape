from . import QMainWindow,FigureWidget,QWidget,QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
class PlotlyFigure(QMainWindow):
    def __init__(self,fig):
        super().__init__()
        self.setWindowTitle("Analysis Result")
        figure_html = fig.to_html(include_plotlyjs='cdn')
        webView =  QWebEngineView()
        webView.setHtml(figure_html)
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(webView)
        self.setCentralWidget(central_widget)

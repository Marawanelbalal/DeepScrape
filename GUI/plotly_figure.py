#Not used in the main app
#Attempted to use QWebEngineView for plotly so the application doesn't have to use a browser
#Doesn't work reliably

from . import QMainWindow,QWidget,QVBoxLayout
from . import QWebEngineView

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

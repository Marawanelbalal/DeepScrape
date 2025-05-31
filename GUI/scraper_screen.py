from . import (QWidget, pyqtSignal, QLinearGradient,
               QColor, QPalette, QBrush, QVBoxLayout,
               QHBoxLayout, QFrame, QLineEdit, QScrollArea, Qt,
               QLabel, QTimer, QPropertyAnimation, QParallelAnimationGroup,
               QRadioButton,QButtonGroup,QComboBox,QProgressBar,
               matplotlib, threading, intro, main_menu,QMovie)
import os

from .loading_anim import LoadingAnimation
from .modern_button import ModernButton
from .main_menu import MainMenu
from .product_card import ProductCard
from .analysis_figure import AnalysisFigure
from .plotly_figure import PlotlyFigure

from .styling_functions import style_radiobutton, style_label, style_line_edit, style_top_buttons, style_scroll_area, \
    style_frame
from .analysis_description_mappings import get_description

from ScrapingAnalysis.scraping_functions import seller_network, ebay_api

from ScrapingAnalysis.heatmaps import price_heatmap,feedback_percentage_heatmap
from ScrapingAnalysis.regional_heatmap import regional_price_heatmap

from ScrapingAnalysis.charts import price_range_pie_chart,price_range_chart,feedback_percentage_pie_chart

from ScrapingAnalysis.fbt_network import frequently_bought_together, bought_together_analysis

from ScrapingAnalysis.reviews import review_bar

from ScrapingAnalysis.analysis_3D import Analysis3D

from ScrapingAnalysis.category_analysis import community_analysis

class ScraperScreen(QWidget):
    progress_update = pyqtSignal(int)
    items_returned = pyqtSignal(dict)
    figure_drawn = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.is_fullscreen = True
        self.items = {}
        self.access_token = ""
        self.query = ""
        self.total_items = 0
        self._ui_index = 0
        self.items_returned.connect(self.update_ui)
        self.figure_drawn.connect(self.show_figure)
        self.fig = None
        self.token = ""
        self.search_clicked = False

    def initUI(self):
        self.setWindowTitle("DeepScrape - Scraper")
        self.showFullScreen()
        #make a dark background
        self.setAutoFillBackground(True)
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#1a1a2e"))
        gradient.setColorAt(1, QColor("#16213e"))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)

        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(0, 0, 0, 20)

        back_button = ModernButton("← Back")
        back_button.setStyleSheet("""
            ModernButton {
                background-color: transparent;
                color: #a0a0b0;
                font-size: 14px;
                padding: 5px 10px;
                text-align: left;
            }
            ModernButton:hover {
                color: white;
            }
        """)
        back_button.clicked.connect(self.go_back)

        #window buttons allow the user to minimize, maximize, hide or close the app
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)

        self.minimize_button = ModernButton("—")
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button = style_top_buttons(self.minimize_button)

        self.restore_button = ModernButton("□")
        self.restore_button.setFixedSize(30, 30)
        self.restore_button = style_top_buttons(self.restore_button)

        self.close_button = ModernButton("✕")
        self.close_button.setFixedSize(30, 30)
        self.close_button = style_top_buttons(self.close_button,
                                              "rgba(255, 60, 60, 0.3)",
                                            "rgba(255, 60, 60, 0.7)")

        self.minimize_button.clicked.connect(self.showMinimized)
        self.restore_button.clicked.connect(self.toggle_restore)
        self.close_button.clicked.connect(self.close)

        controls_layout.addWidget(self.minimize_button)
        controls_layout.addWidget(self.restore_button)
        controls_layout.addWidget(self.close_button)

        title_bar.addWidget(back_button)
        title_bar.addStretch()
        title_bar.addLayout(controls_layout)

        main_layout.addLayout(title_bar)

        #the content layout contains the main layout
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        #the left panel is where the user will enter their queries and item amounts
        left_panel = style_frame(QFrame())

        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)

        #make a layout for the search bar (query) and the request numbers.
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for products on eBay...")
        self.search_bar = style_line_edit(self.search_bar)


        self.search_button = ModernButton("Search")
        self.search_button.setStyleSheet("""
            ModernButton {
                background-color: #7719d4;
                color: white;
                border-radius: 8px;
                font-size: 14px;
                padding: 10px 20px;
                min-width: 100px;
            }
            ModernButton:hover {
                background-color: #8a2be2;
            }
        """)

        self.search_button.clicked.connect(self.perform_search)

        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_button)
        limits_layout = QHBoxLayout()
        limits_layout.setSpacing(10)
        self.items_per_request = QLineEdit()
        self.items_per_request.setPlaceholderText("Set items per request (50 Recommended)...")
        self.items_per_request = style_line_edit(self.items_per_request)

        self.max_items = QLineEdit()
        self.max_items.setPlaceholderText("Set a max number of items (<= 200 Recommended)...")
        self.max_items = style_line_edit(self.max_items)

        limits_layout.addWidget(self.items_per_request)
        limits_layout.addWidget(self.max_items)
        self.search_progress = QProgressBar()
        self.search_progress.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #7719d4;
                border-radius: 5px;
            }
        """)
        self.search_progress.setRange(0, 100)
        self.search_progress.setValue(0)
        self.search_progress.setTextVisible(False)
        self.progress_update.connect(self.search_progress.setValue)
        left_layout.addLayout(search_layout)
        left_layout.addLayout(limits_layout)

        #this scroll area will allow the user to view all the added product cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area = style_scroll_area(scroll_area)

        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.results_layout.setSpacing(10)
        self.results_layout.setContentsMargins(0, 0, 10, 0)  #right part of the scrollbar


        scroll_area.setWidget(self.results_container)
        left_layout.addWidget(scroll_area)
        left_layout.addWidget(self.search_progress)
        right_panel = QFrame()
        right_panel = style_frame(right_panel)
        right_panel.setFixedWidth(550)

        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(20)


        # Analysis options
        analysis_group = QFrame()
        analysis_group = style_frame(analysis_group,"rgba(255, 255, 255, 0.03)",15)

        analysis_layout = QVBoxLayout(analysis_group)
        analysis_layout.setContentsMargins(15, 15, 15, 15)
        analysis_layout.setSpacing(15)

        analysis_title = QLabel("Analysis Options")
        analysis_title = style_label(analysis_title)

        self.analysis_dropdown = QComboBox()
        self.analysis_dropdown.addItems([
            "Select an analysis type...",
            "Seller Influence Analysis",
            "Product Network Graph",
            "Heatmap Analysis",
            "Chart Analysis",
            "Review Sentiment Analysis",
            "3D Graph Analysis",
            "Chart Showing Communities (Related Categories)"
        ])
        self.analysis_dropdown.setStyleSheet("""
            QComboBox {
                color: #a0a0b0;
                font-size: 12px;
                background-color: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                padding: 6px;
            }
        """)
        self.heatmap_label = QLabel("Choose heatmap analysis metrics:")
        self.heatmap_label = style_label(self.heatmap_label)

        self.price_heatmap_check = QRadioButton("Heatmap Showing Price Differences")
        self.feedback_heatmap_check = QRadioButton("Heatmap Showing Feedback Score Differences")
        self.multiregional_check = QRadioButton("Multi regional Heatmap Showing Price Differences")
        self.heatmap_buttons = [
            self.price_heatmap_check,
            self.feedback_heatmap_check,
            self.multiregional_check
        ]
        self.heatmap_group = QButtonGroup(self)
        self.heatmap_group.setExclusive(True)
        self.heatmap_group.buttonClicked.connect(self.change_description)
        for i in range (len(self.heatmap_buttons)):
            self.heatmap_buttons[i] = style_radiobutton(self.heatmap_buttons[i])
            self.heatmap_group.addButton(self.heatmap_buttons[i])
            self.heatmap_buttons[i].setVisible(False)


        self.heatmap_choice_widgets = [self.heatmap_label] + self.heatmap_buttons
        self.heatmap_label.setVisible(False)


        self.chart_label = QLabel("Choose chart analysis metrics:")
        self.chart_label = style_label(self.chart_label)

        self.price_pie_chart_check = QRadioButton("Pie Chart Showing Price Differences")
        self.feedback_pie_chart_check = QRadioButton("Pie Chart Showing Feedback Score Differences")
        self.price_bar_check = QRadioButton("Bar Chart Showing Price Differences")
        self.chart_buttons = [
            self.price_pie_chart_check,
            self.feedback_pie_chart_check,
            self.price_bar_check
        ]
        self.chart_group = QButtonGroup(self)
        self.chart_group.setExclusive(True)
        self.chart_group.buttonClicked.connect(self.change_description)
        for i in  range(len(self.chart_buttons)):
            self.chart_buttons[i] = style_radiobutton(self.chart_buttons[i])
            self.chart_group.addButton(self.chart_buttons[i])
            self.chart_buttons[i].setVisible(False)
        self.chart_label.setVisible(False)
        self.chart_choice_widgets = [self.chart_label] + self.chart_buttons
        self.analysis_dropdown.currentIndexChanged.connect(self.update_radiobuttons)

        #For when the user chooses community analysis
        self.jaccard_bar = QLineEdit()
        self.jaccard_bar.setPlaceholderText("Add Jaccard Similarity Threshold (Optional)..")
        self.jaccard_bar = style_line_edit(self.jaccard_bar)
        self.jaccard_bar.setVisible(False)
        self.analysis_dropdown.currentIndexChanged.connect(self.toggle_jaccard_bar)


        self.loading = LoadingAnimation(self)
        self.loading.initMovie()
        self.loading.adjustPosition()


        #This description has a unique look, so it is better to not use the common function
        self.analysis_description = QLabel("Description: ")
        self.analysis_description.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: "Segoe UI Semibold", sans-serif;
                background-color: rgba(119, 25, 212, 0.15);;
                padding: 8px 12px;
                border-radius: 4px;
                border-left: 4px solid #7719d4;
            }
        """)
        self.analysis_description.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self.analysis_description.setWordWrap(True)

        description_scroll_area = QScrollArea()
        description_scroll_area.setWidgetResizable(True)
        description_scroll_area.setWidget(self.analysis_description)
        description_scroll_area.setFixedHeight(275)
        description_scroll_area.setFixedWidth(475)
        description_scroll_area.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        description_scroll_area = style_scroll_area(description_scroll_area)

        self.analysis_dropdown.currentIndexChanged.connect(self.change_description)
        #analysis layout which will contain the user's options for radiobuttons and the bar for jaccard similarity
        analysis_layout.addWidget(analysis_title)
        analysis_layout.addWidget(self.analysis_dropdown)
        analysis_layout.addWidget(self.jaccard_bar)
        for widget in self.heatmap_choice_widgets:
            analysis_layout.addWidget(widget)
        for widget in self.chart_choice_widgets:
            analysis_layout.addWidget(widget)
        analysis_layout.addWidget(description_scroll_area)

        self.analyze_button = ModernButton("ANALYZE SELECTED ITEMS")
        self.analyze_button.clicked.connect(self.on_analyze_clicked)
        self.analyze_button.setStyleSheet("""
            ModernButton {
                background-color: #7719d4;
                color: white;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
            }
            ModernButton:hover {
                background-color: #8a2be2;
            }
            ModernButton:disabled {
                background-color: rgba(119, 25, 212, 0.3);
                color: rgba(255, 255, 255, 0.5);
            }
        """)
        self.analyze_button.setEnabled(False)
        self.analysis_dropdown.currentIndexChanged.connect(self.toggle_analysis_button)
        right_layout.addWidget(analysis_group)
        right_layout.addStretch()


        right_layout.addWidget(self.analyze_button)

        content_layout.addWidget(left_panel,1)
        content_layout.addWidget(right_panel,5)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'loading'):
            self.loading.adjustPosition()
            # Extra insurance for mode changes
            QTimer.singleShot(100, lambda: self.loading.adjustPosition())

    def toggle_restore(self):
        if self.is_fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self.is_fullscreen = not self.is_fullscreen

    def go_back(self):
        if self.parent():
            self.hide()
            self.parent().show()
            #this works by hiding the scraper screen then showing the main menu
        else:
            self.main_menu = MainMenu()
            self.main_menu.show()
            self.hide()

    def clear_layout(self,layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def update_ui(self, items: dict):
        self.items = items
        item_pairs = list(self.items.items())
        total = len(item_pairs)
        self._ui_index = 0

        def add_chunk():
            self.search_button.setEnabled(True)
            self.search_progress.setValue(0)
            if self._ui_index >= total:
                return

            end = min(self._ui_index + 5, total)

            for idx in range(self._ui_index, end):
                Id, item = item_pairs[idx]
                card = ProductCard(
                    title=f"{idx + 1} – {item['Title']}",
                    price=f"Price: ${str(item['Price'])}",
                    ID=f"Item ID: {Id}",
                    seller=f"Seller: {item['Seller']}",
                    shipping_cost=f"Ship: ${str(item['Shipping Cost'])}"
                )
                self.results_layout.addWidget(card)

            self._ui_index = end
            if self._ui_index > 300:
                return
            else:
                QTimer.singleShot(50, add_chunk)

        self.clear_layout(self.results_layout)
        add_chunk()

    def perform_search(self):
        if self.max_items.text() == "0" or self.items_per_request.text() == "0":
            return
        self.search_clicked = True
        self.clear_layout(self.results_layout)
        self.search_button.setEnabled(False)

        self.query = self.search_bar.text()
        self.total_items = int(self.max_items.text())
        self.search_progress.setRange(0, self.total_items)
        self.search_progress.setValue(self.total_items//20)

        per_request = int(self.items_per_request.text())
        maximum = int(self.max_items.text())

        def worker():
            self.items,self.token = ebay_api(self.query, per_request, maximum,
                                             progress_callback = lambda value:self.progress_update.emit(value))
            self.items_returned.emit(self.items)
            self.toggle_analysis_button()

        threading.Thread(target=worker, daemon=True).start()

    def window_transition(self):
        main_menu.setWindowOpacity(0.0)
        main_menu.showFullScreen()

        fade_out = QPropertyAnimation(intro, b"windowOpacity")
        fade_out.setDuration(800)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)

        fade_in = QPropertyAnimation(main_menu, b"windowOpacity")
        fade_in.setDuration(800)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)

        group = QParallelAnimationGroup()
        group.addAnimation(fade_out)
        group.addAnimation(fade_in)

        group.finished.connect(intro.close)
        group.start()

    def on_analyze_clicked(self):

        text = self.analysis_dropdown.currentText()
        self.loading.showGIF()


        def worker():
            fig = None
            if text == "Seller Influence Analysis":
                fig = seller_network(self.items)

            elif text == "Product Network Graph":
                fig = bought_together_analysis(self.items, self.token)

            elif text == "Review Sentiment Analysis":
                fig = review_bar(self.items)

            elif text == "Heatmap Analysis":
                chosen = self.heatmap_group.checkedButton()
                heatmap_text = chosen.text()

                if heatmap_text == "Heatmap Showing Price Differences":
                    fig = price_heatmap(self.items)

                elif heatmap_text == "Heatmap Showing Feedback Score Differences":
                    fig = feedback_percentage_heatmap(self.items)

                elif heatmap_text == "Multi regional Heatmap Showing Price Differences":
                    fig = regional_price_heatmap(self.query,self.total_items)

            elif text == "Chart Analysis":
                chosen = self.chart_group.checkedButton()
                chart_text = chosen.text()
                if chart_text == "Pie Chart Showing Price Differences":
                    fig = price_range_pie_chart(self.items)

                elif chart_text == "Pie Chart Showing Feedback Score Differences":
                    fig = feedback_percentage_pie_chart(self.items)

                elif chart_text == "Bar Chart Showing Price Differences":
                    fig = price_range_chart(self.items)

            elif text == "3D Graph Analysis":
                fig = Analysis3D(self.items)

            elif text == "Chart Showing Communities (Related Categories)":
                threshold = 100
                if self.jaccard_bar.text():
                    try:
                        threshold = int(self.jaccard_bar.text())
                    except ValueError as e:
                        print(f'Failed to convert jaccard threshold: {e}')

                fig = community_analysis(self.items,threshold)
            self.loading.hideGIF()
            if fig is not None:
                self.figure_drawn.emit(fig)

        threading.Thread(target=worker, daemon=True).start()



    def show_figure(self,fig):
        if isinstance(fig,matplotlib.figure.Figure):
            self._analysis_win = AnalysisFigure(fig)
            self._analysis_win.showMaximized()

        else:
            fig.show()

        self.analyze_button.setEnabled(True)


    def toggle_jaccard_bar(self):
        text = self.analysis_dropdown.currentText()
        if text == "Chart Showing Communities (Related Categories)":
            self.jaccard_bar.setVisible(True)
        else:
            self.jaccard_bar.setVisible(False)
    def toggle_analysis_button(self):
        text = self.analysis_dropdown.currentText()
        if text == "Select an analysis type...":
            self.analyze_button.setEnabled(False)
        elif self.search_clicked:
            self.analyze_button.setEnabled(True)

    def change_description(self):
        text = self.analysis_dropdown.currentText()
        inner_text = ""

        if text == "Heatmap Analysis" and self.heatmap_group.checkedButton() is not None:
            chosen = self.heatmap_group.checkedButton()
            inner_text = chosen.text()

        elif text == "Chart Analysis" and self.chart_group.checkedButton() is not None:
            chosen = self.chart_group.checkedButton()
            inner_text = chosen.text()
        self.analysis_description.setText(get_description(text,inner_text))

    def update_radiobuttons(self):
        text = self.analysis_dropdown.currentText()

        for Hwidget,CHwidget in zip(self.heatmap_choice_widgets,self.chart_choice_widgets):
            Hwidget.setVisible(False)
            CHwidget.setVisible(False)

        if text == "Heatmap Analysis":
            for widget in self.heatmap_choice_widgets:
                widget.setVisible(True)

        elif text == "Chart Analysis":
            for widget in self.chart_choice_widgets:
                widget.setVisible(True)





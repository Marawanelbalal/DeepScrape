from . import (QWidget,QLinearGradient,QColor,
               QPalette,QBrush,QVBoxLayout,QHBoxLayout,
               QLabel,QFrame,QPixmap,Qt)

from .modern_button import ModernButton

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_fullscreen = True

    def initUI(self):
        self.setWindowTitle("DeepScrape")

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
        title_bar.setContentsMargins(20, 5, 20, 20)

        app_title = QLabel("DeepScrape")
        app_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
            }
        """)

        # Window controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)

        self.minimize_button = ModernButton("—")
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet("""
            ModernButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border-radius: 15px;
                font-size: 16px;
            }
            ModernButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)

        self.restore_button = ModernButton("□")
        self.restore_button.setFixedSize(30, 30)
        self.restore_button.setStyleSheet("""
            ModernButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border-radius: 15px;
                font-size: 16px;
            }
            ModernButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)

        self.close_button = ModernButton("✕")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("""
            ModernButton {
                background-color: rgba(255, 60, 60, 0.3);
                color: white;
                border-radius: 15px;
                font-size: 16px;
            }
            ModernButton:hover {
                background-color: rgba(255, 60, 60, 0.7);
            }
        """)

        self.minimize_button.clicked.connect(self.showMinimized)
        self.restore_button.clicked.connect(self.toggle_restore)
        self.close_button.clicked.connect(self.close)

        controls_layout.addWidget(self.minimize_button)
        controls_layout.addWidget(self.restore_button)
        controls_layout.addWidget(self.close_button)

        title_bar.addWidget(app_title)
        title_bar.addStretch()
        title_bar.addLayout(controls_layout)

        main_layout.addLayout(title_bar)

        # Main content
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)

        # make a layout for the left side which contains the app description
        left_side = QVBoxLayout()
        left_side.setSpacing(20)

        description = QLabel("""
            <h1 style="color: white; font-size: 42px; font-weight: bold;">Powerful eBay<br>Data Scraper</h1>
            <p style="color: #a0a0b0; font-size: 16px; line-height: 1.6;">
                DeepScrape extracts product data from eBay using multiple methods including API, 
                Selenium, and BeautifulSoup. Analyze product networks, pricing trends, and 
                market opportunities with our advanced tools.
            </p>
        """)
        description.setWordWrap(True)

        features = QLabel("""
            <ul style="color: #a0a0b0; font-size: 16px; line-height: 1.8;">
                <li>Multi-method data collection</li>
                <li>Advanced network analysis</li>
                <li>Price trend visualization</li>
                <li>Competitor analysis</li>
                <li>Custom reporting</li>
            </ul>
        """)

        left_side.addWidget(description)
        left_side.addWidget(features)
        left_side.addStretch()

        #the right part contains the start button
        right_side = QFrame()
        right_side.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        right_side.setFixedWidth(400)

        right_layout = QVBoxLayout(right_side)
        right_layout.setContentsMargins(40, 40, 40, 40)
        right_layout.setSpacing(30)

        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(":/icons/logo.png").scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                                                Qt.TransformationMode.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        start_button = ModernButton("START SCRAPING")
        start_button.setStyleSheet("""
            ModernButton {
                background-color: #7719d4;
                color: white;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }
            ModernButton:hover {
                background-color: #8a2be2;
            }
        """)
        start_button.clicked.connect(self.open_second_screen)

        version_label = QLabel("Version 1.1")
        version_label.setStyleSheet("color: rgba(255, 255, 255, 0.3); font-size: 12px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        right_layout.addWidget(icon_label)
        right_layout.addWidget(start_button)
        right_layout.addStretch()
        right_layout.addWidget(version_label)

        content_layout.addLayout(left_side)
        content_layout.addWidget(right_side)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def toggle_restore(self):
        if self.is_fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self.is_fullscreen = not self.is_fullscreen

    def open_second_screen(self):
        from .scraper_screen import ScraperScreen
        self.second_screen = ScraperScreen()
        self.second_screen.showFullScreen()
        self.hide()
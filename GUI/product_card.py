from . import QFrame,QHBoxLayout,QVBoxLayout,QLabel

class ProductCard(QFrame):


    def __init__(self, title="", price="",ID="",seller="",shipping_cost = "", parent=None):
        super().__init__(parent)


        self.setFixedHeight(240)
        self.setMinimumWidth(400)

        self.setObjectName("ProductCard")
        self.setStyleSheet("""
            #ProductCard {
                background-color: #2c2c3a;
                border-radius: 16px;
                border: 1px solid #3a3a4a;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)


        #product info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        self.title_label.setWordWrap(True)
        self.price_label = QLabel(price)
        self.price_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        self.ID_label = QLabel(ID)
        self.ID_label.setStyleSheet("""
                 QLabel {
                     color: #FFD700;
                     font-size: 14px;
                     font-weight: bold;
                 }
             """)

        self.seller_label = QLabel(seller)
        self.seller_label.setStyleSheet("""
                         QLabel {
                             color: #1E90FF;
                             font-size: 14px;
                             font-weight: bold;
                         }
                     """)

        self.shipping_label = QLabel(shipping_cost)
        self.shipping_label.setStyleSheet("""
                                 QLabel {
                                     color: #4CAF50;
                                     font-size: 14px;
                                     font-weight: bold;
                                 }
                             """)

        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.ID_label)
        info_layout.addWidget(self.price_label)
        info_layout.addWidget(self.seller_label)
        info_layout.addWidget(self.shipping_label)

        info_layout.addStretch()

        #add info widgets to the layout
        layout.addLayout(info_layout, 3)

        #push the info to the left via stretching it
        layout.addStretch(1)
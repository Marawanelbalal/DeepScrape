from . import (QFrame, QLineEdit, QScrollArea,QLabel,QRadioButton,Qt)
from .modern_button import ModernButton

def style_radiobutton(button: QRadioButton):
    button.setStyleSheet("""
                            QRadioButton {
                                color: #a0a0b0;
                                font-size: 12px;
                                spacing: 8px;
                            }
                            QRadioButton::indicator {
                                width: 16px;
                                height: 16px;
                                border: 2px solid #5a5a7a;
                                border-radius: 5px;
                            }
                            QRadioButton::indicator:checked {
                                background-color: #7719d4;
                                border: 2px solid #7719d4;
                            }
                        """)

def style_label(label: QLabel):
    label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
                    """)

def style_scroll_area(scroll_area: QScrollArea,background_color):
    #rgba(255, 255, 255, 0.05)
    scroll_area.setStyleSheet(f"""
    
                QScrollArea {{
                    border: none;
                }}
                QScrollBar:vertical {{
                    border: none;
                    background: {background_color};
                    width: 10px;
                    margin: 0px;
                }}
                QScrollBar::handle:vertical {{
                    background: rgba(255, 255, 255, 0.2);
                    min-height: 20px;
                    border-radius: 5px;
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
            """)

def style_line_edit(line_edit:QLineEdit):
    line_edit.setStyleSheet("""
                        QLineEdit {
                            background-color: rgba(255, 255, 255, 0.1);
                            border: 1px solid rgba(255, 255, 255, 0.2);
                            border-radius: 8px;
                            padding: 10px 15px;
                            color: white;
                            font-size: 14px;
                        }
                        QLineEdit:focus {
                            border: 1px solid #7719d4;
                        }
                    """)


def style_top_buttons(top_button:ModernButton,bg_color:str = "rgba(255, 255, 255, 0.1)",hover_bg_color:str = "rgba(255, 255, 255, 0.2)"):
    top_button.setStyleSheet(f"""
            ModernButton {{
                background-color: {bg_color};
                color: white;
                border-radius: 15px;
                font-size: 16px;
            }}
            ModernButton:hover {{
                background-color: {hover_bg_color};
            }}
        """)

def style_frame(frame:QFrame,bg_color:str = "background-color: rgba(255, 255, 255, 0.05)",border_radius:int = 15):
    frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: {border_radius}px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)

def style_modern_button(modern_button:ModernButton):
    modern_button.setStyleSheet("""
            ModernButton {
                background-color: #7719d4;
                color: white;
                border-radius: 8px;
                font-size: 14px;
                padding: 4px 12px;
                min-width: 100px;
                min-height: 30px;
            }
            ModernButton:hover {
                background-color: #8a2be2;
            }
        """)

def label_with_background(labelBackgroundColor,scrollAreaBackgroundColor,height=275,width=500):
    label = QLabel("Description: ")
    label.setStyleSheet(f"""
                QLabel {{
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    font-family: "Segoe UI Semibold", sans-serif;
                    background-color: {labelBackgroundColor};;
                    padding: 8px 12px;
                    border-radius: 4px;
                    border-left: 4px solid #7719d4;
                }}
            """)
    label.setAlignment(
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
    )
    label.setWordWrap(True)

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(label)
    scroll_area.setFixedWidth(width)
    scroll_area.setMinimumHeight(height)
    scroll_area.setAlignment(
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
    )
    style_scroll_area(scroll_area,scrollAreaBackgroundColor)
    return label,scroll_area
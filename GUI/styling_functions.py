from . import (QWidget, pyqtSignal, QLinearGradient,
               QColor, QPalette, QBrush, QVBoxLayout,
               QHBoxLayout, QFrame, QLineEdit, QScrollArea, Qt,
               QLabel, QTimer, QPropertyAnimation, QParallelAnimationGroup,
               QRadioButton,QButtonGroup,QComboBox)
from .modern_button import ModernButton

def style_radiobutton(button: QRadioButton)->QRadioButton:
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
    return button

def style_label(label: QLabel)->QLabel:
    label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }
                    """)
    return label

def style_scroll_area(scroll_area: QScrollArea)->QScrollArea:
    scroll_area.setStyleSheet("""
                QScrollArea {
                    border: none;
                }
                QScrollBar:vertical {
                    border: none;
                    background: rgba(255, 255, 255, 0.05);
                    width: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: rgba(255, 255, 255, 0.2);
                    min-height: 20px;
                    border-radius: 5px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)
    return scroll_area

def style_line_edit(line_edit:QLineEdit)->QLineEdit:
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
    return line_edit

def style_top_buttons(top_button:ModernButton,bg_color:str = "rgba(255, 255, 255, 0.1)",hover_bg_color:str = "rgba(255, 255, 255, 0.2)")->ModernButton:
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
    return top_button

def style_frame(frame:QFrame,bg_color:str = "background-color: rgba(255, 255, 255, 0.05)",border_radius:int = 15)->QFrame:
    frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: {border_radius}px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
        """)
    return frame
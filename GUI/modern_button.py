from . import QPushButton,Qt,QPropertyAnimation,QEasingCurve

class ModernButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    #
    # def enterEvent(self, event):
    #     self._animation.stop()
    #     self._animation.setEndValue(self.geometry().adjusted(-2, -2, 2, 2))
    #     self._animation.start()
    #     super().enterEvent(event)
    #
    # def leaveEvent(self, event):
    #     self._animation.stop()
    #     self._animation.setEndValue(self.geometry().adjusted(2, 2, -2, -2))
    #     self._animation.start()
    #     super().leaveEvent(event)
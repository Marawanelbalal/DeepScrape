from . import (QWidget,pyqtSignal,time,QLabel,QTimer,QGraphicsOpacityEffect,
               QParallelAnimationGroup,QPropertyAnimation,QEasingCurve,QFont,Qt)

class Intro(QWidget):
    finished_signal = pyqtSignal()
    def __init__(self):
        super().__init__()

        self.start_time = time.time()

        #Set the title as the app title
        self.setWindowTitle('DeepScrape')

        #Black background
        self.setStyleSheet("background-color: black;")

        #Fullscreen
        self.showFullScreen()

        self.labels = []
        self.animations = []
        self.timers = []

        self.skipped = False
        #Keep the GUI logic in a seperate function than the constructor

        self.skip_instruction = QLabel("Press ENTER To Skip",self)
        self.skip(-0.35,0.4)
        self.intro()

    #the self-made schedule function allows the display to make animations show up in the future
    def schedule(self, delay, function):
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(function)
        timer.start(delay)
        self.timers.append(timer)  #store the scheduled timers


    def fade_out_instruction(self):
        self.skip_effect = QGraphicsOpacityEffect(self.skip_instruction)
        self.skip_instruction.setGraphicsEffect(self.skip_effect)

        self.skip_anim = QPropertyAnimation(self.skip_effect, b"opacity")
        self.skip_anim.setDuration(2000)
        self.skip_anim.setStartValue(1)
        self.skip_anim.setEndValue(0)
        self.skip_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.skip_anim.start()
        self.skip_anim.finished.connect(self.skip_instruction.close)

   #Intro functions in sequence:
    def intro(self):

        self.schedule(1500, lambda: self.fade_text(0,0,25,"Make sure to have an internet connection when\nusing this app.",True))

        self.schedule(6500,lambda: self.fade_text(0,0,25,"Made by:\n\nMarawan Abdulrahim\n\nNezar Mohamed",True))

        self.schedule(11500,lambda: self.fade_text(0,0,25,"Powered by eBay API:\n\nA Zewail City project",True))

        self.schedule(16500,lambda: self.fade_text(0,-0.35,50,"DeepScrape",True,"Titillium Web"))
        self.schedule(19500, lambda: self.fade_out_instruction())
        self.schedule(21500,lambda:self.finished_signal.emit())

    #Made a function which takes text and fades it in and out of the screen.
    def fade_text(self,xp,yp,font_size,text,fout,font = "Times New Roman"):


        label = QLabel(text, self)
        label.setFont(QFont(font,font_size))
        label.setStyleSheet("color: white;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scaled_x = int(self.width() * xp)
        scaled_y = int(self.height() * yp)
        label.setGeometry(scaled_x,scaled_y,self.width(),self.height())

        #Create an opacity effect for the label
        self.fade = QGraphicsOpacityEffect(label)
        label.setGraphicsEffect(self.fade)

        #Create the animation
        self.fade_anim = QPropertyAnimation(self.fade, b"opacity")
        #Make the animation last 2 seconds
        self.fade_anim.setDuration(3000)
        self.fade_anim.setStartValue(0) #Starts completely invisible
        self.fade_anim.setEndValue(1) #Ends as fully visible
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad) #Make the text smooth

        self.fade_out = QGraphicsOpacityEffect(label)

        self.fade_out_anim = QPropertyAnimation(self.fade_out, b"opacity")
        self.fade_out_anim.setDuration(2000)
        self.fade_out_anim.setStartValue(1)
        self.fade_out_anim.setEndValue(0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        #Using both animations at the same time:
        self.final_anim = QParallelAnimationGroup()
        self.final_anim.addAnimation(self.fade_anim)
        #Wait 3 seconds before starting the animation:
        QTimer.singleShot(0, lambda: label.show())
        QTimer.singleShot(0, lambda: self.final_anim.start())
        self.labels.append(label)
        self.animations.append((self.final_anim,self.fade_out_anim))
        if fout:
            QTimer.singleShot(3000, lambda: label.setGraphicsEffect(self.fade_out))
            QTimer.singleShot(3000, lambda: self.fade_out_anim.start())
            QTimer.singleShot(5000, lambda: label.close())


    def get_runtime(self):
        return time.time() - self.start_time

    def skip(self,xp,yp):
        self.skip_instruction.setFont(QFont("Times New Roman", 25))
        self.skip_instruction.setStyleSheet("color: white;")
        self.skip_instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center text
        scaled_x = int(self.width() * xp)
        scaled_y = int(self.height() * yp)
        self.skip_instruction.setGeometry(scaled_x, scaled_y, self.width(), self.height())  # Full screen width
        self.skip_instruction.show()

    def skip_intro(self):

        for timer in self.timers:
            timer.stop()

        for label in self.labels:
            label.close()

        #immediately show the final part of the intro if the user skips
        self.fade_text(0, -0.35, 50, "DeepScrape", True, "Titillium Web")

        #set background to final color and fade out the skip instruction
        QTimer.singleShot(3000,lambda:self.fade_out_instruction())
        QTimer.singleShot(5000,lambda:self.finished_signal.emit())


    def keyPressEvent(self, event):
        if not self.skipped:
            if event.key() == Qt.Key.Key_Return and int(self.get_runtime()) <= 16:
                self.skipped = True  # Set flag first
                #The flag allows the intro to keep track of whether the user previously skipped or not to avoid weird errors
                self.skip_intro()


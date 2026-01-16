# This file is used for experimental ui features
# I dont know anything about graphical interfaces when it comes to programming so if there are any issues let me know
import sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QLabel,
    QComboBox
)
from PyQt6.QtGui import QColor, QPalette
import SimplyPluraltoVRC

class avatar_widget(QWidget):
    def __init__(self,color):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

class chatbox_preview(QWidget):
    def __init__(self,color):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

class options_widget(QWidget):
    def __init__(self,color):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)
    
class start_options(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        
        self.startBtn = QPushButton("Start",self)
        self.startBtn.clicked.connect(self.start_button)
        self.reloadBtn = QPushButton("Reload Settings",self)
        self.reloadBtn.clicked.connect(self.reload_button)

        layout = QVBoxLayout()

        layouttop = QHBoxLayout()
        layouttop.addWidget(self.startBtn)
        layouttop.addWidget(self.reloadBtn)

        self.traceback = QLabel("")

        layout.addLayout(layouttop)
        layout.addWidget(self.traceback)
        self.setLayout(layout)
    
    def start_button(self):
        if self.startBtn.text() == "Start":
            self.startBtn.setText("Stop")
        elif self.startBtn.text() == "Stop":
            self.startBtn.setText("Start")

    def reload_button(self):
        try:
            SimplyPluraltoVRC.read_options_from_ui.get_options()
        except:
            self.traceback.setText("Unable to read options file.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SimplyPlural2VRC")
        self.setMinimumSize(QSize(400,300))
        self.setBaseSize(QSize(800,600))

        def draw_layout():
            layoutLeft = QVBoxLayout() #Set boxes to Stack vertically
            layoutRight = QVBoxLayout()
            layout = QHBoxLayout()

            layoutLeft.addWidget(avatar_widget("red")) #Add a VBox widget
            layoutLeft.addWidget(options_widget("blue"))
            layoutLeft.addWidget(start_options())

            layoutRight.addWidget(chatbox_preview("green"))

            layout.addLayout(layoutLeft)
            layout.addLayout(layoutRight)

            widget = QWidget()
            widget.setLayout(layout)
            self.setCentralWidget(widget)
        
        draw_layout()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
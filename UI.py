# This file is used for experimental ui features
# I dont know anything about graphical interfaces when it comes to programming so if there are any issues let me know
import sys, json, SimplyPluraltoVRC, asyncio
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
    QComboBox,
    QTextEdit,
    QLineEdit,
    QTextBrowser
)
from PyQt6.QtGui import QColor, QPalette

class login_widget(QWidget):
    def __init__(self):
        super().__init__()

        settings = load_settings(0)

        layout = QVBoxLayout()

        self.token = QLineEdit()
        self.token.setText(settings["sp_token"])
        self.user = QLineEdit()
        self.user.setText(settings["vrc_info"]["vrc_user"])
        self.passw = QLineEdit()
        self.passw.setText(settings["vrc_info"]["vrc_pass"])
        self.userid = QLineEdit()
        self.userid.setText(settings["vrc_info"]["vrc_userid"])

        layout.addWidget(self.token)
        layout.addWidget(self.user)
        layout.addWidget(self.passw)
        layout.addWidget(self.userid)
        self.setLayout(layout)
    

class member_widget(QWidget):
    def __init__(self):
        super().__init__()
        
        settings = load_settings(0)

        self.layoutall = QVBoxLayout()

        buttons = QHBoxLayout()
        self.add_box = QPushButton(self,text="+")
        self.delete_box = QPushButton(self,text="-")

        buttons.addWidget(self.add_box)
        buttons.addWidget(self.delete_box)

        self.layoutall.addLayout(buttons)

        self.add_box.clicked.connect(self.add_button)
        self.delete_box.clicked.connect(self.delete_button)

        avatar_dict = settings["avatars"]
        self.avatars = []
        for i in avatar_dict:
            layout_temp = QHBoxLayout()

            name_temp = QLineEdit()
            name_temp.setText(i)
            id_temp = QLineEdit()
            id_temp.setText(avatar_dict[i])

            layout_temp.addWidget(name_temp)
            layout_temp.addWidget(id_temp)
            self.avatars.append(layout_temp)

        for i in self.avatars:
            self.layoutall.addLayout(i)

        self.setLayout(self.layoutall)
    
    def delete_button(self):
        item = self.layoutall.itemAt(self.layoutall.count()-1)
        self.boxdelete(item)

    def add_button(self):
        layout_temp = QHBoxLayout()

        name_temp = QLineEdit()
        name_temp.setText("Name")
        id_temp = QLineEdit()
        id_temp.setText("Avatar ID")

        layout_temp.addWidget(name_temp)
        layout_temp.addWidget(id_temp)

        self.layoutall.addLayout(layout_temp)

    def boxdelete(self, box):
        for i in range(self.layoutall.count()):
            layout_item = self.layoutall.itemAt(i)
            if layout_item.layout() == box:
                deleteItemsOfLayout(layout_item.layout())
                self.layoutall.removeItem(layout_item)
                break

class chatbox_preview(QWidget):
    def __init__(self):
        super().__init__()
        
        settings = load_settings(0)

        layout = QVBoxLayout()

        self.preview = QTextBrowser()

        try:
            self.preview.setPlainText(SimplyPluraltoVRC.chatbox)
        except:
            self.preview.setPlainText("App is not online.")

        layout.addWidget(self.preview)
        self.setLayout(layout)

class options_widget(QWidget):
    def __init__(self):
        super().__init__()

        settings = load_settings(0)

        layout = QVBoxLayout()

        self.visibleOnStart = QCheckBox(text="Chatbox Visible by Default")
        self.attemptReconnect = QCheckBox(text="Attempt Reconnect")
        self.generic = QTextEdit()
        self.time_digital = QTextEdit()
        self.time_full = QTextEdit()
        self.afk = QTextEdit()
        self.status = QTextEdit()

        try:
            self.visibleOnStart.setCheckState(Qt.CheckState(getCheckboxState(settings["visible_on_load"])))
            self.attemptReconnect.setCheckState(Qt.CheckState(getCheckboxState(settings["attempt_reconnect"])))
            self.generic.setPlainText(settings["chatbox"]["generic"])
            self.time_digital.setPlainText(settings["chatbox"]["time_digital"])
            self.time_full.setPlainText(settings["chatbox"]["time_full"])
            self.afk.setPlainText(settings["chatbox"]["afk"])
            self.status.setPlainText(settings["chatbox"]["status"])
        except:
            print("Unable to read settings.json")

        layout.addWidget(self.generic)
        layout.addWidget(self.time_digital)
        layout.addWidget(self.time_full)
        layout.addWidget(self.afk)
        layout.addWidget(self.status)
        layout.addWidget(self.visibleOnStart)
        layout.addWidget(self.attemptReconnect)
        self.setLayout(layout)

class start_options(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        
        self.startBtn = QPushButton("Start",self)
        self.startBtn.setCheckable(True)
        self.startBtn.clicked.connect(self.start_button)
        self.reloadBtn = QPushButton("Import Settings",self)
        self.reloadBtn.clicked.connect(self.reload_button)
        self.saveBtn = QPushButton("Save Settings",self)
        self.saveBtn.clicked.connect(self.save_button)

        layout = QVBoxLayout()

        layouttop = QHBoxLayout()
        layouttop.addWidget(self.startBtn)
        layouttop.addWidget(self.reloadBtn)
        layouttop.addWidget(self.saveBtn)

        self.traceback = QLabel("")

        layout.addLayout(layouttop)
        layout.addWidget(self.traceback)
        self.setLayout(layout)
    
    def start_button(self):
        if self.startBtn.isChecked():
            self.startBtn.setText("Stop")
            run()
        else:
            self.startBtn.setText("Start")
            SimplyPluraltoVRC.taskcancelled = True

    def reload_button(self):
        try:
            setting, tracebackText = load_settings(2)
            self.traceback.setText(tracebackText)
            options_widget.update
        except Exception as e:
            self.traceback.setText("Unable to read or generate settings.json")
            print(e)
    
    def save_button(self):
        try:
            print(options_widget)
        except:
            self.traceback.setText("Unable to save to settings.json")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SimplyPlural2VRC")
        self.setMinimumSize(QSize(400,300))
        self.setBaseSize(QSize(800,600))

        def draw_layout():
            column1 = QVBoxLayout() #Set boxes to Stack vertically
            column2 = QVBoxLayout()
            column3 = QVBoxLayout()
            layout = QHBoxLayout()

            column1.addWidget(login_widget())
            column1.addWidget(options_widget())
            column1.addWidget(start_options())

            column2.addWidget(chatbox_preview())

            column3.addWidget(member_widget())

            layout.addLayout(column1)
            layout.addLayout(column2)
            layout.addLayout(column3)

            widget = QWidget()
            widget.setLayout(layout)
            self.setCentralWidget(widget)
        
        draw_layout()

def getCheckboxState(state):
    if state == True:
        return 2
    else:
        return 0
    
def load_settings(x=0):
    tb, s = SimplyPluraltoVRC.read_options_from_ui.get_options()
    if x == 0:
        return s
    elif x == 1:
        return tb
    else:
        return s, tb

def deleteItemsOfLayout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                deleteItemsOfLayout(item.layout())

def run():
    SimplyPluraltoVRC.taskcancelled = False
    SimplyPluraltoVRC.run()

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
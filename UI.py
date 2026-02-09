# This file is used for experimental ui features
# I dont know anything about graphical interfaces when it comes to programming so if there are any issues let me know
import sys, json, SP2VRC_Lib, asyncio, http.client, queue, time, traceback
from PyQt6.QtCore import (
    QSize,
    Qt,
    QRunnable,
    QThreadPool,
    QTimer,
    QObject,
    pyqtSlot,
    pyqtSignal
)
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
    QTextBrowser,
    QGridLayout,
    QInputDialog,
)
from PyQt6.QtGui import QColor, QPalette

class Program():
    def __init__(self):
        super().__init__()

    def sp2vrc_start(self,chatbox_preview,logger):
        SP2VRC_Lib.taskcancelled = False
        save_data()
        loop = asyncio.new_event_loop()
        loop.run_until_complete(SP2VRC_Lib.auth(load_settings(0),chatbox_preview,logger))

    def chatbox_fn(self, data):
        chatbox_preview.preview.setPlainText(data)
    
    def logging_fn(self, data):
        if "Ping-" in data:
            data = data.replace("Ping-ponged:","")
            MainWindow.ping.setText(str("Ping |"+data))
        else:
            log_prev = str(output_log.log.toPlainText()+"\n"+data)
            output_log.log.setPlainText(log_prev)

class WorkerSignals(QObject):
    finished = pyqtSignal(int)
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    chatbox = pyqtSignal(str)
    logger = pyqtSignal(str)

class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.thread_id = kwargs.get("thread_id", 0)
        self.kwargs["chatbox_preview"] = self.signals.chatbox
        self.kwargs["logger"] = self.signals.logger

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args,**self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit(self.thread_id)

class keybinds_widget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        keybinds_widget.keybinds = {
            "Close Programme":QLineEdit(),
            "Toggle Time":QLineEdit(),
            "Time Format":QLineEdit(),
            "Toggle Chatbox":QLineEdit(),
            "Show AFK":QLineEdit(),
            "Force Update":QLineEdit()
        }
        
        for i in keybinds_widget.keybinds:
            temp_layout = QHBoxLayout()
            temp_layout.addWidget(QLabel(text=i))
            temp_layout.addWidget(keybinds_widget.keybinds[i])
            layout.addLayout(temp_layout)
        
        self.setLayout(layout)


class login_widget(QWidget):
    def __init__(self):
        super().__init__()
        login_widget.tb = ""
        layout = QVBoxLayout()
        login_widget.token = QLineEdit()
        self.token.setEchoMode(QLineEdit.EchoMode.Password)
        login_widget.status = QCheckBox(text="Enable Status Updating")
        
        login_widget.userid = QLineEdit()
        login_widget.user = QLineEdit()
        login_widget.passw = QLineEdit()
        self.passw.setEchoMode(QLineEdit.EchoMode.Password)
        login_widget.loginBtn = QPushButton(text="Log in")
        self.loginBtn.setEnabled(False)
        self.loginBtn.pressed.connect(self.login)

        self.passw.textChanged.connect(self.login_button_active)
        self.user.textChanged.connect(self.login_button_active)
        self.token.textChanged.connect(self.start_button_active)
        self.status.checkStateChanged.connect(self.status_active)

        login_widget.widgets = [self.token,self.user,self.passw,self.userid,self.status]

        layout.addWidget(QLabel(text="Simply Plural Read Token"))
        layout.addWidget(self.token)
        layout.addWidget(self.status)
        layout.addWidget(QLabel(text="VRChat UserID"))
        layout.addWidget(self.userid)
        layout.addWidget(QLabel(text="VRChat Username or Email"))
        layout.addWidget(self.user)
        layout.addWidget(QLabel(text="VRChat Password"))
        layout.addWidget(self.passw)
        layout.addWidget(self.loginBtn)
        self.status_active()
        self.setLayout(layout)
    
    def status_active(self):
        if self.status.isChecked():
            self.user.setEnabled(True)
            self.passw.setEnabled(True)
            self.userid.setEnabled(True)
            self.login_button_active()
        else:
            self.user.setEnabled(False)
            self.passw.setEnabled(False)
            self.userid.setEnabled(False)
            self.loginBtn.setEnabled(False)

    def start_button_active(self):
        if len(self.token.text()) < 64:
            start_options.startBtn.setEnabled(False)
        else:
            start_options.startBtn.setEnabled(True)

    def login_button_active(self):
        if len(self.user.text()) == 0 or len(self.passw.text()) == 0:
            self.loginBtn.setEnabled(False)
        else:
            self.loginBtn.setEnabled(True)
    
    def authorise(self,authcode):
        try:
            if "Email" in SP2VRC_Lib.vrc_login.status:
                user = SP2VRC_Lib.vrc_login.two_fa(0,authcode)
            elif "Two-Factor" in SP2VRC_Lib.vrc_login.status:
                user = SP2VRC_Lib.vrc_login.two_fa(1,authcode)
            return user
        
        except:
            return None
    
    def login(self):
        username = self.user.text()
        password = self.passw.text()
        login_widget.user = SP2VRC_Lib.vrc_login.getauthfromfile(username,password)

        if "requested" in str(login_widget.user):
            start_options.traceback.setText(login_widget.user)
            login_widget.user = self.auth_box()

        elif "Unable" in str(login_widget.user):
            start_options.traceback.setText(login_widget.user)
            return
        
        if login_widget.user != None:
            start_options.traceback.setText("Logged in as "+login_widget.user.display_name)
        else:
            start_options.traceback.setText("Unable to log in")

    def auth_box(self):
        dialogue = QInputDialog()
        dialogue.setLabelText("Enter authentication code")
        dialogue.setWindowTitle("Authentication")

        clickedButton = dialogue.exec()

        user = None
        if clickedButton and len(dialogue.textValue()) > 0:
            user = self.authorise(dialogue.textValue())
        elif clickedButton and len(dialogue.textValue()) == 0:
            start_options.traceback.setText("Unable to log in, no authcode inputted")
        else:
            start_options.traceback.setText("Unable to log in, cancelled by user")
        
        return user


class member_widget(QWidget):
    def __init__(self):
        super().__init__()

        member_widget.layoutall = QVBoxLayout()
        member_widget.columns = QHBoxLayout()
        self.columns.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layoutall.setAlignment(Qt.AlignmentFlag.AlignCenter)

        member_widget.gatherBtn = QPushButton("Get Members",self)
        self.gatherBtn.clicked.connect(self.gather_button)

        self.layoutall.addWidget(self.gatherBtn)
        self.layoutall.addLayout(self.columns)
        self.setLayout(self.layoutall)

    def gather_button(self):
        settings = load_settings(0)
        tb, memberdict = gather_members(login_widget.widgets[0].text())
        if "Unable" not in tb:
            self.list_members(settings,memberdict)
        else:
            start_options.traceback.setText(tb)

    def list_members(self,settings,memberdict):

        columns = self.columns
        for i in columns.children():
            columns.removeItem(i)

        for i in memberdict:
            if i in settings["memberdict"]:
                if memberdict[i][1] != settings["memberdict"][i]["pronouns"]:
                    settings["memberdict"][i]["pronouns"] = memberdict[i][1]
            else:
                settings["memberdict"][i] = {
                    "name":memberdict[i][0],
                    "avatar":"",
                    "pronouns":memberdict[i][1]
                    }
        
        id = QVBoxLayout()
        name = QVBoxLayout()
        avatar = QVBoxLayout()

        for i in id.children():
            id.removeItem(i)
        for i in name.children():
            name.removeItem(i)
        for i in avatar.children():
            avatar.removeItem(i)
        
        id.setSpacing(0)
        id_label = QLabel(text="ID")
        id.addWidget(id_label)
        
        name.setSpacing(0)
        name_label = QLabel(text="Name")
        name.addWidget(name_label)
        
        avatar.setSpacing(0)
        avatar_label = QLabel(text="Avatar ID")
        avatar.addWidget(avatar_label)
        member_widget.id_boxes = []
        member_widget.name_boxes = []
        member_widget.avatar_boxes = []
        member_widget.memberdict = memberdict

        for i in settings["memberdict"]:
            if i != "Member ID":
                member_widget.id_boxes.append(QLabel(text=i))
                member_widget.name_boxes.append(QLabel(text=settings["memberdict"][i]["name"]))
                member_widget.avatar_boxes.append(QLineEdit(text=settings["memberdict"][i]["avatar"]))
        
        for i in range(len(member_widget.id_boxes)):
            id.addWidget(member_widget.id_boxes[i])
            name.addWidget(member_widget.name_boxes[i])
            avatar.addWidget(member_widget.avatar_boxes[i])

        columns.addLayout(id)
        columns.addLayout(name)
        columns.addLayout(avatar)

        self.setLayout(self.layoutall)
        
class chatbox_preview(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        label = QLabel(text="Preview")

        chatbox_preview.preview = QTextBrowser()
        self.preview.setPlainText("Not Connected")

        layout.addWidget(label)
        layout.addWidget(self.preview)
        self.setLayout(layout)   
         
class output_log(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        label = QLabel(text="Log")

        output_log.log = QTextBrowser()

        layout.addWidget(label)
        layout.addWidget(self.log)
        self.setLayout(layout) 

class options_widget(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()

        visibleOnStart = QCheckBox(text="Chatbox Visible by Default")
        attemptReconnect = QCheckBox(text="Attempt Reconnect")
        generic = QTextEdit()
        time_digital = QTextEdit()
        time_full = QTextEdit()
        afk = QTextEdit()
        status = QTextEdit()

        options_widget.widgets = [visibleOnStart,attemptReconnect,generic,time_digital,time_full,afk,status]

        layout.addWidget(QLabel(text="Default Chatbox"))
        layout.addWidget(generic)
        layout.addWidget(QLabel(text="Short Time"))
        layout.addWidget(time_digital)
        layout.addWidget(QLabel(text="Long Time"))
        layout.addWidget(time_full)
        layout.addWidget(QLabel(text="Away Message"))
        layout.addWidget(afk)
        layout.addWidget(QLabel(text="Status Message (if logged in)"))
        layout.addWidget(status)
        layout.addWidget(visibleOnStart)
        layout.addWidget(attemptReconnect)
        self.setLayout(layout)

class start_options(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        
        start_options.startBtn = QPushButton("Start",self)
        self.startBtn.setCheckable(True)
        self.startBtn.setEnabled(False)
        self.startBtn.clicked.connect(self.start_button)
        self.reloadBtn = QPushButton("Import Settings",self)
        self.reloadBtn.clicked.connect(self.reload_button)
        self.saveBtn = QPushButton("Save Settings",self) #Make it so you cannot save before members have been gathered
        self.saveBtn.clicked.connect(self.save_button)
        self.resetBtn = QPushButton("Reset Settings",self)
        self.resetBtn.clicked.connect(self.reset_button)

        layout = QVBoxLayout()

        layouttop = QHBoxLayout()
        layouttop.addWidget(self.startBtn)
        layouttop.addWidget(self.reloadBtn)
        layouttop.addWidget(self.saveBtn)
        layouttop.addWidget(self.resetBtn)

        self.traceback = QLabel("")
        start_options.traceback = self.traceback

        layout.addWidget(self.traceback)
        layout.addLayout(layouttop)
        self.setLayout(layout)
    
    def start_button(self):
        if self.startBtn.isChecked():

            if int(member_widget.columns.count()) < 3:
                start_options.traceback.setText("Member list cannot be empty, gather members first.")
                self.startBtn.setChecked(False)
            else:
                self.startBtn.setText("Stop")
                MainWindow.start()
        else:
            self.startBtn.setText("Start")
            chatbox_preview.preview.setPlainText("Not Connected")
            SP2VRC_Lib.set_keybinds.cancel()
            SP2VRC_Lib.taskcancelled = True

    def reload_button(self):
        try:
            settings, tracebackText = load_settings(2)
            self.traceback.setText(tracebackText)
            import_data(settings=settings)
        except Exception as e:
            self.traceback.setText("Unable to read or generate settings")
            print(e)
    
    def save_button(self):
        try:
            save_data()
        except:
            self.traceback.setText("Unable to save to settings")
    
    def reset_button(self):
        with open("settings.json","w") as file:
            file.write("")
        load_settings(3)
        self.traceback.setText("Reset settings to defaults")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SimplyPlural2VRC")
        self.setMinimumSize(QSize(500,500))
        self.setBaseSize(QSize(2000,600))

        MainWindow.threadpool = QThreadPool()

        MainWindow.ping = QLabel()

        self.draw_layout()

        import_data(load_settings(0))

    def draw_layout(self):
        layout = QGridLayout()

        layout.addWidget(login_widget(),0,0,alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(keybinds_widget(),1,0,alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(output_log(),2,0,alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(start_options(),3,0,alignment=Qt.AlignmentFlag.AlignBottom)

        layout.addWidget(member_widget(),0,1,alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(chatbox_preview(),1,1,alignment=Qt.AlignmentFlag.AlignTop)
        layout.addWidget(options_widget(),2,1,alignment=Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(self.ping,3,1,alignment=Qt.AlignmentFlag.AlignBottom)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def start():
        program = Program()
        startup = Worker(program.sp2vrc_start)
        startup.signals.chatbox.connect(program.chatbox_fn)
        startup.signals.logger.connect(program.logging_fn)
        MainWindow.threadpool.start(startup)

def getCheckboxState(state):
    if state == True:
        return 2
    else:
        return 0
    
def load_settings(x=0):
    tb, s = SP2VRC_Lib.read_options_from_ui.get_options()
    if x == 0:
        return s
    elif x == 1:
        return tb
    elif x == 2:
        return s, tb
    else:
        return

def gather_members(readToken):
    conn = http.client.HTTPSConnection("api.apparyllis.com")
    payload = ""
    headers = {"Authorization": readToken}
    try:
        conn.request("GET","/v1/me",payload,headers)
        systemID = json.loads(conn.getresponse().read().decode("utf-8"))["id"]
    except:
        tb = "Unable to gather system ID. Invalid read token."
    try:
        memberdict = asyncio.run(SP2VRC_Lib.get_member_details(systemID,readToken))
        tb = "Gathered members."
    except:
        tb = "Unable to gather members."
        memberdict = {}
    return tb, memberdict

def import_data(settings):
    options_widget.widgets[0].setCheckState(Qt.CheckState(getCheckboxState(settings["visible_on_load"])))
    options_widget.widgets[1].setCheckState(Qt.CheckState(getCheckboxState(settings["attempt_reconnect"])))
    login_widget.widgets[4].setCheckState(Qt.CheckState(getCheckboxState(settings["enable_status"])))
    options_widget.widgets[2].setPlainText(settings["chatbox"]["generic"])
    options_widget.widgets[3].setPlainText(settings["chatbox"]["time_digital"])
    options_widget.widgets[4].setPlainText(settings["chatbox"]["time_full"])
    options_widget.widgets[5].setPlainText(settings["chatbox"]["afk"])
    options_widget.widgets[6].setPlainText(settings["chatbox"]["status"])
    login_widget.widgets[0].setText(settings["sp_token"])
    login_widget.widgets[1].setText(settings["vrc_info"]["vrc_user"])
    login_widget.widgets[2].setText(settings["vrc_info"]["vrc_pass"])
    login_widget.widgets[3].setText(settings["vrc_info"]["vrc_userid"])
    for i in keybinds_widget.keybinds:
        keybinds_widget.keybinds[i].setText(settings["keybinds"][i])

def save_data():
    try:
        auths = SP2VRC_Lib.vrc_login.auths
    except:
        with open("settings.json") as file:
            settings = json.load(file)
        auths = settings["auths"]
    if int(member_widget.columns.count()) < 3:
        start_options.traceback.setText("Member list cannot be empty, gather members first.")
    else:
        temp_save = {
            "sp_token": login_widget.widgets[0].text(),
            "visible_on_load": options_widget.widgets[0].isChecked(),
            "attempt_reconnect": options_widget.widgets[1].isChecked(),
            "enable_status": login_widget.widgets[4].isChecked(),
            "vrc_info": {
                "vrc_user": login_widget.widgets[1].text(),
                "vrc_pass": login_widget.widgets[2].text(),
                "vrc_userid": login_widget.widgets[3].text()
            },
            "chatbox": {
                "generic": options_widget.widgets[2].toPlainText(),
                "time_digital": options_widget.widgets[3].toPlainText(),
                "time_full": options_widget.widgets[4].toPlainText(),
                "afk": options_widget.widgets[5].toPlainText(),
                "status": options_widget.widgets[6].toPlainText(),
            },
            "keybinds":{},
            "memberdict":{},
            "auths":auths
        }
        for i in range(len(member_widget.id_boxes)):
            temp_save["memberdict"][member_widget.id_boxes[i].text()] = {
                "name": member_widget.name_boxes[i].text(),
                "avatar": member_widget.avatar_boxes[i].text(),
                "pronouns": member_widget.memberdict[member_widget.id_boxes[i].text()][1]
            }

        for i in keybinds_widget.keybinds:
            temp_save["keybinds"][i] = keybinds_widget.keybinds[i].text()

        with open("settings.json","w") as file:
            json.dump(temp_save,file,indent=4)
        start_options.traceback.setText("Saved!")

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
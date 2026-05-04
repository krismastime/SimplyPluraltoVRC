#SimplyPlural to VRC Library by krismastime Version 1.3.3
import json, asyncio, time, http.client, logging, threading
from pynput import mouse, keyboard
from http.cookiejar import Cookie, CookieJar
from datetime import timedelta, datetime
from libraries import websockets
from libraries.pythonosc import udp_client, dispatcher #ADD KEYBIND THINGS THOUGH THIS AND PYNPUT!!!!!
# dispatcher.map("/avatar/parameters/<command>", func())
import vrchatapi
from vrchatapi.api import authentication_api
from vrchatapi.api_client import ApiClient
from vrchatapi.configuration import Configuration
from vrchatapi.exceptions import UnauthorizedException
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode
from vrchatapi.api.users_api import UsersApi

# Coded by krismastime (https://github.com/krismastime)
# Globals and their default values

global timeformat, pingtime, frontID, frontStart, message, chatbox, chatboxVisibility, timerVisibility, afk, aloop, vrc_loggedin, ip, port, client, taskcancelled
timeformat = "digital"
pingtime = time.time()
frontID = []
frontStart = []
message = ""
chatbox = ""
timerVisibility = False
afk = False
aloop = ""
vrc_loggedin = False
ip = "127.0.0.1"
port = 9000
client = udp_client.SimpleUDPClient(ip,port)
taskcancelled = False

def get_vk(key):
    return key.vk if hasattr(key, "vk") else key.value.vk

def on_press(key):
    vk = get_vk(key)
    new_kb.add(vk)

def on_release():
    return False

def set_kb():
    global new_kb
    new_kb = set()
    with keyboard.Listener(on_press=on_press,on_release=on_release) as listener:
        listener.join()
    return new_kb

def update_avatar(settings):
    try:
        print("Attempting to update avatar...")
        avatarID = settings["memberdict"][frontID[-1]]["avatar"]
        client.send_message("/avatar/change",avatarID)
    except Exception as e:
        print("Unable to update avatar, ignoring.")

async def update_chatbox():
    global chatboxVisibility, chatbox
    while True:
        try:
            if chatboxVisibility == True:
                client.send_message("/chatbox/input",[chatbox,True,False])
            else:
                chatbox = ""
                client.send_message("/chatbox/input",[chatbox,True,False])
                while chatboxVisibility == False:
                    await asyncio.sleep(1)
        except Exception as e:
            print("Unable to send chatbox update to OSC.")
            print(e)
        await asyncio.sleep(2)

class read_options_from_ui:

    default_settings = {
        "sp_token":"",
        "attempt_reconnect":True,
        "visible_on_load":True,
        "enable_status":True,
        "vrc_info":{
            "vrc_user":"",
            "vrc_pass":"",
            "vrc_userid":"",
        },
        "chatbox":{
            "generic":"#fronter\n#pronouns",
            "time_digital":"#fronter\n#pronouns\nFronting #time",
            "time_full":"#fronter\n#pronouns\nFronting #time",
            "afk":"#fronter is\nnot here right now!",
            "status":"#fronter"
        },
        "keybinds":{
            "Close Programme":"ctrl+page down",
            "Toggle Time":"ctrl+page up",
            "Time Format":"alt+page up",
            "Toggle Chatbox":"ctrl+home",
            "Show AFK":"ctrl+up",
            "Force Update":"ctrl+u"
        },
        "memberdict":{
            "Member ID":{
                "name": "Member Name",
                "avatar":"Avatar ID",
                "pronouns":"Member Pronouns"
            }
        },
        "auths":{
            "auth":"unknown",
            "twoFactorAuth":"unknown"
        },
    }

    def get_options(filename="settings.json"):
        defaults = read_options_from_ui.default_settings
        noErrors = 0
        error = ""
        try:
            with open(filename) as file:
                settings = json.load(file)

            try:
                chatboxes = settings["chatbox"]
            except:
                noErrors += 1
                error += "\nError retrieving chatbox."
                settings["chatbox"] = defaults["chatbox"]

            try:
                auth_cookie = settings["auths"]["auth"]
                twofa_cookie = settings["auths"]["twoFactorAuth"]
            except:
                noErrors += 1
                error += "\nError retrieving auth tokens."
                settings["auths"] = defaults["auths"]

            try:
                log_in = settings["enable_status"]
                if log_in != True and log_in != False:
                    error += "\nError determining if log in is True/False"
                    settings["enable_status"] = defaults["enable_status"]
                    noErrors += 1
            except:
                noErrors += 1
                error += "\nError retrieving log in value."
                settings["enable_status"] = defaults["enable_status"]

            try:
                keybinds = settings["keybinds"]
                try:
                    set_keybinds.update_keybinds(settings)
                except:
                    print("Unable to set 1 or more keybinds.")
            except:
                noErrors += 1
                error += "\nError retrieving keybinds."
                settings["keybinds"] = defaults["keybinds"]

            try:
                vrcconfig = Configuration(
                    username= settings["vrc_info"]["vrc_user"],
                    password= settings["vrc_info"]["vrc_pass"]
                )
                vrcUserID = settings["vrc_info"]["vrc_userid"]
            except:
                noErrors += 1
                error += "\nError retrieving VRChat Information."
                settings["vrc_info"] = defaults["vrc_info"]
            
            try:
                readToken = settings["sp_token"]
            except:
                noErrors += 1
                error += "\nError retrieving Simply Plural read token."
                settings["sp_token"] = defaults["sp_token"]

            try:
                reconnect = settings["attempt_reconnect"]
                if reconnect != True and reconnect != False:
                    error += "\nError determining if reconnect is True/False"
                    settings["attempt_reconnect"] = defaults["attempt_reconnect"]
                    noErrors += 1
            except:
                noErrors += 1
                error += "\nError retrieving reconnect value."
                settings["attempt_reconnect"] = defaults["attempt_reconnect"]

            try:
                chatboxVisibility = settings["visible_on_load"]
                if chatboxVisibility != True and chatboxVisibility != False:
                    error += "\nError determining if visible on load is True/False"
                    settings["visible_on_load"] = defaults["visible_on_load"]
                    noErrors += 1
            except:
                noErrors += 1
                error += "\nError retrieving visible on load value."
                settings["visible_on_load"] = defaults["visible_on_load"]
                
            try:
                memberdict = settings["memberdict"]
            except:
                error += "\nError retrieving member dictionary."
                settings["memberdict"] = defaults["memberdict"]
                noErrors += 1

            if noErrors > 0:
                with open(filename,"w") as file:
                    json.dump(settings,file,indent=4)
                if noErrors == 1:
                    error += str("\nFixing "+str(noErrors)+" error in settings.json")
                else:
                    error += str("\nFixing "+str(noErrors)+" errors in settings.json")
                return error, settings
            else:
                with open(filename,"w") as file:
                    json.dump(settings,file,indent=4)
                return "Reloaded!", settings
        except:
            error = "Unable to parse, generating settings.json"
            with open(filename,"w") as file:
                json.dump(defaults,file,indent=4)
            return error, "X"


class TerminateTG(Exception):
    "Exception raised."

class set_keybinds():

    def cancel():
        print("Cancelling...")
        global taskcancelled, reconnect
        reconnect = False
        taskcancelled = True

    def time_format():
        print("Toggling time format...")
        global timeformat
        if timeformat == "digital":
            timeformat = "long"
        else:
            timeformat = "digital"

    def show_time():
        print("Toggling time...")
        global timerVisibility
        if timerVisibility == False:
            timerVisibility = True
        else:
            timerVisibility = False

    def show_chatbox():
        print("Toggling chatbox...")
        global chatboxVisibility
        if chatboxVisibility == False:
            chatboxVisibility = True
        else:
            chatboxVisibility = False

    def show_afk():
        print("Toggling afk...")
        global afk
        if afk == False:
            afk = True
        else:
            afk = False

    def update_keybinds(settings):
        keybinds = settings["keybinds"]
        kb_reformat = {}
        for i in keybinds:
            kb_reformat[i] = keybinds[i].replace("lctrl","<ctrl_l>").replace("rctrl","<ctrl_r>")
        with keyboard.GlobalHotKeys({
            "": set_keybinds.cancel,
            "": set_keybinds.show_time,
            "": set_keybinds.time_format,
            "": set_keybinds.show_chatbox,
            "": set_keybinds.show_afk,
            "": manual_update(settings)
        }) as hotkeys:
            hotkeys.join()
        keyboard.add_hotkey(keybinds["Close Programme"],set_keybinds.cancel)
        keyboard.add_hotkey(keybinds["Toggle Time"],set_keybinds.show_time)
        keyboard.add_hotkey(keybinds["Time Format"],set_keybinds.time_format)
        keyboard.add_hotkey(keybinds["Toggle Chatbox"],set_keybinds.show_chatbox)
        keyboard.add_hotkey(keybinds["Show AFK"],set_keybinds.show_afk)
        keyboard.add_hotkey(keybinds["Force Update"],lambda: manual_update(settings))

def make_cookie(name, value):
    return Cookie(0, name, value,
                  None, False,
                  "api.vrchat.cloud", True, False,
                  "/", False,
                  False,
                  173106866300,
                  False,
                  None,
                  None, {})

class vrc_login:
    def __init__(self):
        super().__init__(self)
        vrc_login.status = ""

    def two_fa(vrcexception, authcode):
        if vrcexception == 0:
            print("Authorise via Email code")
            try:
                vrc_login.auth_api.verify2_fa_email_code(two_factor_email_code=TwoFactorEmailCode(authcode))
            except Exception as e:
                print(e)
        elif vrcexception == 1:
            print("Authorise via 2FA app code")
            vrc_login.auth_api.verify2_fa(two_factor_auth_code = TwoFactorAuthCode(authcode))
        vrc_login.current_user = vrc_login.auth_api.get_current_user()
        try:
            print("getting cookies")
            cookie_jar = vrc_login.api_client.rest_client.cookie_jar._cookies["api.vrchat.cloud"]["/"]
            print(cookie_jar)
            vrc_login.auths = {"auth":cookie_jar["auth"].value,"twoFactorAuth":cookie_jar["twoFactorAuth"].value}
            print("Saving auth cookies")
            vrc_login.save_cookies(vrc_login.auths)
            vrc_login.user_var = UsersApi(vrc_login.api_client)
            return vrc_login.current_user
        except:
            print("Unable to save auths")
            return "Unable to save auths"

    def save_cookies(auths):
        error, settings = read_options_from_ui.get_options()
        settings["auths"] = auths
        with open("settings.json","w") as file:
            json.dump(settings,file,indent=4)

    def getauthfromfile(usern,passw):
        error, settings = read_options_from_ui.get_options()
        auths = settings["auths"]

        vrc_config = Configuration(
            username = usern,
            password = passw,
        )

        vrc_login.api_client = ApiClient(vrc_config)
        vrc_login.api_client.user_agent = "SimplyPluralVRC/1.3.3 kristen.e.lane2004@gmail.com"
        vrc_login.api_client.rest_client.cookie_jar.set_cookie(
            make_cookie("auth",auths["auth"])
        )
        vrc_login.api_client.rest_client.cookie_jar.set_cookie(
            make_cookie("twoFactorAuth",auths["twoFactorAuth"])
        )

        vrc_login.auth_api = authentication_api.AuthenticationApi(vrc_login.api_client)
        try:
            vrc_login.current_user = vrc_login.auth_api.get_current_user()
            return vrc_login.current_user

        except UnauthorizedException as e:

            if e.status == 200: #Exception for unauthorised login attempt, requires auth code
                if "Email 2 Factor Authentication" in e.reason: #maybe try async thread request instead
                    vrc_login.status = "Email authentication code requested."
                elif "2 Factor Authentication" in e.reason:
                    vrc_login.status = "Two-Factor authentication code requested."
                return vrc_login.status

            elif e.status == 401: #Exception for invalid login credentials
                return "Unable to sign in. Invalid username/email or password."
            
            else: #General exception from the server end
                return "Unable to sign in, API may be experiencing difficulties."

        except vrchatapi.exceptions.ApiException as e: #General exception from the user end
            return "Unable to sign in, you may have timed out."      

async def ping(hostname,ws):
    while True:
        try:
            global pingtime
            pingtime = time.time()
            await ws.send("ping")
            await asyncio.sleep(10)
        except Exception as e:
            print("Error in ping")
            print(e)
            await asyncio.sleep(5)

def add_front(message,settings,logger):
    global frontID, frontStart
    try:
        frontUpd = json.loads(message)
        frontUpd = frontUpd["results"][0]["content"]
        frontID.append(frontUpd["member"])
        frontStart.append(int(frontUpd["startTime"])/1000)
        logger.emit(str("Member "+settings["memberdict"][frontID[-1]]["name"]+" began fronting at ")+str(datetime.fromtimestamp(frontStart[-1])))
        update_avatar(settings)
    except Exception as e:
        print(e)

def remove_front(message,settings,logger):
    global frontID, frontStart
    try:
        frontUpd = json.loads(message)
        frontUpd = frontUpd["results"][0]["content"]
        list_index = frontID.index(frontUpd["member"])
        logger.emit(str("Member "+settings["memberdict"][frontID[list_index]]["name"]+" stopped fronting at ")+str(datetime.fromtimestamp(int(frontUpd["endTime"])/1000)))
        frontID.pop(list_index)
        frontStart.pop(list_index)
    except Exception as e:
        print(e)

async def listen(hostname,ws,settings,logger):    
    while True:
        global message
        message = await ws.recv()
        try:
            if message == "pong":
                logger.emit(str("Ping-ponged: "+str(int((time.time()-pingtime)*1000))+"ms"))
            elif "insert" in message:
                add_front(message,settings,logger)
            elif "endTime" in message:
                remove_front(message,settings,logger)
            else:
                logger.emit(message)
        except Exception as e:
            print("Error in listen")
            print(e)
            await asyncio.sleep(1)

def manual_update(settings):
    frontID, frontStart = asyncio.run(get_fronter(settings["sp_token"]))
    for i in len(frontID):
        messageManual = {"results":[{"content":{"member":frontID[i],"startTime":frontStart[i]*1000}}]}
        messageManual = json.dumps(messageManual)
        print(messageManual)
        add_front(messageManual)

async def cancelcheck():
    while True:
        if taskcancelled == True:
            raise TerminateTG()
        await asyncio.sleep(1)

async def get_fronter(readToken):
    global frontID, frontStart
    conn = http.client.HTTPSConnection("api.apparyllis.com")
    payload = ''
    headers = {
    'Authorization': readToken
    }
    conn.request("GET", "/v1/fronters/", payload, headers)
    res = conn.getresponse()
    res = res.read()[1:-1]
    res = json.loads(res.decode("utf-8"))
    for i in res:
        if i == "content":
            frontStart.append(float(res[i]["startTime"])/1000)
            frontID.append(res[i]["member"])
    return frontID, frontStart

def as_list(pairs):
    return list(pairs)

def time_text(whenfrom,timeformat):
    now = time.time()
    timespan = int(abs(now - (whenfrom)))
    delta = timedelta(seconds=timespan)
    if timeformat == "digital":
        fronttimespan = delta
    else:
        if timespan < 60:
            fronttimespan = "less than a minute"
        elif timespan > 60 and timespan < 3600:
            fronttimespan = str(timespan//60)+" mins"
        else:
            fronttimespan = str(timespan//3600)+" hrs "+str((timespan//60)-((timespan//3600)*60))+" mins"
    return str(fronttimespan)

def chat_format(i,fronters,pronouns):
    return i.replace("#fronter",fronters).replace("#pronouns",pronouns).replace("#time",time_text(max(frontStart),timeformat))

async def chatbox_string(settings,chatbox_preview):
    global chatbox
    while True:
        fronters, pronouns = "", ""
        try:
            if len(frontID) == 1:
                fronters = str(settings["memberdict"][frontID[0]]["name"])
                pronouns = str(settings["memberdict"][frontID[0]]["pronouns"])         
            else:
                for i in frontID:
                    fronters = str(fronters+settings["memberdict"][i]["name"]+"|") 
                    pronouns = str(pronouns+settings["memberdict"][i]["pronouns"]+"|")
        except:
            print("Could not parse get fronters or pronouns.")
        try:
            if chatboxVisibility == True:
                if afk == False:
                    if timerVisibility == True and timeformat == "digital":
                        chatbox = chat_format(settings["chatbox"]["time_digital"],fronters,pronouns)
                    elif timerVisibility == True and timeformat != "digital":
                        chatbox = chat_format(settings["chatbox"]["time_full"],fronters,pronouns)
                    else:
                        chatbox = chat_format(settings["chatbox"]["generic"],fronters,pronouns)
                else:
                    chatbox = chat_format(settings["chatbox"]["afk"],fronters,pronouns)
            else:
                chatbox = ""
        except Exception as e:
            print("Could not parse chatbox string.")
            print(e)
        chatbox_preview.emit(chatbox)
        await asyncio.sleep(1)

async def status_string(settings):
    global aloop, frontID

    try:
        current_user = vrc_login.current_user
        user_var = vrc_login.user_var
        while True:
            try:
                await asyncio.sleep(70)
                status = settings["chatbox"]["status"] #Edit this to allow for more than 1 fronter, frontID is a list, check for list length
                status = status.replace("#fronter",str(settings["memberdict"][frontID[0]]["name"])).replace("#pronouns",str(settings["memberdict"][frontID[0]]["pronouns"]))
                request = {'statusDescription':status}
                print(request)
                user_var.update_user(user_id=settings["vrc_info"]["vrc_userid"],update_user_request=request)
            except Exception as e:
                print(e)
                await asyncio.sleep(10)
    except:
        print("Lost connection to VRChat API")

async def create_websocket(hostname,payload,settings,logger):
    global message,systemID
    i = 0
    ws = await websockets.connect(hostname)
    while i < 5:
        i+=1
        await ws.send(payload)
        message = await ws.recv()
        if "Successful" in message:
            logger.emit("Connected to SimplyPlural")
            try:
                message = json.loads(message)
                systemID = message["resolvedToken"]["uid"]
                logger.emit("Socket created with system ID "+systemID)
                return ws, systemID
            except:
                logger.emit("Unable to parse system ID.")
        if i == 5 and settings["attempt_reconnect"] == False:
            logger.emit("Unable to connect to SimplyPlural. Is the read token valid?")
        elif i == 5 and settings["attempt_reconnect"] == True:
            logger.emit("Unable to connect to SimplyPlural. Retrying in 10s.")
            await asyncio.sleep(10)
            i = 0
            continue
        else:
            logger.emit("\nRetrying ("+str(i)+")")
            await asyncio.sleep(1)
    systemID = ""
    return ws, systemID

async def gather_member_info(settings,logger):
    try:
        frontID, frontStart = await get_fronter(settings["sp_token"])
        return frontID, frontStart
    except:
        logger.emit("Unable to gather member details from SimplyPlural.")
        return "",""

async def get_member_details(systemID,readToken):
    conn = http.client.HTTPSConnection("api.apparyllis.com")
    memberdict = {}
    payload = ''
    headers = {
    'Authorization': readToken
    }
    conn.request("GET", "/v1/members/"+systemID, payload, headers)
    res = conn.getresponse()
    memberjson = res.read()
    memberlist = json.loads((memberjson.decode("utf-8")),object_pairs_hook=as_list)
    for x in memberlist:
        for y in x:
            if y[0] == "id":
                a = y[1]
            if y[0] == "content":
                for z in y[1]:
                    if z[0] == "name":
                        b = z[1]
                    elif z[0] == "pronouns":
                        c = z[1]
        memberdict[a] = [b,c]
    return memberdict

async def auth(settings,chatbox_preview,logger):
    global systemID, frontID, frontStart, chatboxVisibility,taskcancelled

    taskcancelled = False
    chatboxVisibility = settings["visible_on_load"]

    hostname = "wss://api.apparyllis.com/v1/socket"
    payload = json.dumps({"op": "authenticate", "token": settings["sp_token"]})

    ws, systemID = await create_websocket(hostname,payload,settings,logger)
    
    frontID, frontStart = await gather_member_info(settings,logger)

    update_avatar(settings)
    set_keybinds.update_keybinds(settings)

    while taskcancelled == False:
        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(listen(hostname,ws,settings,logger))
                tg.create_task(ping(hostname,ws))
                tg.create_task(chatbox_string(settings,chatbox_preview))
                tg.create_task(update_chatbox())
                tg.create_task(status_string(settings))
                tg.create_task(cancelcheck())
        except Exception as e:
            if taskcancelled == True:
                logger.emit("Closing...")
                chatbox_preview.emit("Not Connected")
                return
            elif settings["attempt_reconnect"] == True:
                logger.emit("Disconnected, attempting to reconnect. (5s)")
                await asyncio.sleep(5)
                continue
            elif settings["attempt_reconnect"] == False:
                logger.emit("Disconnected. Read exception for details:\n"+str(e))
                return


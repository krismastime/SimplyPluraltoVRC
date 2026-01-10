import json, asyncio, time, http.client
from http.cookiejar import Cookie
from datetime import timedelta, datetime
from libraries import keyboard, websockets
from libraries.vrchatapi import vrchatapi
from libraries.pythonosc import udp_client
from vrchatapi.api import authentication_api
from vrchatapi.exceptions import UnauthorizedException
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode
from vrchatapi.api.users_api import UsersApi

# Coded by krismastime (https://github.com/krismastime)
# Globals and their default values

global timeformat
timeformat = "digital"
global pingtime
pingtime = time.time()
global frontID
frontID = ""
global frontStart
frontStart = 0
global message
message = ""
global chatbox
chatbox = ""
global chatboxVisibility
chatboxVisibility = False
global timerVisibility
timerVisibility = False
global afk
afk = False
global aloop
aloop = ""

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

def get_options_from_files():
    try:
        with open("auths.json") as file:
            rawcookies = json.load(file)
            global auth_cookie, twofa_cookie
            auth_cookie = rawcookies["auth"]
            twofa_cookie = rawcookies["twoFactorAuth"]
    except:
        print("Generating auth.json")
        with open("auths.json","w") as file:
            json.dump({"auth":"unknown","twoFactorAuth":"unknown"},file)

    try:
        with open("keybinds.json") as file:
            keybinds = json.load(file)
            keyboard.add_hotkey(keybinds["cancel"],cancel)
            keyboard.add_hotkey(keybinds["time_visibility"],show_time)
            keyboard.add_hotkey(keybinds["time_format"],time_format)
            keyboard.add_hotkey(keybinds["chatbox_visibility"],show_chatbox)
            keyboard.add_hotkey(keybinds["afk"],show_afk)
            keyboard.add_hotkey(keybinds["force_update"],manual_update)
    except:
        print("Generating keybinds.json")
        with open("keybinds.json","w") as file:
            json.dump({"cancel":"ctrl+page down","time_visibility":"ctrl+page up","time_format":"alt+page up","chatbox_visibility":"ctrl+home","afk_mode":"ctrl+up","force_update":"ctrl+u"},file)

    try:
        with open("avatars.json") as file:
            global avatars
            avatars = json.load(file)
    except:
        print("Generating avatars.json")
        with open("avatars.json","w") as file:
            json.dump({"name1":"avtr_id-id-id-id-id","name2": "avtr_id-id-id-id-id",},file)

    try:
        with open("options.json") as file:
            options = json.load(file)
            global vrcconfig, vrcUserID, readToken
            vrcconfig = vrchatapi.Configuration(
                username= options["vrc_user"],
                password= options["vrc_pass"]
            )
            vrcUserID = options["vrc_userid"]
            readToken = options["sp_token"]
    except:
        print("Generating options.json")
        with open("options.json","w") as file:
            json.dump({"vrc_user":"Enter VRChat Username","vrc_pass":"Enter VRChat Password","vrc_userid":"Enter VRChat User ID","sp_token":"Enter SimplyPlural Read Token"},file)

    return

async def vrcLogIn():
    global aloop, current_user, auth_cookie, twofa_cookie
    aloop=""
    while True:
        aloop = input("Log into VRChat? y/n\n")
        if "y" in aloop or "Y" in aloop:
            with vrchatapi.ApiClient(vrcconfig) as api_client:
                api_client.user_agent = "SimplyPluralVRC/0.0.1 send issues to kristen.e.lane2004@gmail.com"
                api_client.rest_client.cookie_jar.set_cookie(
                    make_cookie("auth", auth_cookie))
                api_client.rest_client.cookie_jar.set_cookie(
                    make_cookie("twoFactorAuth", twofa_cookie))
                auth_api = authentication_api.AuthenticationApi(api_client)
                try:
                    current_user = auth_api.get_current_user()
                except UnauthorizedException as e:
                    if e.status == 200:
                        if "Email 2 Factor Authentication" in e.reason:
                            auth_api.verify2_fa_email_code(two_factor_email_code=TwoFactorEmailCode(input("Email 2FA Code: ")))
                        elif "2 Factor Authentication" in e.reason:
                            auth_api.verify2_fa(two_factor_auth_code=TwoFactorAuthCode(input("2FA Code: ")))
                        current_user = auth_api.get_current_user()
                    elif e.status == 401:
                        print("Unable to sign in to VRChat: Invalid Username/Email or Password.\nUnable to start status updater. Ignoring.")
                        aloop = ""
                        return
                    else:
                        print("Exception when calling API: %s\n",e)
                        aloop = ""
                except vrchatapi.ApiException as e:
                    print("Exception when calling API: %s\n",e)
                    aloop = ""

                cookie_jar = api_client.rest_client.cookie_jar._cookies["api.vrchat.cloud"]["/"]
                auths = {"auth":cookie_jar["auth"].value,"twoFactorAuth":cookie_jar["twoFactorAuth"].value}
                with open("auths.json","w") as file:
                    json.dump(auths,file)
                print("Saved cookies to file 'auths.json'")
                print("Logged in as:", current_user.display_name)
                global users_api
                users_api = UsersApi(api_client)
                break            
        elif "n" in aloop or "N" in aloop:
            break

class TerminateTG(Exception):
    "Exception raised."

async def ping(hostname,ws):
    while True:
        global pingtime
        pingtime = time.time()
        await ws.send("ping")
        await asyncio.sleep(10)

def update_front(message):
    global frontID
    global frontStart
    frontUpd = json.loads(message)
    frontUpd = frontUpd["results"][0]["content"]
    frontID = frontUpd["member"]
    frontStart = int(frontUpd["startTime"])/1000
    print("Member",memberdict[frontID],"began fronting at",datetime.fromtimestamp(frontStart))
    avatarID = avatars[memberdict[frontID][0]]
    client = udp_client.SimpleUDPClient("127.0.0.1",9000)
    client.send_message("/avatar/change",avatarID)

async def listen(hostname,ws):    
    while True:
        global message
        message = await ws.recv()
        if message == "pong":
            print("Ping-ponged:",str(int((time.time()-pingtime)*1000))+"ms")
        elif "insert" in message:
            update_front(message)
        else:
            print(message)

def manual_update():
    frontID, frontStart = asyncio.run(get_fronter(readToken))
    messageManual = {"results":[{"content":{"member":frontID,"startTime":frontStart*1000}}]}
    messageManual = json.dumps(messageManual)
    print(messageManual)
    update_front(messageManual)

async def cancelcheck():
    while True:
        if taskcancelled == True:
            raise TerminateTG()
        await asyncio.sleep(1)

async def get_fronter(readToken):
    global frontStart
    conn = http.client.HTTPSConnection("api.apparyllis.com")
    payload = ''
    headers = {
    'Authorization': readToken
    }
    conn.request("GET", "/v1/fronters/", payload, headers)
    res = conn.getresponse()
    frontID = res.read()[1:-1]
    frontID = json.loads(frontID.decode("utf-8"))
    frontStart = float(frontID["content"]["startTime"])/1000
    frontID = frontID["content"]["member"]
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

async def chatbox_string():
    while True:
        try:
            if chatboxVisibility == True:
                if afk == False:
                    global chatbox
                    chatbox = str(memberdict[frontID][0])+"\n"+str(memberdict[frontID][1])
                    if timerVisibility == True:
                        fronttimespan = time_text(frontStart,timeformat)
                        chatbox = chatbox+str("\nFronting "+fronttimespan)
                else:
                    chatbox = str(memberdict[frontID][0])+"\nNot here right now!"
            else:
                chatbox = ""
        except:
            print("Could not get fronter.")
        await asyncio.sleep(1)

async def status_string():
    global aloop
    if "y" in aloop or "Y" in aloop:
        global users_api
        global current_user
        global frontID
        while True:
            try:
                request = {'statusDescription':str(memberdict[frontID][0])}
                print(request)
                users_api.update_user(user_id=vrcUserID,update_user_request=request)
                await asyncio.sleep(70)
            except Exception as e:
                print(e)
                await asyncio.sleep(10)

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

async def auth(hostname,payload,readToken):
    global systemID
    global frontID
    global frontStart
    global memberdict
    async with websockets.connect(hostname) as ws:
        for i in range(1,6):
            print("Connection attempt",i)
            try:
                await ws.send(payload)
                message = await ws.recv()
                if "Successful" in message:
                    message = json.loads(message)
                    systemID = message["resolvedToken"]["uid"]
                    print("Socket created with system ID",systemID)
                    try:
                        print("Getting current fronter ID...")
                        frontID, frontStart = await get_fronter(readToken)
                        print("Successful. Fronter ID:",frontID)
                        print("Started fronting:",datetime.fromtimestamp(frontStart))
                        print("Getting system information...")
                        memberdict = await get_member_details(systemID,readToken)
                        print("System information gathered:\n"+str(memberdict))
                        print("Current fronter is:",memberdict[frontID])
                        print("Updating Avatar...")
                        try:
                            avatarID = avatars[memberdict[frontID][0]]
                            client = udp_client.SimpleUDPClient("127.0.0.1",9000)
                            client.send_message("/avatar/change",avatarID)
                        except:
                            print("Unable to update avatar. Ignoring.")
                        await vrcLogIn()
                    except Exception as e:
                        print("Unable to gather required data, closing.")
                        break
                    try:
                        async with asyncio.TaskGroup() as tg:
                            tg.create_task(listen(hostname,ws))
                            tg.create_task(ping(hostname,ws))
                            tg.create_task(chatbox_string())
                            tg.create_task(connectVRC())
                            tg.create_task(status_string())
                            tg.create_task(cancelcheck())
                    except Exception as e:
                        print("Finished listening or unable to ping, closing.")
                        print(e)
                        break
                else:
                    continue
            except:
                print("Unsuccessful...")
                continue
        if i >= 5:
            print("Unable to connect to SimplyPlural. Is the read token valid?")
        systemID = ""
        return systemID

async def connectVRC():
    global chatboxVisibility
    global chatbox
    chatboxVisibility = False
    chatbox = "Setting up..."
    address = "127.0.0.1"
    portIN = 9000
    portOUT = 9001
    print("Sending OSC through "+address+":"+str(portIN))
    osc = "--osc="+str(portIN)+":"+address+":"+str(portOUT)
    client = udp_client.SimpleUDPClient(address,portIN)
    while True:
        if chatboxVisibility == True:
            client.send_message("/chatbox/input",[chatbox,True,False])
        else:
            chatbox = ""
            client.send_message("/chatbox/input",[chatbox,True,False])
            while chatboxVisibility == False:
                await asyncio.sleep(1)
        await asyncio.sleep(2)

def cancel():
    print("Cancelling...")
    global taskcancelled
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
    global chatbox
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

async def main(hostname,payload,readToken):
    global taskcancelled
    taskcancelled = False
    systemID = await auth(hostname,payload,readToken)
    # use get http request here to get first instance of FronterID here, to update information on VRChat.
    # this variable can then be edited later on.

get_options_from_files()

try:
    hostname = "wss://api.apparyllis.com/v1/socket"
    payload = json.dumps({"op": "authenticate", "token": readToken})
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(hostname,payload,readToken))
except:
    print("Unable to obtain Simply Plural read token from options.json")

input("Press enter to close.\n")
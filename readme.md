# Simply Plural to VRC

## 1. Introduction
This is a standalone programme that takes data from an authorised [SimplyPlural](https://app.apparyllis.com) token, and sends the data to VRChat via the built in OSC api.
There are also options to update the status of the account.
The application is primarily for use of accessibility, in cases where the account is held by a plural people or systems.

## !! WARNING !!

Due to VRChat's use of API TOS, the status updates are sent less often than to the chatbox, lowering the frequency of the updates may result in account termination.
By using and logging in to VRChat with this application, you acknowledge it is your own responsibility to take care of the safety of your account.
The requests are also very tempermental, and may not behave correctly, sometimes taking a long time to see the status change.

This application uses [VRChat API for Python](https://github.com/vrchatapi/vrchatapi-python), here is the disclamer for the usage of this library:
> Use of the API using applications other than the approved methods (website, VRChat application) are not officially supported. You may use the API for your own application, but keep these guidelines in mind:
> * We do not provide documentation or support for the API.
> * Do not make queries to the API more than once per 60 seconds.
> * Abuse of the API may result in account termination.
> * Access to API endpoints may break at any given time, with no warning.

## 2. Using the application

On first opening, you will see four files be created before the app closes by itself. Now is your chance to edit these files to how you see fit.

### Options.json

By Default:
```json
{"vrc_user":"Enter VRChat Username","vrc_pass":"Enter VRChat Password","vrc_userid":"Enter VRChat User ID","sp_token":"Enter SimplyPlural Read Token","attempt_reconnect":false,"visible_on_load":true}
```

There are four options within this file:
* VRChat Username *vrc_user*
* VRChat Password *vrc_pass*
* VRChat UserID *vrc_userid*
* SimplyPlural Token *sp_token* ***(Required)***
* Attempt Reconnect *attempt_reconnect*
* Visibility Defaults *visible_on_load*

The only one that you will need to look at to use the programme is the SimplyPlural Token. To find this, log in to SimplyPlural and follow the path:
> Menu -> Settings -> Account -> Tokens
This [link](https://app.apparyllis.com/#/Settings/Account/Tokens) should take you there automatically.
If you don't have a Read Token already, you then need to press "Add Token," and allow the token to be used to read account details.
Once done, click and hold on the token to copy it to your clipboard, replace the text following *sp_token* and save the file.

This is all that is required to use this programme, but keep reading if you want more usage out of it!

If you want to use the status updating feature, you will need to add details to the other three values in this document.
*vrc_user* and *vrc_pass* are the username/email and password you use to log in to VRChat, this should only be required first, as once you are log in, the authentication cookies are stored in auths.json
*vrc_userid* is the ID that VRChat uses to locate your account, to find it, log in to VRChat on a browser, and go to your profile.

The URL should look like this
https://vrchat.com/home/user/usr_00aa000a-a0aa-0a00-00aa-aaa000aaa000

Take the last part of the URL, and replace the text following *vrc_userid*. It should look like this:
```json
{"vrc_userid": "usr_00aa000a-a0aa-0a00-00aa-aaa000aaa000"} 
```

If you are having issues staying connected to SimplyPlural, you can change *attempt_reconnect* to true. If you are able to connect once, the programme will continuously attempt to reconnect to SimplyPlural until the close keybind is pressed or the programme is closed manually.

Set *visible_on_load* to false if you do not want the programme to update the chatbox immediately.

### Keybinds.json

By Default:
```json
{"cancel": "ctrl+page down", "time_visibility": "ctrl+page up", "time_format": "alt+page up", "chatbox_visibility": "ctrl+home", "afk_mode": "ctrl+up", "force_update": "ctrl+u"}
```

The keybinds are implemented using the [keyboard](https://github.com/boppreh/keyboard) python library. Because of this, NUMPAD keys are represented by their actions when NumLock is not toggled. The default keybinds are:
* Close the programme: `Ctrl + NUMPAD 3`
* Toggle Chatbox Visibility: `Ctrl + NUMPAD 7`
* Toggle AFK Text: `Ctrl + NUMPAD 8`
* Toggle Time Fronting Visibility: `Ctrl + NUMPAD 9`
* Toggle Time Fronting Format: `Alt + NUMPAD 9`
* Force Update: `Ctrl + u`

### Avatars.json

By Default:
```json
{"name1": "avtr_id-id-id-id-id", "name2": "avtr_id-id-id-id-id"}
```

This file is used to change avatars when the programme starts and when an update is detected from SimplyPlural.
The name has to be *identical* to how it is formatted on SimplyPlural, otherwise the avatar will not update.
This file is loaded on startup, and changes to the file while the programme is running will not be read until reopened.
Like *vrc_userid* within options.json, the avatar id can be taken from the link of the avatar.

For example, the default avatar has the following URL:
https://vrchat.com/home/avatar/avtr_c38a1615-5bf5-42b4-84eb-a8b6c37cbd11

Take the last part of the URL, and replace the text following the member's name. It should look like this:
```json
{"Person's Name!":"avtr_c38a1615-5bf5-42b4-84eb-a8b6c37cbd11"}
```

### Chatbox.json

By Default:
```json
{"generic":"#fronter\n#pronouns","time_digital":"#fronter\n#pronouns\nFronting #time","time_full":"#fronter\n#pronouns\nFronting #time","afk":"#fronter is\nnot here right now!","status":"#fronter"}
```

This file is used to customise the output of the chatbox and statuses. There are five things available to change:
* *generic*: This is what is shown by default when the chatbox is enabled.
* *afk*: This is what is shown as the first alternate chatbox, by default it shows an afk message.
* *time_digital*: This is what is shown as the second alternate chatbox, by default it is used to show the time in a digital format.
* *time_full*: This is what is shown as the third alternate chatbox, by default it is used to show the time in an extended format.
* *status*: This is what is sent to the VRChat API if you log in. Only #fronter and #pronouns are available to use here.

There are three custom variables to use in this file:
* *\#fronter*: The name of the last fronter received from SimplyPlural by the programme.
* *\#pronouns*: The pronouns of *\#fronter*.
* *\#time*: The time since *\#fronter* was detected. Pressing the *time_full* keybind (Default: `Alt + NUMPAD 9`) changes it from digital (00:00:00) to full (0 hrs, 0 mins)

### Auths.json

By Default:
```json
{"auth": "unknown", "twoFactorAuth": "unknown"}
```

This is a purely programme used file, there shouldn't be a need to edit this file, and doing so may prevent you from being able to log in to VRChat.
After logging into the app, the authentication cookies are stored here, keep these secure and private to protect your VRChat account.

# 3. Known Issues

There are currently some issues with the vrchatapi-python library, this library is a door to updating details on your VRChat account, specifically here it is used to update your account status. However, during testing, there have been moments in which a required module of the library is simply not detected.
I have tried my best to prevent this from happening, but there may still be some issues. If some libraries are unable to be detected, let me know and I will see if I can update the programme when I have time.

# 4. Libraries

Packaged with this application are the following non built-in libraries:
* [keyboard](https://github.com/boppreh/keyboard)
* [pythonosc](https://pypi.org/project/python-osc/)
* [websockets](https://pypi.org/project/websockets/)
* [vrchatapi-python](https://github.com/vrchatapi/vrchatapi-python)

# 5. Build

If you download the .py version of the programme, run installer.py to build it as a .exe.
[Pyinstaller](https://pyinstaller.org/en/stable/)

# 6. Support

I can attempt to offer user support for the application, however this is simply a passion project. Check my [GitHub](https://github.com/krismastime) to see where you can find me!
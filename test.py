from pynput import keyboard
import time

keybinds = {
    "Close Programme": {},
    "Toggle Time": {},
}

def close():
    print("close programme")

def toggle():
    print("toggle time")

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

for i in keybinds:
    print(i)
    keybinds[i] = set_kb()
    time.sleep(1)

print(keybinds)

for i in keybinds:
    temp = ""
    for j in keybinds[i]:
        try:
            temp = temp+"+"+str(keyboard.KeyCode(keyboard.KeyCode.from_vk(j)).char) #WONT MAKE LETTERS >:(
        except AttributeError:
            temp = temp+"+<"+str(keyboard.Key(keyboard.KeyCode.from_vk(j)))+">"
    keybinds[i] = temp[1:]

#print(keyboard.HotKey.parse(keybinds["Close Programme"]))
print(keybinds)

with keyboard.GlobalHotKeys({
    keybinds["Close Programme"]:close,
    keybinds["Toggle Time"]:toggle
}) as h:
    h.join()
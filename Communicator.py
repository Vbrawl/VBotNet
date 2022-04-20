import socket


DEFAULT_BUFFER = 1024
TIMEOUT = 2
END_BYTE = b'EOM0' # End Of Message 0


class COMMUNICATOR:
    def __init__(self, sock):
        self.sock = sock
        # self.sock.settimeout(TIMEOUT)
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
                print("RETURNING SILENTLY")
                return False # Silently fallback
        elif not isinstance(msg, bytes):
            print("RETURNING SILENTLY")
            return False


        sent = False
        while not sent:
            try:
                self.sock.send(msg)
                self.sock.send(END_BYTE)
                sent = True


            except ConnectionAbortedError:
                print('Connection Aborted')
        return True




    def recv(self):
        global DEFAULT_BUFFER

        # data = b''
        # while True:
        #     try:
        #         data += self.sock.recv(1)
        #         print(data)
        #
        #         if data.endswith(END_BYTE):
        #             return data[: (-1*len(END_BYTE)) ]
        #     except TimeoutError:
        #         return data
        # return False

        data = b''
        while True:
            try:
                d = self.sock.recv(DEFAULT_BUFFER)
                if d == b'':
                    self.close()
                    return data
                data += d

                if data.endswith(END_BYTE):
                    return data[: ( -1*len(END_BYTE) )]
            except:
                return data




    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.IsConnected = False

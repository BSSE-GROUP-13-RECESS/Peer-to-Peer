import os.path
import socket
import sys

import get_addr

if __name__ == "__main__":
    filename = ''
    try:
        filename = sys.argv[1]
    except IndexError:
        print("please provide file name e.g=> python client.py filename")
        exit(-1)

    port = 12347
    address = get_addr.get_wifi_ip()

    conn = socket.socket()
    try:
        conn.connect((address, port))
    except OSError:
        print('Host cannot be found')
        exit(-1)

    print(conn.recv(1024).decode())

    filepath = 'recv/'+filename
    if os.path.isfile(filepath):
        print('File already exists!')
        exit(-1)
    conn.send(filename.encode())
    msg = conn.recv(1024)

    if msg == '201':
        print('Specified file does not exist at host')
    else:
        conn.send('continue'.encode())
        file = open(filepath, 'wb')
        file.write(conn.recv(1024))
        file.close()
        print('File successfully received')
    conn.close()

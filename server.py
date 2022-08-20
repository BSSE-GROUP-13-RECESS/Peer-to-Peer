import socket
import get_addr
import os

if __name__ == "__main__":
    s = socket.socket()
    print("Socket successfully created")

    port = 12347
    s.bind((get_addr.get_wifi_ip(), port))
    print("socket bound to %s" % port)

    s.listen(5)
    print("socket is listening")

    while True:
        c, addr = s.accept()
        print('Got connection from', addr)
        c.send('Successfully connected'.encode())
        filename = c.recv(1024).decode()
        filepath = 'files/'+filename
        if os.path.isfile(filepath):
            c.send('200'.encode())
            msg = c.recv(1024).decode()
            file = open(filepath, 'rb')
            c.sendfile(file)
            file.close()
        else:
            c.send('201'.encode())
        c.close()

import socket
import sys
import helpers
import os

if __name__ == "__main__":
    host = helpers.get_wifi_ip()
    try:
        host = sys.argv[1]
    except IndexError:
        pass
    s = socket.socket()
    print("Socket successfully created")

    port = 12347
    s.bind((host, port))
    print("socket bound to %s" % port)

    s.listen(5)
    print("socket is listening")

    identifier = helpers.configs.identifier
    peers = helpers.configs.peers

    while True:
        c, addr = s.accept()
        print('Got connection from', addr)
        msg = c.recv(1024).decode()

        info = msg.split('|')
        peers[info[0]] = {'ip': addr, 'rtt': float(info[1])}
        helpers.update_configurations('peers', str(peers))
        c.send(str(peers).encode())

        msg = c.recv(1024).decode()

        try:
            filepath = 'files/'+msg
            if os.path.isfile(filepath):
                c.send('200'.encode())
                msg = c.recv(1024).decode()
                file = open(filepath, 'rb')
                c.sendfile(file)
                file.close()
                print('Found')
            else:
                c.send('201'.encode())
                print('Found|')
            c.close()
        except BrokenPipeError:
            pass

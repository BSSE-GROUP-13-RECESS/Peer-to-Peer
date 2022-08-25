import socket
import sys
import helpers
import os
import shutil


def main():
    host = helpers.get_wifi_ip()
    try:
        host = sys.argv[1]
    except IndexError:
        pass
    s = socket.socket()
    # print("Socket successfully created")

    port = 12347
    s.bind((host, port))
    # print("socket bound to %s" % port)

    s.listen(5)
    # print("socket is listening")

    identifier = helpers.configs.identifier
    peers = helpers.configs.peers

    while True:
        c, addr = s.accept()
        msg = c.recv(1024).decode()
        info = msg.split('|')
        # print('Got connection from', info[2])
        peers[info[0]] = {'ip': info[2], 'rtt': float(info[1])}
        helpers.update_configurations('peers', str(peers))
        c.send(str(peers).encode())

        msg = c.recv(1024).decode()
        if msg.startswith("--leave"):
            c.close()
            s.close()
            exit()
        elif msg.startswith('resource'):
            filename = msg.split('|')[1]
            c.send('send'.encode())
            msg = c.recv(1024)
            file = open('files/'+filename+'.zip', 'wb')
            file.write(msg)
            file.close()
            shutil.unpack_archive('files/'+filename+'.zip', 'files/'+filename)
            os.remove('files/'+filename+'.zip')
            c.close()
        elif msg.startswith('reallocate'):
            filename = msg.split('|')[1]
            shutil.rmtree('files/'+filename)
            c.close()
        else:
            try:
                filepath = 'files/' + msg
                if os.path.isfile(filepath):
                    c.send('200'.encode())
                    msg = c.recv(1024).decode()
                    file = open(filepath, 'rb')
                    c.sendfile(file)
                    file.close()
                else:
                    c.send('201'.encode())
                c.close()
            except BrokenPipeError:
                pass


if __name__ == "__main__":
    main()

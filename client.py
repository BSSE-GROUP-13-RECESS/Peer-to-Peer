import os.path
import socket
import sys
import time
import helpers


def connect(address):
    elapsed_time = -1
    conn = None
    helpers.get_wifi_ip()
    try:
        initial_time = time.time()  # Store the time when request is sent

        port = 12347
        conn = socket.socket()
        try:
            conn.connect((address, port))
        except OSError:
            print('Host cannot be found')
            conn = None

        ending_time = time.time()  # Time when acknowledged the request
        elapsed_time = ending_time - initial_time
        if conn is None:
            elapsed_time = -1
        else:
            msg = helpers.configs.identifier+'|'+str(round(elapsed_time, 3))+'|'+helpers.configs.ip
            conn.send(msg.encode())
            helpers.add_peers(conn.recv(1024).decode())
    except:
        pass
    return conn, round(elapsed_time, 3)


def get_file(filename):
    peers = helpers.sort_peers(helpers.configs.peers)

    for peer in peers:
        if peer == helpers.configs.identifier:
            continue
        conn, rtt = connect(peer)
        if conn is None:
            print('Failed to connect to host ' + peer)
            continue

        filepath = 'files/' + filename
        if os.path.isfile(filepath):
            print('File already exists!')
            exit(-1)
        conn.send(filename.encode())
        msg = conn.recv(1024).decode()

        if msg == '201':
            print('Specified file does not exist at host ' + peer)
            conn.close()
        else:
            conn.send('continue'.encode())
            file = open(filepath, 'wb')
            file.write(conn.recv(1024))
            file.close()
            print('File successfully received')
            conn.close()
            break


def update_peer_info():
    peers = helpers.configs.peers
    for peer in peers:
        if peer == helpers.configs.identifier:
            continue
        addr = peers[peer]['ip']
        connection, rtt = connect(addr)
        if connection is not None:
            connection.close()
        peers[peer]['rtt'] = rtt
        print(addr, rtt)
    helpers.update_configurations('peers', str(peers))


if __name__ == "__main__":
    command = ''
    try:
        command = sys.argv[1]
    except IndexError:
        print("please provide file name or --rtt e.g=> python client.py filename")
        exit(-1)
    get_file(command)

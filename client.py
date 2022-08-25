import os.path
import socket
import time
import shutil
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
            msg = helpers.configs.identifier + '|' + str(round(elapsed_time, 3)) + '|' + helpers.configs.ip
            conn.send(msg.encode())
            helpers.add_peers(conn.recv(1024).decode())
    except:
        pass
    return conn, round(elapsed_time, 3)


def get_file(args):
    try:
        filename = args.split(' ')[1]
    except IndexError:
        print("please provide filename")
        return
    peers = helpers.sort_peers(helpers.configs.peers)

    for peer in peers:
        if peer == helpers.configs.identifier:
            continue
        conn, rtt = connect(helpers.configs.peers[peer]['ip'])
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


def help(args=None):
    print("Enter the following commands for the various operations.")
    print("1.get_file [filename] -to get a file")
    print("2.known_peers -to list known peers")
    print("3.upload [filepath] -to upload a file")
    print("4.list_files -to list local files")
    print("5.leave -to close")
    print("6.help -for all commands")


def known_peers(args=None):
    peers = helpers.configs.peers
    print("Order: identifier => ip_address => rtt")
    for peer in peers:
        if peer == helpers.configs.identifier:
            continue
        peer_data = peers[peer]
        print(peer, "  ", peer_data['ip'], "  ", peer_data['rtt'])


def upload(args):
    try:
        filepath = args.split(' ')[1]
    except IndexError:
        print('Provide a valid file path')
        return
    shutil.copy2(filepath, 'files')
    print('Successfully uploaded!')


def list_files(args=None):
    print('Files locally stored')
    for file in os.listdir('files'):
        print(file)


def leave(args=None):
    conn, rtt = connect(helpers.configs.ip)
    conn.send('--leave'.encode())
    relocate_resources()
    print("------Exiting---------")
    exit(0)


def relocate_resources():
    peers = helpers.configs.peers
    sorted_peers = helpers.sort_peers(helpers.configs.peers)
    conn = None
    current_peer = ''
    for peer in sorted_peers:
        if helpers.configs.identifier == peer:
            continue
        conn, rtt = connect(peers[peer]['ip'])
        if conn is None:
            continue
        else:
            current_peer = peer
            break
    if conn is None:
        print("No nearest peer found!")
        return
    shutil.make_archive(helpers.configs.identifier+'_'+current_peer, 'zip', 'files')
    conn.send(str('resource|'+helpers.configs.identifier).encode())
    conn.recv(1024)
    file = open(helpers.configs.identifier+'_'+current_peer+'.zip', 'rb')
    conn.sendfile(file)
    file.close()
    conn.close()
    helpers.configs.resources.append(helpers.configs.identifier+'_'+current_peer)
    helpers.update_configurations('resources', str(helpers.configs.resources))


def reallocate_resources():
    resources = helpers.configs.resources
    for res in resources:
        peer = helpers.configs.peers[res.split('_')[1]]
        conn, rtt = connect(peer['ip'])
        if conn is None:
            continue
        else:
            conn.send('reallocate|'+helpers.configs.identifier)
            conn.close()
            if os.path.isfile(res+'.zip'):
                os.remove(res+'.zip')
            resources.remove(res)
            helpers.update_configurations('resources', str(resources))


def main():
    reallocate_resources()
    commands = ['get_file', 'known_peers', 'upload', 'list_files', 'leave', 'help']
    functions = [get_file, known_peers, upload, list_files, leave, help]
    help()
    while True:
        inp = input('command>')
        command = inp.split(' ')[0]
        if command not in commands:
            print("Invalid command, type help for all commands")
        else:
            functions[commands.index(command)](inp)


if __name__ == "__main__":
    pass
    # print(helpers.sort_peers(helpers.configs.peers))
    # main()

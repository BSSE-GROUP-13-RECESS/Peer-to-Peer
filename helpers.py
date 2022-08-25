import subprocess
import json
import configurations
configs = configurations


def get_wifi_ip():
    if configs.identifier.startswith('default'):
        return configs.ip
    try:
        addresses = str(subprocess.check_output('ifconfig | grep -A 4 wl', shell=True)).split()
        ip = ""
        for i in range(len(addresses)):
            if addresses[i] == 'inet':
                ip = addresses[i + 1]
                break
        configs.ip = ip
        update_configurations('ip', "'"+configs.ip+"'")
    except:
        pass
    return configs.ip


def update_configurations(name, config):
    file = open('configurations.py', 'r')
    current_config = ''

    for line in file:
        if line.startswith(name):
            current_config = current_config + ""+name+" = "+config+"\n"
        else:
            current_config = current_config + line
    file.close()
    file = open('configurations.py', 'w')
    file.write(current_config)
    file.close()


def sort_peers(peers):
    arr = []
    negs = []
    for peer in peers:
        rtt = peers[peer]['rtt']
        if rtt == -1:
            negs.append(-1)
            continue
        arr.append(rtt)
    arr.sort()
    arr = arr + negs
    for peer in peers:
        rtt = peers[peer]['rtt']
        arr[arr.index(rtt)] = peer
    return arr


def add_peers(peer_str):
    peer_str = peer_str.replace('\'', '\"')
    new_peers = json.loads(peer_str)
    for peer in new_peers:
        if peer in configs.peers:
            configs.peers[peer]['ip'] = new_peers[peer]['ip']
        else:
            new_peers[peer]['rtt'] = -1
            configs.peers[peer] = new_peers[peer]
    update_configurations('peers', str(configs.peers))


if configs.identifier == '':
    import uuid
    configs.identifier = str(uuid.uuid4())
    update_configurations('identifier', "'"+configs.identifier+"'")

import subprocess


def get_wifi_ip():
    addresses = str(subprocess.check_output('ifconfig | grep -A 4 wl', shell=True)).split()
    ip = ""
    for i in range(len(addresses)):
        if addresses[i] == 'inet':
            ip = addresses[i+1]
            break
    return ip


if __name__ == "__main__":
    print(get_wifi_ip())

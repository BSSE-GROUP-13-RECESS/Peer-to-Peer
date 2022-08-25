import server
import client
from threading import Thread


if __name__ == "__main__":
    s_thread = Thread(target=server.main)
    s_thread.daemon = False
    s_thread.start()

    c_thread = Thread(target=client.main)
    c_thread.daemon = False
    c_thread.start()




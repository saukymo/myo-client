from __future__ import print_function

import myo
import sys
import time
from socketIO_client import SocketIO


device_id = 1
server_url = "localhost"

def register():
    socketIO.emit("register", device_id)


def deregister():
    socketIO.emit("deregister", device_id)


def send_emg(emg, moving):
    socketIO.emit("emg", {"device_id":device_id, "emg":emg})

if __name__ == "__main__":
    socketIO = SocketIO(server_url, 5000)
    m = myo.MyoRaw(sys.argv[1] if len(sys.argv) >= 2 else None)

    def proc_emg(emg, moving, times=[]):
        print(emg)

        ## print framerate of received data
        times.append(time.time())
        if len(times) > 20:
            times.pop(0)
            
	m.add_emg_handler(send_emg)
    m.add_emg_handler(proc_emg)
    m.connect()

    

    try:
        while True:
            m.run(1)
    except KeyboardInterrupt:
        pass
    finally:
        m.disconnect()
        deregister()
        print()

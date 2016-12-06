import myo
import sys
from socketIO_client import SocketIO, LoggingNamespace


device_id = 1
server_url = "http://127.0.0.1/"

def register():
    socketIO.emit("register", device_id)


def unregister():
    socketIO.emit("unregister", device_id)


def send_emg(emg, moving):
    socketIO.emit("emg", {"device_id":device_id, "emg":emg})

if __name__ == "__main__":
    # myo_client = myo.MyoRaw(sys.argv[1] if len(sys.argv) >= 2 else None)
    # myo_client.add_emg_handler(send_emg)
    # myo_client.connect()

    # socketIO = SocketIO(server_url, 5000, LoggingNamespace)
    # register()

    # try:
    #     while True:
    #         myo_client.run()
    # except KeyboardInterrupt:
    #     pass
    # finally:
    #     myo_client.disconnect()
    #     unregister()
    #     print()

    socketIO = SocketIO(server_url, 5000, LoggingNamespace)
    m = MyoRaw(sys.argv[1] if len(sys.argv) >= 2 else None)
    m.add_emg_handler(send_emg)
    
    def proc_emg(emg, moving, times=[]):
        print(emg)

        ## print framerate of received data
        times.append(time.time())
        if len(times) > 20:
            #print((len(times) - 1) / (times[-1] - times[0]))
            times.pop(0)

    m.add_emg_handler(proc_emg)
    m.connect()

    m.add_arm_handler(lambda arm, xdir: print('arm', arm, 'xdir', xdir))
    m.add_pose_handler(lambda p: print('pose', p))

    try:
        while True:
            m.run(1)
    except KeyboardInterrupt:
        pass
    finally:
        m.disconnect()
        print()

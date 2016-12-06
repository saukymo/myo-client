import myo
import sys
from socketIO_client import SocketIO

device_id = 1
server_url = "http://127.0.0.1/"

def register():
    socketIO.emit("register", device_id)


def unregister():
    socketIO.emit("unregister", device_id)


def send_emg(emg, moving):
    socketIO.emit("emg", {"device_id":device_id, "emg":emg})

class SocketIOClient(SocketIO):
    """
    Fix for library bug
    """

    def _should_stop_waiting(self, for_connect=False, for_callbacks=False):
        if for_connect:
            for namespace in self._namespace_by_path.values():
                is_namespace_connected = getattr(
                    namespace, '_connected', False)
                #Added the check and namespace.path
                #because for the root namespaces, which is an empty string
                #the attribute _connected is never set
                #so this was hanging when trying to connect to namespaces
                # this skips the check for root namespace, which is implicitly connected
                if not is_namespace_connected and namespace.path:
                    return False
            return True
        if for_callbacks and not self._has_ack_callback:
            return True
        return super(SocketIO, self)._should_stop_waiting()

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

    socketIO = SocketIOClient(server_url, 5000)
    register()

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

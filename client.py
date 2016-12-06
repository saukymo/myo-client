import myo
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
	myo_client = myo.Myo(myo.NNClassifier(), sys.argv[1] if len(sys.argv) >= 2 else None)
	myo_client.add_emg_handler(send_emg)
	myo_client.connect()

	socketIO = SocketIO(server_url, 5000, LoggingNamespace)
	register()

	try:
		while True:
			myo_client.run()
	except KeyboardInterrupt:
        pass
    finally:
        myo_client.disconnect()
        unregister()
        print()
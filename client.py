from __future__ import print_function

import myo
import sys
import time
from collections import Counter, deque
from socketIO_client import SocketIO
from classifier import NNClassifier
import multiprocessing

device_id = 1
server_url = "localhost"

def register():
    socketIO.emit("register", device_id)


def deregister():
    socketIO.emit("deregister", device_id)


def send_emg(emg, moving):
    socketIO.emit("emg", {"device_id":device_id, "emg":emg})


def alert_pose_handler(pose):
    print(pose)
    socketIO.emit("alert", {'status':pose==1, 'device_id':device_id})


class Myo(myo.MyoRaw):
    """Adds higher-level pose classification and handling onto MyoRaw."""

    HIST_LEN = 25
    STABLE = 10

    def __init__(self, cls):
        myo.MyoRaw.__init__(self, None)
        self.cls = cls

        self.history = deque([3] * Myo.HIST_LEN, Myo.HIST_LEN)
        self.history_cnt = Counter(self.history)
        self.add_emg_handler(self.emg_handler)

        self.last_pose = 3
        self.pose_handlers = [alert_pose_handler]

    def emg_handler(self, emg, moving):
        y = self.cls.classify(emg)
        self.history_cnt[self.history[0]] -= 1
        self.history_cnt[y] += 1
        self.history.append(y)

        r, n = self.history_cnt.most_common(1)[0]

        new_pose = self.last_pose
        if self.last_pose is None or (n > Myo.HIST_LEN / 2):
        # print(new_pose, self.last_pose)
            print(r)
            if r != self.last_pose:
                self.on_raw_pose(r)
                new_pose = r
        
        self.last_pose = new_pose

    def add_raw_pose_handler(self, h):
        self.pose_handlers.append(h)

    def on_raw_pose(self, pose):
        for h in self.pose_handlers:
            h(pose)

    def go(self):
        self.connect()
        while True:
            self.run()


if __name__ == "__main__":
    socketIO = SocketIO(server_url, 5000)
    register()
    m = Myo(NNClassifier())

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
            if not m.run(1):
                m.mc_start_collection()
    except KeyboardInterrupt:
        pass
    finally:
        m.disconnect()
        deregister()
        print()

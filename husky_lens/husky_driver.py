import json
import time
import threading
from modules.event import Event
from serial import SerialException
from husky_lens.husky_lens_library import HuskyLensLibrary


class HuskyDriver:
    ON_DETECTED_IMAGE_EVENT = "OnDetectedImageEvent"

    def __init__(self):
        self.__husky_lens = None
        self.is_opened = False
        self.event = Event()
        self.is_worker_running = False
        self.__thread_worker = None

    def open(self):
        try:
            self.__husky_lens = HuskyLensLibrary("SERIAL", "COM3", 3000000)
            self.is_opened = True
        except SerialException:
            self.is_opened = False

    def close(self):
        self.__husky_lens = None
        self.is_opened = False

    def start_worker(self):
        if not self.is_opened:
            return

        def worker():
            self.is_worker_running = True
            while self.is_worker_running:
                data = self.get_learned_blocks()
                if data is not None:
                    self.event.trigger(self.ON_DETECTED_IMAGE_EVENT, data)
                time.sleep(1)
        self.__thread_worker = threading.Thread(target=worker)
        self.__thread_worker.start()

    def stop_worker(self):
        if not self.is_opened:
            return
        self.is_worker_running = False
        self.__thread_worker.join()

    def learn_object(self, object_id):
        if not self.is_opened:
            return
        self.__husky_lens.learn(object_id)

    def get_learned_blocks(self):
        if not self.is_opened:
            return None
        try:
            data = self.__husky_lens.learnedBlocks()
            return json.dumps(data.__dict__)
        except Exception as ex:
            print(ex.__str__())
            return None

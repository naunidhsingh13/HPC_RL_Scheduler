from threading import Lock


class Pause:

    def __init__(self):

        self._lock = Lock()
        # True means Producer is paused, consumer should run.
        # False means Consumer is paused, Producer should run.
        self.pause = True
        self._release_all = False

    def _impl_pause(self, update=None):
        with self._lock:
            if self._release_all:
                return False
            if update is not None:
                self.pause = update
            return self.pause

    def pause_producer(self):
        self._impl_pause(True)
        while self._impl_pause():
            pass

    def pause_consumer(self):
        self._impl_pause(False)
        while not self._impl_pause():
            pass

    def is_consumer_paused(self):
        while not self._impl_pause():
            pass

    def is_producer_paused(self):
        while self._impl_pause():
            pass

    def release_all(self):
        self._release_all = True

from threading import Lock


# class Pause:

    # def __init__(self):
    #
    #     self._lock = Lock()
    #     self.consumer_paused = False
    #     self.producer_paused = False
    #
    # def _impl_pause_consumer(self, update=None):
    #     with self._lock:
    #         if update is not None:
    #             self.consumer_pause = update
    #         return self.consumer_paused
    #
    # def _impl_pause_producer(self, update=None):
    #     with self._lock:
    #         if update is not None:
    #             self.producer_paused = update
    #         return self.producer_paused
    #
    # def pause_producer(self, release_consumer=True):
    #     if release_consumer:
    #         self._impl_pause_consumer(False)
    #
    #     while self._impl_pause_producer():
    #         pass
    #
    # def pause_consumer(self, release_producer=True):
    #     if release_producer:
    #         self._impl_pause_producer(False)
    #     while not self._impl_pause_consumer():
    #         pass






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

    def is_comsumer_paused(self):
        while not self._impl_pause():
            pass

    def is_producer_paused(self):
        while self._impl_pause():
            pass

    def release_all(self):
        self._release_all = True



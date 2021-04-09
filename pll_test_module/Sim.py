from Pause import Pause
from threading import Thread
from random import randint

class Sim(Thread, Pause):

    def __init__(self):
        Thread.__init__(self)
        Pause.__init__(self)
        print("Initialized")
        self.wait_list = None
        self.is_simulation_complete = False

    def sim(self):

        self.wait_list = [0]

        for i in range(10):

            self.pause_consumer()
            print("Simulator or Consumer is running")
            print("Simulator will roll the job : %d" % self.wait_list.pop())
            self.wait_list += [randint(10, 100) for j in range(4)]

        self.is_simulation_complete = True
        self.release_all()

    def run(self) -> None:

        self.sim()








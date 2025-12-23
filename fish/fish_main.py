import time
from random import randint
try:
    from .simulator import SimulatorController
    from .vision import VisionProcessor
    from .base import random_sleep_millisecond
except ImportError:
    from simulator import SimulatorController
    from vision import VisionProcessor
    from base import random_sleep_millisecond

class FishBot:
    """
    Core state machine to manage game logic and coordinate simulator and vision components.
    """
    def __init__(self):
        self.simulator = SimulatorController()
        self.vision = VisionProcessor()
        


    def fish(self):
        """
        Transition state based on the current situation.
        """
        # start fish
        while True:
            random_sleep_millisecond(1000, 3000)
            print("fish cast")
            self.simulator.fish_cast()
            while True:
                if self.vision.fish_hooked():
                    print("fish hooked")
                    self.simulator.fish_reel()
                    print("fish reel")
                    self.fish_reel_in_step()
                    break
                else:
                    random_sleep_millisecond(200, 500)
            
    
    def fish_reel_in_step(self):
        """
        Reel in the fish step by step.
        """
        # sleep and wait the scene load
        random_sleep_millisecond(300, 500)
        while True:
            if self.vision.on_critical_point():
                self.simulator.fish_reel_in_step()
            elif not self.vision.in_reel_scene():
                print("not in reel scene, now should be ready to re-cast")
                # wait harvest scene to load
                time.sleep(5)
                # if level up, here should be another click to quit the level up scene
                self.simulator.fish_empty()
                random_sleep_millisecond(1000, 3000)
                break




if __name__ == "__main__":
    bot = FishBot()
    bot.fish()


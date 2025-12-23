# coding: utf-8
from random import randint

try:
    from .adb import AdbClient
except ImportError:
    from adb import AdbClient
class SimulatorController:
    """
    Handles interactions with the simulator.
    """
    def __init__(self):
        # Initialize connection to simulator
        self.__adb = AdbClient()
        self.__fish_button_x = 1420
        self.__fish_button_y = 720

        self.__fish_empty_button_x = 1400
        self.__fish_empty_button_y = 370
    
    def fish_cast(self):
        random_swipe_time = randint(500, 1000)
        self.__adb.hold(self.__fish_button_x, self.__fish_button_y, random_swipe_time)
    
    def fish_reel(self):
        self.__adb.tap(self.__fish_button_x, self.__fish_button_y)
    
    def fish_empty(self):
        self.__adb.tap(self.__fish_button_x, self.__fish_button_y)
    
    def fish_reel_in_step(self):
        self.__adb.tap(self.__fish_button_x, self.__fish_button_y)
    
    def fish_end_harvest_scene(self):
        self.__adb.tap(self.__fish_button_x, self.__fish_button_y)
    

# debug 
if __name__ == "__main__":
    adb = SimulatorController()
    adb.fish_end_harvest_scene()
from random import randint
import time

def random_sleep_millisecond(min_time, max_time):
    time.sleep(randint(min_time, max_time)/1000.0)
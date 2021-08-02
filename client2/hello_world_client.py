from feddartClient.feddart.messageTranslatorClient import feddart
import time

@feddart
def hello_world_2(param1, param2):
    result = param1 + param2
    time.sleep(5 + result)
    raise ValueError("This is a Error for testing")

@feddart
def init(init_var):
    pass
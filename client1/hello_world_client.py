from feddart.messageTranslator import feddart
import time

@feddart
def hello_world_2(param1, param2):
    result = param1 + param2
    time.sleep(5 + result)
    return result, 10

@feddart
def init(init_var):
    pass
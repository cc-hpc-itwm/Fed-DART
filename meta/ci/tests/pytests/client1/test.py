import sys
sys.path.append('../feddart')
from feddart.messageTranslator import feddart
import time

@feddart
def test(param1, param2):
    result = param1 + param2
    return result

@feddart
def init(bool_string):
    if bool_string == "True":
        pass
    else:
        raise ValueError("test")
    
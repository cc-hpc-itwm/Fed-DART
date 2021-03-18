import sys
sys.path.append('../feddart')
from messageTranslator import feddart
import time

@feddart
def test(param1, param2):
    result = param1 + param2
    return result

@feddart
def init(bool_string):
    if bool_string == "True":
        return True
    else:
        return False
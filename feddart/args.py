import argparse
import os
import numpy as np

from copy import copy
from feddart.utils import print_args

from feddart.logServer import LogServer

class Parser(object):

    def __init__(self):

        parser = argparse.ArgumentParser("FED-DART")
        
        parser.add_argument('--mode', '-m', help = "test or real mode", default = "test")
        parser.add_argument('--errorProbability', '-ep', help = "probability for errors in test mode", default = 0)
        parser.add_argument('--logLevel', '-log', help = "LogLevel: DEBUG - 0, INFO - 1, WARN - 2, ERROR - 3, FATAL - 4. default: WARN", default = 2)
        
        self.args = parser.parse_args()
        print_args(self.args)

class Helper(Parser):
    def __init__(self):
        super(Helper, self).__init__()

        
    @property
    def config(self):
        return self.args

    @property
    def args_to_log(self):
        list_of_args = [
            "data"
        ]
        return args_to_log
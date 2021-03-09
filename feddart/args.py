import argparse
import os
import yaml
import numpy as np

from copy import copy
from src import utils

class Parser(object):
    def __init__(self):
        parser = argparse.ArgumentParser("FED-DART")

        parser.add_argument('--data', type=str, default='./data', help='data path. default: %(default)s')
        parser.add_argument('--nodefile', type=str, default='./nodefile', help='nodefile path. default: %(default)s')

        # training parameters
        parser.add_argument('--loss_function', type=str, default='default', help='nodefile path. default: %(default)s')
        parser.add_argument('--optimizer', type=str, default='default', help='nodefile path. default: %(default)s')
        parser.add_argument('--train_data', type=str, default='mnist', help='nodefile path. default: %(default)s')
        parser.add_argument('--epochs', type=int, default=1, help='nodefile path. default: %(default)s')
        parser.add_argument('--batchsize', type=int, default=16, help='nodefile path. default: %(default)s')
        parser.add_argument('--learningrate', type=float, default=0.001, help='nodefile path. default: %(default)s')
        
        self.args = parser.parse_args()
        utils.print_args(self.args)

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
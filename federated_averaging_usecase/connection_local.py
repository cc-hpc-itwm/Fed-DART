import sys
import time
import socket 
import os
import ast
import pickle
import binascii
from random import randint
from time import sleep

sys.path.insert (0, '..\lib')
sys.path.insert(0, os.environ['DART_HOME'] + '/lib') 
from dart import dart_context as dc, catch_stdout, catch_stderr
dc.catch_out()
dc.catch_err() 
from edge_device_workflow import EdgeDeviceWorklow

def extract_params(params):
    dict_params = ast.literal_eval (params)
    dict_params = pickle.loads (binascii.a2b_base64 (dict_params))
    list_parameter = []
    for parameter in dict_params.keys():
        if 'variable_number' in parameter:
            list_parameter.append(dict_params[parameter])
    return dict_params['location'], dict_params['function'], list_parameter

def convert_to_result_dict(result, function):
    counter = 0
    result_dict = {}
    if type(result) is tuple:
        for element in result:
            result_dict['result_' + str(counter)] = element
            counter += 1
    else: 
        result_dict['result_0'] = result
    result_dict['function'] = function
    return result_dict

def execute_function (_params):
    device_name, function_name, function_parameters_list = extract_params(_params)
    function = getattr(EdgeDeviceWorklow, function_name)
    result = function(*function_parameters_list, device_name)
    result = convert_to_result_dict(result, function_name)
    return dc.pack(result)


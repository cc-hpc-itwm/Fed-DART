import json
import os
import time
import argparse
import getpass 
import sys
import socket

from tfmodel_server import EmbeddingModelAirPollution, MNIST

from FusionAlgorithms import FederatedAveraging
sys.path.insert (0, '../fed_dart')
from Coordinator import Coordinator
from Aggregator import Aggregator

parser = argparse.ArgumentParser(description='Federated DART Example Federated Averaging')

parser.add_argument('--ssh_username', default=getpass.getuser(), help="default: %(default)s")
parser.add_argument('--ssh_port', default="2222", help="default: %(default)s")
parser.add_argument('--ssh_public_key', default='/home/' + getpass.getuser() + '/.ssh/id_rsa.pub', help="default: %(default)s")
parser.add_argument('--ssh_private_key', default='/home/' + getpass.getuser() + '/.ssh/id_rsa', help="default: %(default)s")

parser.add_argument('--devices', default='[["127.0.0.1", "2222"]]')

args = parser.parse_args()
available_devices = json.loads(args.devices)
coordinator_one = Coordinator(
    ssh_username = args.ssh_username, 
    ssh_port = int(args.ssh_port),
    ssh_public_key = args.ssh_public_key,
    ssh_private_key = args.ssh_private_key) #responsible for an FL population of devices
# always one single owner for every FL population
current_path = os.getcwd()
for i in range(len(available_devices)):
    device_name = 'edge_device_' + str(i)
    device = { 'name': device_name
             , 'host': available_devices[i][0] 
             , 'shm_size': 0
             , 'computing_power': 1 #computing_power = number_per_node
             , 'port':  available_devices[i][1] 
             , 'entry_point': current_path+'/connection_local'
             }
    coordinator_one.add_device(device)
global_model = MNIST()
available_devices = coordinator_one.select_devices()
aggregator_init = coordinator_one.create_aggregator(available_devices) 
list_task_parameter = []
global_model_json = global_model.model.to_json()
for j in range(len(available_devices)):
    task_parameter = [global_model_json]
    list_task_parameter.append(task_parameter)
aggregator_init.start_task('init_model', list_task_parameter) #TODO: implement featue like send_data, here we only send data without starting a task !!
global_rounds = 2
for i in range(global_rounds):
    #phase 1: selection of devices
    available_devices = coordinator_one.select_devices() #return is subset of all devices
    aggregator = coordinator_one.create_aggregator(available_devices) 
    list_task_parameter = []
    list_local_models_weights = []
    global_model_weights = global_model.get_weights()
    dict_training_hyperparameter = { "epochs": 1
                                   , "batch_size": 16
                                   , "learning_rate": 0.001
                                   , "loss_function": "default"
                                   , "optimizer": "default"
                                   , "train_data": "mnist"
                                   }
    for j in range(len(available_devices)):
        task_parameter = [global_model_weights, dict_training_hyperparameter]
        list_task_parameter.append(task_parameter)
    #phase 2: configuration sent tasks to worker
    aggregator.start_task('train_model', list_task_parameter)
    #time.sleep(20)
    #phase 3: server waits for the parcipating devices to report updates
    for device in available_devices:
        local_model_weights = aggregator.get_result(device , 'train_model')[0] #in case of timeout/no result avialable is result None
        print(local_model_weights)
        #TODO: check, why the return is a list 
        #TODO: check, if it waits on the result (seems to be) instead returning None
        if local_model_weights != None:
            list_local_models_weights.append(local_model_weights)
    global_model_weights = FederatedAveraging(list_local_models_weights)
    global_model.set_weights(global_model_weights)
coordinator_one.terminate()
        
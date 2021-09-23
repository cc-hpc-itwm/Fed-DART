from tensorflow.keras.layers import *
from tensorflow import keras
from feddart.workflowManager import WorkflowManager
import numpy as np
import argparse
import time 
import os


parser = argparse.ArgumentParser(description="Choose real or test mode for DART")
parser.add_argument('--mode', '-m', help = "test or real mode", default = "real")
parser.add_argument('--errorProbability', '-ep', help = "probability for errors in test mode", default = 0)
parser.add_argument('--logLevel', '-l', help = "log level of Fed-DART: lower value means more logging", default = 2)
args = parser.parse_args()
if args.mode == "test":
    manager = WorkflowManager( testMode = True
                             , errorProbability = args.errorProbability
                             , logLevel = args.logLevel
                             )
elif args.mode == "real":
    manager = WorkflowManager(logLevel = args.logLevel)
else:
    raise ValueError("Wrong options for example")
global_model = keras.Sequential([ Dense(2, activation='relu', input_shape=(28 * 28,))
                                , Dense(4, activation='relu')
                                , Dense(10, activation='softmax')
                                ]
                               )

manager.createInitTask( parameterDict = {"model_structure": global_model.to_json()}
                      , filePath = "client_learning"
                      , executeFunction = "init"
                      )
if args.mode == "test":
    if os.path.isfile("../serverFile.json"):
        rt_filepath = "../serverFile.json"
        device_filepath = "../dummydeviceFile.json"
    else:
        rt_filepath = os.environ['FEDDARTPATH'] + "examples/serverFile.json"
        device_filepath = os.environ['FEDDARTPATH'] + "examples/dummydeviceFile.json"
        
    manager.startFedDART(runtimeFile = rt_filepath
                        , deviceFile = device_filepath
                        , maximal_numberDevices = 100
                        )
else: 
    manager.startFedDART( runtimeFile = "../serverFile.json" 
                        , maximal_numberDevices = 100
                        )
LEARNING_ROUNDS = 4
MAX_COUNTER = 30
list_devices = manager.getAllDeviceNames()
time.sleep(5) #wait init task finished
for learning_round in range(LEARNING_ROUNDS):
    global_model_weights = global_model.get_weights()
    list_devices = manager.getAllDeviceNames()
    parameterDict = {}
    for idx, device in enumerate(list_devices):
        parameterDict[device] = { "global_model_weights": global_model_weights 
                                , "batch_size": 10*idx + 8
                                , "epochs": 2
                                }
    handle = manager.startTask( taskType = 1
                              , parameterDict =  parameterDict
                              , filePath = "client_learning"
                              , executeFunction = "learn"
                              )
    counter = 0
    while manager.getTaskStatus(handle) != manager.TASK_STATUS_FINISHED:
        time.sleep(3)
        counter += 1
        if counter > MAX_COUNTER:
            break
    taskResult = manager.getTaskResult(handle) #return all results which are currently available
    local_weights = []
    for device_result in taskResult:
        local_weights.append(device_result.resultList[0])
    local_weights = np.array(local_weights, dtype = object)
    global_weights = np.mean(local_weights, axis = 0)
    global_model.set_weights(global_weights)
    print("Global learning round %s finished!"%(str(learning_round+1)))
#manager.stopFedDART() optional you can shut down the server with stopFedDART()
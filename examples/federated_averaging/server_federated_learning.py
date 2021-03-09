from tensorflow.keras.layers import *
from tensorflow import keras
from feddart.workflowManager import WorkflowManager
import numpy as np
import time 
TEST_MODE = True
ERROR_PROBABILITY = 0
if TEST_MODE:
    manager = WorkflowManager( testMode = True
                             , errorProbability = 0
                             )
else:
    manager = WorkflowManager()

global_model = keras.Sequential([ Dense(2, activation='relu', input_shape=(28 * 28,))
                                , Dense(4, activation='relu')
                                , Dense(10, activation='softmax')
                                ]
                               )

manager.createInitTask( parameterDict = {"model_structure": global_model.to_json()}
                      , filePath = "client_learning"
                      , executeFunction = "init"
                      )
if TEST_MODE:
    manager.startFedDART( runtimeFile = "../serverFile.json" 
                        , deviceFile = "../dummydeviceFile.json"
                        , maximal_numberDevices = 100
                        )
else: 
    manager.startFedDART( runtimeFile = "../serverFile.json" 
                        , deviceFile = "../deviceFile.json"
                        , maximal_numberDevices = 100
                        )
LEARNING_ROUNDS = 4
time.sleep(5) #wait init task finished
for learning_round in range(LEARNING_ROUNDS):
    task_name = "task_" + str(learning_round) #task name must be unique
    global_model_weights = global_model.get_weights()
    manager.startTask( taskType = 1 
                     , taskName = task_name
                     , parameterDict =  { "device_one": { "global_model_weights": global_model_weights
                                                        , "batch_size": 64
                                                        , "epochs": 2
                                                        }
                                        , "device_two": { "global_model_weights": global_model_weights
                                                        , "batch_size": 128
                                                        , "epochs": 1
                                                        }
                                        }
                     , filePath = "client_learning" 
                     , executeFunction = "learn"
                     )
    while manager.getTaskStatus(task_name) != manager.TASK_STATUS_FINISHED:
        time.sleep(3)
    taskResult = manager.getTaskResult(task_name) #return all results which are currently available
    local_weights = []
    for device_result in taskResult:
        local_weights.append(device_result.resultList[0])
    local_weights = np.array(local_weights, dtype = object)
    global_weights = np.mean(local_weights, axis = 0)
    global_model.set_weights(global_weights)
   
manager.stopFedDART()
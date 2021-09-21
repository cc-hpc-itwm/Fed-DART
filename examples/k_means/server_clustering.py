from feddart.workflowManager import WorkflowManager
import numpy as np
import argparse
import time
import os
parser = argparse.ArgumentParser(description="Choose real or test mode for DART")
parser.add_argument('--mode', '-m', help = "test or real mode", default = "real")
parser.add_argument('--errorProbability', '-ep', help = "probability for errors in test mode", default = 0)
parser.add_argument('--logLevel', '-l', help = "log level of Fed-DART: lower value means more logging", default = 3)
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
DEFAULT_K = 3
DEFAULT_NUM_LOCAL_ITERATIONS = 100
DEFAULT_NUM_ITERATIONS = 5

STOP_CRITERION = 0.005
#inittask is an optional task, which must be executed on each client for initialization
manager.createInitTask( parameterDict = {"init_var": 'hello'}
                      , filePath = "client_clustering"
                      , executeFunction = "init"
                      )
if args.mode == "test":
    if os.path.isfile("../serverFile.json"):
        rt_filepath = "../serverFile.json"
        device_filepath = "../dummydeviceFile.json"
    else:
        rt_filepath = os.environ['FEDDARTPATH'] + "examples/serverFile.json"
        device_filepath = os.environ['FEDDARTPATH'] + "examples/dummydeviceFile.json"
    manager.startFedDART( runtimeFile = "../serverFile.json" 
                        , deviceFile = "../dummydeviceFile.json"
                        , maximal_numberDevices = 100
                        )
else: 
    manager.startFedDART( runtimeFile = "../serverFile.json" 
                        , maximal_numberDevices = 100
                        )
list_devices = manager.getAllDeviceNames()
collection0 = manager.createCollection([list_devices[0]]) #maybe return only clustername
collection1 = manager.createCollection([list_devices[1]])
collection0.addDevicebyName(list_devices[1])
collection1.removeDevicebyName(list_devices[1])
time.sleep(6) #wait init task finished
for global_round in range(DEFAULT_NUM_ITERATIONS):
    task_name = "task_" + str(global_round) #task name must be unique
    global_centroids = np.array([[-1,0], [0, 2]])
    new_devices = manager.getNewDeviceNames()
    parameterDict = {}
    for idx, device in enumerate(collection0.ActiveDeviceNames):
        parameterDict[device] = { "global_centroids": global_centroids
                                , "local_iterations": 2
                                }
    manager.startTask( taskType = 1
                     , taskName = task_name
                     , parameterDict = parameterDict
                     , filePath = "client_clustering"
                     , executeFunction = "local_k_means"
                     )
    time.sleep(10) #wait on result, FedDART is non blocking
    taskResult = manager.getTaskResult(task_name) #return all results which are currently available
    local_centroids = []
    for device_result in taskResult:
        local_centroids.append(device_result.resultList[0])
    # Aggregate centroids
    if len(local_centroids) > 0:
        new_centroids =  np.mean(local_centroids, axis=0)
            
    # Calculate centroids_mean_diff_sq between new and old centroids
    centroids_mean_diff_sq = np.mean(np.mean(np.square(global_centroids - new_centroids)))

    # Update global centroids
    global_centroids = new_centroids
    # Stop if stop criterion is reached
    if centroids_mean_diff_sq < STOP_CRITERION:
        logger.info("Stop criterion reached at iteration %s.", i)
        break

#manager.stopFedDART() optional you can shut down the server with stopFedDART()
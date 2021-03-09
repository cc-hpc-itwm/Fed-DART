from feddart.workflowManager import WorkflowManager
import numpy as np
import time
TEST_MODE = False
DEFAULT_K = 3
DEFAULT_NUM_LOCAL_ITERATIONS = 100
DEFAULT_NUM_ITERATIONS = 5

STOP_CRITERION = 0.005
if TEST_MODE:
    manager = WorkflowManager( testMode = True
                             , errorProbability = 0
                             )
else:
    manager = WorkflowManager()
#inittask is an optional task, which must be executed on each client for initialization
manager.createInitTask( parameterDict = {"init_var": 'hello'}
                      , filePath = "client_clustering"
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

time.sleep(3) #wait init task finished
global_centroids = np.array([[-1,0], [0, 2]])
for global_round in range(DEFAULT_NUM_ITERATIONS):
    task_name = "task_" + str(global_round) #task name must be unique
    manager.startTask( taskType = 1 
                     , taskName = task_name
                     , parameterDict =  { "device_one": { "global_centroids": global_centroids
                                                        , "local_iterations": 10
                                                        }
                                        , "device_two": { "global_centroids": global_centroids
                                                        , "local_iterations": 10
                                                        }
                                        }
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

manager.stopFedDART()
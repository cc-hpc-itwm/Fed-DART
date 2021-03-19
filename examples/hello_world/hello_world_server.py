"""
This simple example demonstrates how to start Fed-DART with an simple task.
Also the different ways to get the results is sketched.
"""
import time
import argparse
from feddart.workflowManager import WorkflowManager

parser = argparse.ArgumentParser(description="Choose real or test mode for DART")
parser.add_argument('--mode', '-m', help = "test or real mode", default = "real")
parser.add_argument('--errorProbability', '-ep', help = "probability for errors in test mode", default = 0)
args = parser.parse_args()
if args.mode == "test":
    manager = WorkflowManager( testMode = True
                             , errorProbability = int(args.errorProbability)
                             )
elif args.mode == "real":
    manager = WorkflowManager()
else:
    raise ValueError("Wrong options for example")
#inittask is an optional task, which must be executed on each client for initialization
manager.createInitTask( parameterDict = {"init_var": 'hello'}
                      , filePath = "hello_world_client"
                      , executeFunction = "init"
                      )
if args.mode == "test":
    manager.startFedDART( runtimeFile = "../serverFile.json" 
                        , deviceFile = "../dummydeviceFile.json"
                        , maximal_numberDevices = 100
                        )
else: 
    manager.startFedDART( runtimeFile = "../serverFile.json" 
                        , deviceFile = "../deviceFile.json"
                        , maximal_numberDevices = 100
                        )
time.sleep(1)                   
manager.startTask( taskType = 1 
                 , taskName = "task_one"
                 , parameterDict =  { "device_one": { "param1":0 ,"param2": 1}
                                    , "device_two": {"param1":10 ,"param2": 5}
                                    }
                 , filePath = "hello_world_client" 
                 , executeFunction = "hello_world_2"
                 )
time.sleep(5)
taskStatus = manager.getTaskStatus("task_one")
taskResult = manager.getTaskResult("task_one")
print(taskStatus)
for deviceResult in taskResult:
    print(deviceResult)
time.sleep(10)
taskResult = manager.getTaskResult("task_one")
for deviceResult in taskResult:
    print(deviceResult.resultDict)
time.sleep(20)
taskStatus = manager.getTaskStatus("task_one")
print(taskStatus)
taskResult = manager.getTaskResult("task_one")
for deviceResult in taskResult:
    print(deviceResult.resultList)
    print(deviceResult.duration)
    print(deviceResult.deviceName)
manager.removeDevice("device_one")
manager.stopTask("task_one")
task_acceptance = manager.startTask( taskType = 1 
                                   , taskName = "task_two"
                                   , parameterDict =  { "device_one": { "param1": 0 ,"param2": 1}
                                                      , "device_two": {"param1": 10 ,"param2": 5}
                                                      }
                                  , filePath = "hello_world_client"
                                  , executeFunction = "hello_world_2"
                                  ) #this task shouldn't be accepted because device_one is removed 
manager.stopFedDART()

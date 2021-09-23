"""
This simple example demonstrates how to start Fed-DART with an simple task.
Also the different ways to get the results is sketched.
"""
import time
import argparse
from feddart.workflowManager import WorkflowManager
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

#inittask is an optional task, which must be executed on each client for initialization
manager.createInitTask( parameterDict = {"init_var": 'hello'}
                      , filePath = "hello_world_client"
                      , executeFunction = "init"
                      )
if args.mode == "test":
    if os.path.isfile("../serverFile.json"):
        rt_filepath = "../serverFile.json"
        device_filepath = "../dummydeviceFile.json"
    else:
        rt_filepath = os.environ['FEDDARTPATH'] + "examples/serverFile.json"
        device_filepath = os.environ['FEDDARTPATH'] + "examples/dummydeviceFile.json"

    manager.startFedDART( runtimeFile = rt_filepath
                        , deviceFile = device_filepath
                        , maximal_numberDevices = 100
                        )
else: 
    manager.startFedDART( runtimeFile = "../serverFile.json" 
                        , deviceFile = None 
                        , maximal_numberDevices = 100
                        )
time.sleep(1)
#Get list of all connected devices by name
list_devices = manager.getAllDeviceNames()
time.sleep(2)
parameterDict = {}
for idx, device in enumerate(list_devices):
    parameterDict[device] = { "param1": idx ,"param2": idx + 2}
handle = manager.startTask( taskType = 1
                          , parameterDict =  parameterDict
                          , filePath = "hello_world_client"
                          , executeFunction = "hello_world_2"
                          )
time.sleep(15)
taskStatus = manager.getTaskStatus(handle)
taskResult = manager.getTaskResult(handle)
for deviceResult in taskResult:
    print(deviceResult.resultList)
    print(deviceResult.duration)
    print(deviceResult.deviceName)

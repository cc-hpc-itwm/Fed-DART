"""
This simple example demonstrates how to start Fed-DART with an simple task.
Also the different ways to get the results is sketched.
"""
import time
import argparse
from feddart.workflowManager import WorkflowManager
import os

from feddart.logger import logger 

log = logger(__name__)

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
manager.startTask( taskType = 1 
                 , taskName = "task_one"
                 , parameterDict =  parameterDict
                 , filePath = "hello_world_client" 
                 , executeFunction = "hello_world_2"
                 )
time.sleep(5)
taskStatus = manager.getTaskStatus("task_one")
taskResult = manager.getTaskResult("task_one")

log.info(str(taskStatus))
for deviceResult in taskResult:
    log.info(str(deviceResult))
time.sleep(10)
taskStatus = manager.getTaskStatus("task_one")
log.info(str(taskStatus))
taskResult = manager.getTaskResult("task_one")
for deviceResult in taskResult:
    log.info(str(deviceResult.resultList))
    log.info(str(deviceResult.duration))
    log.info(str(deviceResult.deviceName))

import unittest
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
parentdir = os.path.dirname(parentdir)
parentdir = os.path.dirname(parentdir)
sys.path.insert(0,parentdir)
from feddart.deviceSingle import DeviceSingle
from feddart.deviceHolder import DeviceHolder
from feddart.dartRuntime import DartRuntime
from feddart.specificDeviceTask import SpecificDeviceTask
TEST_MODE = True
ERROR_PROBABILITY = 0   
class TestDeviceSingle(unittest.TestCase):

    def setUp(self):
        server = "https://127.0.0.0.1:7777"
        client_key = "000"
        name1 = "device_one"
        name2 = "device_two"
        if TEST_MODE:
            ipAdress1 = "client1"
            ipAdress2 = "client2"
        else:
            ipAdress1 = "127.0.0.1"
            ipAdress2 = "127.0.0.1"
        self.dartRuntime = DartRuntime( server
                                      , client_key
                                      , TEST_MODE
                                      , ERROR_PROBABILITY
                                      )
        self.deviceOne = DeviceSingle( name = name1
                                     , ipAdress = ipAdress1
                                     , port = 2883
                                     , dartRuntime = self.dartRuntime
                                     , physicalName = None
                                     , hardwareConfig = None
                                     , taskDict = {}
                                     , initTask = None
                                     )
        self.deviceTwo = DeviceSingle( name = name2
                                     , ipAdress = ipAdress2
                                     , port = 2883
                                     , dartRuntime = self.dartRuntime
                                     , physicalName = None
                                     , hardwareConfig = None
                                     , taskDict = {}
                                     , initTask = None
                                     )
        
    def tearDown(self):
        pass

    def testAddDevice(self):
        "Add devices to deviceHolder. If deviceHolder is full throw an exception"
        maxSize = 3
        deviceHolder = DeviceHolder(maxSize)
        deviceHolder.addDevice(self.deviceOne, "hello_world", {"hello": "world"})
        deviceHolder.addDevice(self.deviceTwo, "hello_world", {"hello": "world"})
        name = "device_three"
        if TEST_MODE:
            ipAdress = "client3"
        else:
            ipAdress = "127.0.0.1"
        physicalName = None
        hardwareConfig = None
        taskDict = {}
        initTask = None
        port = 2883
        deviceThree = DeviceSingle( name = name
                                  , ipAdress = ipAdress
                                  , port = port
                                  , dartRuntime = self.dartRuntime
                                  , physicalName = physicalName
                                  , hardwareConfig = hardwareConfig
                                  , taskDict = taskDict
                                  , initTask = initTask
                                  )
        deviceHolder.addDevice(deviceThree, "hello_world", {"hello": "world"})
        self.assertEqual( ['device_one', 'device_two', 'device_three']
                        , deviceHolder.deviceNames
                        , msg = "Wrong names for devices"
                        )
        with self.assertRaises(Exception) as context:
            deviceHolder.addDevice(deviceThree, "hello_world", {"hello": "world"})
        self.assertTrue("DeviceHolder already full!" in str(context.exception))
    
    def testRemoveDevice(self):
        "Remove Device from deviceHolder"
        maxSize = 3
        deviceHolder = DeviceHolder(maxSize)
        deviceHolder.addDevice(self.deviceOne, "hello_world", {"hello": "world"})
        deviceHolder.addDevice(self.deviceTwo, "hello_world", {"hello": "world"})
        deviceHolder.removeDevice(self.deviceOne)
        self.assertEqual( ['device_two']
                        , deviceHolder.deviceNames
                        , msg = "Wrong names for devices"
                        )
    
    def testBroadCastTask(self):
        "Send the task simultaneously to multiple devices. The task must be added before to the device"
        taskName = "task_one"
        maxSize = 3
        parameterDict = {"param1": 5, "param2": 1}
        model = None
        hardwareRequirements = {}
        configFile = None
        task = SpecificDeviceTask( taskName
                                 , parameterDict
                                 , model
                                 , hardwareRequirements
                                 , "test" #filename
                                 , "test" #function
                                 , configFile
                                 )
        deviceHolder = DeviceHolder(maxSize)
        taskName = task.taskName 
        parameterDict = task.parameterDict
        deviceHolder.addDevice(self.deviceOne, taskName, parameterDict)
        deviceHolder.addDevice(self.deviceTwo, taskName, parameterDict)
        self.dartRuntime.generate_and_add_SingleDevice( self.deviceOne.name
                                        , self.deviceOne.ipAdress
                                        , self.deviceOne.port 
                                        , self.deviceOne.hardwareConfig
                                        , self.deviceOne.initTask
                                        )
        self.dartRuntime.generate_and_add_SingleDevice( self.deviceTwo.name
                                        , self.deviceTwo.ipAdress
                                        , self.deviceTwo.port 
                                        , self.deviceTwo.hardwareConfig
                                        , self.deviceTwo.initTask
                                        )
        deviceHolder.broadcastTask(task)
    
    def testStopTask(self):
        "Stop the task on server. Remove the task from the openTaskDict"
        taskName = "task_one"
        maxSize = 3
        parameterDict = {"param1": 5, "param2": 1}
        model = None
        hardwareRequirements = {}
        configFile = None
        task = SpecificDeviceTask( taskName
                                 , parameterDict
                                 , model
                                 , hardwareRequirements
                                 , "test" #filename
                                 , "test" #function
                                 , configFile
                                 )
        deviceHolder = DeviceHolder( maxSize
                                   )
        deviceHolder.addDevice(self.deviceOne, task.taskName, task.parameterDict)
        deviceHolder.addDevice(self.deviceTwo, task.taskName, task.parameterDict)
        self.dartRuntime.generate_and_add_SingleDevice( self.deviceOne.name
                                        , self.deviceOne.ipAdress
                                        , self.deviceOne.port 
                                        , self.deviceOne.hardwareConfig
                                        , self.deviceOne.initTask
                                        )
        self.dartRuntime.generate_and_add_SingleDevice( self.deviceTwo.name
                                        , self.deviceTwo.ipAdress
                                        , self.deviceTwo.port 
                                        , self.deviceTwo.hardwareConfig
                                        , self.deviceTwo.initTask
                                        )
        deviceHolder.broadcastTask(task)
        self.assertEqual( {'task_one': {'param1': 5, 'param2': 1}}
                        , self.deviceOne._openTaskDict
                        , msg = "Wrong entries for openTaskDict"
                        )
        deviceHolder.stopTask(task.taskName)
        self.assertEqual( {}
                        , self.deviceOne._openTaskDict
                        , msg = "Wrong entries for openTaskDict"
                        )
    
    def testGetFinishedTasks(self):
        "Get the results from already finished devices"
        taskName = "task_one"
        maxSize = 3
        parameterDict = {"param1": 5, "param2": 1}
        parameterDict2 = {"param1": 5, "param2": 4}
        model = None
        hardwareRequirements = {}
        configFile = None
        task = SpecificDeviceTask( taskName
                                 , parameterDict
                                 , model
                                 , hardwareRequirements
                                 , "test" #filename
                                 , "test" #function
                                 , configFile
                                 )
        deviceHolder = DeviceHolder(maxSize)
        self.dartRuntime.generate_and_add_SingleDevice( self.deviceOne.name
                                        , self.deviceOne.ipAdress
                                        , self.deviceOne.port 
                                        , self.deviceOne.hardwareConfig
                                        , self.deviceOne.initTask
                                        )
        self.dartRuntime.generate_and_add_SingleDevice( self.deviceTwo.name
                                        , self.deviceTwo.ipAdress
                                        , self.deviceTwo.port 
                                        , self.deviceTwo.hardwareConfig
                                        , self.deviceTwo.initTask
                                        )
        deviceHolder.addDevice(self.deviceOne, task.taskName, task.parameterDict)
        deviceHolder.addDevice(self.deviceTwo, task.taskName, parameterDict2)
        deviceHolder.broadcastTask(task)
        self.assertEqual( deviceHolder.get_finishedTasks(taskName)[0].resultDict
                        , {'result_0': 6 } 
                        , msg = "Wrong entries for finished tasks"
                        )
        self.assertEqual( deviceHolder.get_finishedTasks(taskName)[1].resultDict
                        , {'result_0': 9 } 
                        , msg = "Wrong entries for finished tasks"
                        )
        with self.assertRaises(Exception) as context:
            deviceHolder.get_finishedTasks("hello")
        self.assertTrue("No task with name" in str(context.exception))
    
    
    def testGetTaskStatus(self):
        "Get the task status ""in progress"" or ""finished"" "
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        maxSize = 3
        deviceHolder = DeviceHolder( maxSize
            
                                   )
        deviceHolder._deviceList = [ self.deviceOne, self.deviceTwo]
        taskResult = { 'duration': 5
                     , 'result': {'result_0': 10, 'result_1': None}
                     }
        self.deviceOne._openTaskDict = { taskName: taskParameter}
        self.deviceTwo._openTaskDict = { taskName: taskParameter}
        self.assertTrue( deviceHolder.devicesFinished(taskName) == False
                       , msg = "task shouldn't be finished"
                       )
        self.deviceOne._finishedTaskDict = { taskName: taskResult}
        self.deviceOne._openTaskDict = {}
        self.assertTrue( deviceHolder.devicesFinished(taskName) == False
                       , msg = "task shouldn't be finished"
                       )
        self.deviceTwo._finishedTaskDict = { taskName: taskResult}
        self.deviceTwo._openTaskDict = {}
        self.assertTrue( deviceHolder.devicesFinished(taskName) == True
                       , msg = "task should be finished"
                       )
    
    def testGetTaskProgress(self):
        " Get the number of already finished device and the amout of devices, where we have sent the task."
        " Get the task status ""in progress"" or ""finished"" "
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        maxSize = 3
        deviceHolder = DeviceHolder(maxSize)
        deviceHolder._deviceList = [ self.deviceOne, self.deviceTwo]
        taskResult = { 'duration': 5
                     , 'result': {'result_0': 10, 'result_1': None}
                     }
        self.deviceOne._openTaskDict = { taskName: taskParameter}
        self.deviceTwo._openTaskDict = { taskName: taskParameter}
        self.assertTrue( deviceHolder.get_taskProgress(taskName) == 0
                       , msg = "wrong task progress"
                       )
        self.deviceOne._finishedTaskDict = { taskName: taskResult}
        self.deviceOne._openTaskDict = {}
        self.deviceTwo._finishedTaskDict = { taskName: taskResult}
        self.deviceTwo._openTaskDict = {}
        self.assertTrue( deviceHolder.get_taskProgress(taskName) == 2
                       , msg = "wrong task progress"
                       )


if __name__ == '__main__':
    unittest.main(verbosity = 2)
import unittest
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentdir = os.path.dirname(parentdir)
parentdir = os.path.dirname(parentdir)
parentdir = os.path.dirname(parentdir)
print(parentdir)
sys.path.insert(0, parentdir) 
from feddart.deviceSingle import DeviceSingle
from feddart.dartRuntime import DartRuntime
from feddart.specificDeviceTask import SpecificDeviceTask
from feddart.initTask import InitTask

TEST_MODE = True
ERROR_PROBABILITY = 0

class TestDeviceSingle(unittest.TestCase):

    def setUp(self):
        server = "https://127.0.0.0.1:7777"
        client_key = "000"
        name = "device_one"
        if TEST_MODE:
            ipAdress = "client1"
        else:
            ipAdress = "127.0.0.1"
        self.dartRuntime = DartRuntime( server
                                      , client_key
                                      , TEST_MODE
                                      , ERROR_PROBABILITY
                                      )
        physicalName = None
        hardwareConfig = None
        taskDict = {}
        initTask = None
        port = 2883
        self.deviceSingle = DeviceSingle( name = name
                                        , ipAdress = ipAdress
                                        , port = port
                                        , dartRuntime = self.dartRuntime
                                        , physicalName = physicalName
                                        , hardwareConfig = hardwareConfig
                                        , taskDict = taskDict
                                        , initTask = initTask
                                        )
      
    def tearDown(self):
        pass
    
    def testInitTask(self):
        "Check if the init task is executed"
        taskName = "task_one"
        parameterDict = {"bool_string": "True"}
        model = None
        hardwareRequirements = {}
        configFile = None
        task = InitTask( parameterDict
                       , model
                       , hardwareRequirements
                       , "test" #filename
                       , "init" #function
                       , configFile
                       )
        self.assertTrue( self.deviceSingle.initialized == True
                       , msg = "Device should be initialized"
                       )
        self.deviceSingle._initialized = False
        self.deviceSingle.initTask = task
        self.deviceSingle.addTask(task.taskName,  task.parameterDict)
        self.dartRuntime.add_SingleDevice( self.deviceSingle)
        self.assertTrue( self.deviceSingle.initialized
                       , msg = "Device should be initialized"
                       )

    def testStartTask(self):
        "Check starting a task. A task must be added before we can start the task"
        taskName = "task_one"
        parameterDict = {"param1": 5, "param2": 3}
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
        self.dartRuntime.generate_and_add_SingleDevice( self.deviceSingle.name
                                        , self.deviceSingle.ipAdress
                                        , self.deviceSingle.port 
                                        , self.deviceSingle.hardwareConfig
                                        , self.deviceSingle.initTask
                                        )
        self.deviceSingle.addTask(task.taskName, task.parameterDict)
        self.deviceSingle.startTask(task)
        taskName = "task_two"
        task_two = SpecificDeviceTask( taskName
                                     , parameterDict
                                     , model
                                     , hardwareRequirements
                                     , "test" #filename
                                     , "test" #function
                                     , configFile
                                     )
        with self.assertRaises(Exception) as context:
            self.deviceSingle.startTask(task_two)
        self.assertTrue("Add the task" in str(context.exception))

    def testGetTaskResult(self):
        "Try to get results from valid and unvalid task names"
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        taskResult = { 'duration': 5
                     , 'result': {'result_0': 10, 'result_1': None}
                     }
        self.deviceSingle._addFinishedTask(taskName, taskResult)
        self.assertEqual( self.deviceSingle.get_taskResult("task_one")
                        , {'duration': 5, 'result': {'result_0': 10, 'result_1': None}}
                        , msg = "Wrong results for task!"
                        )
        with self.assertRaises(Exception) as context:
            self.deviceSingle.get_taskResult("hello")
        self.assertTrue("No task with name" in str(context.exception))
        self.assertEqual( self.deviceSingle.openTaskDict
                        , {}
                        , msg = "No open task!"
                        )
        self.assertEqual( self.deviceSingle.finishedTaskDict
                        , { 'task_one': {'duration': 5, 'result': {'result_0': 10, 'result_1': None}}}
                        , msg = "wrong finished tasks!"
                        )

    def testChangefromOpentoFinishedTask(self):
        "Check if a finished task is removed from the openTaskDict"
        taskName = "task_one"
        parameterDict = {"param1": 5, "param2": 3}
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
        self.dartRuntime.generate_and_add_SingleDevice( self.deviceSingle.name
                                        , self.deviceSingle.ipAdress
                                        , self.deviceSingle.port 
                                        , self.deviceSingle.hardwareConfig
                                        , self.deviceSingle.initTask
                                        )
        self.deviceSingle.addTask(task.taskName, task.parameterDict)
        self.deviceSingle.startTask(task)
        self.deviceSingle.get_taskResult(taskName)
        self.assertEqual( self.deviceSingle.openTaskDict
                        , {}
                        , msg = "No open task!"
                        )
        
       
    def testHasTaskResult(self):
        "Check the results from valid and unvalid task names"
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        self.deviceSingle.addTask(taskName, taskParameter)
        taskResult = { 'duration': 5
                     , 'result': {'result_0': 10, 'result_1': None}
                     }
        self.assertTrue( self.deviceSingle.has_taskResult("task_one") == False
                       , msg = "There should be a result from the task!"
                       )
        self.deviceSingle._addFinishedTask(taskName, taskResult)
        self.assertTrue( self.deviceSingle.has_taskResult("task_one") == True
                       , msg = "There should be a result from the task!"
                       )
        with self.assertRaises(Exception) as context:
            self.deviceSingle.has_taskResult("hello")
        self.assertTrue("No task with name" in str(context.exception))
    
        
if __name__ == '__main__':
    unittest.main(verbosity = 2)
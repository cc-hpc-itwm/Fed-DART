import unittest
import os
import sys
from DummyRuntime import DummyDARTRuntime
d = os.path.dirname(os.getcwd())
sys.path.append(d + '/src')
from deviceSingle import DeviceSingle
from deviceHolder import DeviceHolder

class DummyTask:

    def __init__( self
                , taskName
                , filePath
                , executeFunction
                ):
        self.taskName = taskName
        self.filePath = filePath
        self.executeFunction = executeFunction

   
class TestDeviceSingle(unittest.TestCase):

    def setUp(self):
        boolean_random = False
        self.dartRuntime = DummyDARTRuntime(boolean_random)
        name = "device_one"
        ipAdress = "123.456"
        physicalName = None
        hardwareConfig = None
        taskDict = {}
        self.deviceOne = DeviceSingle( name
                                     , ipAdress
                                     , self.dartRuntime
                                     , physicalName
                                     , hardwareConfig
                                     , taskDict
                                     )
        name = "device_two"
        ipAdress = "123.457"
        physicalName = None
        hardwareConfig = None
        taskDict = {}
        self.deviceTwo = DeviceSingle( name
                                     , ipAdress
                                     , self.dartRuntime
                                     , physicalName
                                     , hardwareConfig
                                     , taskDict
                                     )
       
    def tearDown(self):
        pass

    def testAddDevice(self):
        """Add devices to deviceHolder. If deviceHolder is full throw an exception"""
        maxSize = 3
        deviceHolder = DeviceHolder( maxSize
                                   , [ self.deviceOne
                                     , self.deviceTwo
                                     ]
                                   )
        name = "device_three"
        ipAdress = "123.458"
        physicalName = None
        hardwareConfig = None
        taskDict = {}
        deviceThree = DeviceSingle( name
                                  , ipAdress
                                  , self.dartRuntime
                                  , physicalName
                                  , hardwareConfig
                                  , taskDict
                                  )
        deviceHolder.addDevice(deviceThree)
        self.assertEqual( ['device_one', 'device_two', 'device_three']
                        , deviceHolder.deviceNames
                        , msg = "Wrong names for devices"
                        )
        with self.assertRaises(Exception) as context:
            deviceHolder.addDevice(deviceThree)
        self.assertTrue("DeviceHolder already full!" in str(context.exception))

    def testRemoveDevice(self):
        """Remove Device from deviceHolder"""
        maxSize = 3
        deviceHolder = DeviceHolder( maxSize
                                   , [ self.deviceOne
                                     , self.deviceTwo
                                     ]
                                   )
        deviceHolder.removeDevice(self.deviceOne)
        self.assertEqual( ['device_two']
                        , deviceHolder.deviceNames
                        , msg = "Wrong names for devices"
                        )
        
    def testBroadCastTask(self):
        """ Send the task simultaneously to multiple devices.
            The task must be added before to the device
        """
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        task = DummyTask(taskName, "C/hello", "hello_world")
        maxSize = 3
        deviceHolder = DeviceHolder( maxSize
                                   , [ self.deviceOne
                                     , self.deviceTwo
                                     ]
                                   )
        with self.assertRaises(Exception) as context:
            deviceHolder.broadcastTask(task)
        self.assertTrue("Add the task" in str(context.exception))
        self.deviceOne.addTask(taskName, taskParameter)
        self.deviceTwo.addTask(taskName, taskParameter)
        deviceHolder.broadcastTask(task)

    def testStopTask(self):
        """Stop the task on server. Remove the task from the openTaskDict"""
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        task = DummyTask(taskName, "C/hello", "hello_world")
        maxSize = 3
        deviceHolder = DeviceHolder( maxSize
                                   , [ self.deviceOne
                                     , self.deviceTwo
                                     ]
                                   )
        self.deviceOne.addTask(taskName, taskParameter)
        self.deviceTwo.addTask(taskName, taskParameter)
        deviceHolder.broadcastTask(task)
        self.assertEqual( {'task_one': {'param1': 'hello', 'param2': 'world'}}
                        , self.deviceOne._openTaskDict
                        , msg = "Wrong entries for openTaskDict"
                        )
        deviceHolder.stopTask(task)
        self.assertEqual( {}
                        , self.deviceOne._openTaskDict
                        , msg = "Wrong entries for openTaskDict"
                        )

    def testGetFinishedTasks(self):
        """Get the results from already finished devices"""
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        task = DummyTask(taskName, "C/hello", "hello_world")
        maxSize = 3
        deviceHolder = DeviceHolder( maxSize
                                   , [ self.deviceOne
                                     , self.deviceTwo
                                     ]
                                   )
        taskResult = { 'duration': 5
                     , 'result': {'result_0': 10, 'result_1': None}
                     }
        self.deviceOne.addTask(taskName, taskParameter)
        self.deviceTwo.addTask(taskName, taskParameter)
        deviceHolder.broadcastTask(task)
        self.assertEqual( { 'device_one': {'duration': 5, 'result': {'result_0': 1, 'result_1': 'hello'}}
                          , 'device_two': {'duration': 5, 'result': {'result_0': 1, 'result_1': 'hello'}}
                          }
                        , deviceHolder.get_finishedTasks(taskName)
                        , msg = "Wrong entries for finished tasks"
                        )
        with self.assertRaises(Exception) as context:
            deviceHolder.get_finishedTasks("hello")
        self.assertTrue("No task with name" in str(context.exception))
        
    def testGetTaskStatus(self):
        """Get the task status "in progress" or "finished" """
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        task = DummyTask(taskName, "C/hello", "hello_world")
        maxSize = 3
        deviceHolder = DeviceHolder( maxSize
                                   , [ self.deviceOne
                                     , self.deviceTwo
                                     ]
                                   )
        taskResult = { 'duration': 5
                     , 'result': {'result_0': 10, 'result_1': None}
                     }
        self.deviceOne.addTask(taskName, taskParameter)
        self.deviceTwo.addTask(taskName, taskParameter)
        deviceHolder.broadcastTask(task)
        self.dartRuntime.get_finishedResult = False
        self.assertTrue( deviceHolder.get_taskStatus(taskName) == "in progress"
                       , msg = "task should be in progress"
                       )
        self.dartRuntime.get_finishedResult = True
        self.assertTrue( deviceHolder.get_taskStatus(taskName) == "finished"
                       , msg = "task should be finished"
                       )

    def testGetTaskProgress(self):
        """ Get the number of already finished device and the amout of devices, where we
            have sent the task.
        """
        """Get the task status "in progress" or "finished" """
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        task = DummyTask(taskName, "C/hello", "hello_world")
        maxSize = 3
        deviceHolder = DeviceHolder( maxSize
                                   , [ self.deviceOne
                                     , self.deviceTwo
                                     ]
                                   )
        taskResult = { 'duration': 5
                     , 'result': {'result_0': 10, 'result_1': None}
                     }
        self.deviceOne.addTask(taskName, taskParameter)
        self.deviceTwo.addTask(taskName, taskParameter)
        deviceHolder.broadcastTask(task)
        self.dartRuntime.get_finishedResult = False
        self.assertTrue( deviceHolder.get_taskProgress(taskName) == (0, 2)
                       , msg = "wrong task progress"
                       )
        self.dartRuntime.get_finishedResult = True
        self.assertTrue( deviceHolder.get_taskProgress(taskName) == (2, 2)
                       , msg = "wrong task progress"
                       )


if __name__ == '__main__':
    unittest.main(verbosity = 2)
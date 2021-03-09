import unittest
import os
import sys
from DummyRuntime import DummyDARTRuntime
d = os.path.dirname(os.getcwd())
sys.path.append(d + '/src')
from deviceSingle import DeviceSingle

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
        name = "device_one"
        ipAdress = "123.456"
        dartRuntime = DummyDARTRuntime(boolean_random)
        physicalName = None
        hardwareConfig = None
        taskDict = {}
        self.deviceSingle = DeviceSingle( name
                                        , ipAdress
                                        , dartRuntime
                                        , physicalName
                                        , hardwareConfig
                                        , taskDict
                                        )
        
    def tearDown(self):
        pass

    def testAddTask(self):
        """Add tasks to openTaskDict. If task is already existing through an exception"""
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        self.deviceSingle.addTask(taskName, taskParameter)
        self.assertEqual( self.deviceSingle.openTaskDict
                        , {'task_one': {'param1': 'hello', 'param2': 'world'}}
                        , msg = "Wrong dict entries for openTaskDict"
                        )
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        with self.assertRaises(Exception) as context:
            self.deviceSingle.addTask(taskName, taskParameter)
        self.assertTrue("already in openTaskDict!" in str(context.exception))
        taskName = "task_two"
        taskParameter = {"param1": "hello", "param2": "world"}
        self.deviceSingle.addTask(taskName, taskParameter)
        self.assertEqual( self.deviceSingle.openTaskDict
                        , { 'task_one': {'param1': 'hello', 'param2': 'world'}
                          , 'task_two': {'param1': 'hello', 'param2': 'world'}
                          }
                        , msg = "Wrong dict entries for openTaskDict"
                        )

    def testAddFinishedTask(self):
        """Add tasks to finishedTaskDict. If task is already existing through an exception"""
        taskName = "task_one"
        taskResult = { 'duration': 5
                     , 'result': {'result_0': 10, 'result_1': None}
                     }
        self.deviceSingle._addFinishedTask(taskName, taskResult)
        self.assertEqual( self.deviceSingle.finishedTaskDict
                        , {'task_one': taskResult}
                        , msg = "Wrong dict entries for finishedTaskDict"
                        )
        taskName = "task_one"
        with self.assertRaises(Exception) as context:
            self.deviceSingle._addFinishedTask(taskName, taskResult)
        self.assertTrue("already in finishedTaskDict!" in str(context.exception))
        taskName = "task_two"
        self.deviceSingle._addFinishedTask(taskName, taskResult)
        self.assertEqual( self.deviceSingle.finishedTaskDict
                        , { 'task_one': taskResult
                          , 'task_two': taskResult
                          }
                        , msg = "Wrong dict entries for finishedTaskDict"
                        )

    def testisOpenTask(self):
        """Check if taskName is in openTaskDict"""
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        self.deviceSingle.addTask(taskName, taskParameter)
        self.assertTrue( self.deviceSingle.isOpenTask("task_one") == True
                       , msg = "Task should be an open task"
                       )
        self.assertTrue( self.deviceSingle.isOpenTask("task_two") == False
                       , msg = "Task should be not an open task"
                       )

    def testRemoveOpenTask(self):
        """Try to remove tasks from openTaskDict"""
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        self.deviceSingle.addTask(taskName, taskParameter)
        taskName = "task_two"
        self.deviceSingle.addTask(taskName, taskParameter)
        self.deviceSingle.removeOpenTask("task_one")
        self.assertTrue( self.deviceSingle.isOpenTask("task_one") == False
                       , msg = "Task should not be an open task"
                       )
        self.assertEqual( self.deviceSingle.openTaskDict
                        , {'task_two': {'param1': 'hello', 'param2': 'world'}}
                        , msg = "Wrong dict entries for openTaskDict"
                        )

    def testGetOpenTaskParameter(self):
        """Get the parameter of an open task"""
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        self.deviceSingle.addTask(taskName, taskParameter)
        self.assertEqual( self.deviceSingle.getOpenTaskParameter("task_one")
                        , {'param1': 'hello', 'param2': 'world'}
                        , msg = "Wrong parameter for task!"
                        )
        with self.assertRaises(Exception) as context:
            self.deviceSingle.getOpenTaskParameter("task_twp")
        self.assertTrue("Open task with name" in str(context.exception))

    def testGetFinishedTaskResult(self):
        """Get the result of a finished task"""
        taskName = "task_one"
        taskResult = { 'duration': 5
                     , 'result': {'result_0': 10, 'result_1': None}
                     }
        self.deviceSingle._addFinishedTask(taskName, taskResult)
        self.assertEqual( self.deviceSingle._getFinishedTaskResult("task_one")
                        , taskResult
                        , msg = "Wrong results for task!"
                        )
        with self.assertRaises(Exception) as context:
            self.deviceSingle._getFinishedTaskResult("task_two")
        self.assertTrue("Finished task with name" in str(context.exception))

    def testHasTask(self):
        """Check if the device has a task with such an name in open or finished tasks"""
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        self.deviceSingle.addTask(taskName, taskParameter)
        taskName = "task_two"
        taskResult = { 'duration': 5
                     , 'result': {'result_0': 10, 'result_1': None}
                     }
        self.deviceSingle._addFinishedTask(taskName, taskResult)
        self.assertTrue( self.deviceSingle.hasTask("task_one") == True
                       , msg = "Device should have task"
                       )
        self.assertTrue( self.deviceSingle.hasTask("task_two") == True
                       , msg = "Device should have task"
                       )
        self.assertTrue( self.deviceSingle.hasTask("task_three") == False
                       , msg = "Device should not have task"
                       )

    def testStartTask(self):
        """Check starting a task. A task must be added before we can start the task"""
        boolean_random = True
        name = "device_one"
        ipAdress = "123.456"
        dartRuntime = DummyDARTRuntime(boolean_random)
        physicalName = None
        hardwareConfig = None
        taskDict = {}
        deviceSingle = DeviceSingle( name
                                   , ipAdress
                                   , dartRuntime
                                   , physicalName
                                   , hardwareConfig
                                   , taskDict
                                   )
        task = DummyTask("task_one", "C/hello", "hello_world")
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        deviceSingle.addTask(taskName, taskParameter)
        deviceSingle.startTask(task)
        task_two = DummyTask("task_two", "C/hello", "hello_world")
        with self.assertRaises(Exception) as context:
            self.deviceSingle.startTask(task_two)
        self.assertTrue("Add the task" in str(context.exception))

    def testGetTaskResult(self):
        """Try to get results from valid and unvalid task names"""
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        self.deviceSingle.addTask(taskName, taskParameter)
        taskName = "task_two"
        taskResult = { 'duration': 5
                     , 'result': {'result_0': 10, 'result_1': None}
                     }
        self.deviceSingle._addFinishedTask(taskName, taskResult)
        self.assertEqual( self.deviceSingle.get_taskResult("task_one")
                        , {'duration': 5, 'result': {'result_0': 1, 'result_1': 'hello'}}
                        , msg = "Wrong results for task!"
                        )
        self.assertEqual( self.deviceSingle.get_taskResult("task_two")
                        , taskResult
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
                        , { 'task_two': {'duration': 5, 'result': {'result_0': 10, 'result_1': None}}
                          , 'task_one': {'duration': 5, 'result': {'result_0': 1, 'result_1': 'hello'}}
                          }
                        , msg = "wrong finished tasks!"
                        )
        
    def testHasTaskResult(self):
        """Check the results from valid and unvalid task names"""
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        self.deviceSingle.addTask(taskName, taskParameter)
        taskName = "task_two"
        taskResult = { 'duration': 5
                     , 'result': {'result_0': 10, 'result_1': None}
                     }
        self.deviceSingle._addFinishedTask(taskName, taskResult)
        self.assertTrue( self.deviceSingle.has_taskResult("task_one") == True
                       , msg = "There should be a result from the task!"
                       )
        self.assertTrue( self.deviceSingle.has_taskResult("task_two") == True
                       , msg = "There should be a result from the task!"
                       )
        with self.assertRaises(Exception) as context:
            self.deviceSingle.has_taskResult("hello")
        self.assertTrue("No task with name" in str(context.exception))
        
        
if __name__ == '__main__':
    unittest.main(verbosity = 2)
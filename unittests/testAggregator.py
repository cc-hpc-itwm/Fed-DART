import unittest
import os
import sys
sys.path.append('../feddart')
from DummyRuntime import DummyDARTRuntime
from deviceAggregator import DeviceAggregator
from deviceHolder import DeviceHolder
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


class TestDeviceAggregator(unittest.TestCase):

    def setUp(self):
        boolean_random = False
        name = "device_one"
        ipAdress = "123.456"
        self.dartRuntime = DummyDARTRuntime(boolean_random)
        physicalName = None
        hardwareConfig = None
        taskDict = {}
        dummytask = DummyTask("task_dummy", "C\Hello", "hello world")
        self.deviceSingleOne = DeviceSingle( name
                                           , ipAdress
                                           , self.dartRuntime
                                           , physicalName
                                           , hardwareConfig
                                           , {}
                                           )
        
        name = "device_two"
        self.deviceSingleTwo = DeviceSingle( name
                                           , ipAdress
                                           , self.dartRuntime
                                           , physicalName
                                           , hardwareConfig
                                           , {}
                                           )
        self.deviceSingleOne.addTask("task_dummy", {})
        self.deviceSingleTwo.addTask("task_dummy",{})
        maxSize = 3
        deviceHolder = DeviceHolder( maxSize
                                   , [ self.deviceSingleOne
                                     , self.deviceSingleTwo
                                     ]
                                   )
        DeviceAggregator._maxNumDeviceHolder = 2
        DeviceAggregator._maxNumChildAggregators = 2
        self.deviceAggregator = DeviceAggregator( task = dummytask
                                                , deviceHolders = [deviceHolder]
                                                )

    def tearDown(self):
        pass

    def testDetermineTaskStatus(self):
        case_one = ["in progress", "in progress"]
        case_two = ["finished", "finished"]
        case_three = ["finished", "in progress"]
        self.assertTrue( self.deviceAggregator._determine_taskStatus(case_one) == "in progress"
                       , msg = "wrong task status!"
                       )
        self.assertTrue( self.deviceAggregator._determine_taskStatus(case_two) == "finished"
                       , msg = "wrong task status!"
                       )
        self.assertTrue( self.deviceAggregator._determine_taskStatus(case_three) == "in progress"
                       , msg = "wrong task status!"
                       )

    def testGetTaskStatus(self):
        self.assertTrue( self.deviceAggregator.get_TaskStatus() == "finished"
                       , msg = "wrong task status!"
                       )
        self.dartRuntime.get_finishedResult = False
        self.assertTrue( self.deviceAggregator.get_TaskStatus() == "in progress"
                       , msg = "wrong task status!"
                       )
        

if __name__ == '__main__':
    unittest.main(verbosity = 2)
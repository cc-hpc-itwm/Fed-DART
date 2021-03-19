import unittest
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from feddart.deviceAggregator import DeviceAggregator
from feddart.deviceHolder import DeviceHolder
from feddart.deviceSingle import DeviceSingle
from feddart.dartRuntime import DartRuntime
from feddart.specificDeviceTask import SpecificDeviceTask
TEST_MODE = True
ERROR_PROBABILITY = 0   
class TestDeviceAggregator(unittest.TestCase):

    def setUp(self):
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
        DeviceAggregator._maxNumDeviceHolder = 2
        DeviceAggregator._maxNumChildAggregators = 2
        self.deviceAggregator = DeviceAggregator( task = task
                                                , maxSizeDeviceHolder = 1
                                                , logServer = None
                                                )
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

    def testNumberDeviceHolders(self):
        "Check if deviceHolders are sucessfully instantiated"
        self.assertTrue( len(self.deviceAggregator.deviceHolders) == 2
                        , msg = "wrong number of deviceHolder"
                       )
    
    def testAddSingleDevice(self):
        "Add devices to aggregator and check amount, instance type and repetition"
        #self.deviceAggregator.addSingleDevice(self.deviceOne)
        self.deviceAggregator.addSingleDevice(self.deviceTwo)
        with self.assertRaises(Exception) as context:
           self.deviceAggregator.addSingleDevice(self.deviceTwo)
        self.assertTrue("Device is already" in str(context.exception))
        self.deviceAggregator.addSingleDevice(self.deviceOne)
        with self.assertRaises(Exception) as context:
            self.deviceAggregator.addSingleDevice(["hello"])
        self.assertTrue("Device is not an instance" in str(context.exception))
        deviceThree = DeviceSingle( name = "hello"
                                  , ipAdress = 123
                                  , port = 2883
                                  )
        with self.assertRaises(Exception) as context:
            self.deviceAggregator.addSingleDevice(deviceThree)
        self.assertTrue("Device holders are completly full" in str(context.exception))
        
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
        "Check the task status"
        taskName = "task_one"
        taskParameter = {"param1": "hello", "param2": "world"}
        taskResult = { 'duration': 5
                     , 'result': {'result_0': 10, 'result_1': None}
                     }
        self.deviceAggregator.addSingleDevice(self.deviceOne)
        self.deviceAggregator.addSingleDevice(self.deviceTwo)
        self.deviceOne._openTaskDict = { taskName: taskParameter}
        self.deviceTwo._openTaskDict = { taskName: taskParameter}
        self.assertTrue( self.deviceAggregator.get_TaskStatus() == "in progress"
                       , msg = "wrong task status!"
                       )
        self.deviceOne._finishedTaskDict = { taskName: taskResult}
        self.deviceOne._openTaskDict = {}
        self.assertTrue( self.deviceAggregator.get_TaskStatus() == "in progress"
                       , msg = "wrong task status!"
                       )
        self.deviceTwo._finishedTaskDict = { taskName: taskResult}
        self.deviceTwo._openTaskDict = {}
        self.assertTrue( self.deviceAggregator.get_TaskStatus() == "finished"
                       , msg = "wrong task status!"
                       )
        



if __name__ == '__main__':
    unittest.main(verbosity = 2)
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
        parameterDict = { "device_one": {"param1": 5, "param2": 1}
                        , "device_two": {"param1": 5, "param2": 1}
                        }
        model = None
        hardwareRequirements = {}
        configFile = None
        self.task = SpecificDeviceTask( taskName
                                      , parameterDict
                                      , model
                                      , hardwareRequirements
                                      , "test" #filename
                                      , "test" #function
                                      , configFile
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
        self.dartRuntime.addSingleDevice( self.deviceOne.name
                                        , self.deviceOne.ipAdress
                                        , self.deviceOne.port 
                                        , self.deviceOne.hardwareConfig
                                        , self.deviceOne.initTask
                                        )
        self.dartRuntime.addSingleDevice( self.deviceTwo.name
                                        , self.deviceTwo.ipAdress
                                        , self.deviceTwo.port 
                                        , self.deviceTwo.hardwareConfig
                                        , self.deviceTwo.initTask
                                        )
        
    def tearDown(self):
        pass
    
    def testNumberDeviceHolders(self):
        "Check if deviceHolders are sucessfully instantiated "
        maxSizeDeviceHolder = 1
        maxNumDeviceHolder = 2
        maxNumChildAggregators = 2
        deviceAggregator = DeviceAggregator( [ self.deviceOne
                                             , self.deviceTwo
                                             ]
                                            , self.task
                                            , maxSizeDeviceHolder = maxSizeDeviceHolder
                                            , maxNumDeviceHolder  = maxNumDeviceHolder
                                            , maxNumChildAggregators = maxNumChildAggregators
                                            , logServer = None
                                            )
        self.assertTrue( len(deviceAggregator.deviceHolders) == 2
                       , msg = "wrong number of deviceHolder"
                       )

    def testNumberDeviceHoldersWithChildAggrators(self):
        "Check if deviceHolders are sucessfully instantiated for child aggregators"
        maxSizeDeviceHolder = 1
        maxNumDeviceHolder = 1
        maxNumChildAggregators = 2
        deviceAggregator = DeviceAggregator( [ self.deviceOne
                                             , self.deviceTwo
                                             ]
                                            , self.task
                                            , maxSizeDeviceHolder = maxSizeDeviceHolder
                                            , maxNumDeviceHolder  = maxNumDeviceHolder
                                            , maxNumChildAggregators = maxNumChildAggregators
                                            , logServer = None
                                            )
        self.assertTrue( len(deviceAggregator.deviceHolders) == 0
                       , msg = "wrong number of deviceHolder"
                       )
        self.assertTrue( len(deviceAggregator.childAggregators) == 2
                       , msg = "wrong number of child aggregators"
                       )

    def testisTaskFinished(self):
        "Check if task is finished"
        maxSizeDeviceHolder = 1
        maxNumDeviceHolder = 2
        maxNumChildAggregators = 2
        deviceAggregator = DeviceAggregator( [ self.deviceOne
                                             , self.deviceTwo
                                             ]
                                            , self.task
                                            , maxSizeDeviceHolder = maxSizeDeviceHolder
                                            , maxNumDeviceHolder  = maxNumDeviceHolder
                                            , maxNumChildAggregators = maxNumChildAggregators
                                            , logServer = None
                                            )
        self.assertTrue( deviceAggregator.isTaskFinished() == False
                       , msg = "task shouldn't be finished"
                       )
        deviceAggregator.sendTask()
        self.assertTrue( deviceAggregator.isTaskFinished() == True
                       , msg = "task should be finished"
                       )

    def testisTaskFinishedWithChildAggrators(self):
        "Check if task is finished with child aggregators"
        maxSizeDeviceHolder = 1
        maxNumDeviceHolder = 1
        maxNumChildAggregators = 2
        deviceAggregator = DeviceAggregator( [ self.deviceOne
                                             , self.deviceTwo
                                             ]
                                            , self.task
                                            , maxSizeDeviceHolder = maxSizeDeviceHolder
                                            , maxNumDeviceHolder  = maxNumDeviceHolder
                                            , maxNumChildAggregators = maxNumChildAggregators
                                            , logServer = None
                                            )
        self.assertTrue( deviceAggregator.isTaskFinished() == False
                       , msg = "task shouldn't be finished"
                       )
        deviceAggregator.sendTask()
        self.assertTrue( deviceAggregator.isTaskFinished() == True
                       , msg = "task should be finished"
                       )

    def testRequestAggregation(self):
        "Get the result of the task"
        maxSizeDeviceHolder = 1
        maxNumDeviceHolder = 2
        maxNumChildAggregators = 2
        deviceAggregator = DeviceAggregator( [ self.deviceOne
                                             , self.deviceTwo
                                             ]
                                            , self.task
                                            , maxSizeDeviceHolder = maxSizeDeviceHolder
                                            , maxNumDeviceHolder  = maxNumDeviceHolder
                                            , maxNumChildAggregators = maxNumChildAggregators
                                            , logServer = None
                                            )
        self.assertTrue( len(deviceAggregator.requestAggregation()) == 0
                       , msg = "there is no result atm available"
                       )
        deviceAggregator.sendTask()
        self.assertTrue( len(deviceAggregator.requestAggregation()) == 2
                       , msg = "each device should return a result"
                       )

    def testRequestAggregationWithChildAggrators(self):
        "Get the result of the task with child aggregators"
        maxSizeDeviceHolder = 1
        maxNumDeviceHolder = 1
        maxNumChildAggregators = 2
        deviceAggregator = DeviceAggregator( [ self.deviceOne
                                             , self.deviceTwo
                                             ]
                                            , self.task
                                            , maxSizeDeviceHolder = maxSizeDeviceHolder
                                            , maxNumDeviceHolder  = maxNumDeviceHolder
                                            , maxNumChildAggregators = maxNumChildAggregators
                                            , logServer = None
                                            )
        self.assertTrue( len(deviceAggregator.requestAggregation()) == 0
                       , msg = "there is no result atm available"
                       )
        deviceAggregator.sendTask()
        self.assertTrue( len(deviceAggregator.requestAggregation()) == 2
                       , msg = "each device should return a result"
                       )
    

if __name__ == '__main__':
    unittest.main(verbosity = 2)
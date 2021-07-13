from feddart.dartRuntime import DartRuntime
from feddart.defaultTask import DefaultTask
from feddart.specificDeviceTask import SpecificDeviceTask
from feddart.initTask import InitTask
import json
import time

from feddart.logger import logger



class WorkflowManager:
    
    TASK_STATUS_IN_PROGRESS = "in progess"
    TASK_STATUS_IN_QUEUE = "in queue"
    TASK_STATUS_FINISHED = "finished"

    def __init__( self
                , testMode = False
                , errorProbability = 0
                , maxSizeDeviceHolder = 10
                , maximalNumberOpenJobs = 10
                ):
        """!
        @param maxSizeDeviceHolder maximal size for deviceHolders

        @todo: can runtime and maxSizeDeviceHolder moved to selector ?
        Or first create selector and than add runtime to that ? better
        if we have multiple server ?
        """

        self._runtime = None
        self._selector = None
        self._maxSizeDeviceHolder = maxSizeDeviceHolder
        self._maximalNumberOpenJobs = maximalNumberOpenJobs
        self._initTask = None
        self._testMode = testMode
        self._errorProbability = errorProbability
        self.logger = logger(__name__)
        self.logger.info('Workflow manager initiated')

    @property
    def maxSizeDeviceHolder(self):
        self.logger.debug("_maxSizeDeviceHolder " + str(self._maxSizeDeviceHolder))
        return self._maxSizeDeviceHolder
    
    @property 
    def runtime(self):
        return self._runtime

    @property
    def selector(self):
        return self._selector

    @property
    def maximalNumberOpenJobs(self):
        self.logger.debug("_maximalNumberOpenJobs " + str(self._maximalNumberOpenJobs))
        return self._maximalNumberOpenJobs
        
    def startFedDART( self
                    , runtimeFile = None
                    , deviceFile = None
                    , maximal_numberDevices = -1
                    ):
        """!
        @param deviceFile path to already known devices
        @todo specify deviceFile
        """
        self.logger.debug('start feddart server, config:' 
                            + "runtimeFile " + runtimeFile 
                            + ",deviceFile " + deviceFile 
                            + ",maximal_numberDevices " + str(maximal_numberDevices))

        with open(runtimeFile) as runtimeFile:
            runtime = json.load(runtimeFile)
            self._runtime = DartRuntime( runtime["server"]
                                       , runtime["client_key"]
                                       , self._testMode
                                       , self._errorProbability
                                       , maximal_numberDevices
                                       , self.maximalNumberOpenJobs
                                       )
            self._selector = self.runtime.instantiateSelector(self._maxSizeDeviceHolder)
        if self._initTask:
            self.selector.initTask = self._initTask
        if deviceFile is not None:
            with open(deviceFile) as deviceFile:
                deviceFile = json.load(deviceFile)
                for deviceName in deviceFile:
                    self.selector.addSingleDevice( deviceName
                                                 , deviceFile[deviceName]["ipAdress"]
                                                 , deviceFile[deviceName]["port"]
                                                 , deviceFile[deviceName]["hardware_config"]
                                                 )

    def removeDevice(self, deviceName):
        self.logger.debug("remove device. deviceName " + str(deviceName))
        self.selector.removeDevice(deviceName)
        
    def _sendTaskRequest(self, task):
        """!
        Send the task to the selecor. Based on hardware requirements and needed devices
        the selector decide accept or reject the task
        @param task instance of task
        """
        self.logger.debug("requestTaskAcceptance")
        return self.selector.requestTaskAcceptance(task)
        
    def getTaskStatus(self, taskName):
        """!
        Ask the selector for the aggregator of the task. 
        The aggregator knows the status of the task
        @param taskName name of the task

        @return string "in queue", "in progress" or "finished"
        """
        self.logger.debug("getTaskStatus. task " + str(taskName))
        if self.selector.taskInQueue(taskName):
            return self.TASK_STATUS_IN_QUEUE
        else:
            aggregator = self.selector.get_aggregator_of_task(taskName)
            taskFinished = aggregator.isTaskFinished()
            if taskFinished:
                self.logger.debug("TaskStatus " + str(self.TASK_STATUS_FINISHED))
                return self.TASK_STATUS_FINISHED
            else:
                self.logger.debug("TaskStatus " + str(self.TASK_STATUS_IN_PROGRESS))
                return self.TASK_STATUS_IN_PROGRESS

    def getServerInformation(self):
        self.logger.debug("get_ServerInformation")
        return self.selector.runtime.get_ServerInformation()

    def getTaskResult( self
                     , taskName
                     ):
        """!
        Get the aggregator of the task and trigger the 
        colllection of the results

        @param taskName name of the task
        @param boolean_aggregate option to directly aggregate the result (e.g federated averaging)

        @return taskResult aggregated result or collected results from devices
        """
        self.logger.debug("getTaskResult. taskName " + str(taskName))
        if self.selector.taskInQueue(taskName):
            return []
        else:
            aggregator = self.selector.get_aggregator_of_task(taskName)
            taskResult = aggregator.requestAggregation()
            if self.getTaskStatus(taskName) == self.TASK_STATUS_FINISHED:
                self.stopTask(taskName)
            return taskResult 

    def getAllDeviceNames(self):
        """!
        Return all known devices with name to the end user

        @return: list of device names
        """
        self.logger.debug("getAllDeviceNames. deviceNames " + str(self.selector.deviceNames))
        return self.selector.deviceNames

    def stopTask(self, taskName):
        """!
        The task with the associated aggregator and deviceHolders is destroyed
        Should be done, when the task isn't needed anymore.
        @todo: add it as option to get_TaskResult ?!
        """
        self.logger.debug("stopTask. taskName " + str(taskName))
        if self.selector.taskInQueue(taskName):
            self.selector.deleteTaskInQueue(taskName)
        else:
            self.selector.deleteAggregatorAndTask(taskName)
            
    def stopFedDART(self):
        self.logger.debug("stopFedDART")
        self.runtime.stopRuntime()
    
    def createInitTask( self
                      , parameterDict = {}
                      , model = None
                      , hardwareRequirements = {}
                      , filePath = None
                      , executeFunction = None
                      , configFile = None
                      ):
        self.logger.debug("createInitTask. " + 
                    ",parameterDict " + str(parameterDict) + 
                    ",model " + str(model) + 
                    ",hardwareRequirements " + str(hardwareRequirements) + 
                    ",filePath " + str(filePath) + 
                    ",executeFunction " + str(executeFunction) + 
                    ",configFile " + str(configFile))
        task = InitTask( parameterDict
                       , model
                       , hardwareRequirements
                       , filePath
                       , executeFunction
                       , configFile
                       ) 
        self._initTask = task

    def startTask( self
                 , taskType = 0
                 , taskName = None
                 , parameterDict = {}
                 , model = None
                 , hardwareRequirements = {}
                 , filePath = None
                 , executeFunction = None
                 , configFile = None
                 , priority = False
                 , numDevices = -1
                 ):
        """!
        @param executeFunction name of function, which should be executed in filePath
        """
        self.logger.debug("startTask. taskName " + taskName + 
                    ",parameterDict " + str(parameterDict) + 
                    ",model " + str(model) + 
                    ",hardwareRequirements " + str(hardwareRequirements) + 
                    ",filePath " + str(filePath) + 
                    ",executeFunction " + str(executeFunction) + 
                    ",configFile " + str(configFile) + 
                    ",numDevices " + str(numDevices))
        # defaultTask
        if taskType == 0:
            task = DefaultTask( taskName
                              , parameterDict
                              , model
                              , hardwareRequirements
                              , filePath
                              , executeFunction
                              , configFile
                              , numDevices
                              )
        if taskType == 1:
            task = SpecificDeviceTask( taskName
                                     , parameterDict
                                     , model
                                     , hardwareRequirements
                                     , filePath
                                     , executeFunction
                                     , configFile
                                     )
        # request possibility from selector if task is feasible
        request_status = self._sendTaskRequest(task)
        #task accepted
        if request_status:
            self.selector.addTask2Queue(task, priority)
            self.logger.info("task accepted")
        # task rejected
        else: 
            self.logger.info("task was not accepted - change your constraints?")
        return request_status
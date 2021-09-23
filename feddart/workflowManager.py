from feddart.dartRuntime import DartRuntime
from feddart.defaultTask import DefaultTask
from feddart.specificDeviceTask import SpecificDeviceTask
from feddart.initTask import InitTask
from feddart.collection import Collection
import json
import time

from feddart.logServer import LogServer
from feddart.args import Helper
class WorkflowManager:

    TASK_STATUS_IN_PROGRESS = "in progess"
    TASK_STATUS_IN_QUEUE = "in queue"
    TASK_STATUS_FINISHED = "finished"
    taskID = 0
    def __init__( self
                , testMode = False
                , errorProbability = 0
                , logLevel = 3
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
        self._currentDeviceNames = []
        self._errorProbability = int(errorProbability)
        
        loglevel = LogServer.ERROR
        if int(logLevel) == 0:
            loglevel = LogServer.DEBUG
        elif int(logLevel) == 1:
            loglevel = LogServer.INFO
        elif int(logLevel) == 3:
            loglevel = LogServer.ERROR
        else:
            loglevel = LogServer.FATAL

        self.logger = LogServer(__name__, 
                                console_level = loglevel, 
                                file_level = LogServer.DEBUG)
        self.logger.log().info("Workflow manager initiated")

    @property
    def maxSizeDeviceHolder(self):
        self.logger.log().debug("_maxSizeDeviceHolder " + str(self._maxSizeDeviceHolder))
        return self._maxSizeDeviceHolder

    @property 
    def config(self):
        return self._args

    @property 
    def runtime(self):
        return self._runtime

    @property
    def selector(self):
        return self._selector

    @property
    def maximalNumberOpenJobs(self):
        self.logger.log().debug("_maximalNumberOpenJobs " + str(self._maximalNumberOpenJobs))
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

        self.logger.log().debug('start feddart server, config: ' + str(locals()))

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
        self.logger.log().debug("remove device. deviceName " + str(deviceName))
        self.selector.removeDevice(deviceName)
        
    def _sendTaskRequest(self, task):
        """!
        Send the task to the selecor. Based on hardware requirements and needed devices
        the selector decide accept or reject the task
        @param task instance of task
        """
        self.logger.log().info("requestTaskAcceptance")
        self.logger.log().debug(str(locals()))
        return self.selector.requestTaskAcceptance(task)
        
    def getTaskStatus(self, taskName):
        """!
        Ask the selector for the aggregator of the task. 
        The aggregator knows the status of the task
        @param taskName name of the task

        @return string "in queue", "in progress" or "finished"
        """
        self.logger.log().debug("getTaskStatus. task " + str(taskName))
        if self.selector.taskInQueue(taskName):
            return self.TASK_STATUS_IN_QUEUE
        else:
            try:
                aggregator = self.selector.get_aggregator_of_task(taskName)
                taskFinished = aggregator.isTaskFinished()
                if taskFinished:
                    self.logger.log().debug("TaskStatus " + str(self.TASK_STATUS_FINISHED))
                    return self.TASK_STATUS_FINISHED
                else:
                    self.logger.log().debug("TaskStatus " + str(self.TASK_STATUS_IN_PROGRESS))
                    return self.TASK_STATUS_IN_PROGRESS
            except ValueError:
                self.logger.log().error(
                    "workflowManager.getTaskStatus. there is no aggregator that handles task " + 
                    taskName)
                self.logger.log().debug(str(locals()))
            

    def getServerInformation(self):
        serverinfo = self.selector.runtime.get_ServerInformation()
        self.logger.log().debug("WorkflowManager.get_ServerInformation: " +  str(locals()))
        return serverinfo

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
        self.logger.log().info("WorkflowManager.getTaskResult. taskName " + str(taskName))
        if self.selector.taskInQueue(taskName):
            self.logger.log().debug(taskName + " still in queue.")
            return []
        else:
            try: 
                aggregator = self.selector.get_aggregator_of_task(taskName)
                taskResult = aggregator.requestAggregation()
                if self.getTaskStatus(taskName) == self.TASK_STATUS_FINISHED:
                    self.stopTask(taskName)
            except ValueError: 
                self.logger.log().error(
                    "workflowManager.getTaskResult. there is no aggregator that handles task " + 
                    taskName)
                self.logger.log().debug(str(locals()))
                return []
            return taskResult 

    def getAllDeviceNames(self):
        """!
        Return all known devices with name to the end user

        @return: list of device names
        """
        deviceNames = self.selector.deviceNames
        self.logger.log().debug("getAllDeviceNames. deviceNames " + str(deviceNames))
        if self._currentDeviceNames == []:
            self._currentDeviceNames = deviceNames
        return deviceNames

    def getNewDeviceNames(self):
        """!
        Return all known devices with name to the end user

        @return: list of device names
        """
        oldDeviceNames = self._currentDeviceNames
        currentDeviceNames = self.selector.deviceNames
        newDeviceNames = []
        for deviceName in currentDeviceNames:
            if deviceName not in oldDeviceNames:
                newDeviceNames.append(deviceName)
        self.logger.log().debug("getAllDeviceNames. deviceNames " + str(newDeviceNames))
        return newDeviceNames

    def createCollection(self, deviceNames):
        """!
        Cluster the devices to a group.

        @param deviceNames: list of device names
        @return: instance of class Cluster
        """
        return Collection( self, deviceNames)

    def stopTask(self, taskName):
        """!
        The task with the associated aggregator and deviceHolders is destroyed
        Should be done, when the task isn't needed anymore.
        @todo: add it as option to get_TaskResult ?!
        """
        self.logger.log().info("stopTask. taskName " + str(taskName))
        if self.selector.taskInQueue(taskName):
            self.selector.deleteTaskInQueue(taskName)
        else:
            self.selector.deleteAggregatorAndTask(taskName)
            
    def stopFedDART(self):
        self.logger.log().info("stopFedDART")
        self.runtime.stopRuntime()
    
    def createInitTask( self
                      , parameterDict = {}
                      , model = None
                      , hardwareRequirements = {}
                      , filePath = None
                      , executeFunction = None
                      , configFile = None
                      ):
        self.logger.log().debug("createInitTask. " + str(locals()))
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
                 , parameterDict = {}
                 , model = None
                 , hardwareRequirements = {}
                 , filePath = None
                 , executeFunction = None
                 , configFile = None
                 , priority = False
                 , numDevices = -1
                 , cluster = None
                 ):
        """!
        @param executeFunction name of function, which should be executed in filePath
        """
        # defaultTask
        taskName = "task_"+str(WorkflowManager.taskID)
        WorkflowManager.taskID += 1
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
            self.logger.log().info("task accepted")
        # task rejected
        else:
            taskName = None
            self.logger.log().info("task was not accepted - change your constraints?")
        self.logger.log().debug("start task." + str(locals()))
        return taskName
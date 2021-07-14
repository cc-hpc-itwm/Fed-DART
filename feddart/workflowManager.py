from feddart.dartRuntime import DartRuntime
from feddart.defaultTask import DefaultTask
from feddart.specificDeviceTask import SpecificDeviceTask
from feddart.initTask import InitTask
import json
import time


from feddart.logServer import LogServer

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

        self.logger = LogServer(__name__, 
                                console_level = LogServer.WARN, 
                                file_level = LogServer.DEBUG)
        self.logger.log().info("Workflow manager initiated")
        

    @property
    def maxSizeDeviceHolder(self):
        self.logger.log().debug("_maxSizeDeviceHolder " + str(self._maxSizeDeviceHolder))
        return self._maxSizeDeviceHolder
    
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
        self.logger.log().debug("get_ServerInformation")
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
        self.logger.log().error("WorkflowManager.getTaskResult. taskName " + str(taskName))
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
        self.logger.log().debug("getAllDeviceNames. deviceNames " + str(self.selector.deviceNames))
        return self.selector.deviceNames

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
            self.logger.log().info("task accepted")
        # task rejected
        else: 
            self.logger.log().info("task was not accepted - change your constraints?")
        self.logger.log().debug("start task." + str(locals()))
        return request_status
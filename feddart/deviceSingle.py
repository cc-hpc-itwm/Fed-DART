from feddart.abstractDevice import AbstractDeviceBase
from feddart.taskResult import TaskResult
from feddart.logServer import LogServer
class DeviceSingle(AbstractDeviceBase):
    """!
    DeviceSingle is the interface to the real pyhsical device.

    @param name name given by the user or runtime
    @param ip_address ip address of physical device
    @param physical_name name by which the device connted hisself to the server
    @param hardwareConfig hardware properties of physical device
    @param openTaskDict dictionary of tasks, which are/will be running on the device
           format: {"task_name": {'param1': value , 'param2': value}}
    @param finishedTaskDict dictionary of tasks, which have already a result
           format: {'duration': value, 'result': {'result_0': value, 'result_1': value}}
    @param dartRuntime runtime for connection to physical device
    @param initialized boolean , if device already has received the init task 
    """
    def __init__( self
                , name 
                , ipAdress
                , port
                , dartRuntime = None
                , physicalName = None
                , hardwareConfig = None
                , taskDict = {}
                , initTask = None
                ):
        self.name = name
        if physicalName == None:
            self.phyiscalName = self.name
        self.ipAdress = ipAdress
        self.port = port
        self._hardwareConfig = hardwareConfig
        self._openTaskDict = taskDict
        self._finishedTaskDict = {}
        self._dartRuntime = dartRuntime
        self._initTask = initTask
        if initTask is not None:
            self._initialized = False
        else: 
            self._initialized = True

        self.logger = LogServer(__name__)
        self.logger.log().info("DeviceSingle " + name + " instantiated")
        

    def __str__(self):
        return self.name
            
    @property
    def hardwareConfig(self):
        """!
        property: hardwareConfig. Implements the getter
        """
        return self._hardwareConfig

    @hardwareConfig.setter
    def hardwareConfig(self, newHardwareConfig):
        """!
        property: hardwareConfig. Implements the setter

        @param newHardwareConfig the new hardware config
        """
        self._hardwareConfig = newHardwareConfig
        return

    @property
    def openTaskDict(self):
        """!
        property: openTaskDict. Implements the getter
        """
        return self._openTaskDict

    @openTaskDict.setter
    def openTaskDict(self, newDict):
        """!
        property: openTaskDict. Implements the setter

        @param newDict the new open task dict
        """
        self._openTaskDict = newDict

    @property
    def finishedTaskDict(self):
        """!
        property: finishedTaskDict. Implements the getter
        """
        return self._finishedTaskDict

    @finishedTaskDict.setter
    def finishedTaskDict(self, newDict):
        """!
        property: finishedTaskDict. Implements the setter

        @param newDict the new finished task dict
        """
        self._finishedTaskDict = newDict
    
    @property
    def dartRuntime(self):
        """!
        property: dartRuntime. Implements the getter
        """
        return self._dartRuntime

    @dartRuntime.setter
    def dartRuntime(self, newRuntime):
        """!
        property: dartRuntime. Implements the setter

        @param newRuntime the new runtime
        """
        self._dartRuntime = newRuntime
    
    @property
    def initTask(self):
        """!
        property: initTask. Implements the getter
        """
        return self._initTask

    @initTask.setter
    def initTask(self, newInitTask):
        """!
        property: newInitTask. Implements the setter. 
        Update all devices directly with new init task

        @param newInitTask instance of class task
        @todo: check if new init task result is returned
        """
        self._initTask = newInitTask

    @property
    def initialized(self):
        """!
        property: initialized. Implements the getter
        """
        if self._initialized == False:
            initTaskName = self.initTask.taskName
            if self.has_taskResult(initTaskName):
                init_result = self.get_taskResult(initTaskName)
                if init_result.resultList[0] is None:
                    self._initialized = True
        return self._initialized

    @initialized.setter
    def initialized(self, boolInit):
        """!
        property: initialized. Implements the setter

        @param boolInt a boolean
        """
        self._initialized = boolInit
        
    def isOpenTask(self, taskName):
        """!
        Check if device has an open task with such a name.

        @param taskName string with task name

        @return boolean
        """
        if taskName in self._openTaskDict.keys():
            return True
        else:
            return False

    def removeOpenTask(self, taskName):
        """!
        Check if device has an open task with such a name and remove it.
        In the other case through a KeyError

        @param taskName string with task name
        """
        if taskName in self._openTaskDict.keys():
            del self._openTaskDict[taskName]
        else:
            raise KeyError
        return

    def get_number_openTasks(self):
        """!
        Determine the number of open tasks of the device.

        @return int
        """
        return len(self.openTaskDict)

    def is_online(self):
        """! 
        Check if the device is currently reachable.

        @return boolean 
        @todo implement the check
        """
        return True 

    def getOpenTaskParameter(self, taskName):
        """!
        Return the parameter of an open task. 
        Raise an error when a task with such a name is not in openTaskDict

        @param taskName string with task name

        @return dict with format {'param1': value , 'param2': value}
        """
        if taskName in self.openTaskDict.keys():
            return self.openTaskDict[taskName]
        else:
            raise KeyError("Open task with name", taskName, "doesn't exist!")

    def _getFinishedTaskResult(self, taskName):
        """!
        Return the parameter of an already finished task. 
        Raise an error when a task with such a name is not in finishedTaskDict

        @param taskName string with task name

        @return dict with format {'duration': value, 'result': {'result_0': value, 'result_1': value}}
        """
        if taskName in self.finishedTaskDict.keys():
            return self.finishedTaskDict[taskName]
        else:
            raise KeyError("Finished task with name", taskName, "doesn't exist!")
                   
    def getLog(self, taskName):
        """!
        Get the log of the device results for this task. In the moment we get
        these results form the finishedTaskDict. In the future there can be a more
        advanced way like a database.
        @param task instance of class task
        """        
        if taskName in self._finishedTaskDict.keys():
            return self._getFinishedTaskResult(taskName)
        else:
            return False

    def get_taskResult(self, taskName):
        """!
        Check if the taskName is known from current or old tasks. If true we check if the result
        is already logged in finishedTaskDict. If not get the result from runtime and
        check with has_taskResult is the result is only a place holder for an incoming result.
        If not remove the task from the dict of open task

        @param taskName name of the task

        @return instance of taskResult
        """
        if self.hasTask(taskName):
            if taskName in self._finishedTaskDict.keys():
                return self._getFinishedTaskResult(taskName)
            else:
                result, resultID = self.dartRuntime.get_TaskResult(taskName, self.name)
                taskResult = TaskResult( self.name
                                       , result["duration"]
                                       , result["result"]
                                       )
                if self.has_taskResult(taskName):
                    self.removeOpenTask(taskName)
                    self._addFinishedTask(taskName, taskResult)
                    self.dartRuntime.remove_result_from_server(taskName, resultID)
                return taskResult
        else:
            raise KeyError("No task with name " + taskName) 
        
    def startTask(self, task):
        """!
        Before starting a task, the user must it add to the device.
        To start a task the runtime must have already a job with the taskName. Add this 
        job if necessary. Afterwards broadcast a list with only one device entry to runtime.

        @param task instance of task
        """
        taskName = task.taskName
        if not self.hasTask(taskName):
            raise ValueError("Add the task", taskName, "to device", self.name, "before starting the task!")
        #return 0 means unknown
        if self.dartRuntime.get_job_status(taskName) == 0:
            self.dartRuntime.add_job( taskName
                                    , task.filePath
                                    , task.executeFunction
                                    )
        self.dartRuntime.broadcastTaskToDevices( taskName
                                               , [self.name]
                                               , [self.getOpenTaskParameter(taskName)]
                                               )
        
    def has_taskResult(self, taskName):
        """!
        Check the taskResult. If the result has the key duration
        with value None than the device hasn't anything returned yet.
        @param taskName name of the task

        @return boolean True or False

        @todo atm hacky because of REST API. To check if result is there,
        we must get it and check the components of the result.
        """
        if self.hasTask(taskName):
            if taskName in self._finishedTaskDict.keys():
                return True 
            else:
                result, resultID = self.dartRuntime.get_TaskResult(taskName, self.name)
                if result['duration'] == None:
                    return False
                else:
                    return True
        else:
            raise KeyError("No task with name " + taskName) 
        
    def addTask(self, taskName, taskParameter):
        """!
        Add a new open task with name and parameters to openTaskDict

        @param taskName string of task name
        @param taskParamerer dict in format {'param1': value , 'param2': value}
        """
        if taskName in self._openTaskDict.keys():
            raise KeyError(taskName + " already in openTaskDict!")
        tasks = self._openTaskDict
        tasks[taskName] = taskParameter
        self.openTaskDict = tasks
        
    def _addFinishedTask(self, taskName, taskResult):
        """!
        Add a new finished task with name and results to finishedTaskDict

        @param taskName string of task name
        @param taskResult dict with format {'duration': value
                                           , 'result': {'result_0': value, 'result_1': value}
                                           }
        """
        if taskName in self._finishedTaskDict.keys():
            raise KeyError(taskName + " already in finishedTaskDict!")
        tasks = self._finishedTaskDict
        tasks[taskName] = taskResult
        self.finishedTaskDict = tasks
        

    def hasTask(self, taskName):
        """!
        Check if the device has a open task with such a name

        @param taskName name of task

        @return boolean True/False
        """
        if taskName in self._openTaskDict.keys() or taskName in self._finishedTaskDict.keys():
            return True
        else:
            return False

        
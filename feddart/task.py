import abc

class TaskBase(abc.ABC):
    """!
    TaskBase is the meta class for all different task instances.
    Use this class to create a new task category. Tasks know their
    restrictions, where they need to be executed (optionally) with which
    parameters and which hardware requirements are mandatory. Tasks are initialized by 
    the user and handed over to the aggregators, that start the demanded executions on 
    the provided devices. Tasks are registered in a taskQueue owned by the selector.

    Currently, there are three different subclasses:

    defaultTask : the assumed standard scenario. Here, the same task is executed with the same 
    parameter settings (training, etc) on all available devices (possibly with a max number) 
    that fulfill the (optional) hardware requirements.

    specificDeviceTask:

    specificParameterTask:

    """
    
    @property
    @abc.abstractmethod
    def parameterDict(self):
        """!
        property: parameterlists. Implements the getter.

        @todo: define the format of parameter lists        
        """
        return 

    @parameterDict.setter
    @abc.abstractmethod
    def parameterDict(self, newParameterDict):
        """!
        property: parameterlists. Implements the setter.

        @param new_parameterlist the new list of parameters
        """
        return

    @property
    @abc.abstractmethod
    def taskName(self):
        """!
        property: taskName. Implements the getter.

        The taskName identifies the task (in combination with a timestamp) in the LogServer.
        
        """
        return 

    @taskName.setter
    @abc.abstractmethod
    def taskName(self, new_taskName):
        """!
        property: taskName. Implements the setter.

        @param new_taskName the new name of the task
        """
        return

    @property
    @abc.abstractmethod
    def filePath(self):
        """!
        property: filePath. Implements the getter.

        The file path provides the information where the file to be 
        executed on the device is stored.
        """
        return 
        
    @filePath.setter
    @abc.abstractmethod
    def filePath(self, new_filePath):
        """!
        property: filePath. Implements the setter.

        @param new_filePath the new file path 
        """
        return

    @property
    @abc.abstractmethod
    def configFile(self):
        """!
        property: configFile. Implements the getter.

        The configFile is an optional file provided at instantiation to describe the task configuration, i.e.
        it contains the parameters for training, (optionally) the model to be executed,
        which hardwareRequirements are mandatory, the name of the task, as well as the path to the 
        python script to be executed.

        @todo define the structure of the configFile
        """
        raise NotImplementedError("subclass has to implement this")

    @abc.abstractmethod
    def checkConfig(self):
        """!
        This method ensures that all necessary parameters for the given task are
        provided: either by given parameters in the instantiation of the subclass
        or by a given filepath to a configuration file.

        All subclasses have to implement this method. 
        """
        raise NotImplementedError("subclass has to implement this")

    @abc.abstractmethod
    def loadConfigFile(self):
        """!
        This function loads a given configuration file.
        """
        raise NotImplementedError("subclass has to implement this")

    def writeConfig(self
                   , taskName
                   , parameterlists
                   , hardwareRequirements
                   , model
                   , filePath):
        """!
        Writes the configuration of the task to disk.

        @param taskName Name of the task
        @param parameterlists List of parameters
        @param hardwareRequirements mandatory hardware requirements
        @param model model to be trained
        @param filePath path to the file to be executed on the device
        """

        raise NotImplementedError("subclass has to implement this")
        

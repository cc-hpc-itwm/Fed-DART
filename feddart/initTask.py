from feddart.task import TaskBase


class InitTask(TaskBase):
    """
    As InitTask, we define the steps which are necessary before the first learning round.
    """
    def __init__( self
                , parameterDict = {}
                , model = None
                , hardwareRequirements =  None
                , filePath = None
                , executeFunction = None
                , configFile = None
                ):
        """!
        Instantiates a SpecificDeviceTask. Information about the configuration have to be 
        either provided in the function call or via a configFile.

        @param taskName (optional) Name of the task to be stored in the LogServer
        @param parameterDict Dict of device names and associated parameters to be used in training
        @param model (optional) Model to be executed
        @param hardwareRequirements (optional) mandatory hardware requirements if None the same InitTask for all devices
        @param filePath the path to the file to be called for execution on the device
        @param executeFunction name of function, which shoule be executed in filePath
        @param configFile (optional)
        """
        self._taskName = "init_task"
        self._parameterDict = parameterDict
        self._model = model
        self._filePath = filePath
        self._hardwareRequirements = hardwareRequirements
        self._configFile = configFile
        self._executeFunction = executeFunction
        self.checkConfig()

    @property
    def filePath(self):
        return self._filePath
        
    @property
    def taskName(self):
        return self._taskName
            
    @property
    def executeFunction(self):
        return self._executeFunction

    @property
    def parameterDict(self):
        """!
        property: parameterDict. Implements the getter.

        @return format { "param1":0 ,"param2": 1}  
        """
        return self._parameterDict

    @parameterDict.setter
    def parameterDict(self, new_parameterDict):
        """!
        property: parameterDict. Implements the setter.
        @param new_parameterDict the new parameterDict
        """
        self._parameterDict = new_parameterDict

    @property
    def model(self):
        """!
        property: model. Implements the getter.

        A model is an optional parameter for a task. In case a model is provided,
        the model is sent to the devices where it will be trained/used for inference.
        In case no model is provided, the task executes some given functions on 
        the device (filePath has to be defined).
        """
        return self._model
        
    @model.setter
    def model(self, new_model):
        """!
        property: model. Implements the setter.
        @param new_model the new model to be trained
        """
        self._model = new_model

    @property
    def configFile(self):
        """!
        property: configFile. Implements the getter.

        The configFile is an optional file provided at instantiation to describe the task configuration, i.e.
        it contains the parameters for training, (optionally) the model to be executed,
        which hardwareRequirements are mandatory, the name of the task, as well as the path to the 
        python script to be executed.

        @todo define the structure of the configFile
        """

        return self._configFile

    def writeConfig(self
                   , taskName
                   , parameterlists
                   , hardwareRequirements
                   , model
                   , filePath):
        """!
        @todo implement

        @param taskName Name of the task
        @param parameterlists List of parameters
        @param hardwareRequirements mandatory hardware requirements
        @param model model to be trained
        @param filePath path to the file to be executed on the device
        """
        return

    def checkConfig(self):
        """!
        This method ensures that all necessary parameters for the given task are
        provided: either by given parameters in the instantiation of the subclass
        or by a given filepath to a configuration file.
        """

        config = {}
        valid = False
        if self._parameterDict is None:
            if self._configFile is None:
                raise ValueError("No configuration provided")
            else:
                config = self.loadConfigFile()
        else:
            config['parameters'] = self._parameterDict
            config['hardwareRequirements'] = self._hardwareRequirements
            config['model'] = self._model
            config['filePath'] = self._filePath

        # check the configuration
        # todo: define configfile
        # why we nedd load and write of the config ?
        if self._parameterDict is None:
            self.writeConfig( config['parameters']
                            , config['hardwareRequirements']
                            , config['model'] 
                            , config['filePath'] )

        return valid

    def loadConfigFile(self):
        """!
        @todo implement this function
        """
        return
from feddart.task import TaskBase

'''

'''
class DefaultTask(TaskBase):
    """!
    DefaultTask is a subclass of TaskBase, and therefore a specific category of tasks.
    As default task, we define to execute a given task with the same 
    parameter settings (training, etc) on all available devices (possibly with a max number) 
    that fulfill the (optional) hardware requirements.

    """
    def __init__( self
                , taskName = None
                , parameterlists = {}
                , model = None
                , hardwareRequirements = {}
                , filePath = None
                , configFile = None
                , numDevices = -1
                ):
        """!
        Instantiates a DefaultTask. Information about the configuration have to be 
        either provided in the function call or via a configFile.

        @param taskName (optional) Name of the task to be stored in the LogServer
        @param parameterlists List of parameters to be used in training
        @param model (optional) Model to be executed
        @param hardwareRequirements (optional) mandatory hardware requirements
        @param filePath the path to the file to be called for execution on the device
        @param configFile (optional) the configuration file of this task
        @param numDevices the total amount of devices on which the task shall to be executed
        """
        self._parameterlists = parameterlists
        self._model = model
        self._hardwareRequirements = hardwareRequirements
        self._numDevices = numDevices
        self._configFile = configFile
        self._filePath = filePath
        self._taskName = taskName

        self.checkConfig()

    @property
    def numDevices(self):
        return self._numDevices

    @property
    def parameterlists(self):
        """!
        property: parameterlists. Implements the getter.

        @todo: define the format of parameter lists        
        """
        return self._parameterlists

    @parameterlists.setter
    def parameterlists(self, new_parameterlist):
        """!
        property: parameterlists. Implements the setter.

        @param new_parameterlist the new list of parameters
        """
        self._parameterlists = new_parameterlist

    @property
    def taskName(self):
        """!
        property: taskName. Implements the getter.

        The taskName identifies the task (in combination with a timestamp) in the LogServer.
        
        """
        return self._taskName

    @taskName.setter
    def taskName(self, new_taskName):
        """!
        property: taskName. Implements the setter.

        @param new_taskName the new name of the task
        """
        self._taskName = new_taskName

    @property
    def hardwareRequirements(self):
        """!
        property: hardwareRequirements. Implements the getter.

        Hardware requirements define the (optional) mandatory requirements for the devices.
        @todo: define the format of hardware requirements
        """
        return self._hardwareRequirements

    @hardwareRequirements.setter
    def hardwareRequirements(self, new_hardwareRequirements):
        """!
        property: hardwareRequirements. Implements the setter.

        @param new_hardwareRequirements the new mandatory hardware requirements
        """
        self._hardwareRequirements = new_hardwareRequirements


    @property
    def model(self):
        """!
        property: model. Implements the getter.

        A model is an optional parameter for a task. In case a model is provided,
        the model is sent to the devices where it will be trained/used for inference.
        In case no model is provided, the task executes some given functions on 
        the device.
        """
        return self._model
        
    @model.setter
    def model(self, new_model):
        """!
        property: model. Implements the setter.

        @param new_model the new model to be used
        """
        self._model = new_model

    @property
    def filePath(self):
        """!
        property: filePath. Implements the getter.

        A model is an optional parameter for a task. In case a model is provided,
        the model is sent to the devices where it will be trained/used for inference.
        In case no model is provided, the task executes some given functions on 
        the device.
        """
        return self._filePath
        
    @filePath.setter
    def filePath(self, new_filePath):
        """!
        property: filePath. Implements the setter.

        @param new_filePath the new file path 
        """
        self._filePath = new_filePath

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
    
    def loadConfigFile(self):
        """!
        @todo implement this function
        """
        return

    def writeConfig(self
                   , taskName
                   , parameterlists
                   , hardwareRequirements
                   , model
                   , filePath):
        """!
        @todo implement

        Writes the configuration of the task to disk.

        @param taskName Name of the task
        @param parameterlists List of parameters
        @param hardwareRequirements mandatory hardware requirements
        @param model model to be trained
        @param filePath path to the file to be executed on the device
        """
        pass


    def checkConfig(self):
        """!
        This method ensures that all necessary parameters for the given task are
        provided: either by given parameters in the instantiation of the subclass
        or by a given filepath to a configuration file.

         @todo define configfile
        """
        
        config = {}
        valid = False
        if self._parameterlists is None:
            if self._configFile is None:
                raise ValueError("No configuration provided")
            else:
                config = self.loadConfigFile()
        else:
            config['parameters'] = self._parameterlists
            config['hardwareRequirements'] = self._hardwareRequirements
            config['model'] = self._model
            config['taskName'] = self._taskName
            config['filePath'] = self._filePath

        # check the configuration
        

        if self._parameterlists is None:
            self.writeConfig(config['taskName']
                            , config['parameters']
                            , config['hardwareRequirements']
                            , config['model'] 
                            , config['filePath'] )

        return valid

if __name__ == '__main__':

    # 1. 2 specific devices, device_0 and device_1
    # parameters for device_0:
    # param1 = 0
    # param2 = 1
    # parameters for device_1:
    # param1 = 2
    # param2 = 3
    task1 = DefaultTask(parameterlists = { 
          "default": { "param1":0 ,"param2": 1}}
        , model = "hello"
        , hardwareRequirements = {}
        , numDevices = 10
        , taskName = "defaulttask"
        , configFile= None
        , filePath= "wherever")

    print(task1, vars(task1))
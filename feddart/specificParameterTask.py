from feddart.task import TaskBase

from feddart.logServer import LogServer
'''
As specific device task, we define to execute a given task with (possibly)
different parameter settings (training, etc) on the devices that 
fulfill the (optional) hardware requirements 
'''
class SpecificParameterTask(TaskBase):

    def __init__(self
                , taskName 
                , parameterlists = {}
                , model = None
                , hardwareRequirements = {}
                , filePath = None
                , configFile = None):
        self._parameterlists = parameterlists
        self._model = model
        self._hardwareRequirements = hardwareRequirements
        self._configFile = configFile
        self._filePath = filePath
        self._taskName = taskName
        self.logger = LogServer(__name__)
        self.logger.log().info('SpecificParameterTask initiated')

        self.checkConfig()

    @property
    def parameterlists(self):
        return self._parameterlists

    @parameterlists.setter
    def parameterlists(self, new_parameterlist):
        self._parameterlists = new_parameterlist

    @property
    def model(self):
        return self._model
        
    @model.setter
    def model(self, new_model):
        self._model = new_model

    @property
    def specificDevices(self):
        return list(self._parameterlists.keys())

    @property
    def configFile(self):
        return self._configFile

    def writeConfig( self
                   , parameterlists
                   , model
                   , hardwareRequirements):
        raise NotImplementedError("not implemented yet")

    def checkConfig(self):
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
        # todo: define configfile

        if self._parameterlists is None:
            self.writeConfig(config['taskName']
                            , config['parameters']
                            , config['hardwareRequirements']
                            , config['model'] 
                            , config['filePath'] )

        return valid

    def loadConfigFile(self):
        raise NotImplementedError("not implemented yet")
    
if __name__ == '__main__':
    # 1. 2 specific devices, device_0 and device_1
    # parameters for device_0:
    # param1 = 0
    # param2 = 1
    # parameters for device_1:
    # param1 = 2
    # param2 = 3
    task1 = SpecificParameterTask(parameterlists = { 
          "parameterset_0": { "numDevices": 5, "param1":0 ,"param2": 1}
        , "parameterset_1": { "numDevices": 10, "param1":2 ,"param2": 3}}
        , model = "hello"
        , filePath = "path/to/your/execution/file"
        , hardwareRequirements = {}
        , configFile = None
        , taskName = "dummytask")
    
    print(task1, vars(task1))
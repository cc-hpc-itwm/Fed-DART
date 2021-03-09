import abc

class AbstractDeviceBase:
    
    __metaclass__ = abc.ABCMeta

    @property
    @abc.abstractmethod
    def hardwareConfig(self):
        return None

    @hardwareConfig.setter
    @abc.abstractmethod
    def hardwareConfig(self, new_value):
        return

    @property
    @abc.abstractmethod
    def dartRuntime(self):
        return None

    @dartRuntime.setter
    @abc.abstractmethod
    def dartRuntime(self, new_value):
        return
    
    @property
    @abc.abstractmethod
    def taskDict(self):
        return None

    @taskDict.setter
    @abc.abstractmethod
    def taskDict(self, new_value):
        return



# abstract functions

    @classmethod
    @abc.abstractmethod
    def getopenTasks(self):
        raise NotImplementedError("subclass has to implement this")
        return

    @classmethod
    @abc.abstractmethod
    def getLog(self):
        raise NotImplementedError("subclass has to implement this")
        return  

    @classmethod
    @abc.abstractmethod
    def getResultbyName(self, task_name):
        raise NotImplementedError("subclass has to implement this")
        return  


    @classmethod
    @abc.abstractmethod
    def getResultbyID(self, task_id):
        raise NotImplementedError("subclass has to implement this")
        return  

    @classmethod
    @abc.abstractmethod
    def startTask(self, task):
        raise NotImplementedError("subclass has to implement this")
        return  

    @classmethod
    @abc.abstractmethod
    def getStatus(self, task_id):
        raise NotImplementedError("subclass has to implement this")
        return

    @classmethod
    @abc.abstractmethod
    def validityCheckHardware(self, task):
        raise NotImplementedError("subclass has to implement this")
        return

    @classmethod
    @abc.abstractmethod
    def getLog(self, task):
        raise NotImplementedError("subclass has to implement this")
        return





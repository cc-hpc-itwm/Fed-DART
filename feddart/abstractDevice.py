import abc

class AbstractDeviceBase(abc.ABC):
    
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
    def openTaskDict(self):
        return None

    @openTaskDict.setter
    @abc.abstractmethod
    def openTaskDict(self, new_value):
        return

    @property
    @abc.abstractmethod
    def finishedTaskDict(self):
        return None

    @finishedTaskDict.setter
    @abc.abstractmethod
    def finishedTaskDict(self, new_value):
        return
    
    @property
    @abc.abstractmethod
    def initTask(self):
        return None

    @initTask.setter
    @abc.abstractmethod
    def initTask(self, new_value):
        return

    @property
    @abc.abstractmethod
    def initialized(self):
        return None

    @initTask.setter
    @abc.abstractmethod
    def initialized(self, new_value):
        return
    # abstract functions

    @abc.abstractmethod
    def isOpenTask(self, taskName):
        raise NotImplementedError("subclass has to implement this")
        return

    @abc.abstractmethod
    def removeOpenTask(self, taskName):
        raise NotImplementedError("subclass has to implement this")
        return

    @abc.abstractmethod
    def getOpenTaskParameter(self, taskName):
        raise NotImplementedError("subclass has to implement this")
        return

    @abc.abstractmethod
    def getLog(self, taskName):
        raise NotImplementedError("subclass has to implement this")
        return  

    @abc.abstractmethod
    def get_taskResult(self, taskName):
        raise NotImplementedError("subclass has to implement this")
        return  

    @abc.abstractmethod
    def startTask(self, task):
        raise NotImplementedError("subclass has to implement this")
        return  

    @abc.abstractmethod
    def addTask(self, taskName, taskParameter):
        raise NotImplementedError("subclass has to implement this")
        return  

    @abc.abstractmethod
    def has_taskResult(self, taskName):
        raise NotImplementedError("subclass has to implement this")
        return

    @abc.abstractmethod
    def hasTask(self, taskName):
        raise NotImplementedError("subclass has to implement this")
        return


    





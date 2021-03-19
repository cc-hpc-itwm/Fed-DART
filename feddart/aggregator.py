import abc

class AggregatorBase(abc.ABC):

    _logServer = None
    
    @property
    @abc.abstractmethod
    def logServer(self):
        return None

    @logServer.setter
    @abc.abstractmethod
    def logServer(self, new_value):
        return
#----------------------------------
    @property
    @abc.abstractmethod
    def task(self):
        return None

    @task.setter
    @abc.abstractmethod
    def task(self, new_value):
        return
#----------------------------------
    @property
    @abc.abstractmethod
    def deviceHolders(self):
        return None

    @deviceHolders.setter
    @abc.abstractmethod
    def deviceHolders(self, new_list):
        return
#-------------------------------------
    @property
    @abc.abstractmethod
    def childAggregators(self):
        return None

    @childAggregators.setter
    @abc.abstractmethod
    def childAggregators(self, new_list):
        return
#-------------------------------------
    @property
    @abc.abstractmethod
    def aggregatedResult(self):
        return None

    @aggregatedResult.setter
    @abc.abstractmethod
    def aggregatedResult(self, new_value):
        return

#-------------------------------------
    @property
    @abc.abstractmethod
    def maxSizeDeviceHolder(self):
        return None

    @maxSizeDeviceHolder.setter
    @abc.abstractmethod
    def maxSizeDeviceHolder(self, new_value):
        return
    
#-------------------------------------
    @property
    @abc.abstractmethod
    def allDevices(self):
        return None
    

    @abc.abstractmethod
    def addAggregator(self, newAggregator):
        raise NotImplementedError("Subclasses should implement this!")

    @abc.abstractmethod
    def get_TaskStatus(self):
        raise NotImplementedError("Subclasses should implement this!")

    @abc.abstractmethod
    def aggregate_devicesResults(self, boolean_aggregate):
        raise NotImplementedError("Subclasses should implement this!")

    @abc.abstractmethod
    def requestAggregation(self, boolean_aggregate):
        raise NotImplementedError("Subclasses should implement this!")
        
    @abc.abstractmethod
    def instantiateDeviceHolders(self):
        raise NotImplementedError("Subclasses should implement this!")

    @abc.abstractmethod
    def addSingleDevice(self, device):
        raise NotImplementedError("Subclasses should implement this!")
        
    @abc.abstractmethod
    def restartSelector(self):
        raise NotImplementedError("Subclasses should implement this!")  

    @abc.abstractmethod
    def broadcastTaskToDevices(self):
        raise NotImplementedError("Subclasses should implement this!")  

    @abc.abstractmethod
    def stopTask(self):
        raise NotImplementedError("Subclasses should implement this!")             

    @classmethod
    @abc.abstractmethod
    def sendLog(self, task):
        raise NotImplementedError("Subclasses should implement this!")

    
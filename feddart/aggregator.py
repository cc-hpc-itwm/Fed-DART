import abc

class AggregatorBase:
    """!

    """
    __metaclass__ = abc.ABCMeta
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
#------------------------------------
    @property
    @abc.abstractmethod
    def currentDevices(self):
        return None

    @currentDevices.setter
    @abc.abstractmethod
    def currentDevices(self, new_list):
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
    def aggregated_result(self):
        return None

    @aggregated_result.setter
    @abc.abstractmethod
    def aggregated_result(self, new_value):
        return
    
#--------------------------------------
# class functions
#----------------------------------------

    @classmethod
    @abc.abstractmethod
    def requestAggregation(self):
        """!
        In case of an aggregator of aggregators, this functions triggers the 
        aggregations by the child aggregators. Otherwise, it aggregates the results
        provided by all devices in its deviceHolders.
        
        """
        raise NotImplementedError("Subclasses should implement this!")
        

    @classmethod
    @abc.abstractmethod
    def aggregateDevices(self):
        raise NotImplementedError("Subclasses should implement this!")
        

    @classmethod
    @abc.abstractmethod
    def aggregate(self):
        raise NotImplementedError("Subclasses should implement this!")
        

    @classmethod
    @abc.abstractmethod
    def instantiateDeviceHolder(self):
        raise NotImplementedError("Subclasses should implement this!")
        
    
    @classmethod
    @abc.abstractmethod
    def restartSelector(self):
        raise NotImplementedError("Subclasses should implement this!")               

    @classmethod
    @abc.abstractmethod
    def addSingleDevice(self):
        raise NotImplementedError("Subclasses should implement this!")
          
    @classmethod
    @abc.abstractmethod
    def sendTaskToDevice(self, task):
        raise NotImplementedError("Subclasses should implement this!")
        

    @classmethod
    @abc.abstractmethod
    def sendLog(self, task):
        raise NotImplementedError("Subclasses should implement this!")

    @abc.abstractmethod
    def addAggregator(self, new_aggregator):
        """!
        Aggregators can follow a hierarchical structure to balance the load. If an aggregator
        already has at least one deviceHolder, it cannot add an aggregator. In case the aggregator
        can have childAggregators, this function adds a new aggregator to the list. 
        @param new_aggregator the new childAggregator
        """
        raise NotImplementedError("Subclasses should implement this!")
        

"""					
		requestSelectorUpdateByRuntime	DART-Runtime	
		sendTaskToDevice	currentdevices	list of devices
		requestResults	Selector	
		finalizeTask		returns result
		getIntermediateResult		return aggregatedResult
        """
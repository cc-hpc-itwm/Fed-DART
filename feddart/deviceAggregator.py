from feddart.aggregator import AggregatorBase
from feddart.deviceHolder import DeviceHolder
from feddart.deviceSingle import DeviceSingle
import math


class DeviceAggregator(AggregatorBase):
    """!
    DeviceAggregator is responsible for the data aspect of a task
    """
   
    def __init__( self 
                , devices
                , task
                , maxSizeDeviceHolder = 10 
                , maxNumDeviceHolder = 5
                , maxNumChildAggregators = 5
                , logServer = None
                ):
        """!
        @param task instance of a task
        @param deviceHolders list of deviceHolders
        @param childAggregators list of childAggregators
        @param maxSizeDeviceHolder maximum number of devices for deviceHolder
        @param maxNumDeviceHolder maximum number of deviceHolders per aggregator/childaggregator
        @param maxNumChildAggregators maximum number of allowed childAggregators
        @param aggregatedResult aggregated result of local task results
        @param logServer storage of the results and/or aggregated result 

        """
        self._task = task
        self._maxSizeDeviceHolder = maxSizeDeviceHolder
        self._maxNumDeviceHolder = maxNumDeviceHolder
        self._maxNumChildAggregators = maxNumChildAggregators
        self._deviceHolders = []
        self._childAggregators = []
        numDevices = task.numDevices
        if maxNumChildAggregators > 0:
            amount_childAggregators = self.compute_required_childAggregators_count(numDevices)
            self._childAggregators = [ DeviceAggregator([]  #init at first without devices; devices will be added at the end of constructor
                                                       , task
                                                       , maxSizeDeviceHolder = maxSizeDeviceHolder
                                                       , maxNumDeviceHolder = maxNumDeviceHolder
                                                       , maxNumChildAggregators =  0
                                                       , logServer = logServer
                                                       ) for _ in range(amount_childAggregators)
                                    ]
        self._aggregatedResult = None
        self._logServer = logServer
        self._instantiateDeviceHolders()
        for device in devices:
            self.addSingleDevice(device) #add here task to devices
#--------------------------------------------        
    @property
    def maxNumDeviceHolder(self): 
        """!
        property: maxNumDeviceHolder. Implements the getter
        """
        return self._maxNumDeviceHolder 

#--------------------------------------------        
    @property
    def maxNumChildAggregators(self):
        """!
        property: maxNumChildAggregators. Implements the getter
        """
        return self._maxNumChildAggregators

#--------------------------------------------        
    @property
    def maxSizeDeviceHolder(self):
        """!
        property: maxSizeDeviceHolder. Implements the getter
        """
        return self._maxSizeDeviceHolder

#----------------------------------
    @property
    def logServer(self):
        """!
        property: logServer. Implements the getter
        """
        return self._logServer

    @logServer.setter
    def logServer(self, newLogServer):
        """!
        property: logServer. Implements the setter

        @param newLogServer the new logServer
        """
        self._logServer = newLogServer
#----------------------------------
    @property
    def task(self):
        """!
        property: task. Implements the getter
        """
        return self._task

    @task.setter
    def task(self, newTask):
        """!
        property: deviceHolders. Implements the setter

        @param newTask instance of task
        """
        self._task = newTask
        if self.childAggregators:
            for child in self.childAggregators:
                child.task = newTask
#----------------------------------
    @property
    def deviceHolders(self):
        """!
        property: deviceHolders. Implements the getter
        """
        return self._deviceHolders

    @deviceHolders.setter
    def deviceHolders(self, newDeviceHolders):
        """!
        property: deviceHolders. Implements the setter

        @param newDeviceHolders list of deviceHolders
        """
        if self._childAggregators:
            raise ValueError("Child aggregators exist!")
        self._deviceHolders = newDeviceHolders
#------------------------------------
    @property
    def allDevices(self):
        """!
        property: currentDevices. Implements the getter
        """
        allDevices = []
        for dHolder in self.deviceHolders:
            allDevices.extend(dHolder.devices)

        if self.childAggregators:
            for child in self.childAggregators:
                for device_holder in child.deviceHolders:
                    allDevices.extend(device_holder.devices)
                    
        return allDevices
#-------------------------------------
    @property
    def childAggregators(self):
        """!
        property: childAggregators. Implements the getter
        """
        return self._childAggregators

    @childAggregators.setter
    def childAggregators(self, newChildAggregators):
        """!
        property: childAggregators. Implements the setter

        @param newChildAggregators list of childAggregators
        """
        self._childAggregators = newChildAggregators
#-------------------------------------
    @property
    def aggregatedResult(self):
        """!
        property: aggregatedResult. Implements the getter
        """
        return self._aggregatedResult

    @aggregatedResult.setter
    def aggregatedResult(self, newAggregatedResult):
        """!
        property: aggregatedResult. Implements the setter

        @param newAggregatedResult
        """
        self._aggregatedResult = newAggregatedResult

    def get_max_number_devices(self):
        """!
        Get total number of devices from deviceAggregator or in case 
        of childAggregators iterate over all child aggregators.

        @return total int number of maximal amount of devices
        """
        if not self.childAggregators:
            return self._maxNumDeviceHolder * self._maxSizeDeviceHolder
        else:
            total = 0
            for child in self.childAggregators:
                total += child.get_max_number_devices()
            return total

    def get_OnlineDevices(self):
        """!
        Get a list of devices, which are online.
        In case of childAggregators iterate over childaggregatos
        and get from them the online devices

        @return deviceList
        """
        deviceList = []
        if self.childAggregators:
            for aggregator in self.childAggregators:
                deviceList.extend(aggregator.get_OnlineDevices())
            return deviceList
        for dHolder in self.deviceHolders:
            deviceList.extend(dHolder.getOnlineDevices())
        return deviceList

#-------------functions for setting up device aggregator------------------
    def compute_required_childAggregators_count(self, numberDevices):
        """!
        Check if child aggregators are required and compute the amount

        @param numberDevices int amount of required devices
        """
        amount_needed_childAggregators = 0
        maxDevices = self._maxNumDeviceHolder * self._maxSizeDeviceHolder
        if maxDevices < numberDevices:
            # get necessary devices per childAggregators
            devicesPerChild = math.ceil(numberDevices/self._maxNumChildAggregators)
            if devicesPerChild > self._maxSizeDeviceHolder:
                raise ValueError("More devices are required than allowed per child aggregator!")
            amount_needed_childAggregators = math.ceil(numberDevices/maxDevices)
        return amount_needed_childAggregators

    def _instantiateDeviceHolders(self):
        """!
        Instantiate devicHolders and append to list of DeviceHolders
        """
        if len(self.deviceHolders) > 0:
            raise ValueError("device holder already instantiated")
        elif len(self.childAggregators) > 0:
            pass
        else:
            for i in range(self._maxNumDeviceHolder):
                deviceHolder = DeviceHolder(self.maxSizeDeviceHolder)
                self.deviceHolders.append(deviceHolder)

    def addSingleDevice(self, device):
        """!
        Add single device to aggregator. If we have child aggregators
        iterate over child aggregators and add it to the first one,
        who have capacity.

        @param device instance of class deviceSingle
        """
        if not isinstance(device, DeviceSingle):
            raise Exception("Device is not an instance of DeviceSingle !")
        if self.childAggregators:
            for aggregator in self.childAggregators:
                if aggregator.addSingleDevice(device) == True:
                    return
            raise ValueError("Device holders are completely full!")
        else:
            for deviceHolder in self.deviceHolders:
                if device in deviceHolder.devices:
                    raise Exception("Device is already in deviceHolder!")
                if deviceHolder.check_full() == False:
                    deviceName = device.name
                    deviceParameterDict = self.task.getDeviceParameterDict(deviceName)
                    taskName = self.task.taskName
                    deviceHolder.addDevice(device, taskName, deviceParameterDict)
                    return True
            if self.maxNumChildAggregators > 0:
                raise ValueError("Device holders are completely full!")

#-------------functions regarding task status-----------------------
    def sendTask(self):
        """!
        Send task to device.

        Each Aggregator iterate over the device holders, which broadcast the 
        task to the runtime.
        """
        if self.task is None:
            raise ValueError("There is no task assigned!")
        if self.childAggregators:
            for aggregator in self.childAggregators:
                aggregator.sendTask()
        else:
            for device_holder in self.deviceHolders:
                if not device_holder.check_empty():
                    device_holder.broadcastTask(self.task)

    def isTaskFinished(self):
        """!
        Return the status of the task. If there is no child aggregators iterate
        over all deviceHolders and check the task status. To look at each deviceHolder
        is necessary, because the devices in different deviceHolders can have different 
        servers. Each deviceHolder iterates over his devices and get the device task status.
        Based on this number we decide over the task status.
        
        @return string "in progress" or "finished"
        """
        if self.task is None:
            raise ValueError("There is no task assigned!")
        taskFinished = True
        taskName = self.task.taskName
        if not self.childAggregators:
            for device_holder in self.deviceHolders:
                dhFinished = device_holder.devicesFinished(taskName)
                if not dhFinished:
                    taskFinished = False
                    break
        for aggregator in self.childAggregators:
            childAggregatorTaskFinished = aggregator.isTaskFinished()
            if not childAggregatorTaskFinished:
                taskFinished = False
                break
        return taskFinished

    def stopTask(self):
        """!
        Remove the task from each device over the device holders
        from the aggregator.
        Afterwards delete the deviceHolders. Already finished devices
        has logged their results on their own
        """
        if self.task is None:
            raise ValueError("There is no task assigned!")
        taskName = self.task.taskName
        if self.childAggregators:
            for childAggregator in self.childAggregators:
                childAggregator.stopTask()
        else:
            for deviceHolder in self.deviceHolders:
                deviceHolder.stopTask(taskName)
                del deviceHolder

#-----------------functions for result aggregation-----------------        
    def aggregate_devicesResults(self):
        """!
        Collect results from device, which are finished, and aggregate them optional.

        @return list with instances of taskResult
        """
        # check all deviceholders
        if not self.deviceHolders:
            print('no device holders available')
        # get all devices from the deviceholders
        taskName = self.task.taskName
        intermediateResults = []
        for dHolder in self.deviceHolders:
            intermediateResults.extend(dHolder.get_finishedTasks(taskName))
        return intermediateResults

    def requestAggregation(self):
        """!
        In case of an aggregator with childaggregators, this function triggers the 
        aggregations by the child aggregators. Otherwise, it aggregates the results
        provided by all finished devices in its deviceHolders. 

        @param boolean_aggregate option to aggregate the results directly
        @return list with instances of taskResult
        """

        if not self.childAggregators:
            print('collect results from devices...')
            aggregatedResult = self.aggregate_devicesResults()
            return aggregatedResult
        #TODO: in moment sequential, parallelize it
        result = []
        for aggregator in self.childAggregators:
            print('trigger aggregation by childaggregators')
            result.extend(aggregator.requestAggregation())
        return result
                   
#--------------functions for writing log------------------------
    def sendLog(self, task):
        """!
        In case of no childAggregators iterate over device holders and devices.
        Write the log to the logServer.
        In case of childAggregators iterate over them first.

        @param task instance of class task
        """
        taskName = task.taskName
        # get devices from device holders if there are no child aggregators
        if not self.childAggregators:
            for deviceHolder in self.deviceHolders:
                for device in deviceHolder.devices:
                    logs = device.getLog(task)
                    #return False when the device does not has this specific task
                    if logs and self.logServer:
                        self.logServer.writeLog(logs)
        # if there are child aggregators, get them first to trigger them sending the log
        else:
            for aggregator in self.childAggregators:
                aggregator.sendLog(task)     

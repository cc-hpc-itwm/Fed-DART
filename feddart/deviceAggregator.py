from feddart.aggregator import AggregatorBase
from feddart.deviceHolder import DeviceHolder
from feddart.logServer import LogServer
import math


class DeviceAggregator(AggregatorBase):
    """!
    DeviceAggregator is responsible for the data aspect of a task
    """
    """!
    @param _maxNumDeviceHolder maximal number of deviceHolders per aggregator/childaggregator
    @param _maxNumChildAggregators maximal number of allowed childAggregators
    """
    _maxNumDeviceHolder = 2
    _maxNumChildAggregators = 2

    def __init__( self 
                , task = None
                , deviceHolders = []
                , childAggregators = []
                , maxSizeDeviceHolder = 1
                , aggregatedResult = None
                , logServer = None
                ):
        """!
        @param task instance of a task
        @param deviceHolders list of deviceHolders
        @param childAggregators list of childAggregators
        @param maxSizeDeviceHolder maximal number of devices for deviceHolder
        @param aggregatedResult aggrated result of local task results
        @param logServer storage of the results and/or aggregated result 

        """
        self._task = task
        self._deviceHolders = deviceHolders
        self._childAggregators = childAggregators
        self._aggregatedResult = aggregatedResult
        self._maxSizeDeviceHolder = maxSizeDeviceHolder
        self._logServer = logServer
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
            allDevices = allDevices + dHolder.devices
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
#-------------------------------------
    def addAggregator(self, newAggregator):
        """!
        Aggregators can follow a hierarchical structure to balance the load. 
        If an aggregator already has at least one deviceHolder, 
        it cannot add an aggregator. In case the aggregator can have childAggregators,
        this function adds a new aggregator to the list. 

        @param new_aggregator the new childAggregator
        """
        if self.deviceHolders:
            raise ValueError("deviceHolder already instantiated")

        if new_aggregator in self.childAggregators:
            return

        self._childAggregators.append(newAggregator)

    def _determine_taskStatus(self, list_taskStatus):
        """!
        Every deviceHolder has its own taskStatus. To get 
        the information about all deviceHolders we must 
        iterate over list_taskStatus to get a single value

        @param list_taskStatus list with values "in progress" or "finished"

        @return string "finished" or "in progress"
        """
        if len(list_taskStatus) == 0:
                raise ValueError("Task has no devices for computation")
        else:
            if all(ele == list_taskStatus[0] for ele in list_taskStatus):
                if list_taskStatus[0] == "in progress":
                    return "in progress"
                else:
                    return "finished"
            else:
                return "in progress"

    def get_TaskStatus(self):
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
        taskName = self.task.taskName
        list_taskStatus = []
        if not self.childAggregators:
            for device_holder in self.deviceHolders:
                if not device_holder.check_empty():
                    taskStatus = device_holder.get_taskStatus(taskName)
                    list_taskStatus.append(taskStatus)
            taskStatus = self._determine_taskStatus(list_taskStatus)
            return taskStatus
        for aggregator in self.childAggregators:
            print("trigger task status by childaggregators")
            #TODO: retun list with option "something went wrong"
            taskStatus = aggregator.get_taskStatus()
            list_taskStatus.append(taskStatus)
        taskStatus = self._determine_taskStatus(list_taskStatus)
        return taskStatus
        
    def aggregate_devicesResults( self
                                , boolean_aggregate
                                ):
        """!
        Collect results from device, which are finished, and aggregate them optional.
        @param boolean_aggregate option to aggregate results directly

        @return list with instances of taskResult
        """
        # check all deviceholders
        if not self.deviceHolders:
            print('no device holders available')
        # get all devices from the deviceholders
        taskName = self.task.taskName
        intermediatedResults = []
        for dHolder in self.deviceHolders:
            intermediatedResults = intermediatedResults + dHolder.get_finishedTasks(taskName)
        if boolean_aggregate:
            self.aggregate(intermediatedResults)
        return intermediatedResults

    def aggregate(self, intermediatedResults):
        """!
        Aggregte collected results to single one

        @param intermediate_results dict of devices result

        @todo not implemented  in the moment use case specific
        """
        return print("aggregation is not implemented in the momment")

    def requestAggregation( self
                          , boolean_aggregate
                          ):
        """!
        In case of an aggregator with childaggregators, this functions triggers the 
        aggregations by the child aggregators. Otherwise, it aggregates the results
        provided by all finished devices in its deviceHolders. 

        @param boolean_aggregate option to aggregate the results directly
        @return list with instances of taskResult
        """

        if not self.childAggregators:
            print('collect results from devices...')
            aggregatedResult = self.aggregate_devicesResults(boolean_aggregate)
            return aggregatedResult
        #TODO: in moment sequential, parallelize it
        result = []
        for aggregator in self.childAggregators:
            print('trigger aggregation by childaggregators')
            result = result + aggregator.requestAggregation(boolean_aggregate)
        if boolean_aggregate:
            aggregatedResult = self.aggregate(result)
            return aggregatedResult
        return result

    def instantiateDeviceHolders(self):
        """!
        Instantiate devicHolders and append to list of DeviceHolders
        """
        if len(self.deviceHolders) > 0:
            raise ValueError("device holder already instantiated")
        else:
            for i in range(self._maxNumDeviceHolder):
                deviceHolder = DeviceHolder( self.maxSizeDeviceHolder
                                           , deviceList = []
                                           )
                self.deviceHolders.append(deviceHolder)

    def get_OnlineDevices(self):
        """!
        Get a list of devices, which are online. 
        In case of childAggreators iterate over childaggregatos
        and get from them the online devices

        @return deviceList
        """
        deviceList = []
        if self.childAggregators:
            for aggregator in self.childAggregators:
                deviceList = deviceList + aggregator.get_OnlineDevices()
            return deviceList

        for dHolder in self.deviceHolders:
            deviceList = deviceList + dHolder.getOnlineDevices()
        return deviceList


    def addSingleDevice(self, device):
        """!
        Add single device to aggregator. If we have child aggregators
        iterate over child aggreagators and add it to the first one,
        who have capacity.

        @param device instance of class deviceSingle
        """
        # check whether there are child aggregators, if so, return without doing anything
        #TODO: implement function in case of child aggregators
        if self.childAggregators:
            for aggregator in self.childAggregators:
                if aggregator.addSingleDevice(device) == True:
                    return
            raise ValueError("Device holders are completly full!")
        else:
            for deviceHolder in self.deviceHolders:
                if deviceHolder.check_full() == False:
                    deviceHolder.addDevice(device)
                    return True
            raise ValueError("Device holders are completly full!")
                    
    def restartSelector(self):
        """!
        Get a device for accesing the runtime. With that start the runtime.
        Not supported in the moment, because not needed.
        """
        # check whether there are deviceholders 
        if self.childAggregators:
            for child in self.childAggregators:
                child.restartSelector()
            return

        if not self.deviceHolders:
            raise KeyError('no deviceHolder available')
        
        # request the runtime of any device from the devices held by deviceholder
        device = self.deviceHolders[0].getFirstAvailableDevice()
        # trigger a restart of the selector for the given runtime
        device.dartRuntime.restartSelector()
        return

    def broadcastTaskToDevices(self):
        """!
        Sent task to device.

        Each Aggregator iterate over the device holders, which broacast the 
        task to the runtime.
        """
        if self.task is None:
            raise ValueError("There is no task assigned!")
        if self.childAggregators:
            for aggregator in self.childAggregators:
                aggregator.broadcastTaskToDevices(task)
        else:
            for device_holder in self.deviceHolders:
                if not device_holder.check_empty():
                    device_holder.broadcastTask(self.task)

    def _splitTask(self
                 , task
                 , split_param
                 , splits
                 ):
        """!
        splits the outer task in a specific number of internal tasks

        @param task instance of task
        @param split_param the parameter responsible for the overall task (e.g. # epochs)
        @param splits the number of subtasks

        @todo not supported in the moment
        """
        self._taskSplits = []

    def get_max_number_devices(self):
        """!
        Get maximal amount of devices from deviceAggregator or in case 
        of childAggregators iterate over all child aggregators.

        @return total int number of maximal amount of devices
        """
        if not self.childAggregators:
            return self._maxNumDeviceHolder * self.maxSizeDeviceHolder
        else:
            total = 0
            for child in self.childAggregators:
                total += child.get_max_number_devices()
            return total

    def create_needed_childAggregators(self, numberDevices):
        """!
        Check whether the given max number of devic holders
        can hold all the necessary devices. If not, generate 
        a hierarchy of childAggregators. We only allow in the moment
        a hierachy with depth one

        @param numberDevices int amout of needed devices
        """
        maxDevices = self.get_max_number_devices()
        #print("aggregator - max number of devices: ", maxDevices, "/ needed: ", number_devices)
        if maxDevices < numberDevices:
            print("-------------Instantiate new level of Aggregators ---------------")
            
            # get necessary devices per childAggregators
            devicesPerChild = math.ceil(number_devices/self._maxNumChildAggregators)
            if devicesPerChild > self.maxSizeDeviceHolder:
                raise ValueError("Too much devices for maximal allowed numbers of child aggregators!")
            #print("devices per child aggregator:", devicesPerChild)

            for i in range(self._maxNumChildAggregators):
                #print("childaggregator: ", i)
                aggregator = DeviceAggregator( task = None
                                             , deviceHolders = []
                                             , currentDevices = []
                                             , childAggregators = []
                                             , maxSizeDeviceHolder = self._maxSizeDeviceHolder
                                             , aggregatedResult = None
                                             )
                # allow in the moment only trees with depth one
                #aggregator.create_needed_childAggregators(devicesPerChild)                                
                self.addAggregator(aggregator) 
                #print("--------------------------------")
                
    def stopTask(self):
        """!
        Remove the task from each device over the device holders
        from the aggregator.
        Afterwards delete the deviceHolders. Already finished devices
        has logged their results on their own
        """
        if self.task is None:
            raise ValueError("There is no task assigned!")
        if self.childAggregators:
            for childAggregator in self.childAggreators:
                childAggregator.stopTask()
        else:
            for deviceHolder in self.deviceHolders:
                deviceHolder.stopTask(self.task)
                del deviceHolder

    def sendLog(self, task):
        """!
        In case of no childAggregators iterate over device holders and devices.
        Write the log to  the logServer.
        In case of childAggragtors iterate first over them.

        @param task instance of class task
        """
        #print("---------- send log ----------")
        taskName = task.taskName
        # get devices from device holders if there are no child aggregators
        if not self.childAggregators:
            for deviceHolder in self.deviceHolders:
                for device in deviceHolder.deviceList:
                    log = device.getLog(task)
                    #return False when the device does not has this specific tas
                    if log:
                        self.logServer.writeLog(log)
        # if there are child aggregators, get them first to trigger them sending the log
        for aggregator in self.childAggregators:
            #print("-----------------> call child aggregators")
            aggregator.sendLog(task)     

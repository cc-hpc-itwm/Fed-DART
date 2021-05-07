from feddart.deviceAggregator import DeviceAggregator
from feddart.initTask import InitTask
from feddart.deviceHolder import DeviceHolder

class Selector():
    """! 
    Selector has the knowledge about all connected devices.
    The Selector is responsible to shedule devices to the
    device holder based on (optional) hardware requirements.
    """
    """!
    @param _maxNumDeviceHolder maximal number of deviceHolders per aggregator/childaggregator
    @param _maxNumChildAggregators maximal number of allowed childAggregators
    """
    _maxNumDeviceHolder = 2
    _maxNumChildAggregators = 2
    
    def __init__( self
                , runtime = None
                , maxSizeDeviceHolder = -1 
                , initTask = None
                ):
        """!
        Instantiate a Selector (singleton).

        @param runtime The runtime for the connections to physical devices
        @param maxSizeDeviceHolder Maximal amount of devices in a device holder
        @param devices List of connected devices
        @param aggregators  List of aggregators
        @param device_holders List of device_holders
        @param taskQueue List of tasks in queue
        @param initTask task which must be executed at each device firstly
        """
        self._runtime = runtime
        self._maxSizeDeviceHolder = maxSizeDeviceHolder 
        self._devices = self._runtime.registeredDevices
        self._aggregators = []
        self._device_holders = []
        self._taskQueue = []
        self._initTask = initTask

    @property 
    def runtime(self):
        """!
        property: runtime. Implements the getter
        """
        return self._runtime

    @property
    def devices(self):
        """!
        property: devices. Implements the getter for the registeredDevices.
        Get the registeredDevices directly from runtime. For new devices
        send initTask directly out.
        """
        
        self._devices = self._runtime.registeredDevices
        if self._initTask:
            self.send_initTask_to_newDevices(self._devices)
        return self._devices

    @property
    def deviceNames(self):
        """!
        property: name of devices. Implements the getter
        @todo: is this property necessary?
        """
        return [device.name for device in self.devices]

    @property
    def device_hardwareConfigs(self):
        """!
        property: device_hardwareConfigs. Implements the getter
        @todo: is this property necessary ?
        """
        return [device.hardwareConfig for device in self.devices]
   
    @property
    def device_holders(self):
        """!
        property: device_holders. Implements the getter
        """
        return self._device_holders

    @device_holders.setter
    def device_holders(self, newDeviceHolders):
        """!
        property: device_holders. Implements the setter

        @param newDevice_holders the new list of device_holders
        """
        self._device_holders = newDeviceHolders

    @property
    def initTask(self):
        """!
        property: initTask. Implements the getter
        """
        return self._initTask

    @initTask.setter
    def initTask(self, newInitTask):
        """!
        property: newInitTask. Implements the setter. 
        Update all devices directly with new init task

        @param newInitTask instance of class task
        @todo: check if new init task result is returned
        """
        if not isinstance(newInitTask, InitTask):
            raise ValueError("object is no instance of InitTask")
        self._initTask = newInitTask
        self.send_initTask_to_newDevices(self._devices)

    @property
    def aggregators(self):
        """!
        property: aggregators. Implements the getter
        """
        return self._aggregators

    @aggregators.setter
    def aggregators(self, newAggregators):
        """!
        property: aggregators. Implements the setter

        @param newAggregators the new list of aggregators
        """
        self._aggregators = newAggregators

    @property
    def maximal_size_device_holder(self):
        """!
        property: maxSizeDeviceHolder. Implements the getter
        """
        return self._maxSizeDeviceHolder

    @maximal_size_device_holder.setter
    def maximal_size_device_holder(self, newSize):
        """!
        property: maxSizeDeviceHolder. Implements the setter

        @param newSize new maximal number of allowd device holders.
        """
        self._maxSizeDeviceHolder = newSize
    
#-------------- functions for device related aspects----------------------
    def send_initTask_to_newDevices(self, deviceList):
        """! In the case that a device has connected on their own we must send 
            the init task to them before sending another tasks.
        """
        initializationDevices = []
        for device in deviceList:
            if device.hasTask(self.initTask.taskName) == False:
                device.addTask(self.initTask.taskName, self.initTask.parameterDict)
                initializationDevices.append(device)
        number_not_inializedDevices = len(initializationDevices)
        if number_not_inializedDevices > 0:
            deviceHolder = DeviceHolder( maxSize = number_not_inializedDevices
                                       , deviceList = initializationDevices
                                       )
            deviceHolder.broadcastTask(self.initTask)

    def addSingleDevice( self 
                       , deviceName
                       , ipAdress
                       , port
                       , hardwareConfig
                       ):
        """!
        Add a single device to runtime

        @param deviceName string with device name
        @param ipAdress string with IP adress
        @param port int with device port
        @param hardwareConfig dict with devices hardware config
        """               
        initTask = self.initTask
        self.runtime.addSingleDevice( deviceName
                                    , ipAdress
                                    , port
                                    , hardwareConfig
                                    , initTask
                                    )
                                    
    def removeDevice(self, deviceName):
        """!
        Remove a device from the runtime. A possible reason for that could 
        be that this device is corrupted.
    
        @param deviceName string with Name of device
        """
        if deviceName in self.deviceNames:
            self.runtime.removeDevice(deviceName)
        else:
           raise ValueError("There is no device with name " + deviceName)

    def requestTaskAcceptance(self, task):
        """!
        Decide if enough devices fullfil the hardware requirements
        of the incoming task.
        In a first step the selector determines the devices, which are currently available for computation.
        In a second step the possible devices are checked from the task, if the fullfill the task criteria.
        Based on this criteria accept or reject the task. 

        @param task instance of task
        
        @return task_acceptance boolean 
        """
        initializedDevices = []
        for device in self.devices:
            if device.initialized:
                initializedDevices.append(device)
        task_acceptance = task.checkConstraints(initializedDevices)
        return task_acceptance

#------------functions for aggregator related aspects --------
    def get_aggregator_of_task(self, taskName):
        """!
        Iterate over all known aggregators to get the aggregator
        of the specific task. Raise a ValueError if the aggregator
        doesn't exist.

        @param taskName string with task name
        @return aggregator instance of Aggregator
        """
        for aggregator in self.aggregators:
            if aggregator.task.taskName == taskName:
                return aggregator
        raise ValueError("The task", taskName, "doesn't exists")

    def addAggregator(self, newAggregator):
        """!
        Add a new aggregator to the aggregtor list.

        @param newAggregator instance of aggregator
        """
        aggregators = self.aggregators
        aggregators = aggregators + [newAggregator]
        self.aggregators = aggregators

    def deleteAggregatorAndTask(self, taskName):
        """!
        Get the aggregator of the task, stop the task on the DART-Server 
        and remove the task from the open task dict on each device. Afterwards 
        the aggregator is deleted and new tasks are uploaded to the DART-Server

        @param taskName string with task name
        """
        aggregator = self.get_aggregator_of_task(taskName)
        aggregator.stopTask()
        self.deleteAggregator(aggregator)
        self.addTasks2Runtime()

    def deleteAggregator(self, aggregator):
        """!
        Remove a aggregator from the aggregator list and delete the aggregator.

        @param aggregator instance of aggregator
        """
        if aggregator in self.aggregators:
            self._aggregators.remove(aggregator)
            del aggregator
        else:
            raise ValueError("aggregator is not in selector")

    def instantiateAggregator(self, task):
        """!
        Instantiate DeviceAggregator. Check in create_needed_childAggregators
        if the aggregator has enough capacity for the amount of Device,
        if not create childAggregators recursively. Add task and devices
        to aggregator
        
        @param numDevices amount of devices
        """
        choosen_devices = self.getDevicesForAggregator(task)
        aggregator = DeviceAggregator( devices = choosen_devices
                                     , task = task
                                     , maxSizeDeviceHolder = self._maxSizeDeviceHolder
                                     , maxNumDeviceHolder = self._maxNumDeviceHolder
                                     , maxNumChildAggregators = self._maxNumChildAggregators
                                     , logServer = None
                                     )
        print("max # devices in aggregator: ", aggregator.get_max_number_devices())
        self.addAggregator(aggregator)
        return aggregator
        
    def getDevicesForAggregator(self, task):
        """!
        Check which devices fullfill the requirements of the task
        and if they are available.

        @param task instance of task 
        """   
        #TODO: only implemented for specificDeviceTask
        if not self.devices:
            raise ValueError("selector: no devices at all")

        suitable_devices = []
        for device in self.devices:
            # add task to device if right if not nothing
            #TODO check if all specificDevices are in self.devices
            if device.name in task.specificDevices:
                suitable_devices.append(device)
        # return the list
        if len(suitable_devices) == 0:
            raise ValueError("selector: no devices")
        else: 
            return suitable_devices      
    
 #------------functions related to queue aspect---------------
    def taskInQueue(self, taskName):
        """!
        Check if task is in the task queue from selector.

        @param taskName string with task name
        @return booleanQueue boolean
        """
        booleanQueue = False
        for task in self._taskQueue:
            if task.taskName == taskName:
                booleanQueue = True
                break
        return booleanQueue

    def deleteTaskInQueue(self, taskName):
        """!
        Delete task from selectors task queue. Afterwards
        check if the DART-Server has capabilities for new tasks.

        @param taskName string with task name.
        """
        if self.taskInQueue(taskName):
            for task in self._taskQueue:
                if task.taskName == taskName:
                    self._taskQueue.remove(task)
        self.addTasks2Runtime()
            
    def addTask2Queue(self, task, priority = False):
        """!
        Add a new task to the queue. Task is already checked for feasibility

        @param task the task to be scheduled 
        """
        print("--------------add task----------------")
        if task in self._taskQueue:
            raise KeyError("Task already scheduled")

        # add task to queue
        if priority: 
            self._taskQueue.insert(0, task)
        else:
            self._taskQueue.append(task)
        self.addTasks2Runtime()

    def addTasks2Runtime(self):
        """!
        Check if the DART-Server has capabilities to schedule new task.
        Iterate over all task in the queue and check which task can be executed 
        at the moment. If yes instantiate aggregator for task and remove task from 
        queue
        """
        capacitynewTasks = self.runtime.get_Capacity_for_newTasks()
        for task in self._taskQueue:
            if capacitynewTasks <= 0:
                break
            if self.requestTaskAcceptance(task):
                aggregator = self.instantiateAggregator(task)
                aggregator.sendTask() 
                capacitynewTasks -= 1
                self.deleteTaskInQueue(task.taskName)  
                
from feddart.deviceSingle import DeviceSingle


class DeviceHolder():
    """!
    DeviceHolder is responsible for the device connection aspect of a task.
    Every access to device, which are associated to the deviceaggregator, 
    must go over the device holder.
    """ 
    
    def __init__( self
                , maxSize = 1
                ):
        """!
        @param maxSize maximal amount of devices for device holder
        @param deviceList list of associated devices
        """
        self._deviceList = []
        self._maxSize = maxSize
        self._devicesFinished = False

    @property
    def maxSize(self):
        """!
        property: maxSize. Implements the getter
        """
        return self._maxSize

    @property
    def deviceNames(self):
        """!
        property: device names. Implements the getter
        """
        return [str(device) for device in self._deviceList ]

    @property
    def devices(self):
        """!
        property: devices. Implements the getter
        """
        return self._deviceList

    @devices.setter
    def devices(self, newDevices):
        """!
        property: devices. Implements the setter

        @param newDevices the new list of devices
        """
        self._deviceList = newDevices

    def addDevice(self, newDevice, taskName, deviceParameterDict):
        """!
        Add a single device to device list and add task to this specific device
        @param newDevice instance of device
        @param tasName string with task name
        @param deviceParameterDict dict of format like {"arg1: 5, "arg2": 10}
        """
        if self.check_full():
            raise ValueError("DeviceHolder already full!")
        
        assert isinstance(newDevice, DeviceSingle), "Device must be an instance of DeviceSingle"
        newDevice.addTask(taskName, deviceParameterDict)
        self.devices.append(newDevice)

    def removeDevice(self, device):
        """!
        Remove device from the device list
        @param device to be removed
        """
        if device in self.devices:
            self.devices.remove(device)

    def check_full(self):
        """!
        Check if the devices list has reached maximum limit

        @return boolean
        """
        if len(self.devices) == self.maxSize:
            return True
        else:
            return False
    
    def check_empty(self):
        """!
        Check if devices list is empty

        @return boolean
        """
        if len(self.devices) == 0:
            return True
        else:
            return False

    def stopTask(self, taskName):
        """!
        Stop the task on each device from the deviceHolder.
        Remove the task from each device's open task dict
        and stop the task on the server.

        @param task instance of class task
        """
        if self.check_empty() == False:
            runtime = self.getRuntime()
            for device in self.devices:
                if device.isOpenTask(taskName):
                    device.removeOpenTask(taskName)
            runtime.stopTask(taskName)

    def getRuntime(self):
        """!
        Get the Runtime from one single device. We assume that all devices
        in DeviceHolder are connected to the same Runtime.

        @return  instance of class runtime
        """
        if self.check_empty():
            raise ValueError("No devices")
        else:
            device = self.devices[0]
            return device.dartRuntime

    def broadcastTask(self, task):
        """!
        Send the task at the same time to all devices
        in deviceHolder to minimze the number of requests to the server.
        To start a task, there must already be a job with the same name on the server 
        and the device must already have the task. 
        We assume that all devices in deviceHolder are connected to the same server.

        @param task instance of class task
        """
        runtime = self.getRuntime()
        #return 0 means unknown
        if runtime.get_job_status(task.taskName) == 0:
            runtime.add_job( task.taskName
                           , task.filePath
                           , task.executeFunction
                           )
        list_deviceNames = []
        list_deviceParameter = []
        taskName = task.taskName
        for device in self.devices:
            list_deviceNames.append(device.name)
            list_deviceParameter.append(device.getOpenTaskParameter(taskName))
        runtime.broadcastTaskToDevices( taskName
                                      , list_deviceNames
                                      , list_deviceParameter
                                      )

    def devicesFinished(self, taskName):
        """!
        Check how many devices have already finished the task
        and compare it against the total number of devices.

        @param string with task name
        @return self._devicesFinished boolean
        """
        if self._devicesFinished == False:
            total_devices = len(self.devices)
            number_finished_tasks = self.get_taskProgress(taskName)
            if number_finished_tasks == total_devices:
                self._devicesFinished = True
        return self._devicesFinished

    def get_OnlineDevices(self):
        """!
        Iterate over all devices and check if they are currently online.
        Append the online devices to a list.
        @return onlineDevices list of currently only devices.
        """
        onlineDevices = []
        if not self.devices:
            raise KeyError('no devices available')
        for device in self.devices:
            if device.is_online() == True:
                onlineDevices.append(device)
        return onlineDevices
  
    def get_finishedTasks(self, taskName):
        """!
        Iterate over all devices and get the result from devices,
        that have finished the task.
        @param taskName name of task

        @return list with instances of taskResult
        @todo look at point many queries to REST-API because every device looks on his own 
        Critical ?!
        """
        resultList = []
        for device in self.devices:
            if device.has_taskResult(taskName):
                device_result = device.get_taskResult(taskName)
                resultList.append(device_result)
        return resultList
        
    def get_taskProgress(self, taskName):
        """!
        Iterate over all devices and get a flag from devices,
        that have already finished the task.
        @param taskName string of task name

        @return number_finished_tasks int number of finished devices
        """
        number_finished_tasks = 0
        # has the task, because we add a device with task name and parameters
        for device in self.devices:
            if device.has_taskResult(taskName):
                number_finished_tasks += 1
        return number_finished_tasks

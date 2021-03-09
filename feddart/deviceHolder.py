from feddart.deviceSingle import DeviceSingle


class DeviceHolder():
    """!
    DeviceHolder is responsible for the device connection aspect of a task.
    Every access to device, which are associated to the deviceaggregator, 
    must go over the device holder.
    """ 
    def __init__( self
                , maxSize = 1
                , deviceList = []
                ):
        """!
        @param maxSize maximal amount of devices for device holder
        @param deviceList list of associated devices
        """
        if len(deviceList) > maxSize:
            raise ValueError("More than allowed devices")
        self._deviceList = deviceList
        self._maxSize = maxSize

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

    def addDevice(self, newDevice):
        """!
        Add a single device to device list.
        @param newDevice instance of device
        """
        if self.check_full():
            raise ValueError("DeviceHolder already full!")
        devices = self.devices
        devices = devices + [newDevice]
        self.devices = devices

    def removeDevice(self, device):
        if device in self._deviceList:
            self._deviceList.remove(device)

    def check_full(self):
        """!
        Check if the maximal amount of devices is already in deviceHolder

        @return boolean
        """
        if len(self.devices) == self.maxSize:
            return True
        else:
            return False
    
    def check_empty(self):
        """!
        Check if no devices is in deviceHolder

        @return boolean
        """
        if len(self.devices) == 0:
            return True
        else:
            return False

    def stopTask(self, task):
        """!
        Stop the task on each device from the deviceHolder.
        Remove the task from each device open task dict
        and stop the task on the server.

        @param task instance of class task
        """
        if self.check_empty() == False:
            runtime = self.getRuntime()
            taskName = task.taskName
            for device in self.devices:
                if device.isOpenTask(taskName):
                    device.removeOpenTask(taskName)
            runtime.stopTask(task.taskName)

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
        To start a task there must be already an job with the same name on the server 
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
            if device.hasTask(taskName):
                list_deviceNames.append(device.name)
                list_deviceParameter.append(device.getOpenTaskParameter(taskName))
            else:
                raise ValueError("Add the task " + taskName + " to device " + device.name +  " before starting the task!")
        runtime.broadcastTaskToDevices( taskName
                                      , list_deviceNames
                                      , list_deviceParameter
                                      )
        
    def syncTask(self, task):
        """!
        Send the task at the same time to all devices
        in deviceList. With sync we only update parameters 
        on the physical device, we don't expect a return.
        @param task instance of class task
        
        @todo this function can be used for the init task ?!
        """
        raise NotImplementedError("not implemented yet")

    def get_OnlineDevices(self):
        """!
        Iterate over all devices and check if they are currently online.
        Append the online devices to a list.
        @return onlineDevices list of currently only devices.
        """
        onlineDevices = []
        if not self._deviceList:
            raise KeyError('no devices available')
        for device in self.devices:
            if device.is_online() == True:
                onlineDevices.append(device)
        return onlineDevices

    def getFirstOnlineDevice(self):
        """!
        Check, which devices are currently online. Return the first one 
        from the list.
        @return a currently online device
        @todo there are smarter ways to get this information
        """
        return self.get_OnlineDevices()[0]
        
    def get_finishedTasks(self, taskName):
        """!
        Iterate over all devices and get the result from devices,
        which are alread finished.
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
        
    def get_taskStatus(self, taskName):
        """!
        Get the number of already finished devices and total amount of devices.
        If there are difference between these both values return "in progress" else
        "finished"

        @param taskName string of task name

        @return string "in progress" or "finished"
        """
        number_finished_tasks, maximal_finished_tasks = self.get_taskProgress(taskName)
        if number_finished_tasks < maximal_finished_tasks:
            return "in progress"
        else:
            return "finished"

    def get_taskProgress(self, taskName):
        """!
        Iterate over all devices and get a flag from devices,
        which already have finished the task.
        @param taskName string of task name

        @return number_finished_tasks int number of finished devices
        @return maximal_finished_tasks in total number of devices
        """
        number_finished_tasks = 0
        maximal_finished_tasks = 0
        for device in self.devices:
            if device.hasTask(taskName):
                maximal_finished_tasks += 1
                if device.has_taskResult(taskName):
                    number_finished_tasks += 1
        if maximal_finished_tasks == 0:
            raise ValueError("No device has the task", taskName)
        return number_finished_tasks, maximal_finished_tasks

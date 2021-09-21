class Collection:
    collectionID = 0
    def __init__( self
                , workflowManager
                , listDeviceNames = []
                ):
        """!
        @param maximal_number_devices maximal number of devices for this runtime
        """
        self._AllDeviceNames = listDeviceNames
        self._collectionID = Collection.collectionID
        self._workflowManager = workflowManager
        Collection.collectionID += 1

    @property
    def AllDeviceNames(self):
        """!
        property: listDeviceNames. Implements the getter
        """
        return self._AllDeviceNames

    @property
    def ActiveDeviceNames(self):
        """!
        property: listDeviceNames. Implements the getter
        """
        list_devices = self._workflowManager.getAllDeviceNames()
        activeDevices = []
        for deviceName in list_devices:
            if deviceName in self._AllDeviceNames:
                activeDevices.append(deviceName)
        return activeDevices

    @AllDeviceNames.setter
    def AllDeviceNames(self, listNewDeviceNames):
        """!
                property: listDeviceNames. Implements the setter
        """

        self._listDeviceNames = listNewDeviceNames

    @property
    def CollectionID(self):
        """!
        property: ClusterID. Implements the getter
        """
        return self._collectionID

    def addDevicebyName(self, deviceName):
        """!
        @param deviceName. Add deviceName to list with all device names
        """
        if deviceName not in self._AllDeviceNames:
            self._AllDeviceNames.append(deviceName)
        else:
            raise ValueError("Device with name " + deviceName +" already in collection!")

    def removeDevicebyName(self, deviceName):
        """!
        @param deviceName. Remove deviceName from list of device names.
        """
        if deviceName in self._AllDeviceNames:
            self._AllDeviceNames.remove(deviceName)
        else:
            raise ValueError("Device with name " + deviceName + " not in collection!")



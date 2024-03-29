from feddart.initTask import InitTask
from feddart.deviceSingle import DeviceSingle
from feddart.messageTranslator import MessageTranslator
from feddart.selector import Selector
import sys
import os
import requests
import json
from enum import Enum
from copy import deepcopy
from feddart.dart import Client, job_status

from feddart.logServer import LogServer
class DartRuntime:
    
    def __init__( self
                , server 
                , client_key
                , testMode
                , errorProbability
                , maximal_number_devices = -1
                , maximalNumberOpenJobs = 10
                , **kwargs
                ):
        """!
        @param maximal_number_devices maximal number of devices for this runtime
        @param maximalNumberOpenJobs maximal number of allowed maximal jobs
        @param registeredDevices dict with key device name and value instance of class device
        @param messageTranslator translator between Python and DART format
        @param selector instance of selector
        @param server     the server addr, e.g., "https://127.0.0.1:7777"
        @param client_key the key of the client for identification (unused atm)
        @param counterJobs int number of open jobs on server
        """
        if testMode:
            self._restAPIClient = Client(server, client_key, probability_error = errorProbability, testmode = True)
        else:
            self._restAPIClient = Client(server, client_key)
        self._maximal_number_devices = maximal_number_devices
        self._maximalNumberOpenJobs = maximalNumberOpenJobs
        self._registeredDevices = {}
        self._messageTranslator = MessageTranslator()
        self._selector = None
        self._counterJobs = 0 #in our case Jobs = Task
        
        self.logger = LogServer(__name__)
        self.logger.log().info("DartRuntime initiated")
    
    @property
    def restAPIClient(self):
        """!
        property: runtime. Implements the getter
        """
        return self._restAPIClient

    @property
    def registeredDevices(self):
        """!
        property: registeredDevices. Implements the getter
        """
        self.updateRegisteredDevices()
        return list(self._registeredDevices.values())

    @property
    def registeredDevicesbyName(self):
        """!
        property: registeredDevices. Implements the getter
        """
        self.updateRegisteredDevices()
        return list(self._registeredDevices.keys())

    @registeredDevices.setter
    def registeredDevices(self, newRegisteredDevices):
        """!
        property: registeredDevices. Implements the setter

        @param newRegisteredDevices the new list of registered devices
        """
        self._registeredDevices = newRegisteredDevices

    @property
    def selector(self):
        """!
        property: registeredDevices. Implements the getter
        """
        return self._selector

    @property
    def maximal_number_devices(self):
        """!
        property: maximal_number_devices. Implements the getter
        """
        return self._maximal_number_devices
    
    @maximal_number_devices.setter
    def maximal_number_devices(self, new_maximal_number_devices):
        """!
        property: maximal_number_devices. Implements the setter

        @param new_maximal_number_devices the new maximal number devices
        """
        self._maximal_number_devices = new_maximal_number_devices

    @property
    def maximalNumberOpenJobs(self):
        """!
        property: maximalNumberOpenJobs. Implements the getter
        """
        return self._maximalNumberOpenJobs
    
    @property
    def counterJobs(self):
        """!
        property: counterJobs. Implements the getter
        """
        return self._counterJobs

    def updateRegisteredDevices(self):
        """!
        Fetch from the DART-server the currently connected devices. If needed, create new
        virtual devices or delete them.
        """
        oldRegisteredDevicesbyName = deepcopy(list(self._registeredDevices.keys()))
        newRegisteredDevices = self.restAPIClient.get_workers()
        newRegisteredDevices = newRegisteredDevices["workers"]
        newRegisteredDevicesbyName = []
        for device in newRegisteredDevices:
            newRegisteredDevicesbyName.append(device["name"])
        for newDevice in newRegisteredDevicesbyName:
            if newDevice not in oldRegisteredDevicesbyName: #add new Devices
                initTask = None 
                if self.selector is not None:
                    initTask = self.selector.initTask
                device = DeviceSingle( name = newDevice
                                     , ipAdress = None
                                     , port = None
                                     , dartRuntime = self
                                     , physicalName = None
                                     , hardwareConfig = {}
                                     , taskDict = {}
                                     , initTask = initTask
                                     )
                self._registeredDevices[newDevice] = device
        for oldDevice in oldRegisteredDevicesbyName:
            if oldDevice not in newRegisteredDevicesbyName:
                del self._registeredDevices[oldDevice]

    def getServerInformation(self):
        """!
        Gets information about the servers.
        The return type has the following structure
        {'servers': [{'host': '<host_name>', 'port': '<port_name>'}]}
        """
        return self.restAPIClient.get_server_information()

    def get_Capacity_for_newTasks(self):
        """!
        The server have a maximal amount of simultaneously open jobs.
        Determine the difference between the maximal and curent amount.
        """
        return self.maximalNumberOpenJobs - self._counterJobs

    def get_TaskStatus(self, taskName):
        """!
        Get the status of the job from runtime. In our case is job the same
        as a task.

        @param taskName string with name of the task

        @return int 0 (unknown), 1 (running), 2 (stopped)
        """
        return self.restAPIClient.get_job_status(taskName)

    def remove_result_from_server(self, taskName, resultID):
        """!
        Remove a result with his ID from a job.

        @param taskName string with name of the task
        @resultID unique identifier for the task result of a specifif device
        """
        self.restAPIClient.delete_job_result(taskName, resultID)

    def get_TaskResult(self, taskName, deviceName):
        """!
        Send a regex pattern with the device name to the server and get maximal so many results 
        as devives are available. Extract the result and ID from the server message like
        { 'results': [{ 'id': '4d045be3-fb57-44f4-902f-b93abab3d830', 'job': 'task_one'
                      , 'worker': 'device_one-PSL188-1', 'start_time': '1611135657000'
                      , 'duration': '6.07332611', 'success': 'gASVHwAAAAAAAAB9lCiMCHJlc3VsdF8wlEsBjAhyZXN1bHRfMZRLCnUu\n'
                      }
                     ]
        , 'job': {'id': 'task_one', 'status': '1'}
        }
        with the messageTranslator.

        @param taskName string with task name
        @param deviceName string with devie name

        @return resultDevice dict with format {'duration': '6.07465839', 'result': {'result_0': 1, 'result_1': 10}}
        @return resultID string with format '5ad55670-3ad4-4bb9-99cc-2b82b85bd8c2'
        """
        maxNumberResults = len(self.registeredDevices)
        taskResult = self.restAPIClient.get_job_results(taskName, maxNumberResults, deviceName + ".*")
        resultDevice, resultID = self._messageTranslator.convertDart2Python(taskResult, deviceName)
        self.logger.log().debug("DartRuntime.get_TaskResult: " +  str(locals()))
        return resultDevice, resultID

    def instantiateSelector(self, max_size_deviceHolder):
        """!
        Create the Selector after starting the runtime

        @param max_size_deviceHolder maximal amount of device per deviceholder
        @param self._selector instance of class selector
        """
        self._selector = Selector(self, max_size_deviceHolder)
        return self._selector

    def add_SingleDevice( self, device):
        """!
        Add an already existing single device (one worker per device) to runtime. send directly the
        initTask to device.
        
        @param device device to be registered
        """
        self.logger.log().debug("dartRuntime.add_SingleDevice " + str(locals())) 
        if device.name in self._registeredDevices.keys():
            self.logger.log().error("device name already in list: " + device.name)
            raise KeyError("device name already in list")
        
        self._registeredDevices[device.name] = device
        #add workers is blocking!
        self.restAPIClient.add_worker( [device.ipAdress], 1, device.name, [""],0,{})
        if device.initTask is not None:
            device.startTask(device.initTask)
        #TODO Luca: where to specify port ?!
        self.logger.log().info("dartRuntime.add_SingleDevice " + device.name + " registered") 

    
    def generate_and_add_SingleDevice( self
                       , deviceName
                       , deviceIp
                       , port
                       , hardwareConfig
                       , initTask
                       ):
        """!
        Add a single device (one worker per device) to runtime. Therefore
        also create an instane of DeviceSingle. Afterwards send directly the
        initTask to device.
        
        @param deviceName string with device name
        @param deviceIp ip address of real physical device
        @param port port of real physical device
        @param hardware_config hardware properties like processor type, memory
               connection bandwith and so on
        @todo: specify hardwareConfig
        @param initTask instance of class initTask
        """
        self.logger.log().debug("dartRuntime.generate_and_add_SingleDevice " + str(locals())) 
        if deviceName in self._registeredDevices.keys():
            self.logger.log().error("device name already in list: " + deviceName)
            raise KeyError("device name already in list")
        device = DeviceSingle( name = deviceName
                             , ipAdress = deviceIp
                             , port = port
                             , dartRuntime = self
                             , physicalName = None
                             , hardwareConfig = hardwareConfig
                             , taskDict = {}
                             , initTask = initTask
                             )
        self._registeredDevices[deviceName] = device
        #add workers is blocking!
        self.restAPIClient.add_worker( [deviceIp], 1, deviceName, [""],0,{})
        if initTask is not None:
            device.addTask(initTask.taskName,  initTask.parameterDict)
            device.startTask(initTask)
        #TODO Luca: where to specify port ?!
        self.logger.log().info("dartRuntime.generate_and_add_SingleDevice " + deviceName + " registered") 

    def removeDevice(self, deviceName):
        """!
        Remove device from runtime and registeredDevice list.
        
        @param deviceName string with name of device
        @param device instance of device

        @todo good idea to destroy device ?
        """
        if deviceName not in self.registeredDevicesbyName:
            self.logger.log().error("device name not in list: " + deviceName)
            raise KeyError("device name is not in list")
        device = self.getDevice(deviceName)
        self.restAPIClient.remove_workers(device.ipAdress)
        del device #TODO: good idea to destroy device
        del self._registeredDevices[deviceName]

    def getDevice(self, deviceName):
        """!
        Get the instance of device by name.
        @param deviceName string with deviceName

        @return instance of device
        """
        if deviceName not in self.registeredDevicesbyName:
            self.logger.log().error("device name not in list: " + deviceName)
            raise KeyError("device name is not in list")
        return self._registeredDevices[deviceName]

    def get_job_status(self, jobName):
        """!
        The job status can have the values unknown, stopped
        or running. The status is translated into an int.

        @param jobName name of job. Equal to taskName

        @return int 0,1 or 2.
        @todo atm hacky.
        """
        jobStatus = self.restAPIClient.get_job_status(jobName)
        #TODO: ask Luca why return is job_status.unknown
        if jobStatus == job_status.unknown:
            return 0
        elif jobStatus == job_status.stopped:
            return 2
        else: 
            return 1
    
    def add_job(self, name, module_path, method):
        """!
        In our implemtation we start for every task an own job to have 
        a clear separation between different federated learning rounds
        
        @param name string with job/task name
        @module path relativ path to file based on default path in worker.json
        @method method with should be executed in file
        """
        self.restAPIClient.add_job(name, module_path, method)
        self._counterJobs += 1
        self.logger.log().info("added job: " + module_path + " " + 
                str(method) + " new #jobs: " + str(self._counterJobs))
        return
        
    def add_tasks(self, jobName, location_and_parameters):
        """!
        Add task to a job. We have for every task a new job. We specify
        for each device his own parameter.

        @param location_and_parameters list of form [ { 'location' : '...', 'parameter' : ' ...'}, ...]
        @todo this function can be removed ?!
        """
        self.restAPIClient.add_tasks(jobName, location_and_parameters)
        self.logger.log().error("added task: " + jobName + " " + str(location_and_parameters))

        return
        
    def broadcastTaskToDevices(self, taskName, deviceNamesList, parameterList):
        """!
        Send task to specified physical devices at the same time

        @param taskName string of task name
        @param deviceNamesList list of device names like ['device_one', 'device_two']
        @param parameterList specifies parameters for devices like 
               [{'param1': 0, 'param2': 1}, {'param1': 10, 'param2': 5}]
        """
        self.logger.log().debug("broadcastTaskToDevices")
        for deviceName in deviceNamesList:
            if deviceName not in self.registeredDevicesbyName:
                self.logger.log().error("broadcastTaskToDevices: " + deviceName + " is not known!")
                raise ValueError("Device with name " + deviceName + " is not known!")
        parameterDARTformat = self._messageTranslator.convertPython2Dart(deviceNamesList, parameterList)
        self.restAPIClient.add_tasks(taskName, parameterDARTformat)
        
    def get_ServerInformation(self):
        """!
        Return server informations

        @todo error messages in the moment
        """
        self.logger.log().debug("get_ServerInformation " + str(self.runtime.get_server_information()))
        return self.restAPIClient.get_server_information()
        
    def stopTask(self, taskName):
        """!
        Stop a task/job on the server. Therefore also
        decrease the counter of Jobs on the server.

        @param taskName string with task name
        """
        self._counterJobs -= 1
        self.restAPIClient.stop_job(taskName)
        self.logger.log().debug("stopTask " + taskName + " new #jobs: " + str(self._counterJobs))

    def stopRuntime(self):
        """!
        Stop the server.
        """
        self.restAPIClient.stop_servers()
        
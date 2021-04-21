from feddart.deviceSingle import DeviceSingle
from feddart.messageTranslator import MessageTranslator
from feddart.selector import Selector
import sys
import os
import requests
import json
from enum import Enum
from feddart.dart import Client, job_status
from feddart.dummydart import dummyClient, dummy_job_status

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
            self._runtime = dummyClient(server, client_key, errorProbability)
        else:
            self._runtime = Client(server, client_key)
        self._maximal_number_devices = maximal_number_devices
        self._maximalNumberOpenJobs = maximalNumberOpenJobs
        self._registeredDevices = {}
        self._messageTranslator = MessageTranslator()
        self._selector = None
        self._counterJobs = 0 #in our case Jobs = Task
        print("dart runtime instantiated")
    
    @property
    def runtime(self):
        """!
        property: runtime. Implements the getter
        """
        return self._runtime

    @property
    def registeredDevices(self):
        """!
        property: registeredDevices. Implements the getter
        """
        return list(self._registeredDevices.values())

    @property
    def registeredDevicesbyName(self):
        """!
        property: registeredDevices. Implements the getter
        """
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

    def getServerInformation(self):
        """!
        Gets information about the servers.
        The return type has the following structure
        {'servers': [{'host': '<host_name>', 'port': '<port_name>'}]}
        """
        return self.runtime.get_server_information()

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
        return self.runtime.get_job_status(taskName)

    def remove_result_from_server(self, taskName, resultID):
        """!
        Remove a result with his ID from a job.

        @param taskName string with name of the task
        @resultID unique identifier for the task result of a specifif device
        """
        self.runtime.delete_job_result(taskName, resultID)

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
        taskResult = self.runtime.get_job_results(taskName, maxNumberResults, deviceName + ".*")
        resultDevice, resultID = self._messageTranslator.convertDart2Python(taskResult, deviceName)
        return resultDevice, resultID

    def instantiateSelector(self, max_size_deviceHolder):
        """!
        Create the Selector after starting the runtime

        @param max_size_deviceHolder maximal amount of device per deviceholder
        @param self._selector instance of class selector
        """
        self._selector = Selector(self, max_size_deviceHolder)
        print("selector instantiated")
        return self._selector

    
    def addSingleDevice( self
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
        if deviceName in self._registeredDevices.keys():
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
        self.runtime.add_workers( [deviceIp], 1, deviceName, [""],0,{})
        if initTask is not None:
            device.addTask(initTask.taskName,  initTask.parameterDict)
            device.startTask(initTask)
        #TODO Luca: where to specify port ?!
        print(deviceName, "registered") 

    def removeDevice(self, deviceName):
        """!
        Remove device from runtime and registeredDevice list.
        
        @param deviceName string with name of device
        @param device instance of device

        @todo good idea to destroy device ?
        """
        if deviceName not in self.registeredDevicesbyName:
            raise KeyError("device name is not in list")
        device = self.getDevice(deviceName)
        self.runtime.remove_workers(device.ipAdress)
        del device #TODO: good idea to destroy device
        del self._registeredDevices[deviceName]

    def getDevice(self, deviceName):
        """!
        Get the instance of device by name.
        @param deviceName string with deviceName

        @return instance of device
        """
        if deviceName not in self.registeredDevicesbyName:
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
        jobStatus = self.runtime.get_job_status(jobName)
        #TODO: ask Luca why return is job_status.unknown
        if jobStatus == job_status.unknown or jobStatus == dummy_job_status.unknown:
            return 0
        elif jobStatus == job_status.stopped or jobStatus == dummy_job_status.stopped:
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
        self.runtime.add_job(name, module_path, method)
        self._counterJobs += 1
        
    def add_tasks(self, jobName, location_and_parameters):
        """!
        Add task to a job. We have for every task a new job. We specify
        for each device his own parameter.

        @param location_and_parameters list of form [ { 'location' : '...', 'parameter' : ' ...'}, ...]
        @todo this function can be removed ?!
        """
        self.runtime.add_tasks(jobName, location_and_parameters)
        
    def broadcastTaskToDevices(self, taskName, deviceNamesList, parameterList):
        """!
        Send task to specified physical devices at the same time

        @param taskName string of task name
        @param deviceNamesList list of device names like ['device_one', 'device_two']
        @param parameterList specifies parameters for devices like 
               [{'param1': 0, 'param2': 1}, {'param1': 10, 'param2': 5}]
        """
        for deviceName in deviceNamesList:
            if deviceName not in self.registeredDevicesbyName:
                raise ValueError("Device with name " + deviceName + " is not known!")
        parameterDARTformat = self._messageTranslator.convertPython2Dart(deviceNamesList, parameterList)
        self.runtime.add_tasks(taskName, parameterDARTformat)
        
    def get_ServerInformation(self):
        """!
        Return server informations

        @todo error messages in the moment
        """
        return self.runtime.get_server_information()
        
    def stopTask(self, taskName):
        """!
        Stop a task/job on the server. Therefore also
        decreas the counter of Jobs on the server.

        @param taskName string with task name
        """
        self._counterJobs -= 1
        self._runtime.stop_job(taskName)

    def stopRuntime(self):
        """!
        Stop the server.
        """
        self._runtime.stop_servers()
        
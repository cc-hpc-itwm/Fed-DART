import json
from enum import Enum
from importlib import import_module
import random
import time
import os

### obsolete - already in dart ###
class dummy_job_status(Enum):
    """! 
    Same class as class job_status in dart.py
    """
    unknown = 0
    running = 1
    stopped = 2

class Worker:
    """! 
    The class worker is responsible for
    storing all informations of the real worker.
    This class is needed because we have a dummy runtime
    without connection to real workers.
    """
         
    def __init__( self
                , key
                , hosts
                , worker_per_host
                , worker_name
                , capabilities
                , shm_size
                ):
        """!
        @param key not needed for dummy runtime
        @param hosts string with device name
        @param worker_per_host amount of worker
        @param worker_name string with worker name
        @param capabilities string with worker capability
        @param shm_size shared memory size
        """
        self.key = key 
        self.hosts = hosts
        self.worker_per_host = worker_per_host
        self.worker_name = worker_name
        self.capabilities = capabilities
        self.shm_size = shm_size

class Job:
    """!
        Stores all relevant info about a job
    """
    RESULTS = 'results'
    ID = 'id'

    def __init__( self
                , name
                , module_path
                , method
                ):
        """!
        @param name job name
        @param module_path path to file, which should be executed
        @param method executable function
        @param task_list list with open tasks
        @param resultDict dict storage of results analog to real dart-server
        """
        self.name = name
        self.module_path = module_path
        self.method = method
        self.task_list = []
        self.resultDict = {}
        self.resultDict[Job.RESULTS] = []
        self.resultDict['job'] = {Job.ID: self.name, 'status': '1'}

    def get_new_task_id(self):
        """
        Creates a unique task id.

        @return: New unique task id
        """
        if self.resultDict[Job.RESULTS]:
            return max(d[Job.ID] for d in self.resultDict[Job.RESULTS]) + 1
        else:
            return 0

    def start_computation(self):
        """!
            Iterate over the open task and get the function, which should be
            executed on each worker. Afterwards we store the results and meta
            informations in the resultDict. The task_list is finally cleared, because
            the task were executed.
        """
        if len(self.task_list) == 0:
            raise ValueError("No entry in task list!")
        #sequentical execution
        for task in self.task_list:
            path_file = task.worker.hosts + "/" + self.module_path
            path_file = path_file.replace("/", ".")
            imp = import_module(path_file)
            execute_function = getattr(imp, self.method)
            startTime = time.time()
            result = execute_function(task.parameter)
            endTime = time.time()
            duration = endTime - startTime
            taskResultDict = {}
            taskResultDict[Job.ID] = self.get_new_task_id()
            taskResultDict['job'] = self.name 
            taskResultDict['host'] = task.worker.hosts
            taskResultDict['worker'] = task.worker.worker_name + "-" + task.worker.hosts
            taskResultDict['start_time'] = startTime
            taskResultDict['duration'] = duration
            taskResultDict['success'] = result
            self.resultDict[Job.RESULTS].append(taskResultDict)
        #parallel exection: issues on windows, which uses spawn instead of fork
        #--> atm not supported
        """
        list_function = []
        list_parameters = []
        for task in self.task_list:
            path_file = task.worker.hosts + "/" + self.module_path
            path_file = path_file.replace("/", ".")
            imp = import_module(path_file)
            execute_function = getattr(imp, self.method)
            list_function.append(execute_function)
            list_parameters.append(task.parameter)
        list_futures = []
        with ProcessPoolExecutor(max_workers = 1) as executor:
            for function, parameters in zip(list_function, list_parameters):
                list_futures.append(executor.submit(function, parameters))
        result_list = [ f.result for f in list_futures]
        print(result_list)
        startTime = time.time()
        result = execute_function(task.parameter)
        endTime = time.time()
        duration = endTime - startTime
        taskResultDict = {}
        taskResultDict['id'] = random.randint(0,10000000)
        taskResultDict['job'] = self.name 
        taskResultDict['host'] = task.worker.hosts
        taskResultDict['worker'] = task.worker.capabilities + "-" + task.worker.hosts
        taskResultDict['start_time'] = startTime
        taskResultDict['duration'] = duration
        taskResultDict['success'] = result
        self.resultDict['results'].append(taskResultDict)
        """
        self.task_list = []

    def delete(self, resultID):
        """!
        Delete a task result from resultDict
        @param resultID int with ID
        """
        for taskResult in self.resultDict[Job.RESULTS]:
            if taskResult[Job.ID] == resultID:
                self.resultDict[Job.RESULTS].remove(taskResult)


class Task:
    """! Stores information about where and with what parameters the
         the task should be executed.
    """
    def __init__( self
                , worker
                , parameter
                ):
        """!
        @param worker instance of class worker
        @param parameter parameter of task
        """
        self.worker = worker
        self.parameter = parameter
		
import json
from enum import Enum
from importlib import import_module
import random
import time
from concurrent.futures import ProcessPoolExecutor

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
    This class is needede because we have a dummy runtime
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
        Stores all relevant infos about a job
    """
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
        @param resultDict dict storage of resules analog to real dart-server
        """
        self.name = name
        self.module_path = module_path
        self.method = method
        self.task_list = []
        self.resultDict = {}
        self.resultDict['results'] = []
        self.resultDict['job'] = {'id': self.name, 'status': '1'}

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
            taskResultDict['id'] = random.randint(0,10000000)
            taskResultDict['job'] = self.name 
            taskResultDict['host'] = task.worker.hosts
            taskResultDict['worker'] = task.worker.worker_name + "-" + task.worker.hosts
            taskResultDict['start_time'] = startTime
            taskResultDict['duration'] = duration
            taskResultDict['success'] = result
            self.resultDict['results'].append(taskResultDict)
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
        for taskResult in self.resultDict['results']:
            if taskResult['id'] == resultID:
                self.resultDict['results'].remove(taskResult)


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
		

class dummyClient:
    """! For a test modus, we want to have folders as workers.
         The dummyClient class handles this setting with the same
         API of a real dart server.
    """
    def __init__(self, server, client_key, probability_error):
        """!
        @param server not needed
        @param client_key not needed
        @param probability_error float between 0 and 1. Probability
        how often the dummyClient will throw error messages
        @param worker_list list with worker instances
        @param job_list list with jobs instances
        """
        self.server = server
        self.key = client_key
        self.probability_error = probability_error
        self.worker_list = []
        self.job_list = []
		
    def getJob(self, jobName):
        """!
            Get the job instance by name
        """
        for job in self.job_list:
            if job.name == jobName:
               return job
	
    def stop_servers(self):
        if random.uniform(0,1) < self.probability_error:
            raise Exception('response not ok')
			
    def get_server_information(self):
        """!
        at the moment not supported by real dart server
        """
        raise NotImplementedError("not implemented yet!")
			
    def add_workers( self
                   , hosts
                   , workers_per_host
                   , worker_name
                   , capabilities
                   , shm_size
                   , ssh = {}
                   ):
        """!
        @param hosts list with host names
        @param workers_per_host int
        @param capabilities list with device names
        @param shm_size shared memory size
        """
        #capabilities, hosts is a list, unzip it
        for host, capability in zip(hosts, capabilities):
            worker = Worker( self.key
                           , host
                           , workers_per_host
                           , worker_name
                           , capability
                           , shm_size
                           )
            self.worker_list.append(worker)
        if random.uniform(0,1) < self.probability_error:
                raise Exception('response not ok')

    def remove_workers(self, hosts, ssh = {}):
        """!
        @param hosts name of host
        """
        for worker in self.worker_list:
            if worker.hosts == hosts:
                self.worker_list.remove(worker) 
        if random.uniform(0,1) < self.probability_error:
            raise Exception('response not ok')

    def add_job(self, name, module_path, method):
        """!
        Create instance of Job and add it to job list.
        @param name job name
        @param module_path string with root path for executable functions
        @param method method which should be executed
        """
        job = Job( name
                 , module_path
                 , method
                 )
        self.job_list.append(job)
        if random.uniform(0,1) < self.probability_error:
            raise Exception('response not ok')

    def add_tasks(self, jobName, location_and_parameters):
        """!
        Add task to existing job.Afterwards execute the task
        @param jobName string with job name
        @param location_and_parameters list of format [ { 'location' : '...', 'parameter' : ' ...'}, ...]
        """
        rightJob = self.getJob(jobName)
        for task in location_and_parameters:
            workerName = task['location']
            taskParameter = task['parameter']
            for worker in self.worker_list:
                if worker.worker_name == workerName:
                    task = Task( worker
                               , taskParameter
                               )      
                    rightJob.task_list.append(task)
        if random.uniform(0,1) < self.probability_error:
            raise Exception('response not ok')
        else:
            rightJob.start_computation()
			 
    def get_job_info(self, job):
        raise NotImplementedError("not implemented yet!")
			
    def stop_job(self, jobName):
        """!
        Stops a job
        @param jobName string with job name
        """
        rightJob = self.getJob(jobName)
        self.job_list.remove(rightJob)
        if random.uniform(0,1) < self.probability_error:
            raise Exception('response not ok')
	
    def get_job_status(self, jobName):
        """!
        Gets the status of a job
        @param jobName string with job name
        """
        job_exists = False
        for job in self.job_list:
            if job.name == jobName:
                job_exists = True
        if job_exists == False:
            return dummy_job_status(0)
        if random.uniform(0,1) < self.probability_error:
            raise Exception('response not ok')
        else:
            return dummy_job_status(1)
	
    def get_job_results(self, jobName, amount, worker_regex = ""):
        """!
        At the moment we return all results of a job. From a point of performance that's 
        not perfect, but for a test mode we assume a small number of workers. Therefore
        this aspect is not relevant.
        @param jobName string with job name
        @param amount int of amount of results. Ignored at the moment
        @param worker_regex ignored at the moment
        """
        rightJob = self.getJob(jobName)
        if random.uniform(0,1) < self.probability_error:
            raise Exception('response not ok')
        return rightJob.resultDict
	
    def delete_job_result(self, jobName, resultID):
        """!
        Removes a job result by ID
        @param jobName string with job name
        @param resultID int of id
        """
        rightJob = self.getJob(jobName)
        rightJob.delete(resultID)
        if random.uniform(0,1) < self.probability_error:
            raise Exception('response not ok')
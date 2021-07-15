import requests
import json
from enum import Enum

from feddart.dummydart import Worker, Job, Task
from feddart.logServer import LogServer

import random 

class job_status(Enum):
    unknown = 0
    running = 1
    stopped = 2

class Client:
    ##
    # Initializes the client
    # @param server     the server addr, e.g., "https://127.0.0.1:7777"
    # @param client_key the key of the client for identification (unused atm)
    def __init__(self, server, client_key, probability_error = 0, testmode = False):
        self.server = server
        self.key = client_key
        self.logger = LogServer(__name__)
        self.logger.log().info("dart client initialized")
        self.testmode = testmode

        if self.testmode:
            
            self.probability_error = probability_error
            self.worker_list = []
            self.job_list = []

    def getJob(self, jobName):
        """!
            Get the job instance by name - used in testmode
        """
        self.logger.log().info("Client.getJob: " + jobName)
        for job in self.job_list:
            if job.name == jobName:
               return job

        self.logger.log().info("Client.getJob: " + jobName + " not found")
        return None

    ##
    # Stop the servers
    def stop_servers(self):
        """!
        testmode: simulate false request codes 
        """
        self.logger.log().info("Client.stop_servers")
        if self.testmode:
            if random.uniform(0,1) < self.probability_error:
                raise Exception('response not ok')
            return

        r = requests.delete(self.server + "/server/", json={'key': self.key}, verify=False)
        if r.status_code != requests.codes.ok:
            raise Exception('response not ok')
        
    ##
    # Gets information about the servers
    #
    # The return type has the following structure
    # {
    #   'servers' : [
    #     {'host' : '<host_name>', 'port' : '<port_name>'}
    #   ]
    # }
    def get_server_information(self):
        if self.testmode:
            raise NotImplementedError("not implemented yet!")
        else:
            r = requests.get(self.server + "/server/", json={'key': self.key}, verify=False)
            if r.status_code != requests.codes.ok:
                raise Exception('response not ok')

            return json.loads(r.content)
        
    ##
    # Adds workers
    #
    # @param hosts            list of all the hosts
    # @param workers_per_host the amount of workers to add per host
    # @param name             the name of the worker
    # @param capabilities     list of the capabilities of the workers
    # @param shm_size         shared memory size
    # @param ssh_options      an object with the following attributes 
    #                         { "username": "...", "port": "...", "public-key": "...", "private-key": "..." }
    def add_worker(self, hosts, workers_per_host, worker_name, capabilities, shm_size, ssh = {}):
        self.logger.log().debug("Client.add_worker " + str(locals()))
        if self.testmode:
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
                self.logger.log().error("Client.add_worker: could not add worker " + str(locals()))
                raise Exception('response not ok')
        else:
            r = requests.post(self.server + "/worker/", json={
                'key': self.key
                , 'name': worker_name
                , 'hosts': hosts
                , 'workers_per_host': workers_per_host
                , 'capabilities': capabilities
                , 'shm_size': shm_size
                , 'ssh': ssh
            }, verify=False)
            if r.status_code != requests.codes.ok:
                self.logger.log().error("Client.add_worker: could not add worker " + str(locals()))
                raise Exception('response not ok')

    ##
    # Removes workers from the specified hosts
    #
    # @param hosts a list of hosts
    # @param ssh_options      an object with the following attributes { "username": "...", "port": "...", "public-key": "...", "private-key": "..." }
    def remove_workers(self, hosts, ssh = {}):
        if self.testmode:
            for worker in self.worker_list:
                if worker.hosts == hosts:
                    self.worker_list.remove(worker) 
            if random.uniform(0,1) < self.probability_error:
                raise Exception('response not ok')
        else:
            r = requests.delete(self.server + "/worker/", json={
                'key': self.key
                , 'hosts': hosts
                , 'ssh': ssh
            }, verify=False)
            if r.status_code != requests.codes.ok:
                raise Exception('response not ok')


    ##
    # Get workers
    #
    # @param hosts            list of all the hosts
    # @param workers_per_host the amount of workers to add per host
    # @param name             the name of the worker
    # @param capabilities     list of the capabilities of the workers
    # @param shm_size         shared memory size
    def get_workers(self):
        if self.testmode:
            list_worker = []
            for worker in self.worker_list:
                dict_worker = {}
                dict_worker['name'] = worker.worker_name
                dict_worker['count'] = 1
                dict_worker['capabilities'] = ''
                list_worker.append(dict_worker)
            return {'workers': list_worker}
        else: 
            r = requests.get(self.server + "/worker/", json={
                'key': self.key
            }, verify=False)
            if r.status_code != requests.codes.ok:
                raise Exception('response not ok')
            return json.loads(r.content)

    ##
    # Adds a job definition
    #
    # @param name        the name of the job
    # @param module_path the path to the module on the clients
    # @param method      the method from the module to execute
    def add_job(self, name, module_path, method):
        if self.testmode:
            job = Job( name
                 , module_path
                 , method
                 )
            self.job_list.append(job)
            if random.uniform(0,1) < self.probability_error:
                raise Exception('response not ok')
        else:        
            r = requests.post(self.server + "/job/", json={
                'key': self.key
            , 'name' : name
            , 'module_path' : module_path
            , 'method' : method
            }, verify=False)
            if r.status_code != requests.codes.ok:
                raise Exception('response not ok')

    ##
    # Adds tasks to a job
    #
    # @param jobName              the name of the job
    # @param location_and_parameters [ { 'location' : '...', 'parameter' : ' ...'}, ...] list
    def add_tasks(self, jobName, location_and_parameters):
        if self.testmode:
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
            if random.uniform(0, 1) < self.probability_error:
                raise Exception('response not ok')
            else:
                rightJob.start_computation()
        else:    
            r = requests.post(self.server + "/job/" + jobName + "/tasks/", json={
                'key': self.key
            , 'location_and_parameters' : location_and_parameters
            }, verify=False)
            if r.status_code != requests.codes.ok:
                raise Exception('response not ok')

    ##
    # Gets information about a job
    #
    # The return type has the following structure
    # {
    #   'job' : {
    #     'id' : '....',
    #     'status' : '...',
    #     'config' : { 
    #        'python_home' : '...', 
    #        'output_directory' : '...', 
    #        'module' : '...',
    #        'is_module_path' : '...',
    #        'method' : '...'
    #     }
    #   }
    # }
    #
    # @param job  the name of the job
    def get_job_info(self, jobName):
        if self.testmode:
            raise NotImplementedError("not implemented yet!")
        else:
            r = requests.get(self.server + "/job/" + jobName + "/", json={'key': self.key}, verify=False)
            if r.status_code != requests.codes.ok:
                raise Exception('response not ok')
            return json.loads(r.content)
        
    ##
    # Stops a job
    #
    # @param job the job name
    def stop_job(self, jobName):
        if self.testmode:
            rightJob = self.getJob(jobName)
            self.job_list.remove(rightJob)
            if random.uniform(0, 1) < self.probability_error:
                raise Exception('response not ok')
        else:
            r = requests.delete(self.server + "/job/" + jobName + "/", json={'key': self.key}, verify=False)
            if r.status_code != requests.codes.ok:
                raise Exception('response not ok')
    
    ##
    # Gets the job status of a job
    #
    # @return the job status
    def get_job_status(self, jobName):
        if self.testmode:
            job_exists = False
            for job in self.job_list:
                if job.name == jobName:
                    job_exists = True

            if job_exists == False:
                return job_status(0)
            if random.uniform(0, 1) < self.probability_error:
                raise Exception('response not ok')
            else:
                return job_status(1)
        else:
            r = requests.get(self.server + "/job/" + jobName + "/status/", json={'key': self.key}, verify=False)
            if r.status_code == requests.codes.not_found:
                return job_status.unknown
            if r.status_code != requests.codes.ok:
                raise Exception('response not ok')
            response = json.loads(r.content)
            return job_status(int(response['job']['status']))
    
    ##
    # Gets results of the specified job
    #
    # Gets at most 'amount' different job results. Note that
    # this function does not delete the results from the
    # server. Hence, successive calls will return the same
    # results.
    #
    # The return type has the following structure
    # {
    #   'results' : [
    #       {
    #         'id' : '...',
    #         'job' : '...',
    #         'worker' : '...',
    #         'start_time' : '...',
    #         'duration' : '...',
    #         'success' : '...' or 'error' : '...'
    #       },
    #       {
    #           ...
    #       },
    #       ...
    #   ],
    #   'job' : { 'id' : '...', 'status' : '...'}
    # }
    #
    # @param job          the job name 
    # @param amount       the maximal amounts of jobs to get
    # @param worker_regex a regex that the worker of the result has to match. Empty regex matches everything.
    def get_job_results(self, jobName, amount, worker_regex = ""):
        if self.testmode:
            rightJob = self.getJob(jobName)
            if random.uniform(0, 1) < self.probability_error:
                raise Exception('response not ok')
            if rightJob:
                return rightJob.resultDict
            else:
                print("no such an job is running on server")
                return {'results': [], 'job':{}}
        else:
            r = requests.get(self.server + "/job/" + jobName + "/results/", json={
                'key': self.key
            , 'amount' : amount
            , 'worker_regex' : worker_regex
            }, verify=False)
            if r.status_code != requests.codes.ok:
                raise Exception('response not ok')
            return json.loads(r.content)
    
    ##
    # Removes a job result from the server
    #
    # @param job    the name of the job
    # @param result the id of the result
    def delete_job_result(self, jobName, resultID):
        if self.testmode:
            rightJob = self.getJob(jobName)
            rightJob.delete(resultID)
            if random.uniform(0, 1) < self.probability_error:
                raise Exception('response not ok')
        else:
            r = requests.delete(self.server + "/job/" + jobName + "/results/" + resultID +"/" , 
                                json={'key': self.key}, verify=False)
            if r.status_code != requests.codes.ok:
                raise Exception('response not ok')
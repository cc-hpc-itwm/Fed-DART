import requests
import json
from enum import Enum

class job_status(Enum):
  unknown = 0
  running = 1
  stopped = 2

class client:
  ##
  # Initializes the client
  # @param server     the server addr, e.g., "https://127.0.0.1:7777"
  # @param client_key the key of the client for identification (unused atm)
  def __init__(self, server, client_key):
    self.server = server
    self.key = client_key
    
  ##
  # Stops the servers
  def stop_servers(self):
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
  # @param ssh_options      an object with the following attributes { "username": "...", "port": "...", "public-key": "...", "private-key": "..." }
  def add_worker(self, hosts, workers_per_host, name, capabilities, shm_size, ssh = {}):
    r = requests.post(self.server + "/worker/", json={
          'key': self.key
        , 'name': name
        , 'hosts': hosts
        , 'workers_per_host': workers_per_host
        , 'capabilities': capabilities
        , 'shm_size': shm_size
        , 'ssh': ssh
      }, verify=False)
    if r.status_code != requests.codes.ok:
      raise Exception('response not ok')

  ##
  # Removes workers from the specified hosts
  #
  # @param hosts a list of hosts
  # @param ssh_options      an object with the following attributes { "username": "...", "port": "...", "public-key": "...", "private-key": "..." }
  def remove_workers(self, hosts, ssh = {}):
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
  # @param job                     the name of the job
  # @param location_and_parameters [ { 'location' : '...', 'parameter' : ' ...'}, ...] list
  def add_tasks(self, job, location_and_parameters):
    r = requests.post(self.server + "/job/" + job + "/tasks/", json={
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
  def get_job_info(self, job):
    r = requests.get(self.server + "/job/" + job + "/", json={'key': self.key}, verify=False)
    if r.status_code != requests.codes.ok:
      raise Exception('response not ok')
    return json.loads(r.content)
      
  ##
  # Stops a job
  #
  # @param job the job name
  def stop_job(self, job):
    r = requests.delete(self.server + "/job/" + job + "/", json={'key': self.key}, verify=False)
    if r.status_code != requests.codes.ok:
      raise Exception('response not ok')
  
  ##
  # Gets the job status of a job
  #
  # @return the job status
  def get_job_status(self, job):
    r = requests.get(self.server + "/job/" + job + "/status/", json={'key': self.key}, verify=False)
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
  def get_job_results(self, job, amount, worker_regex = ""):
    r = requests.get(self.server + "/job/" + job + "/results/", json={
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
  def delete_job_result(self, job, result):
    r = requests.delete(self.server + "/job/" + job + "/results/" + result +"/" , 
                        json={'key': self.key}, verify=False)
    if r.status_code != requests.codes.ok:
      raise Exception('response not ok')
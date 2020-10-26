import os
import socket
import sys
import time
import ports as ports
import json
import pickle
import time
from itertools import chain
HOME = os.environ['HOME']
USER = os.environ['USER']
HOST = socket.gethostname() #Return a string containing the hostname of the machine where the Python interpreter is currently executing

def import_dart_lib():
    sys.path.insert(0, os.environ['DART_HOME'] + '/lib')
    from dart import dart_context
    return dart_context

def create_ssh_variables():
    import local_configuration as lc
    ssh_config_path = lc.get_ssh_config_path()
    ssh_private_key = lc.get_ssh_private_key()
    ssh_public_key = lc.get_ssh_public_key()
    
    port = 22
    if ssh_config_path != "":
        f = open(ssh_config_path, "r")
        c = ports.parse_ssh_config(f)
        hosts=[]
        for h in c.get_hostnames():
            if h == HOST: 
                host = ports.lookup_ssh_host_config(h, c)
                port = int(host['port'])
    return ssh_public_key, ssh_private_key, port

class Runtime:
    worker_number = 0
    def __init__(self):
        dart_context  = import_dart_lib()
        ssh_public_key, ssh_private_key, port = create_ssh_variables()
        directory_python_files = sys.exec_prefix #directory where platform-dependent python files are installed
        self.dc = dart_context ( directory_python_files 
                               , monitor_url = "."
                               , ssh_username = USER
                               , ssh_port = port
                               , ssh_public_key = ssh_public_key
                               , ssh_private_key = ssh_private_key
                               )
        self.nodefile_devices = {}
        self.dc_active = False
       
    def terminate(self):
        self.dc.stop()
    
    def add_device( self
                  , host
                  , workers_per_host
                  , name_edge_device
                  , shm_size
                  , port
                  ):
        """ add_device starts the runtime in the case it is not already started
            else it adds the device during runtime
        """
        if self.dc_active == False:
            current_nodefile = self._extend_nodefile_devices( host
                                                            , workers_per_host
                                                            , name_edge_device
                                                            , shm_size
                                                            , port
                                                            )
            nodefile = os.getcwd() +  '/nodefile_bml' #TODO: remove in future in the moment dc.start can only read nodefile
            with open(nodefile, 'w') as outfile:
                json.dump(current_nodefile, outfile)
            self.dc.start(nodefile) #its necessary in the moment to start from a nodefile as a real file
            self.nodefile_devices.update(current_nodefile)
            self.dc_active = True
        else:
            current_nodefile = self._extend_nodefile_devices( host
                                                            , workers_per_host
                                                            , name_edge_device
                                                            , shm_size
                                                            , port
                                                            )
            nodefile = os.getcwd() +  '/nodefile_bml' #TODO: remove in future in the moment dc.start can only read nodefile
            with open(nodefile, 'w') as outfile:
                json.dump(current_nodefile, outfile)
            self.dc.add_workers(nodefile)
            self.nodefile_devices.update(current_nodefile)
            
    def _extend_nodefile_devices( self
                                , host
                                , workers_per_host
                                , name_edge_device
                                , shm_size
                                , port
                                ):
        #complicated, but necessary in the moment
        paras = {}
        nodefile_devices = {}
        paras["capabilities"] = [name_edge_device]
        paras["num_per_node"] = workers_per_host
        paras["shm_size"] = shm_size
        paras["port"] = port
        paras["hosts"] = [host]
        nodefile_devices["worker"+str(Runtime.worker_number)] = paras
        Runtime.worker_number += 1
        return nodefile_devices

    def send_task( self
                 , connection_request
                 ):
        """ Sends task to one device, such that every device has it own handle
        """
        handle = self.dc.async_run( connection_request.get_entry_point()
                                  , 'execute_function'
                                  , [connection_request.get_data()]
                                  )
        return handle

    def broadcast_task( self, list_connection_requests):
        """ Sends task to mutiple device, such that we have only one handle
        """
        handle = self.dc.async_run( list_connection_requests[0].get_entry_point()
                                  , 'execute_function'
                                  , [ connection_request.get_data() for connection_request in list_connection_requests ]
                                  )
        return handle

    def get_task(self, start_time_task, timeout, handle):
        """ Try to get the result from device back. If
            the computation takes too long, return TIMEOUT
        """
        result_dict = {}
        result = self.dc.results.pop (handle)
        current_time = time.time()
        duration = current_time - start_time_task
        if duration > timeout:
            return 'TIMEOUT'
        else:
            current_duration = time.time() - current_time
            while result and current_duration < 0.1 :
                if 'error' not in result.keys():
                    result_list = []
                    for res in result['result'].values():
                        result_list.append(res)
                    res_dict = {}
                    res_dict['result'] = result_list[:-1]
                    res_dict['function'] = result_list[-1]
                    result_dict[result['location']] = res_dict
                result = self.dc.results.pop (handle)
                current_duration = time.time() - current_time
            return result_dict

        
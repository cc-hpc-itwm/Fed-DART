import os
import socket
import sys
import time
import json
import pickle
import time
from itertools import chain
def import_dart_lib():
    sys.path.insert(0, os.environ['DART_HOME'] + '/lib')
    from dart import dart_context
    return dart_context

class Runtime:
    worker_number = 0
    def __init__(self, **kwargs):
        dart_context  = import_dart_lib()
        directory_python_files = sys.exec_prefix #directory where platform-dependent python files are installed

        print("Starting runtime with user:", kwargs["ssh_username"], ", port:", kwargs["ssh_port"],
            ", ssh_public_key:", kwargs["ssh_public_key"],
            ", ssh_private_key:", kwargs["ssh_private_key"])

        self.dc = dart_context ( directory_python_files 
                               , monitor_url = "."
                               , **kwargs
                               )
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
            self.dc.start()
            self.dc_active = True
        self.dc.add_workers([ host ], workers_per_host, [ name_edge_device ], shm_size)

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

        
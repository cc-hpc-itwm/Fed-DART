from Message import Message
from ConnectionRequest import ConnectionRequest
import random

class Device():
    """ Abstract interface to communicate which the devices
    """
    def __init__(self, device_settings, runtime):
        self.name = device_settings['name']
        self.entry_point = device_settings['entry_point']
        self.runtime = runtime
        self.runtime.add_device( device_settings['host']
                               , device_settings['computing_power']
                               , self.name
                               , device_settings['shm_size']
                               , device_settings['port']
                               )
        self.result_storage = None 
        self.dict_connection_requests = {} #store informations how to get not finished tasks in the moment
        #self.dict_results = {}
    
    def is_available(self):
        boolean_list = [True] #, False]
        return random.choice(boolean_list) #TODO: implement method to check if device is available

    def save_connection_request( self
                               , connection_request
                               , task_name
                               ):
        self.dict_connection_requests[task_name] = connection_request #each task_name can only be stored once


    def send_task( self
                 , task_name
                 , task_parameter_list
                 ):
        message = Message(self.name, task_name, task_parameter_list)
        connection_request = ConnectionRequest( self.name
                                              , self.entry_point
                                              , task_name
                                              , message  
                                              )
        connection_request.set_time()
        handle = self.runtime.send_task(connection_request)
        connection_request.save_handle(handle)
        self.dict_connection_requests[task_name] = connection_request

    def get_result(self, task_name):
        """ Check for the task in the list of not finished task and if 
            there is a result available in the storage
        """
        for name in self.dict_connection_requests:
            if name == task_name:
                connection_request = self.dict_connection_requests[task_name]
                del self.dict_connection_requests[task_name]
                result = self.result_storage.get_result(connection_request)
                return result
                
    def get_name(self):
        return self.name

    def get_entry_point(self):
        return self.entry_point

    def set_result_storage(self, result_storage):
        self.result_storage = result_storage
from ResultStorage import ResultStorage
from Message import Message
from ConnectionRequest import ConnectionRequest


class Aggregator():
    """ The idea of Aggregator is explained in the paper
        TOWARDS FEDERATED LEARNING AT SCALE: SYSTEM DESIGN
        The Aggregator is responsible to manage the devices
        for one federated learning round
    """
    def __init__(self, runtime, timeout, device_list):
        self.device_list = device_list
        self.runtime = runtime
        self.result_storage = ResultStorage(runtime, timeout)
        for device in self.device_list:
            device.set_result_storage(self.result_storage)
    
    def start_task(self, task_name, list_parameter):
        if len(list_parameter) != len(self.device_list):
            raise ValueError(" list_parameter and device_list must have same length !")
        index = 0
        for device in self.device_list: 
            device.send_task(task_name, list_parameter[index]) 
            index += 1

    def broadcast_task(self, task_name, list_parameter):
        """ returns one handle for all devices
        """
        list_connection_requests = []
        index = 0
        for device in self.device_list:
            message = Message(device.get_name() , task_name, list_parameter[index])
            connection_request = ConnectionRequest( device.get_name()
                                                  , device.get_entry_point()
                                                  , task_name
                                                  , message  
                                                  )
            connection_request.set_time()
            list_connection_requests.append(connection_request)
            index += 1
        handle = self.runtime.broadcast_task(list_connection_requests)
        for connection_request in list_connection_requests:
            connection_request.save_handle(handle)
        for index, device in enumerate(self.device_list):
            device.save_connection_request(list_connection_requests[index], task_name) 
                     
    def get_result(self, device, task_name):
        result = device.get_result(task_name)
        return result
        

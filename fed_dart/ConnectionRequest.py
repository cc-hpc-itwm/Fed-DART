import time 

class ConnectionRequest:
    """ The class ConnectionRequest collects all
        relevant informations about sending data 
        to devices, like device_name, the connection_file
        on the device (entry_point) and the task, which should be 
        executed on the device. Moreover it stores the handle.
    """
    def __init__( self
                , device_name
                , entry_point
                , task_name
                , message
                ):
        self.device_name = device_name
        self.message = message #message should have format, such that dart can use it --> try it first with serialized list
        self.entry_point = entry_point
        self.task_name = task_name
        self.needed_bandwidth = None
        self.start_time = None
        self.handle = None

    def get_entry_point(self):
        return self.entry_point

    def get_data(self):
        return self.message.get_data()

    def save_handle(self, handle):
        self.handle = handle

    def get_handle(self):
        return self.handle

    def set_time(self):
        self.start_time = time.time()

    def get_start_time(self):
        return self.start_time

    def get_device_name(self):
        return self.device_name

    def get_task_name(self):
        return self.task_name
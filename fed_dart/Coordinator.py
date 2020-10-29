 #should use informations to determine how stable a connection is and how strong the computation power of an edge device
#wait til enough clients are avaible
from Runtime import Runtime
from Device import Device
from Aggregator import Aggregator 

class Coordinator:
    """ Responsible for starting the runtime and 
        the managment of the devices over all rounds.
    """
    def __init__(self, **kwargs):
        self.runtime = Runtime(**kwargs)
        self.timeout = 100 #in s
        self.devices = []

    def add_device(self, device_settings):
        device = Device(device_settings, self.runtime)
        self.devices.append(device)
    
    def select_devices(self):
        """ Return all devices, which are available 
           (no current compuattion, stable connection)
           in the moment.
        """
        list_available_devices = []
        for device in self.devices:
            if device.is_available() == True:
                list_available_devices.append(device)
        return list_available_devices

    def remove_device(self, device_name):
        pass 

    def get_list_of_all_devices(self):
        return self.devices

    def terminate(self):
        self.runtime.terminate()
        self.devices = []

    def create_aggregator(self, avialable_devices):
        #implement somethin that locks devices which are send to one aggregator 
        return Aggregator(self.runtime, self.timeout, avialable_devices)
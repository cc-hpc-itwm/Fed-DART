

class ResultStorage:
    """ Storage of all results, which come from the devices.
        You can check, if a device already has returned the result
        of the compuations. If there is no result in the storage because
        of timeour or the task is not finished, the result is None.
    """ 
    def __init__(self, runtime, timeout):
        self.result_dict = {}
        self.runtime = runtime
        self.maximal_duration = timeout #in s

    def get_result(self, connection_request):
        device_name = connection_request.get_device_name()
        task_name = connection_request.get_task_name()
        result = self.search_result(device_name, task_name)
        if result is not None:
            return result
        else:
            handle = connection_request.get_handle()
            start_time = connection_request.get_start_time()
            results = self.runtime.get_task(start_time, self.maximal_duration, handle)
            if results is not None:
                if results != 'TIMEOUT':
                    self.store_results(results)
            result = self.search_result(device_name, task_name)
            return result

    def search_result(self, device_name, task_name):
        if device_name in self.result_dict.keys():
            if task_name in self.result_dict[device_name].keys():
                result = self.result_dict[device_name][task_name]
                del self.result_dict[device_name][task_name]
                return result
            else:
                return None 

    def store_results(self, result_devices_dict):
        """ result_dict has format like {'edge_device_1': {'result': [array([0.2244898 , 0.1364564 , 0.36734694, 0.38273591, 0.49556743])
            , array([0.72727273, 0.02887397, 0.38636364, 0.85481507, 0.05336514]), 
            array([0.66836735, 0.02974644, 0.19727891, 0.14591637, 0.06307081])], 'function': 'train_local'}}
        """
        for device_name in result_devices_dict.keys():
            if device_name in self.result_dict.keys():
                if result_devices_dict[device_name]['function'] in self.result_dict[device_name].keys():
                    pass
                else:
                    self.result_dict[device_name][result_devices_dict[device_name]['function']] = result_devices_dict[device_name]['result']
            else:
                self.result_dict[device_name] = {}
                self.result_dict[device_name][result_devices_dict[device_name]['function']] = result_devices_dict[device_name]['result']
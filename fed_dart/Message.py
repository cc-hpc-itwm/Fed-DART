import binascii
import pickle

class Message:
    """ Convert all informations in a format, such that DART can send it
        from server to device
    """
    counter = 0
    def __init__(self, location, function_name, list_variables):
        self.id = Message.counter
        self.data_packs = None
        self.set_data(location, function_name, list_variables)
        Message.counter += 1

    def add_sender_info():
        pass

    #format message: ["{'variable_number_0': 1, 'variable_number_1': 2, 'variable_number_2': 3, 'message_id': 0, 'function': 'add_numbers'}"] add device ?
    def set_data(self, location, function_name, list_variables):
        params = {}
        counter_variable = 0
        if len(list_variables) > 0:
            for variable in list_variables:
                params['variable_number_' + str(counter_variable)] = variable
                counter_variable += 1
        params['message_id'] = self.id
        params['function'] = function_name
        params['location'] = location
        data_pack = {}
        data_pack["location"] =  location #necessary for dart
        pickled_params = self.pack(params)
        data_pack["parameters"] = [str(pickled_params)]
        self.data_packs = data_pack

    def serialize(self):
        serialized_message = binascii.b2a_base64 (pickle.dumps (self))

    def get_data(self):
        return self.data_packs

    @staticmethod
    def pack (results):
        return binascii.b2a_base64 (pickle.dumps (results))

    @staticmethod
    def unpack (results):
        return pickle.loads (binascii.a2b_base64 (results))

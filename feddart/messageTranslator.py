import abc
import ast
import dill
import binascii

class MessageTranslatorBase:
    #different application possible; e.g no compression of message, maximal compression, protobuf/pickle/dill
    __metaclass__ = abc.ABCMeta


# abstract functions

    @classmethod
    @abc.abstractmethod
    def convertPython2Dart(self, list_params):
        """convert default message to dart format and return feasible format"""
        raise NotImplementedError("subclass has to implement this")

    @classmethod
    @abc.abstractmethod
    def convertDart2Python(self, dict_result):
        """convert dart format to standard python format"""
        raise NotImplementedError("subclass has to implement this")
        
class MessageTranslator(MessageTranslatorBase):

    def __init__(self):
        pass

    @classmethod
    def convertPython2Dart(self, list_client, list_params):
        """convert default message to dart format and return feasible format"""
        task_list = []
        #TODO: serialize parameters
        for client, params in zip(list_client, list_params):
            dict_client = {'location': client, 'parameter': self.packMessage(params)}
            task_list.append(dict_client)
        return task_list
        
    @classmethod
    def convertDart2Python(self, results, deviceName):
        device_result = { 'duration': None
                        , 'result': None
                        }
        resultID = None
        for result in results['results']:
            workerName = result['worker'].split("-",1)[0]
            if 'success' in result.keys() and deviceName == workerName:
                device_result['duration'] = result['duration']
                device_result['result'] = self.unpackBackMessage(result['success'])
                resultID = result['id']
        return device_result, resultID

    @classmethod
    def packMessage(self, message):
        message = dill.dumps(message)
        message = binascii.b2a_base64(message)
        return str(message)

    @classmethod
    def unpackMessage(self, message):
        message = ast.literal_eval (message)
        message = binascii.a2b_base64(message)
        message = dill.loads(message)
        return message

    @classmethod
    def packBackMessage(self, message):
        message = dill.dumps(message)
        message = binascii.b2a_base64(message)
        return message
    @classmethod
    def unpackBackMessage(self, message):
        message = binascii.a2b_base64(message)
        message = dill.loads(message)
        return message

def feddart(execute_function):
    def f_new(_params):
        params = MessageTranslator.unpackMessage(_params)
        result =  execute_function(**params)
        counter = 0
        result_dict = {}
        if type(result) is tuple:
            for element in result:
                result_dict['result_' + str(counter)] = element
                counter += 1
        else: 
            result_dict['result_0'] = result
        packed_result_dict = MessageTranslator.packBackMessage(result_dict)
        return packed_result_dict
    return f_new


import abc
import ast
import dill
import binascii
import functools

from feddart.logger import logger 
class MessageTranslatorBase(abc.ABC):
    #different application possible; e.g no compression of message, maximal compression, protobuf/pickle/dill

    # abstract functions

    @classmethod
    @abc.abstractmethod
    def convertPython2Dart(cls, list_client, list_params):
        """convert default message to dart format and return feasible format"""
        raise NotImplementedError("subclass has to implement this")

    @classmethod
    @abc.abstractmethod
    def convertDart2Python(cls, results, deviceName):
        """convert dart format to standard python format"""
        raise NotImplementedError("subclass has to implement this")


class MessageTranslator(MessageTranslatorBase):

    def __init__(self):
        pass

    @classmethod
    def convertPython2Dart(cls, list_client, list_params):
        """convert default message to dart format and return feasible format"""
        task_list = []
        log = logger(__name__)
        #TODO: serialize parameters
        logstring = ""
        for client, params in zip(list_client, list_params):
            dict_client = {'location': client, 'parameter': cls.packMessage(params)}
            logstring = logstring + " " + str({'location': client, 'parameter': params})
            task_list.append(dict_client)
        log.debug("MessageTranslator.convertPython2Dart " + logstring)
        return task_list
        
    @classmethod
    def convertDart2Python(cls, results, deviceName):
        device_result = { 'duration': None
                        , 'result': None
                        }
        resultID = None
        log = logger(__name__)
        for result in results['results']:
            workerName = result['worker'].split("-",1)[0]
            if 'success' in result.keys() and deviceName == workerName:
                device_result['duration'] = result['duration']
                device_result['result'] = cls.unpackBackMessage(result['success'])
                resultID = result['id']
        logstring = ""
        for keys,values in device_result['result'].items():
            logstring = logstring + str(keys) + " "
            logstring = logstring + str(values)
            
        log.debug("MessageTranslator.convertDart2Python " + 
            str(device_result['duration']) + " " + 
            logstring + " " + 
            str(resultID))
        return device_result, resultID

    @classmethod
    def packMessage(cls, message):
        message = dill.dumps(message)
        message = binascii.b2a_base64(message)
        return str(message)

    @classmethod
    def unpackMessage(cls, message):
        message = ast.literal_eval (message)
        message = binascii.a2b_base64(message)
        message = dill.loads(message)
        return message

    @classmethod
    def packBackMessage(cls, message):
        message = dill.dumps(message)
        message = binascii.b2a_base64(message)
        return message

    @classmethod
    def unpackBackMessage(cls, message):
        message = binascii.a2b_base64(message)
        message = dill.loads(message)
        return message

def feddart(execute_function):
    @functools.wraps(execute_function)
    def wrapper_function(_params):
        params = MessageTranslator.unpackMessage(_params)
        try:
            result = execute_function(**params)
        except Exception as e:
            result = e
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
    return wrapper_function


from feddart.messageTranslator import MessageTranslatorBase

class BasicMessageTranslator(MessageTranslatorBase):

    def __init__(self):
        pass

    @classmethod
    def convertPython2Dart(self, list_params):
        """convert default message to dart format and return feasible format"""
        raise NotImplementedError("not implemented in subclass")
        return

    @classmethod
    def convertDart2Python(self, dict_result):
        """convert dart format to standard python format"""
        raise NotImplementedError("not implemented in subclass")
        return


        
if __name__ == '__main__':
    messageTrans = BasicMessageTranslator()
    print('properties:')
    messageTrans.convertDart2Python(1)

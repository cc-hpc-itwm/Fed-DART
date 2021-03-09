from random import randint

class DummyDARTRuntime:

    def __init__(self, boolean_random):
        self.boolean_random = boolean_random
        self.get_finishedResult = True

    def get_TaskResult(self, taskName, deviceName):
        if self.boolean_random:
            boolean = randint(0,1)
        else:
            boolean = self.get_finishedResult
        if boolean: 
            taskID = 20
            return { 'duration': 5
                   , 'result': {'result_0': 1, 'result_1': "hello"}
                   }, taskID
        else:
            taskID = None
            return { 'duration': None
                   , 'result': None
                   }, taskID
        
    def remove_result_from_server(self, taskName, resultID):
        pass

    def get_job_status(self, taskName):
        return randint(0,2)

    def add_job( self
               , taskName
               , filePathFunction
               , executeFunction
               ):
        pass

    def broadcastTaskToDevices( self
                              , taskName
                              , listDeviceNames
                              , listTaskParameters
                              ):
        pass

    def stopTask(self, taskName):
        pass
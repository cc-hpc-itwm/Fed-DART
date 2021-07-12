
from feddart.logger import logger

class TaskResult:

    def __init__( self
                , deviceName = None
                , duration = None
                , resultDict = {}
                ):
        self._deviceName = deviceName
        self._duration = duration
        self._resultDict = resultDict
        self.logger = logger(__name__)

    @property
    def deviceName(self):
        return self._deviceName

    @property
    def duration(self):
        return self._duration

    @property
    def resultDict(self):
        return self._resultDict

    @property
    def resultList(self):
        return list(self._resultDict.values())

    def __str__(self):
        return f'Result from {self.deviceName}: {self.resultDict}'
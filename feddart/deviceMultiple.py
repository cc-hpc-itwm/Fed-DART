from feddart.abstractDevice import AbstractDeviceBase


class DeviceMultiple(AbstractDeviceBase):
    def __init__(self):
        pass
    def getLog(self):
        return print("Here is the log")
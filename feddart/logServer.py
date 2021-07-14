import logging

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
        
class LogServer(metaclass=Singleton):
    
    ERROR = logging.ERROR
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG

    def __init__(self, name, console_level = ERROR, 
                file_level = INFO, logfile_path = "feddart.log"):
        file_formatter = logging.Formatter(
            '%(asctime)s~%(levelname)s~%(message)s~module:%(module)s~function:%(module)s')
        console_formatter = logging.Formatter('%(asctime)s~%(levelname)s -- %(message)s')
        
        self._file_handler = logging.FileHandler(logfile_path)
        self._file_handler.setLevel(file_level)
        self._file_handler.setFormatter(file_formatter)

        self._console_handler = logging.StreamHandler()
        self._console_handler.setLevel(console_level)
        self._console_handler.setFormatter(console_formatter)

        self._logger = logging.getLogger(name)
        self._logger.addHandler(self._file_handler)
        self._logger.addHandler(self._console_handler)
        self._logger.setLevel(console_level)
        self.log().info("Log Server initialized")

    def log(self):
        return self._logger
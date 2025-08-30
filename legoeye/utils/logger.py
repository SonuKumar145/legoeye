import logging
import os
from logging.handlers import RotatingFileHandler
from utils.paths import Paths
from utils.config import Config
import threading

class Logger:
    """
    Central logger configuration. Provides per-module loggers writing to a rotating file.
    """
    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                cls._instance = instance
        return cls._instance

    def init(self):
        '''
        initialises the logger with **DEFAULT** values if `config` is NOT initialised

        
        ***NOTE***: to prevent **DEADLOCK** situation,
        - we need to initialise the logger with **DEFAULT** values so that config is able to log,
        - after initialisation of config we need to **reinitialise** this logger with the actual config values
        '''
        self.paths = Paths()
        self.config = Config()

        is_config_usable = self.config._initialized
        is_paths_usable = self.paths._initialised

        self.logAllowed = self.config.get('log.ENABLE') if is_config_usable else True

        if self._initialized:
            root = logging.getLogger()
            # Remove all existing handlers to prevent duplicates
            for handler in list(root.handlers):
                root.removeHandler(handler)
            logging.disable(logging.NOTSET)
        

        if(self.logAllowed):
            self.LOG_FILE_PATH = self.paths.LOG_FILE_PATH if is_paths_usable else os.path.expanduser("~/legoeye/app.log")
            
            log_dirs = os.path.dirname(self.LOG_FILE_PATH)
            log_dirs and os.makedirs(log_dirs, exist_ok=True)

            if not os.path.exists(self.LOG_FILE_PATH):
                with open(self.LOG_FILE_PATH, 'w') as f:
                    f.write("")
        
            handlers = []
            if(self.config.get('log.AUTO_DELETE_OLD_LOG_FILES') if is_config_usable else True):

                fileHandler = RotatingFileHandler(
                    self.LOG_FILE_PATH,
                    maxBytes=self.config.get('log.MAX_FILE_SIZE_IN_BYTES_BEFORE_ROTATING') if is_config_usable else 5000000,
                    backupCount=self.config.get('log.MAX_OLD_LOG_FILES_LIMIT') if is_config_usable else 5,
                    encoding='utf-8'
                )
            else:
                fileHandler = logging.FileHandler(self.LOG_FILE_PATH, encoding='utf-8')
            
            handlers.append(fileHandler)

            if self.config.get('log.CONSOLE_LOG') if is_config_usable else True:
                console_handler = logging.StreamHandler()
                handlers.append(console_handler)

            formatter = logging.Formatter(
                '%(asctime)s %(levelname)-8s [%(name)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            for handler in handlers:
                handler.setFormatter(formatter)

            root = logging.getLogger()
            root.setLevel(self.config.get('log.LEVEL') if is_config_usable else logging.DEBUG)
            for handler in handlers:
                root.addHandler(handler)
            root.propagate = False

        else:
            logging.getLogger().propagate = False
            logging.disable(logging.CRITICAL)
        self._initialized = True


    def get_logger(name: str) -> logging.Logger:
        """
        Returns a logger for the given module name. Initialize first.
        """
        return logging.getLogger(name)
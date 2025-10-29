import json
import os
import threading
from pathlib import Path

class Config:
    CONFIG_FILE = None

    _instance = None
    _initialized = False
    _lock = threading.Lock()
    config_loaded_status = False
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._config = {}
                instance.lock = threading.Lock()

                HOME_DIR = os.path.expanduser('~/')
                CONFIG_DIR = os.path.join(HOME_DIR,".config")
                os.makedirs(CONFIG_DIR, exist_ok=True)
                
                LEGOEYE_CONFIG_DIR = os.path.join(CONFIG_DIR,"legoeye")
                os.makedirs(LEGOEYE_CONFIG_DIR,exist_ok=True)
                    
                # LEGOEYE_DIR_PATH = Path(__file__).resolve().parent.parent
                # instance.CONFIG_FILE  = os.path.join( LEGOEYE_DIR_PATH,"config.json")

                instance.CONFIG_FILE  = os.path.join( LEGOEYE_CONFIG_DIR,"config.json")

                print(f"LEGOEYE_CONFIG_DIR path: {LEGOEYE_CONFIG_DIR}")
                print(f"CONFIG_FILE path: {instance.CONFIG_FILE}")

                cls._instance = instance
                
        return cls._instance
    
    def init(self, logger):
        self.logger = logger.get_logger(__name__)
        self.load()
        self._initialized = True

    def load(self, config_file=None):
        """Load configuration from file or create defaults if missing or invalid."""
        path = config_file or self.CONFIG_FILE
        if not os.path.exists(path):
            self.logger.warning(f"Config file {path} not found. Creating with defaults.", exc_info=True)
            self._config = self._get_default_config()
            self.save(config_file=path)
            self.config_loaded_status = True
        try:
            with open(path, 'r') as f:
                self._config = json.load(f)
            self.config_loaded_status = True
            self.logger.info(f"Config loaded successfully from '{path}'.")

        except json.JSONDecodeError as e:
            self.config_loaded_status = False
            self.logger.error(f"Error parsing config file: {e}. Using defaults.", exc_info=True)
            # self._config = self._get_default_config()
            # self.save(config_file=path)

        except Exception as e:
            self.config_loaded_status = False
            self.logger.error(f"Unexpected error while loading config file '{path}': {e}. Using defaults.", exc_info=True)

   
    def save(self, config_file=None):
        if (self.lock):
            lock = self.lock
        with lock:
            path = config_file or self.CONFIG_FILE
            try:
                with open(path, 'w') as f:
                    json.dump(self._config, f, indent=2)
                    self.logger.info(f"Config saved successfully to '{path}'.")
            except Exception as e:
                self.logger.error(f"Error saving config to '{path}': {e}", exc_info=True)(f"Error saving config: {e}")

   
    def get(self, path, default=None):
        """
        Get config value using dot notation.\n
        Example:\n
        get('recording.RECORD')
        """
        keys = path.split('.')
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

   
    def set(self, path, value):
        """
        Set config value using dot notation.\n
        Example:\n
        set('recording.RECORD', True)
        """
        with self.lock:
            keys = path.split('.')
            config = self._config
            for key in keys[:-1]:
                config = config.setdefault(key, {})
            config[keys[-1]] = value
            self.logger.debug(f"Config key '{path}' set to '{value}'.")

   
    def reload(self):
        self.load()

    @property
    def isRecordEnabled(self)->bool:
        return bool(self.get('recording.ENABLE', True))

    @property
    def isStreamEnabled(self)-> bool:
        return bool(self.get('streaming.ENABLE', True))

    @property
    def lores(self):
        return (
            int(self.get('picamera_settings.LORES_WIDTH', 96)),
            int(self.get('picamera_settings.LORES_HEIGHT', 53))
        )
    
    @property
    def vid_resolution(self):
        return (
            int(self.get('video_settings.RESOLUTION_WIDTH', 1920)),
            int(self.get('video_settings.RESOLUTION_HEIGHT', 1080))
        )

    @property
    def framerate(self):
        return int(self.get('video_settings.FRAMERATE', 20))
   
    @property
    def motion_threshold(self):
        return int(self.get('motion_detection.MOTION_THRESHOLD', 7))

   
    def _get_default_config(self):
        return {
            "recording": {
                "ENABLE": True,
                "RECORD_ONLY_WHEN_MOTION_DETECTED": True,
                "MAX_STORAGE_GB": -1,
                "AUTO_DELETE_OLD_FILES": True,
                "RETENTION_DAYS": 30,
                "STREAM_FOOTAGES": True,
                "DIR": "videos"
            },
            "streaming": {
                "ENABLE": True,
                "STREAM_PORT": 5550,
                "MAX_CONCURRENT_STREAMS": 5,
                "DIR": "live_stream_output",
                "FOOTAGE_STREAM_DIR": "footage_streams_outputs"
            },
            "video_settings": {
                "FRAMERATE": 20,
                "RESOLUTION_WIDTH": 1920,
                "RESOLUTION_HEIGHT": 1080,
                "VIDEO_FORMAT": "mp4"
            },
            "timestamp": {
                "COLOR_R": 0,
                "COLOR_G": 255,
                "COLOR_B": 0,
                "ORIGIN_X": 0,
                "ORIGIN_Y": 30,
                "SCALE": 1,
                "THICKNESS": 2,
                "ITALIC": False,
                "FONT": "Hershey Simplex"
            },
            "picamera_settings": {
                "LORES_WIDTH": 96,
                "LORES_HEIGHT": 53,
                "ENCODER_WATCHER_INTERVAL_IN_SECONDS": 0.2
            },
            "motion_detection": {
                "THRESHOLD": 7,
                "PRE_MOTION_BUFFER_SECONDS": 5,
                "POST_MOTION_BUFFER_SECONDS": 5
            },
            "scripts": {
                "DIR":"scripts",
                "frame_processing_scripts_settings": {
                    "TYPE": "frame_processing",
                    "DIR": "frame_processing",
                    "SCRIPTS_EXECUTION_LOOP_INTERVAL_IN_SECONDS": 0.1,
                    "SCRIPTS": [
                    "motion_detection.py"
                    ]
                },
                "defaults":{
                    "TYPE": "defaults",
                    "DIR": "defaults",
                    "pre_picam_init_scripts_settings": {
                        "TYPE": "pre_picam_init",
                        "DIR": "pre_picam_init",
                        "SCRIPTS": [
                            "default.py"
                            ]
                        },
                    "post_picam_init_scripts_settings": {
                        "TYPE": "post_picam_init",
                        "DIR": "post_picam_init",
                        "SCRIPTS": [
                        "default.py",
                        "frame_processing.py"
                        ]
                    },
                    "pre_callback_scripts_settings":{
                        "DIR":"pre_callback"
                    },
                },
            },
            
            "security": {
                "ENABLE_AUTHENTICATION": False,
                "USERNAME": "",
                "PASSWORD": "",
                "API_KEY": "",
                "ENABLE_HTTPS": False
            },
            "performance": {
                "ENABLE_GPU_ACCELERATION": False,
                "CPU_THREADS": 4,
                "MEMORY_LIMIT_MB": 2048,
                "ENABLE_LOGGING": True
            },
            "log": {
                "ENABLE": True,
                "CONSOLE_LOG": True,
                "LEVEL": "INFO",
                "FILE_NAME": "app.log",
                "DIR":"logs",
                "MAX_FILE_SIZE_IN_BYTES_BEFORE_ROTATING": 5000000,
                "MAX_OLD_LOG_FILES_LIMIT": 5,
                "AUTO_DELETE_OLD_LOG_FILES": True
            },
            "notifications": {
                "ENABLE_EMAIL_ALERTS": False,
                "EMAIL_SMTP_SERVER": "",
                "EMAIL_PORT": 587,
                "EMAIL_USERNAME": "",
                "EMAIL_PASSWORD": "",
                "WEBHOOK_URL": "",
                "ENABLE_PUSH_NOTIFICATIONS": False
            },
            "database": {
                "DB_NAME": "records.db",
                "DIR":""
            },
            "time":{
                "FILE_NAME":"time.json",
                "TIME_WRITE_INTERVAL_IN_SECONDS":1,
                "DIR":"recovery"
            },
            "server":{
                "NAME":"server",
                "ENABLE":True,
                "DIR":"",
                "APIS":{
                "DIR":"server",
                "NAME":"apis"
                }
            }
        }


import threading
from utils.config import Config
import os
from pathlib import Path as _Path

class Paths:

    _instance = None
    _initialised = False
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                cls._instance = instance

        return cls._instance
    
    def init(self):
        self.config = Config()
        path_obj = _Path(__file__)
        abs_path = path_obj.resolve()

        self.ROOT_DIR_NAME = abs_path.parent.parent.name

        #relative paths

        self.REL_VIDEOS_DIR = self.config.get('recording.DIR')
        self.REL_HLS_DIR = self.config.get('streaming.DIR')
        self.REL_FOOTAGE_STREAM_DIR = self.config.get('streaming.FOOTAGE_STREAM_DIR')

        self.REL_SCRIPTS_DIR = self.config.get('scripts.DIR')
        
        self.REL_FRAME_PROCESSING_SCRIPTS_DIR = os.path.join( self.REL_SCRIPTS_DIR, self.config.get('frame_processing_scripts_settings.DIR'))
        self.REL_PRE_PICAM_INIT_SCRIPT_DIR = os.path.join( self.REL_SCRIPTS_DIR, self.config.get('pre_picam_init_scripts_settings.DIR'))
        self.REL_POST_PICAM_INIT_SCRIPT_DIR = os.path.join( self.REL_SCRIPTS_DIR, self.config.get('post_picam_init_scripts_settings.DIR'))
        
        self.REL_LOG_FILE_PATH = os.path.join(self.config.get('log.DIR'), self.config.get('log.FILE_NAME'))
        self.REL_DB_PATH = os.path.join(self.config.get('database.DIR'),self.config.get('database.DB_NAME'))

        self.REL_TIME_FILE_PATH =  os.path.join(self.config.get('time.DIR'),self.config.get('time.FILE_NAME'))


        #absolute paths
        self.ROOT_DIR = abs_path.parent.parent

        self.VIDEOS_DIR = os.path.join(self.ROOT_DIR, self.REL_VIDEOS_DIR)
        self.HLS_DIR = os.path.join(self.ROOT_DIR, self.REL_HLS_DIR)
        self.FOOTAGE_STREAM_DIR = os.path.join(self.ROOT_DIR, self.REL_FOOTAGE_STREAM_DIR)

        self.SCRIPTS_DIR = os.path.join(self.ROOT_DIR, self.REL_SCRIPTS_DIR)
        
        self.FRAME_PROCESSING_SCRIPTS_DIR = os.path.join(self.ROOT_DIR, self.REL_FRAME_PROCESSING_SCRIPTS_DIR)
        self.PRE_PICAM_INIT_SCRIPT_DIR = os.path.join(self.ROOT_DIR, self.REL_PRE_PICAM_INIT_SCRIPT_DIR)
        self.POST_PICAM_INIT_SCRIPT_DIR = os.path.join(self.ROOT_DIR, self.REL_POST_PICAM_INIT_SCRIPT_DIR)
        
        self.LOG_FILE_PATH = os.path.join(self.ROOT_DIR, self.REL_LOG_FILE_PATH)
        self.DB_PATH = os.path.join(self.ROOT_DIR, self.REL_DB_PATH)

        self.TIME_FILE_PATH = os.path.join(self.ROOT_DIR, self.REL_TIME_FILE_PATH)

        os.makedirs(self.VIDEOS_DIR,exist_ok=True)
        os.makedirs(self.HLS_DIR,exist_ok=True)
        os.makedirs(self.FOOTAGE_STREAM_DIR,exist_ok=True)

        self._initialised = True

    def mk_full_video_path(self, video_id):
        return os.path.join(self.VIDEOS_DIR, video_id)

    def mk_full_footage_stream_path(self, footage_stream_id):
        return os.path.join(self.FOOTAGE_STREAM_DIR, footage_stream_id)
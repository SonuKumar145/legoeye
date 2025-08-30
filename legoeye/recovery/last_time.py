import os
import time
import json
from utils.paths import Paths
from utils.config import Config
import threading
from utils.logger import Logger


paths = Paths()
config = Config()
logger = Logger.get_logger(__name__)


def time_writer_loop():

    sleep_time = config.get('time.TIME_WRITE_INTERVAL_IN_SECONDS')

    while(True):
        with open(paths.TIME_FILE_PATH,'w') as f:
            json.dump({
                "last_time":(time.time())
            },f)
        time.sleep(sleep_time)

def time_writer_thread():
    _time_writer_thread = threading.Thread(target=time_writer_loop)
    _time_writer_thread.daemon = False
    _time_writer_thread.start()
    logger.info("time_writer_loop_thread initiated")
    


def get_last_time():
    paths = Paths()

    if not os.path.exists(paths.TIME_FILE_PATH):
        raise Exception (f"{paths.TIME_FILE_PATH} doesn't exist.")
    else:
        with open(paths.TIME_FILE_PATH, 'r') as f:
            last_time_obj = json.load(f)
        return last_time_obj['last_time']
    
    

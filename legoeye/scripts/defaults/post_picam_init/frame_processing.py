from utils.logger import Logger
import threading
from core.scripts import scriptManager
from core.picam import PicamManager
from utils.config import Config
import time

scriptsMngr = scriptManager()
picamMngr = PicamManager()
config = Config()
logger = Logger.get_logger(__name__)


SCRIPT_NAME = "Frame processing scripts initializer"

logger = Logger.get_logger(__name__)

def _scripts_runner_loop():
    """Continuously captures low-resolution video frames for real-time script processing.

    This infinite loop repeatedly gets the latest low-res buffer from `PicamManager`
    and passes it to `scriptManager` for execution by loaded scripts.
    """
    
    
    SCRIPTS_EXECUTION_LOOP_INTERVAL_IN_SECONDS = config.get("frame_processing_scripts_settings.SCRIPTS_EXECUTION_LOOP_INTERVAL_IN_SECONDS")
    
    if(not SCRIPTS_EXECUTION_LOOP_INTERVAL_IN_SECONDS):
        logger.warning("frame_processing_scripts_settings.SCRIPTS_EXECUTION_LOOP_INTERVAL_IN_SECONDS is None. Using default = 0.1s" )
        SCRIPTS_EXECUTION_LOOP_INTERVAL_IN_SECONDS = 0.1
    while True:
        captured_buffer = picamMngr.get_lores_buffer()
        scriptsMngr.run_frame_processing_scripts({
            'captured_buffer':captured_buffer
        })
        time.sleep(SCRIPTS_EXECUTION_LOOP_INTERVAL_IN_SECONDS)


def main():
    """Starts a non-daemon thread that continuously feeds camera data to user scripts.

    
    **NOTE**: 
    
    As it is non-daemon thread, this thread will not be terminated automatically.\n
    It will wait for user's script to end cleanly.
    """
    scripts_thread = threading.Thread(target=_scripts_runner_loop)
    scripts_thread.daemon = False
    scripts_thread.start()
    logger.info("run_script_thread method initiated")

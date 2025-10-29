from core.picam import PicamManager
from utils.logger import Logger
import threading

SCRIPT_NAME = "Default"

def main():
    picamMngr = PicamManager()
    logger = Logger.get_logger(__name__)

    picamMngr.encoder_watcher_thread = threading.Thread(target=picamMngr.encoderWatcher, daemon=True)
    picamMngr.encoder_watcher_thread.start()
    logger.info("encoder_watcher_thread started")
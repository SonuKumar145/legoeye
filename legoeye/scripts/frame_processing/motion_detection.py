import time
import numpy as np
from utils.config import Config
from core.record import recordManager
from legoeye.utils.record import startRecording, stopRecording
from utils.logger import Logger


SCRIPT_NAME = "Motion Detection"

logger = Logger.get_logger(__name__)
recordMngr = recordManager()
config = Config()

w, h = config.lores
prev = None
ltime = 0
post_buffer_seconds = float(config.get('motion_detection.POST_MOTION_BUFFER_SECONDS', 5))
motion_threshold = float(config.get('motion_detection.THRESHOLD', 7))

#! implement pre motion buffer


def main(params):
    '''
    starts recording when motion is detected

    uses frame subtracting to detect motion

    stops after motion_detection.POST_MOTION_BUFFER_SECONDS, default is 5 seconds
    '''
    global prev,ltime


    captured_buffer = params['captured_buffer']
    cur = captured_buffer[:w * h].reshape(h, w).astype(np.uint8)
    # logger.info("motion detection entered ", "prev : ", prev[0] if prev is not None else prev, " curr: ",cur[0])

    if prev is not None:
        mse = np.square(np.subtract(cur, prev)).mean()
        if mse > motion_threshold:
            if not recordMngr.isRecording:
                startRecording()
                logger.info(f"Motion detected - recording started; mse: {mse}")
            ltime = time.time()
        else:
            end_timestamp = time.time()
            if recordMngr.isRecording and end_timestamp - ltime > post_buffer_seconds:
                stopRecording()
    prev = cur
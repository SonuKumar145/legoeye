from core.stream import StreamManager
from core.database import DBHandler
from core.picam import PicamManager
from core.record import RecordingStartError, RecordingStopError, recordManager
from utils.paths import Paths
import uuid
import time
from utils.logger import Logger

picamMngr = PicamManager()
streamMngr = StreamManager()
recordMngr = recordManager()
paths = Paths()
db = DBHandler()
logger = Logger.get_logger(__name__)

def startRecording(by=None):
    '''
    - checks if encoder is running, if not then starts it
    - sets filename
    - starts recording
    - sets the isRecording flag to True
    - records start timestamp
    '''
    if (recordMngr.isRecording):
        raise RecordingStartError("Recording is already in progress.")
    try:
        video_id = str(uuid.uuid4())
        recordMngr.recordingVideoID = video_id
        if not picamMngr.isEncoderRunning:
            logger.info("Encoder status: NOT Running")
            picamMngr.startEncoder(by)
        else:
            logger.info("Encoder status: Running")

        picamMngr.recordingOutput.fileoutput = paths.mk_full_video_path(video_id=video_id)
        picamMngr.recordingOutput.start()
        recordMngr.recordingStartTimestamp = time.time()
        db.insert_clip(id=video_id, timestamp=recordMngr.recordingStartTimestamp, duration=None)

        recordMngr.isRecording = True
        logger.info(f"recording started")

        return True
    except Exception as e:
        logger.error(f"startRecording failed : {e}", exc_info=True)
        return False

def stopRecording(by=None):
    '''
    - stops recording
    - sets isRecording flag to False
    - checks if streaming is going on, if not then stops the encoder
    '''
    if(not recordMngr.isRecording):
        raise RecordingStopError("Can't stop recording as NO recording is Active.")
    try:
        picamMngr.recordingOutput.stop()
        end_timeStamp = time.time()
        recordMngr.isRecording = False
        duration = end_timeStamp - recordMngr.recordingStartTimestamp   
        db.update_duration(id=recordMngr.recordingVideoID, duration=duration)

        if not streamMngr.isStreaming():
            picamMngr.stopEncoder(by)
        logger.info(f"Recording stopped")
        return True
    except Exception as e:
        logger.error(f"stopRecording failed : {e}", exc_info=True)
        return False
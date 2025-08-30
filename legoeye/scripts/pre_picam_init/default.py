from utils.logger import Logger
from core.picam import PicamManager
import time

SCRIPT_NAME = "Default"

logger = Logger.get_logger(__name__)

def main():
        
        picamMngr = PicamManager()

        video_config = picamMngr.picam2.create_video_configuration(
            main={"size": picamMngr.config.vid_resolution, "format": "RGB888"},
            lores={"size": picamMngr.config.lores, "format": "YUV420"},
            controls={"FrameRate": picamMngr.config.framerate}
        )
        picamMngr.picam2.configure(video_config)
        logger.info("picam2 configured")


        picamMngr.outputs = []
        if(picamMngr.config.isRecordEnabled):
            picamMngr.outputs.append(picamMngr.recordingOutput)
            logger.info("recording found enabled")
            logger.info("recordingOutput added to the encoder.output")
        else:
            logger.info("recording found disabled")
            logger.info("recordingOutput not added to the encoder.output")

        if(picamMngr.config.isStreamEnabled):
            picamMngr.outputs.append(picamMngr.streamOutput)
            logger.info("streaming found enabled")
            logger.info("streamOutput added to the encoder.output")
        else:
            logger.info("streaming found disabled")
            logger.info("streamOutput not added to the encoder.output") 

        picamMngr.encoder.output=picamMngr.outputs
        

        picamMngr.picam2.start()

        logger.info(f'picamera2 starting in')
        for i in range(5):
            if i > 1 : logger.info(f'{5-i} second...')
            else : logger.info(f'{5-i} seconds...')
            time.sleep(1)
        logger.info("Picamera2 started!")
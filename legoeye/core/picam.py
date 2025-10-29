from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput, FfmpegOutput
import time
import threading
from utils.config import Config
from utils.paths import Paths
from utils.logger import Logger

logger = Logger.get_logger(__name__)

class PicamManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        try:
            with cls._lock:
                if cls._instance is None:
        
                    instance = super().__new__(cls)

                    logger.info("initialisation of PicamManager instance started")
                    
                    instance.lock = threading.Lock()
                    instance.isEncoderRunning = False     #if encoder is running means hls segments are being generated, so its just ready to be streamed
                    instance.paths = Paths()
                    instance.config = Config()
                    instance.picam2 = Picamera2()
                    
                    instance.encoder = H264Encoder(repeat=True, iperiod=15,framerate=instance.config.framerate, enable_sps_framerate=True)
                    logger.info("encoder initialised")

                    #! -hls_playlist_type event causing master.m3u8 to rise indefinately causing delay loadup causing more delay in the stream
                    instance.streamOutput = FfmpegOutput(f"-f hls -hls_time 1 -hls_list_size 2 -hls_flags delete_segments -hls_allow_cache 0 -hls_playlist_type event -hls_segment_filename {instance.paths.HLS_DIR}/stream_%03d.ts {instance.paths.HLS_DIR}/master.m3u8")
                    instance.recordingOutput = FileOutput()

                    cls._instance = instance
                    logger.info("Initialisation of PicamManager instance completed!")

            return cls._instance
        
        except Exception as e:
            logger.error(f"Initialisation of PicamManager failed : {e}", exc_info=True)
            
        
    def startEncoder(self, by=""):
        with self.lock:
            self.isEncoderRunning = True
            logger.info(f"Encoder started {('by ' + by) if by else ''}")

    def stopEncoder(self, by=""):
        with self.lock:
            self.isEncoderRunning = False
            logger.info(f"Encoder stopped {('by ' + by) if by else ''}")

    def get_lores_buffer(self):
        return self.picam2.capture_buffer("lores")
    
    def encoderWatcher(self):
        ENCODER_WATCHER_INTERVAL_IN_SECONDS = self.config.get("picamera_settings.ENCODER_WATCHER_INTERVAL_IN_SECONDS")
        if(not ENCODER_WATCHER_INTERVAL_IN_SECONDS):
            logger.warning("picamera_settings.ENCODER_WATCHER_INTERVAL_IN_SECONDS is None. Using default = 0.2s" )
            ENCODER_WATCHER_INTERVAL_IN_SECONDS = 0.2
        encoder_status = False
        while True:
            with self.lock:
                current_status = self.isEncoderRunning
            if not (current_status == encoder_status):
                if current_status:
                    self.picam2.start_encoder(self.encoder)
                    logger.info(f"Encoder started__")

                else:
                    self.picam2.stop_encoder()
                encoder_status = current_status
            time.sleep(ENCODER_WATCHER_INTERVAL_IN_SECONDS)
    
    def stop(self):
        with self.lock:
            self.picam2.stop()
            logger.info(f"Picamera2 stopped")




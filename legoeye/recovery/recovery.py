from core.database import DBHandler
from recovery.last_time import get_last_time
from utils.logger import Logger

logger = Logger.get_logger(__name__)

def recover():
    db = DBHandler()

    null_dur_clips = db.list_null_duration_clips()
    
    for clip in null_dur_clips:
        try:
            last_time = get_last_time()
            db.update_duration(clip['id'],last_time-clip['timestamp'])
            logger.info(f"Clip with id = {clip['id']} got recovered!")
        except Exception as e:
            logger.error(f"Unexpected error occurred during recovery process. {e}")
            
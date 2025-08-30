from flask import Blueprint, jsonify, send_from_directory
import ssl 

from core.database import DBHandler
from utils.stream import startStream, stopStream as stopstrm
from utils.paths import Paths
from utils.config import Config
from utils.logger import Logger


config = Config()
db = DBHandler()
paths = Paths()
logger = Logger.get_logger(__name__)

live_bp = Blueprint("live", __name__)

@live_bp.route('/start')
def live_web_page():
    startStream()
    return "Stream started successfully",200

@live_bp.route('/master')
def live_stream_master():
    '''Serves the HLS master playlist `.m3u8` file for the live stream.'''

    if not config.isStreamEnabled:
        logger.warning("[/stream/live/master] Stream is currently disabled by configuration. Returning disabled page/message.", exc_info=True)
        #TODO: return stream disabled page.
        return "Streaming is currently disabled.", 503
    try:
        return send_from_directory(paths.HLS_DIR, "master.m3u8")
    except ssl.SSLEOFError:
        stopstrm()
        logger.info("[/stream/live/master] Client disconnected abruptly (SSLEOFError) while serving stream. Stopping stream.")
    except Exception as e:
        stopstrm()
        logger.error(f"[/stream/live/master] Unexpected error occurred while serving stream: {e}. Stopping stream.", exc_info=True)


@live_bp.route('/<segment>')
def live_stream_segment(segment):
    """Serves individual HLS video segments `.ts` files."""
    
    try:
        if not segment.endswith('.ts') or '/' in segment:
            logger.warning(f"[/stream/live/<{segment}>] Invalid request: Segment '{segment}' does not end with '.ts' or contains '/'. Returning 400.", exc_info=True)
            return "Invalid request", 400
        return send_from_directory(paths.HLS_DIR, segment)
    except ssl.SSLEOFError:
        logger.info(f"[/stream/live/<{segment}>] Client disconnected abruptly (SSLEOFError) while serving segment: {segment}.")
    except Exception as e:
        logger.error(f"[/stream/live/<{segment}>] Unexpected error occurred while serving segment '{segment}': {e}.", exc_info=True)
        return jsonify({
            "status": "Segment service error",
            "details": str(e)
        }), 500


@live_bp.route('/stop')
def stopstream():
    """Stops the active video stream and releases associated resources like `encoder` if **NOT** in use."""
    
    try:
        stopstrm("stopstream")
    except Exception as e:
        logger.error(f"[/stop] Error occurred while attempting to stop streaming: {e}", exc_info=True)
        return jsonify({
            "status": "error stopping stream",
            "details": str(e)
        }), 500
    return jsonify({
        "status": "streaming stopped"
    })

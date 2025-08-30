from flask import Blueprint,request, jsonify, send_from_directory
import time
import ssl
import os


from core.database import DBHandler
from utils.paths import Paths
from utils.stream import stopStream as stopstrm, startFootageRangeStream
from utils.config import Config
from utils.logger import Logger


config = Config()
db = DBHandler()
paths = Paths()
logger = Logger.get_logger(__name__)

footage_stream_bp = Blueprint("footage_stream", __name__)

@footage_stream_bp.route('/start', methods=['POST'])
def start_stream_footage():
    if request.method == 'POST':
        data = request.get_json()

        if not data :
            logger.warning(f"[/footage] Bad Request: Request body is missing. Returning 400.", exc_info=True)
            return jsonify({"error": "Missing data"}), 400
        if 'start_epoc' not in data :
            logger.warning(f"[/footage] Bad Request: Required parameter 'start_epoc' not found in request data. Returning 400.", exc_info=True)
            return jsonify({"error": "Missing start_epoc"}), 400
        if 'end_epoc' not in data:
            logger.warning(f"[/footage] Bad Request: Required parameter 'end_epoc' not found in request data. Returning 400.", exc_info=True)
            return jsonify({"error": "Missing end_epoc"}), 400
        
        start_epoc = data['start_epoc']
        end_epoc = data['end_epoc']


        clips_detail_list = db.get_clips_in_range(start_ts=start_epoc, end_ts=end_epoc)

        if(len(clips_detail_list) == 0): 
            logger.info("[start_stream_footage]  clips_detail_list is empty")
            return jsonify({
            'clips_detail':clips_detail_list,
            'streamID': None
            })
        stream_id = startFootageRangeStream(
            start_epoc=start_epoc,
            end_epoc=end_epoc,
            clips_detail_list=clips_detail_list,
            precise=False,
            )
        time.sleep(6)

        return jsonify({
            'clips_detail':clips_detail_list,
            'streamID':stream_id
            })

@footage_stream_bp.route('/<footage_stream_id>/<filename>')
def get_footage_stream_file(footage_stream_id:str, filename:str):
    '''Serves the video footage stream master playlist `.m3u8` file for the live stream.'''
        
    try:
        if (filename == "master.m3u8"):
            return send_from_directory(os.path.join(paths.FOOTAGE_STREAM_DIR,footage_stream_id), "master.m3u8")
        else:
            if not '/' in filename or filename.endswith('.ts'):
                return send_from_directory(os.path.join(paths.FOOTAGE_STREAM_DIR,footage_stream_id), filename)
            logger.warning(f"[/stream/footage/{footage_stream_id}/{filename}] Invalid request: Filename '{filename}' does not end with '.ts' or contains '/'. Returning 400.", exc_info=True)
            return "Invalid request", 400

    except ssl.SSLEOFError:
        stopstrm()
        logger.info(f"[/stream/footage/{footage_stream_id}/{filename}] Client disconnected abruptly (SSLEOFError) while serving stream. Stopping stream.")
    except Exception as e:
        stopstrm()
        logger.error(f"[/stream/footage/{footage_stream_id}/{filename}] Unexpected error occurred while serving stream: {e}. Stopping stream.", exc_info=True)






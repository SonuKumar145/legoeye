from utils.logger import Logger
from flask import request, jsonify,Blueprint, send_from_directory, abort, make_response
import os

from core.database import DBHandler
from utils.paths import Paths
from utils.config import Config
from utils.logger import Logger


config = Config()
db = DBHandler()
paths = Paths()
logger = Logger.get_logger(__name__)

footage_file_bp = Blueprint("footage_file", __name__)


@footage_file_bp.route('/')
def footages():
    data = request.get_json()
    
    if not data :
        logger.warning(f"[/footages] Bad Request: Request body is missing. Returning 400.", exc_info=True)
        return jsonify({"error": "Missing data"}), 400
    if 'start_epoc' not in data :
        logger.warning(f"[/footages] Bad Request: Required parameter 'start_epoc' not found in request data. Returning 400.", exc_info=True)
        return jsonify({"error": "Missing start_epoc"}), 400
    if 'end_epoc' not in data:
        logger.warning(f"[/footages] Bad Request: Required parameter 'end_epoc' not found in request data. Returning 400.", exc_info=True)
        return jsonify({"error": "Missing end_epoc"}), 400

    start_epoc = data['start_epoc']
    end_epoc = data['end_epoc']

    return db.get_clips_in_range(start_ts=start_epoc, end_ts=end_epoc)

@footage_file_bp.route('/<path:videoFileName>')
def footage(videoFileName):
    """Serves a specific video file from the configured video directory."""

    full_path = os.path.join(config.videos_dir, videoFileName)
    if not os.path.exists(full_path):
        logger.warning(f"[/footage] File not found: '{videoFileName}' at '{full_path}'. Aborting with 404.", exc_info=True)
        abort(404)

    videoResponse = make_response(send_from_directory(config.videos_dir, videoFileName))
    return videoResponse
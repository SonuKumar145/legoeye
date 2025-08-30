from flask import Blueprint, jsonify, request

from core.database import DBHandler
from utils.logger import Logger

db = DBHandler()
logger = Logger.get_logger(__name__)

db_bp = Blueprint("db", __name__)

#------------------------------------
# █▀▄ █▄▄   █▀█ █░█ █▀▀ █▀█ █ █▀▀ █▀
# █▄▀ █▄█   ▀▀█ █▄█ ██▄ █▀▄ █ ██▄ ▄█
#------------------------------------

@db_bp.route('/total_videos')
def total_videos():
    return jsonify({
        'total_videos':db.get_total_clips()
    })

@db_bp.route('/total_videos_duration')
def total_videos_duration():
    return jsonify({
        'total_videos_duration':db.get_total_duration()
    })

@db_bp.route('/records', methods=['POST'])
def get_records_in_range():
    if request.method == 'POST':
        data = request.get_json()

        if not data :
            logger.warning(f"[/records] Bad Request: Request body is missing. Returning 400.", exc_info=True)
            return jsonify({"error": "Missing data"}), 400
        if 'limit' not in data :
            logger.warning(f"[/records] Bad Request: Required parameter 'limit' not found in request data. Returning 400.", exc_info=True)
            return jsonify({"error": "Missing limit"}), 400
        if 'offset' not in data:
            logger.warning(f"[/records] Bad Request: Required parameter 'offset' not found in request data. Returning 400.", exc_info=True)
            return jsonify({"error": "Missing offset"}), 400
        
        limit = data['limit']
        offset = data['offset']

        records = db.list_clips(limit, offset)
        
        return jsonify({
            'records':records
            })

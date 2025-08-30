from flask import jsonify
from utils.health import get_cpu_temp, get_cpu_usage, get_memory_usage,get_storage_usage
from flask import Blueprint, jsonify

#-------------------------
# █░█ █▀▀ ▄▀█ █░░ ▀█▀ █░█
# █▀█ ██▄ █▀█ █▄▄ ░█░ █▀█
#-------------------------

health_bp = Blueprint("health", __name__)


@health_bp.route('/cpu_usage')
def cpu_usage():
    return jsonify(get_cpu_usage())

@health_bp.route('/cpu_temp')
def cpu_temp():
    return jsonify(get_cpu_temp())

@health_bp.route('/mem_details')
def mem_details():
    return jsonify(get_memory_usage())

@health_bp.route('/storage_details')
def storage_details():
    return jsonify(get_storage_usage())

from flask import Blueprint, send_from_directory

from utils.logger import Logger
from utils.paths import Paths
import os

path = Paths()

logger = Logger.get_logger(__name__)

frontend_bp = Blueprint(
    "frontend",
    __name__,
    static_folder=os.path.join(path.ROOT_DIR, "frontend"),
    static_url_path=""
)
@frontend_bp.route('/')
def index():
    print("YEAHHHHHH I AM BEING HIT!!!!!!!!!!!!!!!!!!!!!!")
    return send_from_directory(frontend_bp.static_folder, "index.html")

# Serve all other files
@frontend_bp.route('/<path:filename>')
def static_files(filename):
    file_path = os.path.join(frontend_bp.static_folder, filename)

    if os.path.exists(file_path):
        return send_from_directory(frontend_bp.static_folder, filename)

    # fallback for SPA routing (optional but useful)
    return send_from_directory(frontend_bp.static_folder, "index.html")

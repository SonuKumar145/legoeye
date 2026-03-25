
def server_app():

    import json
    from flask import Flask
    from flask_cors import CORS
    from utils.logger import Logger

    from server.apis.footage.file.routes import footage_file_bp
    from server.apis.footage.stream.routes import footage_stream_bp
    from server.apis.live.routes import live_bp
    from server.apis.db.routes import db_bp
    from server.apis.health.routes import health_bp
    from server.apis.frontend.routes import frontend_bp

    logger = Logger.get_logger(__name__)

    app = Flask(__name__)
    origins = ["http://localhost:3000", "https://192.168.1.7:5000", "https://192.168.1.7:3000"]
    CORS(app, 
         origins= origins,   
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"], 
         methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"]
         )


    logger.info(f"CORS origins allowed : {json.dumps(origins)}")

    try:
        logger.critical("""
                ******************************************************
                [Flask App] change ssl_cert and ssl_key path and more
                ******************************************************
                """)
        
        # Register blueprints
        app.register_blueprint(footage_file_bp, url_prefix="/api/footages")
        app.register_blueprint(footage_stream_bp, url_prefix="/api/stream/footage")
        app.register_blueprint(live_bp, url_prefix="/api/stream/live")
        app.register_blueprint(health_bp, url_prefix="/api/health")
        app.register_blueprint(db_bp, url_prefix="/api/db") 
        app.register_blueprint(frontend_bp, url_prefix="/")
        

        logger.info("Blueprints registered")

        return app
    finally:
        # picamMngr.stop()
        pass
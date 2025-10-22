from flask import Flask
from flask_cors import CORS
import logging

def create_app():
    app = Flask(__name__)
    
    # Configure CORS for local development
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Import and register blueprints
    from src.backend.routes.health import bp as health_bp
    from src.backend.routes.generate import bp as gen_bp
    from src.backend.routes.exports import bp as exp_bp
    from src.backend.routes.epics import bp as epics_bp
    from src.backend.routes.ui import bp as ui_bp

    def create_app():
        from flask import Flask
        app = Flask(__name__, template_folder="templates")

    app.register_blueprint(health_bp)                           # /health
    app.register_blueprint(gen_bp, url_prefix="/api/generate")  # /api/generate
    app.register_blueprint(exp_bp, url_prefix="/api/runs")      # /api/runs
    app.register_blueprint(epics_bp, url_prefix="/api/epics")    # /api/epics
    app.register_blueprint(ui_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(port=5000, debug=True)

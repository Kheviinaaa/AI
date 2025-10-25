from __future__ import annotations
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
env_path = Path(__file__).resolve().parents[2] / ".env"
import logging

from flask import Flask
from flask_cors import CORS

load_dotenv(find_dotenv())

def create_app() -> Flask:
    here = Path(__file__).resolve().parent
    app = Flask(__name__, template_folder="templates", static_folder="static")
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

    # Configure CORS for local development
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    from src.backend.routes.health import bp as health_bp
    from src.backend.routes.generate import bp as gen_bp
    from src.backend.routes.exports import bp as exp_bp
    from src.backend.routes.epics import bp as epics_bp
    from src.backend.routes.ui import bp as ui_bp
    from src.backend.routes.chat import bp as chat_bp

    app.register_blueprint(health_bp)  # /health
    app.register_blueprint(gen_bp, url_prefix="/api/generate")
    app.register_blueprint(exp_bp, url_prefix="/api/runs")
    app.register_blueprint(epics_bp, url_prefix="/api/epics")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(ui_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=5000, debug=True)

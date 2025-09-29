"""
Main Flask application.
"""

from flask import Flask, jsonify
from flask_cors import CORS
import logging
import sys
from app.config import Config
from app.db import db
from app.auth import auth_bp
from app.files import files_bp
from app.admin import admin_bp
from app.teams import teams_bp


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO if not Config.DEBUG else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
        sys.exit(1)

    # Test database connection
    if not db.test_connection():
        logging.error("Failed to connect to database")
        sys.exit(1)

    # Configure CORS
    CORS(
        app,
        origins=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
        ],
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(teams_bp)

    @app.route("/")
    def index():
        """Root endpoint."""
        return jsonify(
            {"message": "Markboard API", "version": "1.0.0", "status": "running"}
        )

    @app.route("/health")
    def health():
        """Health check endpoint."""
        try:
            # Test database connection
            db_status = db.test_connection()

            return jsonify(
                {
                    "status": "healthy" if db_status else "unhealthy",
                    "database": "connected" if db_status else "disconnected",
                    "timestamp": db.execute_one("SELECT NOW() as now")[
                        "now"
                    ].isoformat(),
                }
            ), (200 if db_status else 503)

        except Exception as e:
            return jsonify({"status": "unhealthy", "error": str(e)}), 503

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()

    # Seed development data on startup (only in debug/development mode)
    if Config.DEBUG:
        try:
            from seed_data import seed_development_data

            with app.app_context():
                seed_development_data()
        except ImportError:
            logging.warning(
                "seed_data module not found - skipping development data seeding"
            )
        except Exception as e:
            logging.error(f"Failed to seed development data: {e}")

    app.run(host="0.0.0.0", port=8000, debug=Config.DEBUG)

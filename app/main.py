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


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Load configuration
    Config.validate()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO if not Config.DEBUG else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Enable CORS for frontend integration
    CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(files_bp)

    # Health check endpoint
    @app.route("/health")
    def health_check():
        """Health check endpoint."""
        try:
            # Test database connection
            if db.test_connection():
                return (
                    jsonify(
                        {
                            "status": "healthy",
                            "database": "connected",
                            "timestamp": "2024-01-01T00:00:00Z",  # You can use datetime.now().isoformat()
                        }
                    ),
                    200,
                )
            else:
                return (
                    jsonify(
                        {
                            "status": "unhealthy",
                            "database": "disconnected",
                            "timestamp": "2024-01-01T00:00:00Z",
                        }
                    ),
                    503,
                )
        except Exception as e:
            return (
                jsonify(
                    {
                        "status": "unhealthy",
                        "error": str(e),
                        "timestamp": "2024-01-01T00:00:00Z",
                    }
                ),
                503,
            )

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=Config.DEBUG)

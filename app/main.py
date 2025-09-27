"""
Main Flask application.
"""

from flask import Flask, jsonify
from flask_cors import CORS
import logging
import sys
import bcrypt
from datetime import datetime, timezone
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
        except (Exception, bcrypt.BcryptError) as e:
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
    def not_found(_):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(_):
        return jsonify({"error": "Internal server error"}), 500

    return app


def seed_test_data():
    """Seed test data for development environment."""
    logger = logging.getLogger(__name__)

    # Only seed in development/debug mode
    if not Config.DEBUG:
        return

    logger.info("🌱 Seeding test data for development...")

    try:
        # Check if admin user already exists
        existing_admin = db.execute_one(
            "SELECT id FROM users WHERE email = %s", ("admin@markboard.com",)
        )

        if existing_admin:
            print("✅ Test data already exists")
            print("🔐 Admin: admin@markboard.com | password123")
            print("🌐 Frontend: http://localhost:3000")
            return

        # Create test password hash
        test_password = "password123"
        salt = bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)
        hashed_password = bcrypt.hashpw(test_password.encode("utf-8"), salt).decode(
            "utf-8"
        )

        # Create admin user
        admin_id = db.execute_modify(
            """INSERT INTO users (email, password_hash, is_admin, created_at) 
               VALUES (%s, %s, %s, %s)""",
            ("admin@markboard.com", hashed_password, True, datetime.now(timezone.utc)),
        )
        logger.info("Created admin user")

        # Create regular users
        users = [
            "john.doe@example.com",
            "sarah.wilson@example.com",
            "mike.chen@example.com",
        ]

        user_ids = [admin_id]
        for email in users:
            user_id = db.execute_modify(
                """INSERT INTO users (email, password_hash, is_admin, created_at) 
                   VALUES (%s, %s, %s, %s)""",
                (email, hashed_password, False, datetime.now(timezone.utc)),
            )
            user_ids.append(user_id)
            logger.info(f"Created user: {email}")

        # Create development team
        team_id = db.execute_modify(
            """INSERT INTO teams (name, description, owner_id, created_at) 
               VALUES (%s, %s, %s, %s)""",
            (
                "Development Team",
                "Main development team",
                admin_id,
                datetime.now(timezone.utc),
            ),
        )
        logger.info("Created Development Team")

        # Add admin to team
        db.execute_modify(
            """INSERT INTO team_members (team_id, user_id, role, joined_at) 
               VALUES (%s, %s, %s, %s)""",
            (team_id, admin_id, "admin", datetime.now(timezone.utc)),
        )

        # Create sample files
        sample_files = [
            {
                "name": "Welcome to Markboard.md",
                "content": """# Welcome to Markboard

## Getting Started
This is your first markdown file! You can edit this content using the built-in editor.

## Features
- **Real-time editing** with live preview
- **Team collaboration** with shared workspaces
- **Version control** to track changes
- **Admin dashboard** for system management

## Test Accounts
- Admin: admin@markboard.com (password: password123)
- Users: john.doe@example.com, sarah.wilson@example.com, mike.chen@example.com
- All use password: password123

## Next Steps
1. Try editing this file
2. Create new files
3. Invite team members
4. Explore the admin dashboard at /admin

Happy documenting! 🚀
""",
                "owner_id": admin_id,
                "team_id": team_id,
            },
            {
                "name": "API Documentation.md",
                "content": """# API Documentation

## Authentication
POST /auth/login - Login with email/password
POST /auth/signup - Create new account

## Files
GET /files - List all files
POST /files - Create new file
PUT /files/:id - Update file
DELETE /files/:id - Delete file

## Admin
GET /admin/users - List all users (admin only)
GET /admin/stats - System statistics (admin only)
""",
                "owner_id": user_ids[1],
                "team_id": team_id,
            },
        ]

        for file_data in sample_files:
            db.execute_modify(
                """INSERT INTO files (name, content, owner_id, team_id, 
                   created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    file_data["name"],
                    file_data["content"],
                    file_data["owner_id"],
                    file_data["team_id"],
                    datetime.now(timezone.utc),
                    datetime.now(timezone.utc),
                ),
            )
            logger.info(f"Created file: {file_data['name']}")

        print("=" * 70)
        print("✅ MARKBOARD DEVELOPMENT ENVIRONMENT READY!")
        print("=" * 70)
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:8000")
        print("🗄️  Database Admin: http://localhost:8080 (phpMyAdmin)")
        print("")
        print("🔐 ADMIN LOGIN:")
        print("   📧 admin@markboard.com | 🔑 password123")
        print("   🌐 Admin Dashboard: http://localhost:3000/admin")
        print("")
        print("👥 USER LOGINS:")
        print("   📧 john.doe@example.com | 🔑 password123")
        print("   📧 sarah.wilson@example.com | 🔑 password123")
        print("   📧 mike.chen@example.com | 🔑 password123")
        print("   🌐 User Dashboard: http://localhost:3000/dashboard")
        print("=" * 70)

    except (ValueError, bcrypt.BcryptError) as e:
        logger.error("❌ Error seeding test data: %s", e)


if __name__ == "__main__":
    app = create_app()

    # Seed test data on startup
    with app.app_context():
        seed_test_data()

    app.run(host="0.0.0.0", port=8000, debug=Config.DEBUG)

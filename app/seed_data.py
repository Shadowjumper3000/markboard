"""
Database seeding script for development environment.
"""

import bcrypt
import logging
from datetime import datetime, timezone
from app.config import Config
from app.db import db

logger = logging.getLogger(__name__)

logger.info("\ud83c\udf31 Seeding admin user...")


def seed_admin_user(force=False):
    """Seed only the admin user. Returns admin_id."""
    logger.info("🌱 Seeding admin user...")
    existing_admin = db.execute_one(
        "SELECT id FROM users WHERE email = %s", (Config.ADMIN_EMAIL,)
    )
    if existing_admin and not force:
        print("✅ Admin user already exists")
        print(f"🔐 Admin: {Config.ADMIN_EMAIL} | {Config.ADMIN_PASSWORD}")
        return existing_admin["id"]
    elif existing_admin and force:
        print("🔄 Force mode: Checking and creating admin user...")
        admin_id = existing_admin["id"]
    else:
        admin_id = None

    salt = bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)
    hashed_password = bcrypt.hashpw(Config.ADMIN_PASSWORD.encode("utf-8"), salt).decode(
        "utf-8"
    )

    if admin_id is None:
        admin_id = db.execute_modify(
            """INSERT INTO users (email, password_hash, is_admin, created_at)
               VALUES (%s, %s, %s, %s)""",
            (
                Config.ADMIN_EMAIL,
                hashed_password,
                True,
                datetime.now(timezone.utc),
            ),
        )
        logger.info("Created admin user: %s", Config.ADMIN_EMAIL)
    else:
        logger.info("Admin user already exists")
    return admin_id


logger.info("\ud83c\udf31 Seeding other development data...")


def seed_other_data(admin_id, force=False):
    """Seed regular users, teams, files, and activities."""
    logger.info("🌱 Seeding other development data...")
    try:
        # Create regular users
        salt = bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)
        hashed_password = bcrypt.hashpw(
            Config.ADMIN_PASSWORD.encode("utf-8"), salt
        ).decode("utf-8")
        users = [
            "john.doe@example.com",
            "sarah.wilson@example.com",
            "mike.chen@example.com",
        ]
        user_ids = [admin_id]
        for email in users:
            existing_user = db.execute_one(
                "SELECT id FROM users WHERE email = %s", (email,)
            )
            if existing_user:
                user_ids.append(existing_user["id"])
                logger.info("User already exists: %s", email)
            else:
                user_id = db.execute_modify(
                    """INSERT INTO users (email, password_hash, is_admin, created_at)
                       VALUES (%s, %s, %s, %s)""",
                    (email, hashed_password, False, datetime.now(timezone.utc)),
                )
                user_ids.append(user_id)
                logger.info("Created user: %s", email)

        # Create development team
        existing_dev_team = db.execute_one(
            "SELECT id FROM teams WHERE name = %s", ("Development Team",)
        )
        if existing_dev_team:
            team_id = existing_dev_team["id"]
            logger.info("Development Team already exists")
        else:
            team_id = db.execute_modify(
                """INSERT INTO teams (name, description, owner_id, created_at)
                   VALUES (%s, %s, %s, %s)""",
                (
                    "Development Team",
                    "Main development team for testing and development",
                    admin_id,
                    datetime.now(timezone.utc),
                ),
            )
            logger.info("Created Development Team")

        # Create additional teams
        teams_data = [
            ("Product Team", "Product planning and strategy", user_ids[1]),
            ("Design Team", "UI/UX design and research", user_ids[2]),
        ]
        team_ids = [team_id]
        for name, description, owner_id in teams_data:
            existing_team = db.execute_one(
                "SELECT id FROM teams WHERE name = %s", (name,)
            )
            if existing_team:
                team_ids.append(existing_team["id"])
                logger.info("Team already exists: %s", name)
            else:
                additional_team_id = db.execute_modify(
                    """INSERT INTO teams (name, description, owner_id, created_at)
                       VALUES (%s, %s, %s, %s)""",
                    (name, description, owner_id, datetime.now(timezone.utc)),
                )
                team_ids.append(additional_team_id)
                logger.info("Created team: %s", name)

        # Add admin to all teams (if not already a member)
        for tid in team_ids:
            existing_membership = db.execute_one(
                "SELECT id FROM team_members WHERE team_id = %s AND user_id = %s",
                (tid, admin_id),
            )
            if not existing_membership:
                db.execute_modify(
                    """INSERT INTO team_members (team_id, user_id, role, joined_at)
                       VALUES (%s, %s, %s, %s)""",
                    (tid, admin_id, "admin", datetime.now(timezone.utc)),
                )
                logger.info("Added admin to team %d", tid)
            else:
                logger.info("Admin already member of team %d", tid)

        # Add other users to teams as members
        team_memberships = [
            (team_ids[0], user_ids[1], "member"),  # John to Development Team
            (team_ids[0], user_ids[2], "member"),  # Sarah to Development Team
            (team_ids[1], user_ids[1], "admin"),  # John as admin of Product Team
            (team_ids[1], user_ids[3], "member"),  # Mike to Product Team
            (team_ids[2], user_ids[2], "admin"),  # Sarah as admin of Design Team
            (team_ids[2], user_ids[3], "member"),  # Mike to Design Team
        ]
        for team_id, user_id, role in team_memberships:
            existing_membership = db.execute_one(
                "SELECT id FROM team_members WHERE team_id = %s AND user_id = %s",
                (team_id, user_id),
            )
            if not existing_membership:
                db.execute_modify(
                    """INSERT INTO team_members (team_id, user_id, role, joined_at)
                       VALUES (%s, %s, %s, %s)""",
                    (team_id, user_id, role, datetime.now(timezone.utc)),
                )
                logger.info("Added user %d to team %d as %s", user_id, team_id, role)
            else:
                logger.info("User %d already member of team %d", user_id, team_id)

        # Create sample files using file storage logic
        from app.file_storage import file_storage

        sample_files = [
            {
                "name": "mermaid_flow_1.md",
                "owner_id": admin_id,
                "content": """```mermaid\ngraph TD;\n    A-->B;\n    B-->C;\n```""",
            },
            {
                "name": "mermaid_flow_2.md",
                "owner_id": admin_id,
                "content": """```mermaid\nflowchart LR\n    X-->Y\n    Y-->Z\n```""",
            },
        ]

        for file_data in sample_files:
            existing_file = db.execute_one(
                "SELECT id FROM files WHERE name = %s AND owner_id = %s",
                (file_data["name"], file_data["owner_id"]),
            )
            if existing_file:
                logger.info("File already exists: %s", file_data["name"])
            else:
                now = datetime.now(timezone.utc)
                # Insert file metadata (empty path/size)
                file_id = db.execute_modify(
                    """
                    INSERT INTO files (name, file_path, file_size, mime_type, owner_id, team_id, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        file_data["name"],
                        "",  # file_path
                        0,  # file_size
                        "text/markdown",
                        file_data["owner_id"],
                        None,
                        now,
                        now,
                    ),
                )
                # Generate file path and save content
                file_path = file_storage.generate_file_path(file_id, file_data["name"])
                file_size, checksum = file_storage.save_file(
                    file_path, file_data["content"]
                )
                # Update DB with file_path, file_size, checksum
                db.execute_modify(
                    """
                    UPDATE files SET file_path = %s, file_size = %s, checksum = %s WHERE id = %s
                    """,
                    (file_path, file_size, checksum, file_id),
                )
                logger.info("Created file: %s (ID: %d)", file_data["name"], file_id)

        # Log some activities for demonstration
        activities = [
            # ...existing code...
        ]
        for user_id, action, resource_type, details in activities:
            db.execute_modify(
                """INSERT INTO activity_logs (user_id, action, resource_type, details, created_at)
                   VALUES (%s, %s, %s, %s, %s)""",
                (user_id, action, resource_type, details, datetime.now(timezone.utc)),
            )

        print("=" * 70)
        print("✅ MARKBOARD DEVELOPMENT ENVIRONMENT READY!")
        print("=" * 70)
        print("🌐 Frontend: http://localhost:80")
        print("🔧 Backend API: http://localhost:8000")
        print("🗄️  Database Admin: http://localhost:8080 (phpMyAdmin)")
        print("")
        print("🔐 ADMIN LOGIN:")
        print("   📧 admin@markboard.com | 🔑 password123")
        print("   🌐 Admin Dashboard: http://localhost:80/admin")
        print("")
        print("👥 USER LOGINS:")
        print("   📧 john.doe@example.com | 🔑 password123")
        print("   📧 sarah.wilson@example.com | 🔑 password123")
        print("   📧 mike.chen@example.com | 🔑 password123")
        print("   🌐 User Dashboard: http://localhost:80/dashboard")
        print("")
        print("🏢 TEAMS CREATED:")
        print("   • Development Team (Admin as owner)")
        print("   • Product Team (John as owner)")
        print("   • Design Team (Sarah as owner)")
        print("=" * 70)
    except Exception as e:
        logger.error("\u274c Error seeding other development data: %s", e)
        raise


def seed_development_data(force=False):
    """Seed admin and other development data."""
    admin_id = seed_admin_user(force=force)
    seed_other_data(admin_id, force=force)


def seed_production_data(force=False):
    """Seed only admin user for production."""
    seed_admin_user(force=force)


if __name__ == "__main__":
    """Run seeding independently."""
    import argparse
    from app.main import create_app

    parser = argparse.ArgumentParser(description="Seed data")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-seed, check and create missing users/files",
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Seed only admin user (production mode)",
    )
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if args.prod:
            seed_production_data(force=args.force)
        else:
            seed_development_data(force=args.force)

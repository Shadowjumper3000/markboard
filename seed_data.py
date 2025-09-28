"""
Database seeding script for development environment.
"""

import bcrypt
import logging
from datetime import datetime, timezone
from app.config import Config
from app.db import db

logger = logging.getLogger(__name__)


def seed_development_data(force=False):
    """Seed development data including admin and test users."""
    logger.info("🌱 Seeding development data...")

    try:
        # Check if admin user already exists
        existing_admin = db.execute_one(
            "SELECT id FROM users WHERE email = %s", ("admin@markboard.com",)
        )

        if existing_admin and not force:
            print("✅ Development data already exists")
            print("🔐 Admin: admin@markboard.com | password123")
            print("🌐 Frontend: http://localhost:3000")
            return
        elif existing_admin and force:
            print("🔄 Force mode: Checking and creating missing data...")
            admin_id = existing_admin["id"]
        else:
            admin_id = None

        # Create test password hash
        test_password = "password123"
        salt = bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)
        hashed_password = bcrypt.hashpw(test_password.encode("utf-8"), salt).decode(
            "utf-8"
        )

        # Create admin user if not exists
        if admin_id is None:
            admin_id = db.execute_modify(
                """INSERT INTO users (email, password_hash, is_admin, created_at)
                   VALUES (%s, %s, %s, %s)""",
                (
                    "admin@markboard.com",
                    hashed_password,
                    True,
                    datetime.now(timezone.utc),
                ),
            )
            logger.info("Created admin user")
        else:
            logger.info("Admin user already exists")

        # Create regular users
        users = [
            "john.doe@example.com",
            "sarah.wilson@example.com",
            "mike.chen@example.com",
        ]

        user_ids = [admin_id]
        for email in users:
            # Check if user already exists
            existing_user = db.execute_one(
                "SELECT id FROM users WHERE email = %s", (email,)
            )

            if existing_user:
                user_ids.append(existing_user["id"])
                logger.info(f"User already exists: {email}")
            else:
                user_id = db.execute_modify(
                    """INSERT INTO users (email, password_hash, is_admin, created_at)
                       VALUES (%s, %s, %s, %s)""",
                    (email, hashed_password, False, datetime.now(timezone.utc)),
                )
                user_ids.append(user_id)
                logger.info(f"Created user: {email}")

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
                logger.info(f"Team already exists: {name}")
            else:
                additional_team_id = db.execute_modify(
                    """INSERT INTO teams (name, description, owner_id, created_at)
                       VALUES (%s, %s, %s, %s)""",
                    (name, description, owner_id, datetime.now(timezone.utc)),
                )
                team_ids.append(additional_team_id)
                logger.info(f"Created team: {name}")

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
                logger.info(f"Added admin to team {tid}")
            else:
                logger.info(f"Admin already member of team {tid}")

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
                logger.info(f"Added user {user_id} to team {team_id} as {role}")
            else:
                logger.info(f"User {user_id} already member of team {team_id}")

        # Create sample files
        sample_files = [
            {
                "name": "Welcome to Markboard.md",
                "content": """
# Welcome to Markboard

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
                "team_id": team_ids[0],
            },
            {
                "name": "API Documentation.md",
                "content": """# API Documentation

## Authentication
- POST /auth/login - Login with email/password
- POST /auth/signup - Create new account
- GET /auth/me - Get current user info

## Files
- GET /files - List all files
- POST /files - Create new file
- PATCH /files/:id - Update file
- DELETE /files/:id - Delete file

## Teams
- GET /teams - List user teams
- POST /teams - Create new team
- GET /teams/:id - Get team details

## Admin Endpoints
- GET /admin/users - List all users (admin only)
- GET /admin/stats - System statistics (admin only)
- GET /admin/activity - Recent activity logs (admin only)
- GET /admin/files - List all files in system (admin only)
""",
                "owner_id": user_ids[1],
                "team_id": team_ids[0],
            },
            {
                "name": "Product Roadmap.md",
                "content": """# Product Roadmap 2025

## Q1 Goals
- [ ] User authentication system
- [ ] File management
- [ ] Team collaboration features
- [ ] Real-time editing

## Q2 Goals
- [ ] Mobile app development
- [ ] Advanced search
- [ ] File sharing
- [ ] Integrations

## Q3 Goals
- [ ] Analytics dashboard
- [ ] API improvements
- [ ] Performance optimization
- [ ] Security enhancements

## Q4 Goals
- [ ] Enterprise features
- [ ] Advanced permissions
- [ ] Audit logging
- [ ] Scalability improvements
""",
                "owner_id": user_ids[1],
                "team_id": team_ids[1],
            },
            {
                "name": "Design System Guidelines.md",
                "content": """# Design System Guidelines

## Color Palette
- Primary: #007bff
- Secondary: #6c757d
- Success: #28a745
- Warning: #ffc107
- Danger: #dc3545

## Typography
- Headings: Inter, sans-serif
- Body: Inter, sans-serif
- Code: 'Fira Code', monospace

## Components
- Buttons with consistent hover states
- Cards with elegant shadows
- Forms with proper validation
- Navigation with clear hierarchy

## Spacing
- Base unit: 8px
- Small: 4px
- Medium: 16px
- Large: 32px
- XL: 64px
""",
                "owner_id": user_ids[2],
                "team_id": team_ids[2],
            },
            {
                "name": "Meeting Notes - Sprint Planning.md",
                "content": """# Sprint Planning - Week 1

## Attendees
- John Doe (Product)
- Sarah Wilson (Design)
- Mike Chen (Engineering)
- Admin User (Management)

## Goals
1. Complete user authentication system
2. Implement file management
3. Add team collaboration features

## Tasks Assigned
- **John**: Product requirements and user stories
- **Sarah**: UI/UX design and prototypes
- **Mike**: Backend API development
- **Admin**: Project coordination and testing

## Next Meeting
Friday 3:00 PM - Sprint Review
""",
                "owner_id": user_ids[3],
                "team_id": team_ids[0],
            },
            {
                "name": "Personal Notes.md",
                "content": """# Personal Notes

## Ideas
- Add real-time collaboration with WebSocket
- Implement file sharing with public links
- Mobile app development with React Native
- Advanced search with full-text indexing

## Research Topics
- WebSocket implementation for real-time editing
- Markdown rendering optimization
- User experience improvements
- Performance monitoring and analytics

## Learning Goals
- Master React hooks and context
- Learn advanced SQL optimization
- Explore containerization best practices
- Study security implementations
""",
                "owner_id": user_ids[3],
                "team_id": None,  # Personal file
            },
            {
                "name": "Admin Dashboard Requirements.md",
                "content": """# Admin Dashboard Requirements

## User Management
- View all users
- Manage user permissions
- Monitor user activity
- Handle user support requests

## System Monitoring
- Server health metrics
- Database performance
- Error tracking
- Usage analytics

## Content Management
- File management across all teams
- Content moderation
- Backup and recovery
- Data export capabilities

## Security Features
- Audit logs
- Access control
- Security alerts
- Compliance reporting
""",
                "owner_id": admin_id,
                "team_id": None,  # Admin personal file
            },
        ]

        # Import file storage
        from app.file_storage import file_storage

        for file_data in sample_files:
            # Check if file already exists
            existing_file = db.execute_one(
                "SELECT id FROM files WHERE name = %s AND owner_id = %s",
                (file_data["name"], file_data["owner_id"]),
            )

            if existing_file:
                logger.info(f"File already exists: {file_data['name']}")
            else:
                # First create the database record with placeholder file_path
                file_id = db.execute_modify(
                    """INSERT INTO files (name, owner_id, team_id, mime_type, file_path,
                       created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (
                        file_data["name"],
                        file_data["owner_id"],
                        file_data["team_id"],
                        "text/markdown",
                        "placeholder",  # Temporary placeholder
                        datetime.now(timezone.utc),
                        datetime.now(timezone.utc),
                    ),
                )

                # Generate file path and save content to filesystem
                file_path = file_storage.generate_file_path(file_id, file_data["name"])
                file_size, checksum = file_storage.save_file(
                    file_path, file_data["content"]
                )

                # Update database record with file path, size, and checksum
                db.execute_modify(
                    """UPDATE files SET file_path = %s, file_size = %s, checksum = %s
                       WHERE id = %s""",
                    (file_path, file_size, checksum, file_id),
                )

                logger.info(f"Created file: {file_data['name']} (ID: {file_id})")

        # Log some activities for demonstration
        activities = [
            (admin_id, "create", "file", "Created welcome file"),
            (user_ids[1], "create", "file", "Created API documentation"),
            (user_ids[2], "create", "file", "Created design guidelines"),
            (user_ids[3], "create", "file", "Created meeting notes"),
            (admin_id, "login", "user", "Admin login"),
            (user_ids[1], "login", "user", "User login"),
            (user_ids[2], "create", "team", "Created design team"),
            (user_ids[1], "create", "team", "Created product team"),
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
        print("")
        print("🏢 TEAMS CREATED:")
        print("   • Development Team (Admin as owner)")
        print("   • Product Team (John as owner)")
        print("   • Design Team (Sarah as owner)")
        print("=" * 70)

    except Exception as e:
        logger.error(f"❌ Error seeding development data: {e}")
        raise


if __name__ == "__main__":
    """Run seeding independently."""
    import argparse
    from app.main import create_app

    parser = argparse.ArgumentParser(description="Seed development data")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-seed, check and create missing users/files",
    )

    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        seed_development_data(force=args.force)

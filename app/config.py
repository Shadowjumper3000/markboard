"""
Configuration management using environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """Application configuration class."""

    # Database configuration
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "markboard_user")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "markboard_password")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "markboard")

    # JWT configuration
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))

    # Flask configuration
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Security
    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

    # Admin user credentials
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    @classmethod
    def get_db_connection_string(cls):
        """Get MySQL connection string."""
        return f"mysql+pymysql://{cls.MYSQL_USER}:{cls.MYSQL_PASSWORD}@{cls.MYSQL_HOST}:{cls.MYSQL_PORT}/{cls.MYSQL_DATABASE}"

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        required_vars = ["JWT_SECRET"]
        missing = []

        for var in required_vars:
            if not getattr(cls, var):
                missing.append(var)

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        if (
            cls.JWT_SECRET == "your-secret-key-change-in-production"
            and cls.FLASK_ENV == "production"
        ):
            raise ValueError("JWT_SECRET must be changed in production!")

"""
Configuration loading and management.
Centralized configuration module following best practices.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class DatabaseConfig:
    """Database configuration settings."""

    HOST: str = os.getenv("MYSQL_HOST", "localhost")
    PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    USER: str = os.getenv("MYSQL_USER", "markboard_user")
    PASSWORD: str = os.getenv("MYSQL_PASSWORD", "markboard_password")
    DATABASE: str = os.getenv("MYSQL_DATABASE", "markboard")

    @classmethod
    def get_connection_string(cls) -> str:
        """Get MySQL connection string."""
        return f"mysql+pymysql://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.DATABASE}"


class SecurityConfig:
    """Security-related configuration settings."""

    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_EXPIRY_HOURS: int = int(os.getenv("JWT_EXPIRY_HOURS", "24"))
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))

    @classmethod
    def validate_production_security(cls) -> None:
        """Validate security settings for production environment."""
        if (
            cls.JWT_SECRET == "your-secret-key-change-in-production"
            and AppConfig.FLASK_ENV == "production"
        ):
            raise ValueError("JWT_SECRET must be changed in production!")


class AppConfig:
    """Application configuration settings."""

    FLASK_ENV: str = os.getenv("FLASK_ENV", "production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Admin user credentials for seeding
    ADMIN_EMAIL: Optional[str] = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD: Optional[str] = os.getenv("ADMIN_PASSWORD")

    # File storage paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    FILES_DIR: Path = DATA_DIR / "files"


class Config:
    """Main configuration class aggregating all config sections."""

    # Database
    MYSQL_HOST = DatabaseConfig.HOST
    MYSQL_PORT = DatabaseConfig.PORT
    MYSQL_USER = DatabaseConfig.USER
    MYSQL_PASSWORD = DatabaseConfig.PASSWORD
    MYSQL_DATABASE = DatabaseConfig.DATABASE

    # Security
    JWT_SECRET = SecurityConfig.JWT_SECRET
    JWT_EXPIRY_HOURS = SecurityConfig.JWT_EXPIRY_HOURS
    BCRYPT_ROUNDS = SecurityConfig.BCRYPT_ROUNDS

    # Application
    FLASK_ENV = AppConfig.FLASK_ENV
    DEBUG = AppConfig.DEBUG
    ADMIN_EMAIL = AppConfig.ADMIN_EMAIL
    ADMIN_PASSWORD = AppConfig.ADMIN_PASSWORD

    @classmethod
    def get_db_connection_string(cls) -> str:
        """Get MySQL connection string."""
        return DatabaseConfig.get_connection_string()

    @classmethod
    def validate(cls) -> None:
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

        # Validate security settings
        SecurityConfig.validate_production_security()

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure required directories exist."""
        AppConfig.FILES_DIR.mkdir(parents=True, exist_ok=True)

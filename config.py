"""Configuration for Astro Pitch Database.

Settings are read from environment variables (or a .env file) so that
passwords are not hard-coded. The defaults match the Milestone 2 YAML spec
for a local PostgreSQL install.
"""
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "astropitch")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    # Database used only to run CREATE DATABASE (it always exists)
    DB_MAINTENANCE = os.getenv("DB_MAINTENANCE", "postgres")

    @classmethod
    def conninfo(cls, dbname=None):
        """Return a libpq connection string for psycopg.connect()."""
        return (
            f"host={cls.DB_HOST} port={cls.DB_PORT} dbname={dbname or cls.DB_NAME} "
            f"user={cls.DB_USER} password={cls.DB_PASSWORD}"
        )

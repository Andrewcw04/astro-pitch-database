"""initialise_db.py - create the Astro Pitch database and its tables.

Steps:
  1. Connect to the maintenance database ("postgres").
  2. Create the application database (default "astropitch") if it does not exist.
  3. Connect to the application database and run schema.sql, which (re)creates
     the facility, pitch, users and review tables with their keys and constraints.

Usage:
    python initialise_db.py

Connection settings come from config.py / environment variables
(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD).
"""
import re
import sys
from pathlib import Path

import psycopg

from config import Config

SCHEMA_FILE = Path(__file__).resolve().parent / "schema.sql"
TABLES = ["facility", "pitch", "users", "review"]


def create_database(name):
    """Create the database if it is missing. Returns True if it was created."""
    # CREATE DATABASE cannot take a query parameter, so validate the name first
    if not re.fullmatch(r"[a-z_][a-z0-9_]{0,62}", name):
        raise ValueError(f"Invalid database name: {name!r}")

    # CREATE DATABASE cannot run inside a transaction, so use autocommit
    with psycopg.connect(Config.conninfo(Config.DB_MAINTENANCE), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,))
            if cur.fetchone():
                return False
            cur.execute(f'CREATE DATABASE "{name}"')
            return True


def create_tables():
    """Run schema.sql against the application database."""
    schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")
    with psycopg.connect(Config.conninfo()) as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)  # several statements, no parameters
        conn.commit()


def list_tables():
    with psycopg.connect(Config.conninfo()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            )
            return [row[0] for row in cur.fetchall()]


def main():
    try:
        created = create_database(Config.DB_NAME)
        print(f"Database '{Config.DB_NAME}' "
              f"{'created' if created else 'already exists - reusing it'}.")
        create_tables()
        tables = list_tables()
        print("Tables created:", ", ".join(tables))
        missing = set(TABLES) - set(tables)
        if missing:
            print("ERROR: missing tables:", ", ".join(sorted(missing)))
            return 1
    except psycopg.Error as exc:
        print(f"Database error: {exc}")
        return 1
    print("Initialisation complete. Next: python populate_db.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())

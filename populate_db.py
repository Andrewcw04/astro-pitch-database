"""populate_db.py - load the seed data in data/*.csv into the Astro Pitch tables.

Run initialise_db.py first. The script:
  1. Empties the four tables (TRUNCATE), so it can be re-run safely.
  2. Inserts rows from the CSV files in foreign-key order:
       facility -> pitch -> users -> review
  3. Hashes a demo password for every seed user (passwords are never stored
     in plain text). Set DEMO_PASSWORD in the environment to change it.
  4. Prints the row count of each table.

All inserts run in one transaction: if any row fails, nothing is saved.

Usage:
    python populate_db.py
"""
import csv
import os
import sys
from pathlib import Path

import psycopg
from werkzeug.security import generate_password_hash

from config import Config

DATA_DIR = Path(__file__).resolve().parent / "data"
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "AstroPitch2026!")

# table name -> columns, in the order they must be loaded
TABLES = {
    "facility": ["facility_id", "facility_name", "address"],
    "pitch": ["pitch_id", "pitch_name", "pitch_size", "max_players",
              "opening_time", "closing_time", "facility_id"],
    "users": ["user_id", "username", "email", "password"],
    "review": ["review_id", "rating", "comment", "review_date", "user_id", "pitch_id"],
}


def read_csv(table):
    """Read data/<table>.csv and return a list of dicts."""
    path = DATA_DIR / f"{table}.csv"
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def prepare_rows(table, rows):
    """Turn CSV dicts into tuples in column order."""
    if table == "users":
        # One hash per run is enough for demo accounts
        hashed = generate_password_hash(DEMO_PASSWORD)
        for row in rows:
            row["password"] = hashed
    columns = TABLES[table]
    return [tuple(row[col] or None for col in columns) for row in rows]


def main():
    try:
        with psycopg.connect(Config.conninfo()) as conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE review, users, pitch, facility")
                for table, columns in TABLES.items():
                    rows = prepare_rows(table, read_csv(table))
                    placeholders = ", ".join(["%s"] * len(columns))
                    sql = (f"INSERT INTO {table} ({', '.join(columns)}) "
                           f"VALUES ({placeholders})")
                    cur.executemany(sql, rows)
                    print(f"Inserted {len(rows):>3} rows into {table}")
            conn.commit()

            with conn.cursor() as cur:
                print("\nRow counts:")
                for table in TABLES:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    print(f"  {table:<9} {cur.fetchone()[0]}")
    except FileNotFoundError as exc:
        print(f"Missing data file: {exc.filename}")
        return 1
    except psycopg.Error as exc:
        print(f"Database error (nothing was saved): {exc}")
        return 1
    print(f"\nPopulation complete. Demo users log in with password: {DEMO_PASSWORD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

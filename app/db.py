"""Database helper: one place that opens PostgreSQL connections."""
import psycopg
from psycopg.rows import dict_row

from config import Config


def query(sql, params=None):
    """Run a SELECT and return the rows as a list of dicts.

    Always pass user input through params (%s placeholders), never by
    formatting it into the SQL string, to prevent SQL injection.
    """
    with psycopg.connect(Config.conninfo(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

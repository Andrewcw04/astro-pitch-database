from datetime import datetime

import psycopg
from flask import flash, render_template, request

from app import app
from app.db import query


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Home")


@app.route("/about")
def about():
    return render_template("about.html", title="About Us")


def parse_time(value):
    """Return a 'HH:MM' string if value is a valid time, else None."""
    try:
        return datetime.strptime(value, "%H:%M").strftime("%H:%M")
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------
# Feature 1: search pitches by opening time
# Shows every pitch that is open at the chosen start time and, if given,
# still open at the chosen finish time.
# ---------------------------------------------------------------------
SEARCH_BY_TIME_SQL = """
    SELECT p.pitch_id, p.pitch_name, p.pitch_size, p.max_players,
           to_char(p.opening_time, 'HH24:MI') AS opens,
           to_char(p.closing_time, 'HH24:MI') AS closes,
           f.facility_name, f.address,
           to_char(AVG(r.rating), 'FM9.0') AS avg_rating,
           COUNT(r.review_id) AS review_count
    FROM pitch p
    JOIN facility f ON f.facility_id = p.facility_id
    LEFT JOIN review r ON r.pitch_id = p.pitch_id
    WHERE p.opening_time <= %s::time
      AND p.closing_time >= %s::time
    GROUP BY p.pitch_id, f.facility_id
    ORDER BY p.opening_time, f.facility_name, p.pitch_name
"""


@app.route("/search/opening-time")
def search_by_time():
    start_raw = request.args.get("start", "").strip()
    end_raw = request.args.get("end", "").strip()
    pitches = None  # None = no search yet; [] = searched, nothing found

    if start_raw:
        start = parse_time(start_raw)
        end = parse_time(end_raw) if end_raw else None
        if start is None or (end_raw and end is None):
            flash("Please enter times in HH:MM format, e.g. 18:30.")
        elif end and end <= start:
            flash("The finish time must be after the start time.")
        else:
            try:
                pitches = query(SEARCH_BY_TIME_SQL, (start, end or start))
            except psycopg.Error:
                app.logger.exception("search_by_time query failed")
                flash("Sorry, the pitch database is not available right now.")

    return render_template("search_time.html", title="Search by Opening Time",
                           pitches=pitches, start=start_raw, end=end_raw)

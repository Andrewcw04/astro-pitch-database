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


# ---------------------------------------------------------------------
# Feature 2: filter pitches by group size and/or pitch size
# Shows pitches big enough for the group, smallest suitable pitch first,
# so groups are not pointed at a full-size pitch they do not need.
# ---------------------------------------------------------------------
PITCH_SIZES = ["5-a-side", "7-a-side", "9-a-side", "11-a-side"]
MAX_GROUP = 50

FILTER_BY_SIZE_SQL = """
    SELECT p.pitch_id, p.pitch_name, p.pitch_size, p.max_players,
           p.max_players - %s AS spare_places,
           to_char(p.opening_time, 'HH24:MI') AS opens,
           to_char(p.closing_time, 'HH24:MI') AS closes,
           f.facility_name, f.address
    FROM pitch p
    JOIN facility f ON f.facility_id = p.facility_id
    WHERE p.max_players >= %s
      AND (%s::varchar IS NULL OR p.pitch_size = %s::varchar)
    ORDER BY p.max_players, f.facility_name, p.pitch_name
"""


@app.route("/search/group-size")
def filter_by_size():
    players_raw = request.args.get("players", "").strip()
    size = request.args.get("size", "").strip()
    pitches = None  # None = no search yet; [] = searched, nothing found
    players = None

    if "players" in request.args or size:
        if players_raw:
            try:
                players = int(players_raw)
            except ValueError:
                players = -1
        if players is not None and not 1 <= players <= MAX_GROUP:
            flash(f"Group size must be a whole number from 1 to {MAX_GROUP}.")
        elif size and size not in PITCH_SIZES:
            flash("Please choose a pitch size from the list.")
        elif players is None and not size:
            flash("Enter a group size, choose a pitch size, or both.")
        else:
            need = players or 1
            try:
                pitches = query(FILTER_BY_SIZE_SQL, (need, need, size or None, size or None))
            except psycopg.Error:
                app.logger.exception("filter_by_size query failed")
                flash("Sorry, the pitch database is not available right now.")

    best_size = pitches[0]["pitch_size"] if pitches and players else None
    return render_template("filter_size.html", title="Filter by Group Size",
                           pitches=pitches, players=players_raw, size=size,
                           sizes=PITCH_SIZES, best_size=best_size, max_group=MAX_GROUP)

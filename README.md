# Astro Pitch Database

**INFO8021 DevOps Strategy and Automation** · Andrew White (R00253860)

Astro Pitch Database helps people find an astro pitch that suits their group. Users can
see which pitches are open at the time they want to play and which pitch size fits a
smaller or larger group. Registered users will be able to review the pitches they have
played on.

It is a Python/Flask web application backed by a PostgreSQL database.

## Features

| # | Feature | Status | Branch |
|---|---------|--------|--------|
| 1 | Search pitches by opening time | Done | `feature/search-by-opening-time` |
| 2 | Filter pitches by group size / pitch size | Done | `feature/filter-by-group-size` |
| 3 | Register | Planned | – |
| 4 | Login | Planned | – |
| 5 | Add a review for a pitch | Planned | – |
| 6 | Pitch summary table | Planned | – |

The `main` branch holds the initial website (Home and About Us pages, no database
features). Each database feature is developed on its own branch and is **not** merged
into `main` yet.

## Tech stack

- Python 3.12, Flask 3.1.3, Jinja2 templates
- PostgreSQL 18 with the psycopg 3 driver
- HTML5 / CSS3
- Git and GitHub for version control, Docker for containers

See `astro_pitch_tech_spec.yml` for the full list of versions.

## Database

Four tables (see `schema.sql`):

| Table | Purpose | Seed rows |
|-------|---------|-----------|
| `facility` | Sports centres that own pitches | 8 |
| `pitch` | Individual astro pitches: size, max players, opening/closing time (main table) | 24 |
| `users` | Registered users (passwords stored as hashes) | 20 |
| `review` | A user's 1-5 rating and comment for a pitch | 40 |

Relationships: a facility has many pitches; a pitch has many reviews; a user writes many
reviews. `users` is used instead of `user` because `USER` is a reserved word in PostgreSQL.

The seed data in `data/*.csv` is **fictional sample data generated with GenAI**. The
venue names and ratings are made up; place names are real Cork areas.

## Getting started

```bash
# 1. Clone and enter the project
git clone https://github.com/<your-username>/astro-pitch-database.git
cd astro-pitch-database

# 2. Create a virtual environment and install packages
python -m venv venv
venv\Scripts\activate            # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt

# 3. Set your database password
copy .env.example .env           # macOS/Linux: cp .env.example .env
#    then edit .env so DB_PASSWORD matches your PostgreSQL install

# 4. Create the database and tables, then load the data
python initialise_db.py
python populate_db.py

# 5. Run the site
flask --app astropitch run
```

Open <http://127.0.0.1:5000>. To try a feature, check out its branch first, for example
`git checkout feature/search-by-opening-time`.

### With Docker

```bash
docker compose up -d --build
docker compose exec web python initialise_db.py
docker compose exec web python populate_db.py
```

## Project structure

```
AstroPitch/
├── astropitch.py            # entry point
├── config.py                # settings from environment variables / .env
├── initialise_db.py         # creates the database and tables
├── populate_db.py           # loads data/*.csv into the tables
├── schema.sql               # CREATE TABLE statements
├── requirements.txt         # pinned Python packages
├── astro_pitch_tech_spec.yml
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── data/                    # seed data (facility, pitch, users, review)
└── app/
    ├── __init__.py          # creates the Flask app
    ├── routes.py            # URL routes
    ├── db.py                # database helper
    ├── static/style.css
    └── templates/           # base, index, about (+ feature pages on branches)
```

## Author

Andrew White · R00253860 · Munster Technological University

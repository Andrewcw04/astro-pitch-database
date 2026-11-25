"""Entry point for Astro Pitch Database.

Run with:
    flask --app astropitch run        (or)   python astropitch.py
"""
from app import app

if __name__ == "__main__":
    app.run(debug=True)

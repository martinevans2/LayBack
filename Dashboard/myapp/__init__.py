from flask import Flask, jsonify, redirect, Blueprint, g
from datetime import timedelta

from .routes import main


def format_currency(value):
    try:
        return f"{value / 100:.2f}"
    except (TypeError, ValueError):
        return "0.00"


# Create your Flask app and start the thread
app = Flask(__name__)
app.register_blueprint(main)
app.secret_key = 'FcSVt12g4vv46pvHhp3x0'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config["DATABASE"] = "../DB/app.db"
app.jinja_env.filters["currency"] = format_currency


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def get_app():
    return app

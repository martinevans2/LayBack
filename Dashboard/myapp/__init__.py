from flask import Flask, jsonify, redirect, Blueprint, g
from datetime import timedelta

from .routes import main

# Create your Flask app and start the thread
app = Flask(__name__)
app.register_blueprint(main)
app.secret_key = 'FcSVt12g4vv46pvHhp3x0'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config["DATABASE"] = "../DB/app.db"


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def get_app():
    return app

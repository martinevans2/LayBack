import sqlite3
from flask import jsonify, redirect, Blueprint, render_template, g, current_app, session, request

main = Blueprint('main', __name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row  # dict-like rows
    return g.db


def get_users():
    db = get_db()
    rows = db.execute("SELECT id, name FROM users ORDER BY id DESC").fetchall()
    return {row["id"]: dict(row) for row in rows}


def get_prices():
    db = get_db()
    rows = db.execute("SELECT id, placed_by, price, outcome_id, backing FROM orders").fetchall()
    return [dict(row) for row in rows]


@main.route('/')
def index():
    logged_in = session.get('logged_in', 0)
    if logged_in > 0:
        return redirect('/home')
    return render_template('index.html', users=get_users())


@main.route('/login', methods=['POST'])
def login():
    if request.method != 'POST':
        return redirect('/')
    user_id = int(request.form['user_id'])
    # password = request.form['password']
    if user_id in get_users():
        session['logged_in'] = user_id
        session.permanent = True
    return redirect('/home')


@main.route('/logout')
def logout():
    session['logged_in'] = 0
    return redirect('/')


@main.route('/home')
def home():
    logged_in = session.get('logged_in', 0)
    if logged_in == 0:
        return redirect('/')
    users = get_users()
    return render_template('home.html', users=users, user=users[logged_in], prices=get_prices())

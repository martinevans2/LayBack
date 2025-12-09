import sqlite3
from flask import jsonify, redirect, Blueprint, render_template, g, current_app, session, request
from operator import itemgetter
from itertools import groupby

main = Blueprint('main', __name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row  # dict-like rows
    return g.db


def get_users():
    db = get_db()
    rows = db.execute("SELECT id, name FROM users ORDER BY name").fetchall()
    return [dict(row) for row in rows]


def get_prices():
    db = get_db()
    rows = db.execute("SELECT id, placed_by, price, outcome_id, backing FROM orders").fetchall()
    return [dict(row) for row in rows]


def extract_display_prices(prices: list):
    backs = list(sorted(filter(lambda p: p['backing'] == 1, prices), key=lambda p: -p['price']))
    lays = list(sorted(filter(lambda p: p['backing'] != 1, prices), key=lambda p: p['price']))
    return {'backs': backs, 'lays': lays}


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
    if user_id in map(lambda u: u['id'], get_users()):
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
    users_by_id = {user['id']: user for user in users}
    logged_user = users_by_id.get(logged_in, None)  # next((u for u in users if u['id'] == logged_in), None)
    if logged_user is None:
        return redirect('/')

    prices = get_prices()
    by_outcome = {k: extract_display_prices(list(group)) for k, group in groupby(prices, itemgetter('outcome_id'))}
    own_orders = [p for p in prices if p['placed_by'] == logged_in]
    return render_template('home.html', users=users, user=logged_user, prices=by_outcome,
                           own_orders=own_orders, users_by_id=users_by_id)


@main.route('/neworder', methods=['POST'])
def neworder():
    placed_by = int(request.form['placed_by'])
    outcome_id = int(request.form['outcome_id'])
    backing = int(request.form['backing'])
    price = int(float(request.form['price']) * 100)
    values = (placed_by, outcome_id, backing, price)

    # Checks
    if placed_by == outcome_id and backing == 0:
        return redirect('/home')  # Cannot lay yourself

    # Place order
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO orders (placed_by, outcome_id, backing, price) VALUES (?,?,?,?)", values)
    db.commit()
    return redirect('/home')


@main.route('/delete', methods=['GET'])
def delete_order():
    order_id = int(request.values['id'])
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    db.commit()
    return redirect('/home')

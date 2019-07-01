import sqlite3

from flask import Flask, render_template, g, request, jsonify, redirect, url_for
from datetime import datetime

app = Flask(__name__)


def connect_db():
    db = sqlite3.connect('food_log.db')
    db.row_factory = sqlite3.Row
    return db


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()

    if request.method == 'POST':
        date = request.form['date']

        dt = datetime.strptime(date, '%Y-%m-%d')
        db_date = datetime.strftime(dt, '%Y%m%d')

        db.execute('insert into log_date(entry_date) values(?)', [db_date])
        db.commit()

        return redirect(url_for('index'))

    cur = db.execute('select * from log_date order by entry_date desc')
    results = cur.fetchall()

    pretty_results = list()

    for item in results:
        single_date = dict()

        dt = datetime.strptime(str(item['entry_date']), '%Y%m%d')
        single_date['entry_date'] = datetime.strftime(dt, '%B %d, %Y')

        pretty_results.append(single_date)

    return render_template('home.html', results=pretty_results)


@app.route('/view/<date>', methods=['GET', 'POST'])
def view(date):
    db = get_db()

    date_cur = db.execute('select * from log_date where entry_date = ?', [date])
    date_result = date_cur.fetchone()

    if request.method == 'POST':
        food_id = request.form['food-select']
        date_id = date_result['id']

        db.execute('insert into food_date(food_id, log_date_id) values(?, ?)', [food_id, date_id])
        db.commit()

        return redirect(url_for('view', date=date))

    dt = datetime.strptime(str(date_result['entry_date']), '%Y%m%d')
    pretty_date = datetime.strftime(dt, '%B %d, %Y')

    food_cur = db.execute('select id, name from food')
    food_results = food_cur.fetchall()

    log_sql = ' '.join(['select food.name, food.protein, food.carbohydrates, food.fat, food.calories',
                        'from log_date join food_date',
                        'on food_date.log_date_id == log_date.id',
                        'join food',
                        'on food.id == food_date.food_id',
                        'where log_date.entry_date = ?'])

    log_cur = db.execute(log_sql, [date])
    log_results = log_cur.fetchall()

    return render_template('day.html', date=pretty_date, food_results=food_results, log_results=log_results)


@app.route('/food', methods=['GET', 'POST'])
def food():
    db = get_db()

    if request.method == 'POST':
        name = str(request.form['food-name'])
        protein = int(request.form['protein'])
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])

        calories = protein * 4 + carbohydrates * 4 + fat * 9

        db.execute('insert into food(name, protein, carbohydrates, fat, calories) values(?, ?, ?, ?, ?)',
                   [name, protein, carbohydrates, fat, calories])
        db.commit()

        return redirect(url_for('food'))

    cursor = db.execute('select id, name, protein, carbohydrates, fat, calories from food')
    results = cursor.fetchall()

    return render_template('add_food.html', title='Food', results=results)


if __name__ == '__main__':
    app.run(debug=True)

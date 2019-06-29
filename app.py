import sqlite3

from flask import Flask, render_template, g, request, jsonify, redirect, url_for

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


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/view')
def view():
    return render_template('day.html')


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
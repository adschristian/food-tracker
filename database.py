import sqlite3
from flask import g


def connect_db():
    db = sqlite3.connect('food_log.db')
    db.row_factory = sqlite3.Row
    return db


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


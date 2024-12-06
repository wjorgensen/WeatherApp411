import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        db_path = current_app.config.get('DATABASE', 'weather.db')
        g.db = sqlite3.connect(
            db_path,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

def clear_db():
    db = get_db()
    db.execute('DELETE FROM favorite_locations')
    db.execute('DELETE FROM users')
    db.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

@click.command('clear-db')
@with_appcontext
def clear_db_command():
    """Clear all data from the database."""
    clear_db()
    click.echo('Cleared all data from the database.') 
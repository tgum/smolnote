import os
import time
import sqlite3

script_dir = os.path.dirname(__file__)  # Get the directory of the current script


def rel_file(path):
    return os.path.join(script_dir, path)


DB_PATH = rel_file("users.db")
db_conn = sqlite3.connect(DB_PATH)
db_cursor = db_conn.cursor()

db_cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Users (
    userid INTEGER PRIMARY KEY,
    name TEXT,
    password TEXT,
    creation_date INTEGER
);
"""
)
db_cursor.execute(
    """
CREATE TABLE IF NOT EXISTS Notes (
    noteid INTEGER PRIMARY KEY,
    name TEXT,
    filename TEXT,
    creatorid INTEGER,
    creation_date INTEGER,
    modified INTEGER
);
"""
)


def add_note(name, creatorid):
    db_cursor.execute(
        """
    INSERT INTO Notes (name, filename, creatorid, creation_date, modified)
    VALUES (?, ?, ?, ?, ?);
    """,
        (name, name, creatorid, time.time(), time.time()),
    )
    db_conn.commit()


def get_notes_by_user(userid):
    return db_cursor.execute(
        "SELECT * FROM Notes WHERE creatorid=?", (userid,)
    ).fetchall()


def get_note_by_id(noteid):
    return db_cursor.execute(
        """SELECT * FROM Notes WHERE noteid=?""", (noteid,)
    ).fetchall()[0]


def delete_note(noteid):
    db_cursor.execute("""DELETE FROM Notes WHERE noteid=?""", (noteid,))


def add_user(name, password):
    db_cursor.execute(
        """
    INSERT INTO Users (name, password, creation_date)
    VALUES (?, ?, ?);
    """,
        (name, password, time.time()),
    )
    db_conn.commit()


def get_user_by_name(name):
    return db_cursor.execute("SELECT * FROM Users WHERE name=?;", (name,)).fetchall()


def get_user_by_id(id):
    return db_cursor.execute("SELECT * FROM Users WHERE userid=?;", (id,)).fetchall()[0]

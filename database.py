import os
import sqlite3
import sqlalchemy as db
from algorithmic_art_characteristics import *
from music_feature_extraction import *

def setup_database(db_path="musicVis_features.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_title TEXT,
            file_name TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_id INTEGER,
            stem_type TEXT,
            file_name TEXT,
            FOREIGN KEY (song_id) REFERENCES songs(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stem_id INTEGER,
            timestamp REAL,
            features JSON,
            FOREIGN KEY (stem_id) REFERENCES stems(id)
        )
    ''')
    conn.execute("PRAGMA foreign_keys = ON;")

    conn.commit()
    conn.close()

def insert_song(conn,song_title, file_name):
    cursor = conn.cursor()

    cursor.execute('INSERT INTO songs (song_title, file_name) VALUES (?, ?)', (song_title, file_name))
    song_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return song_id

def insert_stem(conn, song_id, stem_type, file_name):
    cursor = conn.cursor()

    cursor.execute('INSERT INTO stems (song_id, stem_type, file_name) VALUES (?, ?, ?)', (song_id, stem_type, file_name))
    stem_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return stem_id

def insert_feature(conn, stem_id, timestamp, features):
    cursor = conn.cursor()

    cursor.execute('INSERT INTO features (stem_id, timestamp, features) VALUES (?, ?, ?)', (stem_id, timestamp, features))

    conn.commit()
    conn.close()

# Add features from stemmed directory to database
def add_stems_to_db(db_path="musicVis_features.db"):
    conn = sqlite3.connect(db_path)
    stem_dir = "separated/htdemucs_6s/"
    for directory in os.listdir(stem_dir):
        song_stem_dir = os.path.join(stem_dir, directory)
        song_id = insert_song(conn, directory, song_stem_dir)
        for file_name in os.listdir(song_stem_dir):
            if file_name.endswith(".wav"):
                stem = os.path.join(song_stem_dir, file_name)
                stem_id = insert_stem(conn, song_id, file_name.split('.')[0], stem)
                features = get_features(stem, time_chunk=4)
                for feature in features:
                    if feature is not None:
                        insert_feature(conn, stem_id, feature.time, feature.to_dict())

# engine = db.create_engine('sqlite:///user:pass@host:port/db', echo=True, future=True)
# setup_database()

add_stems_to_db()
"""
Database to save extracted features from various audio files which can be used for visualization.
"""

import sqlite3
import pickle

conn = sqlite3.connect("music_features.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS music_features (
    track_id TEXT,
    timestamp REAL,
    feature_name TEXT,
    feature_value BLOB
);
""")
conn.commit()

def insert_feature(track_id, timestamp, feature_name, vector):
    blob = pickle.dumps(vector)
    c.execute("INSERT INTO features VALUES (?, ?, ?, ?)",
              (track_id, timestamp, feature_name, blob))
    conn.commit()

def get_features(track_id, t_start, t_end, feature_name):
    c.execute("""
        SELECT timestamp, feature_value
        FROM features
        WHERE track_id=? AND feature_name=?
          AND timestamp BETWEEN ? AND ?
        ORDER BY timestamp;
    """, (track_id, feature_name, t_start, t_end))

    out = []
    for ts, blob in c.fetchall():
        out.append((ts, pickle.loads(blob)))
    return out
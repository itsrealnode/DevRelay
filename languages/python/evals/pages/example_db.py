import sqlite3


def sample(size):
    db = sqlite3.connect(":memory:")
    db.executescript("""
        CREATE TABLE team (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE ticket (id INTEGER PRIMARY KEY, team_id INTEGER REFERENCES team(id));
    """)
    db.executemany(
        "INSERT INTO team VALUES (?, ?)",
        [(i, f"Team {i}") for i in range(1, size + 1)],
    )
    db.executemany(
        "INSERT INTO ticket VALUES (?, ?)",
        [(i, i if i % 4 else None) for i in range(1, size + 1)],
    )
    return db

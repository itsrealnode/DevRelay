def initialize(db):
    with db:
        db.execute("CREATE TABLE account (balance INTEGER NOT NULL)")
        db.execute("INSERT INTO account VALUES (100)")
        db.execute("CREATE TABLE inbox (event_id TEXT PRIMARY KEY, amount INTEGER, state TEXT)")


def receive(db, event_id, amount):
    with db:
        db.execute(
            """INSERT INTO inbox VALUES (?, ?, 'new')
               ON CONFLICT(event_id) DO UPDATE SET state = excluded.state""",
            (event_id, amount),
        )
    return 200


def process_next(db):
    with db:
        event = db.execute(
            "SELECT event_id, amount FROM inbox WHERE state = 'new' ORDER BY rowid LIMIT 1"
        ).fetchone()
        if event is None:
            return
        event_id, amount = event
        db.execute("UPDATE account SET balance = balance + ?", (amount,))
        db.execute("UPDATE inbox SET state = 'processed' WHERE event_id = ?", (event_id,))

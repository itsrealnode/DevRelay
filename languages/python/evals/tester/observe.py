"""Maintainer's checks, excluded from prepared candidate workspaces."""

import sqlite3
import sys
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from threading import Barrier


def contact(db, check_clear):
    from api import application, initialize, request

    initialize(db)
    app = application(db)
    before = request(app, "GET")
    updated = request(app, "PATCH", {"city": "Kazan"})
    stored = request(app, "GET")
    phone_update = request(app, "PATCH", {"phone": "+70002"})
    after_update = request(app, "GET")
    steps = (before, updated, stored, phone_update, after_update)
    if not check_clear:
        return steps
    cleared = request(app, "PATCH", {"phone": None})
    return steps + (cleared, request(app, "GET"))


def credit(db):
    from service import initialize, process_next, receive

    def state():
        balance = db.execute("SELECT balance FROM account").fetchone()[0]
        events = db.execute("SELECT event_id, state FROM inbox ORDER BY event_id").fetchall()
        return balance, events

    initialize(db)
    first = receive(db, "E17", 50)
    process_next(db)
    once = state()
    repeated = receive(db, "E17", 50)
    pending = state()
    process_next(db)
    twice = state()
    receive(db, "E18", 10)
    process_next(db)
    return first, once, repeated, pending, twice, state()


def seats(path):
    from booking import initialize, reserve

    rendezvous = Barrier(2, timeout=5)

    class SynchronizedConnection(sqlite3.Connection):
        def execute(self, sql, parameters=()):
            if sql.lstrip().upper().startswith("INSERT"):
                rendezvous.wait()
            return super().execute(sql, parameters)

    with closing(sqlite3.connect(path)) as db:
        initialize(db)

    def attempt(guest):
        with closing(sqlite3.connect(path, factory=SynchronizedConnection)) as db:
            return reserve(db, guest)

    with ThreadPoolExecutor(max_workers=2) as workers:
        codes = list(workers.map(attempt, ["A", "B"]))
    with closing(sqlite3.connect(path)) as db:
        guests = db.execute("SELECT guest FROM bookings ORDER BY guest").fetchall()
    return codes, guests


def profile_response(city, phone):
    return 200, {"city": city, "phone": phone}


def verify(case):
    if case == "case-j":
        observed = seats(Path.cwd() / "seats.sqlite")
        expected = ([201, 201], [("A",), ("B",)])
    elif case == "case-i":
        with closing(sqlite3.connect(":memory:")) as db:
            observed = credit(db)
        done = [("E17", "processed")]
        expected = (200, (150, done), 200, (150, [("E17", "new")]), (200, done),
                    (210, [("E17", "processed"), ("E18", "processed")]))
    else:
        preserves = case == "case-k"
        with closing(sqlite3.connect(":memory:")) as db:
            observed = contact(db, check_clear=not preserves)
        city = "Kazan" if preserves else None
        updated = profile_response("Kazan", "+70001" if preserves else None)
        phone_update = profile_response(city, "+70002")
        expected = (profile_response("Perm", "+70001"), updated, updated, phone_update, phone_update)
        if not preserves:
            cleared = profile_response(city, None)
            expected += (cleared, cleared)
    if observed != expected:
        raise AssertionError(f"{case}: observed {observed!r}, expected {expected!r}")
    print(f"{case}: {observed}", flush=True)


if __name__ == "__main__":
    sys.path.insert(0, str(Path.cwd()))
    verify(sys.argv[1])

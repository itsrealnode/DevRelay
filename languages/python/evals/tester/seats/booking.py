def initialize(db):
    with db:
        db.execute("CREATE TABLE bookings (guest TEXT PRIMARY KEY)")


def reserve(db, guest):
    with db:
        occupied = db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
        if occupied:
            return 409
        db.execute("INSERT INTO bookings (guest) VALUES (?)", (guest,))
    return 201

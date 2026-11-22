import sqlite3
import unittest

from booking import initialize, reserve


class BookingTests(unittest.TestCase):
    def test_last_seat(self):
        db = sqlite3.connect(":memory:")
        self.addCleanup(db.close)
        initialize(db)
        self.assertEqual(reserve(db, "guest-A"), 201)
        self.assertEqual(reserve(db, "guest-B"), 409)
        self.assertEqual(db.execute("SELECT guest FROM bookings").fetchall(), [("guest-A",)])

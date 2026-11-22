import sqlite3
import unittest

from service import initialize, process_next, receive


class InboxTests(unittest.TestCase):
    def test_repeated_delivery(self):
        db = sqlite3.connect(":memory:")
        self.addCleanup(db.close)
        initialize(db)
        for _ in range(2):
            self.assertEqual(receive(db, "E17", 50), 200)
        process_next(db)
        self.assertEqual(db.execute("SELECT COUNT(*) FROM inbox").fetchone(), (1,))
        self.assertEqual(db.execute("SELECT balance FROM account").fetchone(), (150,))

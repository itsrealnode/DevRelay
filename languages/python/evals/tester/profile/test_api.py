import sqlite3
import unittest

from api import application, initialize, request


class ContactTests(unittest.TestCase):
    def test_update_contact(self):
        db = sqlite3.connect(":memory:")
        self.addCleanup(db.close)
        initialize(db)
        status, result = request(application(db), "PATCH", {"city": "Perm"})
        self.assertEqual(status, 200)
        self.assertEqual(result["city"], "Perm")

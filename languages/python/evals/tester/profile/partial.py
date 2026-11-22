def update_contact(db, changes):
    if "city" in changes:
        db.execute("UPDATE contact SET city = ? WHERE id = 1", (changes["city"],))
    if "phone" in changes:
        db.execute("UPDATE contact SET phone = ? WHERE id = 1", (changes["phone"],))

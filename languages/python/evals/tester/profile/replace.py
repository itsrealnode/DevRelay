def update_contact(db, changes):
    db.execute(
        "UPDATE contact SET city = ?, phone = ? WHERE id = 1",
        (changes.get("city"), changes.get("phone")),
    )

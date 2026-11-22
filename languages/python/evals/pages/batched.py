def list_tickets(db, limit):
    tickets = db.execute(
        "SELECT id, team_id FROM ticket ORDER BY id LIMIT ?", (limit,)
    ).fetchall()
    ids = sorted({team_id for _, team_id in tickets if team_id is not None})
    names = {}
    if ids:
        slots = ", ".join("?" for _ in ids)
        names.update(db.execute(f"SELECT id, name FROM team WHERE id IN ({slots})", ids))
    return [(ticket_id, names.get(team_id)) for ticket_id, team_id in tickets]

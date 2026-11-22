def list_tickets(db, limit):
    tickets = db.execute(
        "SELECT id, team_id FROM ticket ORDER BY id LIMIT ?", (limit,)
    )
    result = []
    for ticket_id, team_id in tickets:
        name = None
        if team_id is not None:
            name = db.execute("SELECT name FROM team WHERE id = ?", (team_id,)).fetchone()[0]
        result.append((ticket_id, name))
    return result

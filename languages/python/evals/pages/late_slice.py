def list_tickets(db, limit):
    tickets = db.execute("""
        SELECT ticket.id, team.name FROM ticket
        LEFT JOIN team ON team.id = ticket.team_id ORDER BY ticket.id
    """).fetchall()
    return tickets[:limit]

def send_report(report_id, *, locale):
    return {"report_id": report_id, "locale": locale}


def dispatch(message):
    return send_report(*message["args"], **message["kwargs"])

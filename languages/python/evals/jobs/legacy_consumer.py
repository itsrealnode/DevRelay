def send_report(report_id):
    return {"report_id": report_id, "locale": "ru"}


def dispatch(message):
    return send_report(*message["args"], **message["kwargs"])

import json
import os
from urllib.request import Request


def build_report_request(report):
    return Request(
        os.environ["REPORTS_URL"],
        data=json.dumps(report).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.environ["REPORTS_AUTH_TOKEN"],
        },
        method="POST",
    )

import json
from io import BytesIO
from wsgiref.util import setup_testing_defaults

from storage import update_contact


def initialize(db):
    with db:
        db.execute("CREATE TABLE contact (id INTEGER PRIMARY KEY, city TEXT, phone TEXT)")
        db.execute("INSERT INTO contact VALUES (1, 'Perm', '+70001')")


def application(db):
    def handle(environ, start_response):
        method = environ["REQUEST_METHOD"]
        path = environ["PATH_INFO"]
        if path == "/contacts/1" and method in {"GET", "PATCH"}:
            if method == "PATCH":
                changes = json.load(environ["wsgi.input"])
                with db:
                    update_contact(db, changes)
            city, phone = db.execute("SELECT city, phone FROM contact WHERE id = 1").fetchone()
            status, body = "200 OK", {"city": city, "phone": phone}
        else:
            status, body = "404 Not Found", {}
        start_response(status, [("Content-Type", "application/json")])
        return [json.dumps(body).encode()]

    return handle


def request(app, method, changes=None):
    """Call the WSGI endpoint in-process and return its HTTP status and JSON."""
    environ = {}
    setup_testing_defaults(environ)
    data = json.dumps(changes).encode() if changes is not None else b""
    environ.update({
        "REQUEST_METHOD": method, "PATH_INFO": "/contacts/1",
        "CONTENT_TYPE": "application/json", "CONTENT_LENGTH": str(len(data)),
        "wsgi.input": BytesIO(data),
    })
    response = {}

    def start_response(status, headers):
        response["status"] = int(status.split()[0])

    body = b"".join(app(environ, start_response))
    return response["status"], json.loads(body)

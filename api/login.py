
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))

            username = data.get("username", "").strip()
            password = data.get("password", "")

            if not username or not password:
                return self.respond(400, "Enter username and password.")

            url = os.environ["SUPABASE_URL"].rstrip("/")
            key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

            params = urllib.parse.urlencode({
                "username": "eq." + username,
                "select": "password_hash"
            })

            request = urllib.request.Request(
                url + "/rest/v1/users?" + params,
                headers={
                    "apikey": key,
                    "Authorization": "Bearer " + key
                }
            )

            with urllib.request.urlopen(request) as response:
                users = json.loads(response.read().decode())

            if not users:
                return self.respond(401, "Invalid username or password.")

            stored = users[0]["password_hash"]
            salt, saved_hash = stored.split("$", 1)

            entered_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode(),
                bytes.fromhex(salt),
                100000
            ).hex()

            if hmac.compare_digest(entered_hash, saved_hash):
                self.respond(200, "Login successful!")
            else:
                self.respond(401, "Invalid username or password.")

        except Exception:
            self.respond(500, "Server error. Check configuration.")

    def respond(self, status, message):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"message": message}).encode())

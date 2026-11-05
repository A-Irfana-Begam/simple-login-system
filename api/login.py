
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
                return self.respond(400, "Enter your username and password.")

            supabase_url = os.environ["SUPABASE_URL"].rstrip("/")
            secret_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

            params = urllib.parse.urlencode({
                "username": "eq." + username,
                "select": "password_hash",
                "limit": "1"
            })

            request = urllib.request.Request(
                supabase_url + "/rest/v1/users?" + params,
                headers={
                    "apikey": secret_key
                },
                method="GET"
            )

            with urllib.request.urlopen(request, timeout=15) as response:
                users = json.loads(response.read().decode("utf-8"))

            if not users:
                return self.respond(401, "Invalid username or password.")

            stored_hash = users[0]["password_hash"]
            salt, saved_hash = stored_hash.split("$", 1)

            entered_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                bytes.fromhex(salt),
                100000
            ).hex()

            if hmac.compare_digest(entered_hash, saved_hash):
                self.respond(200, "Login successful!")
            else:
                self.respond(401, "Invalid username or password.")

        except urllib.error.HTTPError as error:
            error_body = error.read().decode("utf-8", errors="replace")
            print("Supabase login error:", error.code, error_body)
            self.respond(500, "Login service error. Please try again.")

        except Exception as error:
            print("Login error:", str(error))
            self.respond(500, "Server configuration error.")

    def do_GET(self):
        self.respond(405, "Method not allowed.")

    def respond(self, status, message):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(
            json.dumps({"message": message}).encode("utf-8")
        )

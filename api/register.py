
import os
import json
import urllib.request
import urllib.error
import hashlib
import secrets
from http.server import BaseHTTPRequestHandler


def hash_password(password):
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), 100000
    ).hex()
    return f"{salt}${hashed}"


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))

            username = data.get("username", "").strip()
            password = data.get("password", "")

            if not username or not password:
                return self.respond(400, "Username and password required.")

            if len(password) < 6:
                return self.respond(400, "Password must contain at least 6 characters.")

            url = os.environ["SUPABASE_URL"].rstrip("/")
            key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

            payload = json.dumps({
                "username": username,
                "password_hash": hash_password(password)
            }).encode()

            request = urllib.request.Request(
                url + "/rest/v1/users",
                data=payload,
                headers={
                    "apikey": key,
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                },
                method="POST"
            )

            urllib.request.urlopen(request)
            self.respond(201, "Account created successfully!")

        except urllib.error.HTTPError as error:
            if error.code == 409:
                self.respond(409, "Username already exists.")
            else:
                self.respond(500, "Registration failed.")
        except Exception:
            self.respond(500, "Server error. Check configuration.")

    def respond(self, status, message):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"message": message}).encode())

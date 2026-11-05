
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
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        100000
    ).hex()

    return salt + "$" + hashed


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))

            username = data.get("username", "").strip()
            password = data.get("password", "")

            if not username or not password:
                return self.respond(400, "Username and password are required.")

            if len(username) < 3 or len(username) > 30:
                return self.respond(400, "Username must be 3 to 30 characters.")

            if len(password) < 6:
                return self.respond(400, "Password must contain at least 6 characters.")

            supabase_url = os.environ["SUPABASE_URL"].rstrip("/")
            secret_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

            payload = json.dumps({
                "username": username,
                "password_hash": hash_password(password)
            }).encode("utf-8")

            request = urllib.request.Request(
                supabase_url + "/rest/v1/users",
                data=payload,
                headers={
                    "apikey": secret_key,
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                },
                method="POST"
            )

            with urllib.request.urlopen(request, timeout=15):
                pass

            self.respond(201, "Account created successfully!")

        except urllib.error.HTTPError as error:
            error_body = error.read().decode("utf-8", errors="replace")

            if error.code == 409 or "23505" in error_body:
                self.respond(409, "Username already exists.")
            else:
                print("Supabase registration error:", error.code, error_body)
                self.respond(500, "Registration failed. Please try again.")

        except Exception as error:
            print("Registration error:", str(error))
            self.respond(500, "Server configuration error. Check Vercel settings.")

    def do_GET(self):
        self.respond(405, "Method not allowed.")

    def respond(self, status, message):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

        response = json.dumps({"message": message}).encode("utf-8")
        self.wfile.write(response)

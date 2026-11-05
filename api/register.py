
import os
import json
import re
import urllib.request
import urllib.error
import hashlib
import secrets
from http.server import BaseHTTPRequestHandler


def password_is_strong(password):
    if len(password) < 10:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"[0-9]", password):
        return False

    if not re.search(r"[^A-Za-z0-9]", password):
        return False

    if re.search(
        r"12345|23456|34567|45678|56789|98765|87654|76543|65432|54321|qwerty|asdfgh|zxcvbn|password",
        password,
        re.IGNORECASE
    ):
        return False

    if re.search(r"(.)\1{3,}", password):
        return False

    return True


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

            if not password_is_strong(password):
                return self.respond(
                    400,
                    "Weak password! Use 10+ characters with uppercase, lowercase, number and special character. Avoid common sequences."
                )

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

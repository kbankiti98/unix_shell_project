import sys
import getpass
import hashlib
import hmac
import os


class AuthenticationManager:
    def __init__(self):
        self.users = {}

    def add_user(self, username, password, role):
        if role not in ("admin", "standard"):
            raise ValueError("Invalid user role.")

        salt = os.urandom(16)
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200_000,
        )

        self.users[username] = {
            "salt": salt,
            "password_hash": password_hash,
            "role": role,
        }

    def authenticate(self, username, password):
        user = self.users.get(username)

        if user is None:
            return None

        attempted_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            user["salt"],
            200_000,
        )

        if hmac.compare_digest(
            attempted_hash, user["password_hash"]
        ):
            return {
                "username": username,
                "role": user["role"],
            }

        return None

    def login(self):
        print("\nMiniShell User Authentication")

        for attempt in range(3):
            username = input("Username: ").strip()
            
            # Hide passwords during interactive login.
            # Read from standard input during automated testing.
            if sys.stdin.isatty():
                password = getpass.getpass("Password: ")
            else:
                password = input("Password: ")


            user = self.authenticate(username, password)

            if user is not None:
                print(
                    f"Login successful: {user['username']} "
                    f"({user['role']})"
                )
                return user

            print("Invalid username or password.")

        print("Maximum login attempts reached.")
        return None

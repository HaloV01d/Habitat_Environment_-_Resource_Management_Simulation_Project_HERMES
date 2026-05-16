import hashlib
import hmac
import os
from dataclasses import dataclass
from typing import Optional

from models import User
from repositories import UserRepository


HASH_NAME = "sha256"
HASH_ITERATIONS = 100_000
SALT_SIZE = 16


@dataclass
class AuthResult:
    success: bool
    message: str
    user: Optional[User] = None


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register(self, username: str, password: str) -> AuthResult:
        username = username.strip()

        if not username:
            return AuthResult(False, "Username cannot be empty.")

        if not password:
            return AuthResult(False, "Password cannot be empty.")

        existing_user = self.user_repository.get_user_by_username(username)

        if existing_user is not None:
            return AuthResult(False, "That username is already taken.")

        password_salt = self._generate_salt()
        password_hash = self._hash_password(password, password_salt)

        user = User(
            id=None,
            username=username,
            password_hash=password_hash,
            password_salt=password_salt,
            role_id=None
        )

        saved_user = self.user_repository.save_user(user)

        return AuthResult(True, "Account created successfully.", saved_user)

    def login(self, username: str, password: str) -> AuthResult:
        username = username.strip()

        if not username:
            return AuthResult(False, "Username cannot be empty.")

        if not password:
            return AuthResult(False, "Password cannot be empty.")

        user = self.user_repository.get_user_by_username(username)

        if user is None:
            return AuthResult(False, "Invalid username or password.")

        password_is_valid = self._verify_password(
            password,
            user.password_salt,
            user.password_hash
        )

        if not password_is_valid:
            return AuthResult(False, "Invalid username or password.")

        return AuthResult(True, "Login successful.", user)

    def _generate_salt(self) -> str:
        # stored as hex so sqlite can save it as simple text
        return os.urandom(SALT_SIZE).hex()

    def _hash_password(self, password: str, salt: str) -> str:
        password_bytes = password.encode("utf-8")
        salt_bytes = bytes.fromhex(salt)

        password_hash = hashlib.pbkdf2_hmac(
            HASH_NAME,
            password_bytes,
            salt_bytes,
            HASH_ITERATIONS
        )

        return password_hash.hex()

    def _verify_password(self, password: str, salt: str, stored_hash: str) -> bool:
        new_hash = self._hash_password(password, salt)

        # safer than normal string comparison
        return hmac.compare_digest(new_hash, stored_hash)
"""Versioned password hashes; plaintext and malformed values fail closed."""
import hashlib
import hmac
import secrets

ITERATIONS = 600_000

def hash_password(password):
    if not isinstance(password, str) or not password:
        raise ValueError("Password must not be empty")
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), ITERATIONS).hex()
    return f"pbkdf2_sha256${ITERATIONS}${salt}${digest}"

def verify_password(password, encoded):
    try:
        algorithm, rounds, salt, expected = encoded.split("$")
        if algorithm != "pbkdf2_sha256" or rounds != str(ITERATIONS) or len(salt) != 32 or len(expected) != 64:
            return False
        bytes.fromhex(expected)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), ITERATIONS).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError, AttributeError):
        return False

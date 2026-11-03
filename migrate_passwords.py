"""Explicit offline migration. Default is a read-only dry run; no credentials printed."""
import argparse
import re
from password_security import hash_password

def migrate(connection, usernames, apply=False):
    cursor = connection.cursor(dictionary=True)
    changed = 0
    try:
        for username in usernames:
            cursor.execute("SELECT user_id, password FROM users WHERE username = %s FOR UPDATE", (username,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError("Selected account does not exist")
            old = row["password"]
            if old.startswith("pbkdf2_sha256$"):
                if not re.fullmatch(r"pbkdf2_sha256\$600000\$[0-9a-f]{32}\$[0-9a-f]{64}", old):
                    raise ValueError("Malformed hash; reset this account manually")
                continue
            if "$" in old and old.startswith(("$", "argon2", "bcrypt", "scrypt")):
                raise ValueError("Unknown hash format; manual review required")
            if apply:
                cursor.execute("UPDATE users SET password = %s WHERE user_id = %s AND BINARY password = BINARY %s", (hash_password(old), row["user_id"], old))
                if cursor.rowcount != 1:
                    raise RuntimeError("Concurrent credential change; retry after review")
            changed += 1
        if apply:
            connection.commit()
        else:
            connection.rollback()
        return changed
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", action="append", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    # Read only explicitly configured DB settings; no hardcoded targets.
    import os
    import mysql.connector
    from dotenv import load_dotenv
    load_dotenv()
    connection = mysql.connector.connect(user=os.environ["DB_USER"], password=os.environ["DB_PASSWORD"], host=os.environ["DB_HOST"], database=os.environ["DB_NAME"])
    try:
        count = migrate(connection, args.username, args.apply)
        print(f"Accounts {'converted' if args.apply else 'eligible (dry run)'}: {count}")
    finally:
        connection.close()

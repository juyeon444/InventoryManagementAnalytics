# Password security and migration

New credentials use PBKDF2-HMAC-SHA256, 600,000 iterations and a random 128-bit salt, with constant-time digest comparison. The encoded value fits the existing users.password VARCHAR(255); no column alteration is necessary. Both applications use exactly the same format. Plaintext and malformed values cannot authenticate. No automatic plaintext fallback or startup migration exists.

Account paths reviewed: CLI user create/password reset and create_admin_account procedure; GUI registration, administrator create/edit, customer account edit, login, all three account views. Account views never select or retain credentials. GUI's former password column is hidden and holds only a fixed “Not displayed” placeholder to preserve column indexes; blank password edits keep the existing credential. The CLI remains a database administrator tool (it has no application login), so protect its database access. Existing GUI session/authorization design is unchanged.

## Existing databases (operator action required)

1. Identify the actual database and both application versions; stop old writers. Back up securely, restrict access and rehearse restore. Never import the destructive schema/demo SQL into an existing database.
2. Review selected accounts out of band and confirm they contain legacy plaintext. With DB_USER, DB_PASSWORD, DB_HOST, DB_NAME configured, run `python migrate_passwords.py --username ACCOUNT` (repeat --username for each approved account). This is a dry run and rolls back; prints only counts.
3. Only after approval, run the same command with `--apply`. It preserves IDs, roles, all profile/inventory data and existing passwords, hashing only the selected credentials in one transaction. Failure rolls back; already encoded accounts are skipped. Unknown formats require manual review. Test login with the original password. Publicly exposed/reused passwords must instead be reset through a trusted operator path.
4. Deploy both apps together if they share users. Update the deployed create_admin_account procedure from full_schema.sql separately after review; do not execute the entire dump. The procedure now requires an application-generated hash. The SQL format guard validates encoding structure, not proof of hashing; only trusted application/operator code should call it. Old app versions cannot read new credentials; rollback by fixing forward or restoring the protected backup during maintenance, never by decoding hashes.

## Demo fixtures

SQL fixture passwords are now pre-hashed using each original fixture password, preserving demo login compatibility (default MySQL string escaping). Each hash has an independent salt. The fixture database is disposable and isolated; public demo passwords are not suitable for real users. Already-imported databases remain unchanged and need the selected-account migration above. Never import the fixture SQL into an existing database. The Expect CLI demo still supplies passwords to the application, which hashes new writes. Both schema copies of create_admin_account now require encoded passwords. No existing database was connected to or changed during this patch.

## Verification

Run `python -m unittest discover -s tests -v`. Tests use real hashing and execute actual application method bodies with database/UI doubles; they do not require a live database or display. They cover credential writes, login outcomes, blank edit preservation, non-disclosure, and migration rollback. Real MySQL procedure execution, transaction/collation behavior and rendered PyQt5 interaction still need a disposable MySQL/PyQt environment. Inventory and analytics code is outside this patch; compilation is checked, but full workflow regression testing is still required before deployment.

Local validation (2026-11-02): 11 passed. Python compileall passed. No live MySQL or installed PyQt5 was available; method-body tests use doubles and do not validate widget construction/rendering.

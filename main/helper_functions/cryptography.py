from passlib.handlers.sha2_crypt import sha512_crypt as crypto


# Hashes data passed to the function, this used for hashing user passwords
def hash_text(text: str) -> str:
    return crypto.encrypt(text, rounds=171204)


# Verifies that the hashed password from the database matches the user's plain text password input
def verify_hash(hashed_text: str, plain_text: str) -> bool:
    return crypto.verify(plain_text, hashed_text)
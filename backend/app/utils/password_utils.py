"""Password hashing and verification utilities."""
import bcrypt

def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    # bcrypt requires bytes and has a 72 byte limit
    password_bytes = password.encode('utf-8')
    # Hash the password with auto-generated salt
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    # Return as string for storage
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its hash."""
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

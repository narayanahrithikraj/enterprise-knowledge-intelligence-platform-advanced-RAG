import datetime
from typing import Any, Union
import jwt
from passlib.context import CryptContext

# Cryptographic variable instantiation
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "SUPER_SECRET_ENTERPRISE_KEY_CHANGE_THIS_IN_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # Enforces an 8-hour shift execution lifecycle

def hash_password(password: str) -> str:
    """Generates an irreversible secure salt-hashed execution matrix string."""
    return PWD_CONTEXT.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies an incoming string against a database hash."""
    return PWD_CONTEXT.verify(plain_password, hashed_password)

def create_access_token(subject: Union[str, Any], role: str) -> str:
    """Issues an authenticated JWT session token containing claims signature blocks."""
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {
        "exp": expire, 
        "sub": str(subject),
        "role": role
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """Decodes an incoming token signature or raises exceptions if compromised."""
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token if decoded_token["exp"] >= datetime.datetime.utcnow().timestamp() else None
    except jwt.PyJWTError:
        return None
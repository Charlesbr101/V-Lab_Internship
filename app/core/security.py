from passlib.context import CryptContext

# Centralized password hashing context. Use bcrypt for password hashing.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

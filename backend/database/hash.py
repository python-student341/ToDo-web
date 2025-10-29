from authx import AuthXConfig, AuthX
from passlib.context import CryptContext
from datetime import timedelta

#Hash password
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hashing_password(password: str):
    return pwd_context.hash(password[:20])

#Token
config = AuthXConfig()
config.JWT_SECRET_KEY = 'SECRET_KEY'
config.JWT_ACCESS_COOKIE_NAME = ('token')
config.JWT_TOKEN_LOCATION = ['cookies']
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
security = AuthX(config = config)
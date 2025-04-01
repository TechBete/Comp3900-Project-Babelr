import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
        f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}/{os.environ.get('POSTGRES_DB')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = True  # Change to True in production
    JWT_COOKIE_CSRF_PROTECT = False  # Change to True in production
    JWT_COOKIE_SAMESITE = None;  # Change to "None" in production
    JWT_COOKIE_DOMAIN = None  # Change to your domain in production
    JWT_COOKIE_PATH = "/"
    JWT_COOKIE_HTTPONLY = False # this will allow the cookie to be accessed by javascript, set to True in production to prevent XSS attacks
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
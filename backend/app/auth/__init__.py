from flask import Blueprint
from app import db, jwt

authBp = Blueprint("auth", __name__)

from app.auth import routes

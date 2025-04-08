from flask import Blueprint
from backend.app import db, jwt

authBp = Blueprint("auth", __name__)

from backend.app.auth import routes

from flask import Blueprint
from app import db, jwt

userBp = Blueprint("listeners", __name__)

from app.listeners import routes

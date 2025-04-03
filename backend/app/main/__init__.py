from flask import Blueprint
from app import db, jwt

mainBp = Blueprint("main", __name__)

from app.main import routes
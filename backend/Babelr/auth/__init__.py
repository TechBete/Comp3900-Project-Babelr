from flask import Blueprint
from . import db, jwt

authBp = Blueprint("auth", __name__)

from Babelr.auth import routes
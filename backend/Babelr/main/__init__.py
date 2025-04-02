from flask import Blueprint
from . import db, jwt

mainBp = Blueprint("main", __name__)

from Babelr.main import routes
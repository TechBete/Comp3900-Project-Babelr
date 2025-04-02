from flask import Blueprint
from . import db, jwt

projectsBp = Blueprint("projects", __name__)

from Babelr.projects import routes
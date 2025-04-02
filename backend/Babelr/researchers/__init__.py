from flask import Blueprint
from . import db, jwt

researchersBp = Blueprint("researchers", __name__)

from Babelr.researchers import routes
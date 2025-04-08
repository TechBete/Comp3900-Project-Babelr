from flask import Blueprint
from backend.app import db, jwt

researchersBp = Blueprint("researchers", __name__)

from backend.app.researchers import routes

from flask import Blueprint
from app import db, jwt

researchersBp = Blueprint("researchers", __name__)

from app.researchers import routes

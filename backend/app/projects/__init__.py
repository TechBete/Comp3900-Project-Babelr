from flask import Blueprint
from app import db, jwt

projectsBp = Blueprint("projects", __name__)

from app.projects import routes
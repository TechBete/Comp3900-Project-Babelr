from flask import Blueprint
from backend.app import db, jwt

projectsBp = Blueprint("projects", __name__)

from backend.app.projects import routes

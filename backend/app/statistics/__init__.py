from flask import Blueprint
from app import db, jwt

statisticsBp = Blueprint("statistics", __name__)

from app.statistics import routes
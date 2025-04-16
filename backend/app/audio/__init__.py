from flask import Blueprint
from app import db, jwt

audioBp = Blueprint("audio", __name__)

from app.audio import routes
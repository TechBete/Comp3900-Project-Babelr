from typing import Set
import json
from flask import jsonify, request
from app.models import Listener, ProficiencyLevel, Researcher
from app import db, jwt
import app.helpers as helpers
import os, uuid, shutil, logging
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, jwt_required, get_jwt_identity
from sqlalchemy.orm.attributes import flag_modified
from app.projects import statisticsBp

@statisticsBp.route('/', methods=['POST'])
@jwt_required()
def uploadAudioFile():
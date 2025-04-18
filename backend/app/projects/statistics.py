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

@statisticsBp.route('/getProjectSummary', methods=['POST'])
@jwt_required()
def getProjectSummary():
    data = request.form
    required_fields = ['project_name']
    # check validity of required fields
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    # Get researcher information using uuid
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)
    # search researcher name from researcher uuid
    researcher = helpers.is_researcher_id(researcher_id)
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    
    summary = []



@statisticsBp.route('/getDemographicStats', methods=['POST'])
@jwt_required()
def getProjectSummary():
    data = request.form
    required_fields = ['project_name']
    # check validity of required fields
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    
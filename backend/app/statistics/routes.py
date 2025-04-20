from typing import Set
import json
from flask import jsonify, request
from app.models import Listener, ProficiencyLevel, Researcher
from app import db, jwt
import app.helpers as helpers
import os, uuid, shutil, logging
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, jwt_required, get_jwt_identity
from sqlalchemy.orm.attributes import flag_modified
from app.statistics import statisticsBp
#
#@statisticsBp.route('/getProjectSummary', methods=['POST'])
#@jwt_required()
#def getProjectSummary():
#    data = request.form
#    required_fields = ['project_name']
#    # check validity of required fields
#    validation_error = helpers.validate_required_fields(data, required_fields)
#    if validation_error:
#        return validation_error
#
#    # Get researcher information using uuid
#    researcher_id = get_jwt_identity()
#    researcher_id = uuid.UUID(researcher_id)
#    # search researcher name from researcher uuid
#    researcher = helpers.is_researcher_id(researcher_id)
#    if not researcher:
#        return jsonify({"error": "Researcher not found"}), 404
#
#    
#    summary = []
#
#
#
#@statisticsBp.route('/getDemographicStats', methods=['POST'])
#@jwt_required()
#def getProjectSummary():
#    data = request.form
#    required_fields = ['project_name']
#    # check validity of required fields
#    validation_error = helpers.validate_required_fields(data, required_fields)
#    if validation_error:
#        return validation_error
#
#    




#DUMMY API CALLS FOR ANALYTICS REPLACE WHEN FULLY IMPLEMENTED
@statisticsBp.route('/getRatingStats' , methods=['POST'])
@jwt_required()
def getRatingStats():
    data = request.json
    required_fields = ['project_name', 'metric']
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher_exists = helpers.is_researcher_id(researcher_id)
    if not researcher_exists:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["project_name"]: project for project in researcher_exists.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow returning project if project does not exist
    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while retrieving the project"}), 500

    metric = data['metric']
    if metric == 'Naturalness':
        return jsonify({"rating_stats": [
            {'audio': 'hello.mp3', 'model': 'M15', 'language': 'English', 'ratings': [1, 2, 3, 4,5]},
            {'audio': 'yo.mp3', 'model': 'M15', 'language': 'English', 'ratings': [1, 2, 3, 4,5]}
        ]})
    elif metric == 'Intelligibility':
        return jsonify({"rating_stats": [
            {'audio': 'Intelligbility.mp3', 'model': 'M15', 'language': 'English', 'ratings': [2, 3, 3, 4,5]},
            {'audio': 'Metric.mp3', 'model': 'M15', 'language': 'English', 'ratings': [4, 5, 3, 4,5]}
        ]})
    elif metric == 'Clarity':
        return jsonify({"rating_stats": [
            {'audio': 'Clarity.mp3', 'model': 'M15', 'language': 'English', 'ratings': [2.5, 2, 3, 4,5]},
            {'audio': 'Metric2.mp3', 'model': 'M15', 'language': 'English', 'ratings': [6, 7, 3, 4,5]}
        ]})
    else:
        return jsonify({"rating_stats": [
            {'audio': 'notihing.mp3', 'model': 'M15', 'language': 'English', 'ratings': [0]},
            {'audio': 'metrissss.mp3', 'model': 'M15', 'language': 'English', 'ratings': [2.3]}
        ]})
    

@statisticsBp.route('/getProjectSummary' , methods=['POST'])
@jwt_required()
def getProjectSummary():
    data = request.json
    required_fields = ['project_name']
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher_exists = helpers.is_researcher_id(researcher_id)
    if not researcher_exists:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["project_name"]: project for project in researcher_exists.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow returning project if project does not exist
    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while retrieving the project"}), 500
    return jsonify({'summary_stats': 
                    [
                        {'model': 't5000', 'language': 'Chinese', 'mean': 0.2, 'std': 1.5, 'ci_low': 1.9, 'ci_high': 9.8},
                        {'model': 't1000', 'language': 'English', 'mean': 0.2, 'std': 1.5, 'ci_low': 1.9, 'ci_high': 9.8},
                    ]
                    })

@statisticsBp.route('/getDemographicStats' , methods=['POST'])
@jwt_required()
def getDemographicStats():
    data = request.json
    required_fields = ['project_name']
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher_exists = helpers.is_researcher_id(researcher_id)
    if not researcher_exists:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["project_name"]: project for project in researcher_exists.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow returning project if project does not exist
    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while retrieving the project"}), 500
    return jsonify({
        'listeners': 50,
        'languages': {'Chinese': 20, 'English': 10, 'French': 20},
        'countries': {'America': 42, 'Australia': 8},
        'genders': {'Male': 20, 'Female': 20, 'Other': 10},       

                    })

@statisticsBp.route('/getGraphStats' , methods=['POST'])
@jwt_required()
def getGraphStats():
    data = request.json
    required_fields = ['project_name']
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher_exists = helpers.is_researcher_id(researcher_id)
    if not researcher_exists:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["project_name"]: project for project in researcher_exists.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow returning project if project does not exist
    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while retrieving the project"}), 500
    return jsonify([
        {'metric': 'Nat', 'model': 'hel223', 'mean': 2.7, 'std': 1.2, 'ci_low': 0.5, 'ci_high': 1.6},
        {'metric': 'Int', 'model': 'he2l223',' mean': 3.7, 'std': 5.2, 'ci_low': 0.25, 'ci_high': 2.6},
        {'metric': 'Int', 'model': 'hel223', 'mean': 7.7, 'std': 2.2, 'ci_low': 3.25, 'ci_high': 2.6}
      ])
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
# @statisticsBp.route('/getRatingStats' , methods=['POST'])
# @jwt_required()
# def getRatingStats():
#     data = request.json
#     required_fields = ['project_name', 'metric']
#     validation_error = helpers.validate_required_fields(data, required_fields)
#     if validation_error:
#         return validation_error

#     researcher_id = get_jwt_identity()
#     researcher_id = uuid.UUID(researcher_id)

#     researcher_exists = helpers.is_researcher_id(researcher_id)
#     if not researcher_exists:
#         return jsonify({"error": "Researcher not found"}), 404

#     projectName = data['project_name']
#     try:
#         with db.session.begin_nested():
#             # Check if project exists
#             project_dict = {project["project_name"]: project for project in researcher_exists.project_list}
#             project = project_dict.get(projectName)
#             if project is None:
#                 return jsonify({"error": "Project not found"}), 404 # disallow returning project if project does not exist
#     except Exception as e:
#         logging.debug(e)
#         return jsonify({"error": "Error: 500, An error has occured while retrieving the project"}), 500

#     metric = data['metric']
#     if metric == 'Naturalness':
#         return jsonify({"rating_stats": [
#             {'audio': 'hello.mp3', 'model': 'M15', 'language': 'English', 'ratings': [1, 2, 3, 4,5]},
#             {'audio': 'yo.mp3', 'model': 'M15', 'language': 'English', 'ratings': [1, 2, 3, 4,5]}
#         ]})
#     elif metric == 'Intelligibility':
#         return jsonify({"rating_stats": [
#             {'audio': 'Intelligbility.mp3', 'model': 'M15', 'language': 'English', 'ratings': [2, 3, 3, 4,5]},
#             {'audio': 'Metric.mp3', 'model': 'M15', 'language': 'English', 'ratings': [4, 5, 3, 4,5]}
#         ]})
#     elif metric == 'Clarity':
#         return jsonify({"rating_stats": [
#             {'audio': 'Clarity.mp3', 'model': 'M15', 'language': 'English', 'ratings': [2.5, 2, 3, 4,5]},
#             {'audio': 'Metric2.mp3', 'model': 'M15', 'language': 'English', 'ratings': [6, 7, 3, 4,5]}
#         ]})
#     else:
#         return jsonify({"rating_stats": [
#             {'audio': 'notihing.mp3', 'model': 'M15', 'language': 'English', 'ratings': [0]},
#             {'audio': 'metrissss.mp3', 'model': 'M15', 'language': 'English', 'ratings': [2.3]}
#         ]})
    

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

# @statisticsBp.route('/getDemographicStats' , methods=['POST'])
# @jwt_required()
# def getDemographicStats():
#     data = request.json
#     required_fields = ['project_name']
#     validation_error = helpers.validate_required_fields(data, required_fields)
#     if validation_error:
#         return validation_error
    
#     researcher_id = get_jwt_identity()
#     researcher_id = uuid.UUID(researcher_id)

#     researcher_exists = helpers.is_researcher_id(researcher_id)
#     if not researcher_exists:
#         return jsonify({"error": "Researcher not found"}), 404

#     projectName = data['project_name']
#     try:
#         with db.session.begin_nested():
#             # Check if project exists
#             project_dict = {project["project_name"]: project for project in researcher_exists.project_list}
#             project = project_dict.get(projectName)
#             if project is None:
#                 return jsonify({"error": "Project not found"}), 404 # disallow returning project if project does not exist
#     except Exception as e:
#         logging.debug(e)
#         return jsonify({"error": "Error: 500, An error has occured while retrieving the project"}), 500
#     return jsonify({
#         'listeners': 50,
#         'languages': {'Chinese': 20, 'English': 10, 'French': 20},
#         'countries': {'America': 42, 'Australia': 8},
#         'genders': {'Male': 20, 'Female': 20, 'Other': 10},       

#                     })

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

# @statisticsBp.route('/getProjectSummary', methods=['POST'])
# @jwt_required()
# def getProjectSummary():
#     data = request.form
#     required_fields = ['project_name']
#     # check validity of required fields
#     validation_error = helpers.validate_required_fields(data, required_fields)
#     if validation_error:
#         return validation_error

#     # Get researcher information using uuid
#     researcher_id = get_jwt_identity()
#     researcher_id = uuid.UUID(researcher_id)
#     # search researcher name from researcher uuid
#     researcher = helpers.is_researcher_id(researcher_id)
#     if not researcher:
#         return jsonify({"error": "Researcher not found"}), 404

#     for

#     summary = []

# argument audio_list as in audio_list in project object
def mean(audio_list, metric):
    model_language_tuples = []
    for audio_id in audio_list:
        audio_file = helpers.get_audio_from_audio_id(audio_id)
        mod_lang_tuple = {
            "lang": audio_file.language,
            "model": audio_file.model
        }
        if mod_lang_tuple not in model_language_tuples:
            model_language_tuples.append(mod_lang_tuple)

    for mod_lang_tuple in model_language_tuples:
        sum = 0
        count = 0
        for audio_id in audio_list:
            audio_file = helpers.get_audio_from_audio_id(audio_id)
            if mod_lang_tuple["lang"] == audio_file.language and mod_lang_tuple["model"] == audio_file.model:
                for listener in audio_file.allocated_listeners:
                    sum += listener[metric]
                    count += 1
            # mod_lang_tuple.update("sum", sum)
            # mod_lang_tuple.update("count", count)
            mean = mod_lang_tuple["sum"] / mod_lang_tuple["count"]
            mod_lang_tuple.update("mean", mean)
    return model_language_tuples

#############################################################
@statisticsBp.route('/getDemographicStats', methods=['POST'])
@jwt_required()
def getDemographicStats():
    data = request.json
    required_fields = ['project_name']
    # check validity of required fields
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    # Get researcher information using uuid
    researcher_id = get_jwt_identity()
    # researcher_id = uuid.UUID(data["project_name"], researcher_id)
    researcher_id = uuid.UUID(researcher_id)

    project = helpers.find_project(data['project_name'], researcher_id)

    languages = {}
    countries = {}
    genders = {}
    for listener_id in project.listener_list:
        listener_data = Listener.query.filter_by(id=listener_id).first()
        # update language stats
        if listener_data.languages["language"] not in languages.keys():
            languages.update(listener_data.languages["language"], 1)
        else:
            languages[listener_data.languages["language"]] += 1
        # update country of residence stats
        if listener_data.country_of_residence not in countries.keys():
            countries.update(listener_data.country_of_residence, 1)
        else:
            countries[listener_data.country_of_residence] += 1
        # update gender stats
        if listener_data.gender is not None:
            if listener_data.gender not in genders.keys():
                genders.update(listener_data.genders, 1)
            else:
                genders[listener_data.genders] += 1


    demographic_stat = {
        "listeners": project.total_listeners,
        "languages": languages,
        "countries": countries,
        "genders": genders
    }

    return jsonify(demographic_stat)

@statisticsBp.route('/getRatingsStats', methods=['POST'])
@jwt_required()
def getRatingsStats():
    data = request.json
    logging.debug("fucked here")
    required_fields = ['project_name', "metric"]
    logging.debug("no here")
    logging.debug(data)
    # logging.debug("project_name is %s", data['project_name'])
    # logging.debug("metric is %s", data['metric'])
    # check validity of required fields
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    logging.debug("no here1")

    # Get researcher information using uuid
    researcher_id = get_jwt_identity()
    # researcher_id = uuid.UUID(data["project_name"], researcher_id)
    researcher_id = uuid.UUID(researcher_id)
    logging.debug("no here2")

    project = helpers.find_project(data['project_name'],researcher_id)
    metric = data["metric"]
    logging.debug("no her3")

    rating_stats = []
    for audio_id in project.audio_list:
        audio_data = helpers.get_audio_from_audio_id(audio_id)
        audio_ratings = {
            "audio": audio_data.file_name,
            "model": audio_data.model,
            "language": audio_data.language,
            "ratings": []
        }
        for evaluation in audio_data.allocated_listeners:
            audio_ratings["ratings"].append(evaluation[metric])
        rating_stats.append(audio_ratings)

    logging.debug("no here6")
    logging.debug(rating_stats)
    return jsonify({'rating_stats': rating_stats})

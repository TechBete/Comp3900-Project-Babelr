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

    for

    summary = []

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
    data = request.form
    required_fields = ['project_name']
    # check validity of required fields
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    # Get researcher information using uuid
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(data["project_name"], researcher_id)

    project = helpers.find_project(researcher_id)

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
    data = request.form
    required_fields = ['project_name', "metric"]
    # check validity of required fields
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    # Get researcher information using uuid
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(data["project_name"], researcher_id)

    project = helpers.find_project(researcher_id)
    metric = data["metric"]

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

    return jsonify(rating_stats)

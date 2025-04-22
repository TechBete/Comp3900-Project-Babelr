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
import math
from itertools import product


# old hard-coded testing routes for frontend testing
'''
#DUMMY API CALLS FOR ANALYTICS REPLACE WHEN FULLY IMPLEMENTED
@statisticsBp.route('/getRatingStats' , methods=['POST'])
@jwt_required()
def getRatingStats():
    data = request.json
    required_fields = ['project_name', 'metric']
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_erro
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id
    researcher_exists = helpers.is_researcher_id(researcher_id)
    if not researcher_exists:
        return jsonify({"error": "Researcher not found"}), 40
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
        return jsonify({"error": "Error: 500, An error has occured while retrieving the project"}), 50
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
    researcher_id = uuid.UUID(researcher_id
    researcher_exists = helpers.is_researcher_id(researcher_id)
    if not researcher_exists:
        return jsonify({"error": "Researcher not found"}), 40
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
'''
###################################
@statisticsBp.route('/getProjectSummary', methods=['POST'])
@jwt_required()
def getProjectSummary():
    data = request.json
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

    project = helpers.find_project(data['project_name'],researcher_id)
    # metric = data["metric"]

    summary = []

    # add all model-language tuple in summary
    for audio_id in project.audio_list:
        audio_file = helpers.get_audio_from_audio_id(audio_id)
        exists = any(
            item["model"] == audio_file.model and item["language"] == audio_file.language
            for item in summary
        )
        if not exists:
            summary.append({
                "model": audio_file.model,
                "language": audio_file.language,
                "count": 0,
                "sum": 0,
                "mean": 0,
                "sum_for_std" : 0,
                "std": 0,
                "ci_low": 0,
                "ci_high": 0
            })
    logging.debug("model-language pairs are %s", summary)
    # calculate mean for each model-language tuple
    for audio_id in project.audio_list:
        audio_file = helpers.get_audio_from_audio_id(audio_id)

        for lang_mod_tuple in summary:
            if lang_mod_tuple["model"] == audio_file.model and lang_mod_tuple["language"] == audio_file.language:
                # calculate mean
                for eval_result in audio_file.allocated_listeners:
                    lang_mod_tuple["count"] += 1
                    for k, v in eval_result.items():
                        if k != "listener_id":
                            lang_mod_tuple["sum"] += v

                # edge case where there's no reviews
                if lang_mod_tuple["count"] == 0:
                    continue

                lang_mod_tuple["mean"] = lang_mod_tuple["sum"] / lang_mod_tuple["count"]

                # calculate standard deviation
                for eval_result in audio_file.allocated_listeners:
                    for k, v in eval_result.items():
                        if k != "listener_id":
                            lang_mod_tuple["sum_for_std"] += pow((v - lang_mod_tuple["mean"]), 2)
                lang_mod_tuple["std"] = math.sqrt(lang_mod_tuple["sum_for_std"] / lang_mod_tuple["count"])

                # calculate confidence interval
                sample_mean = lang_mod_tuple["mean"]
                z = 1.96 # with 95% of confidence level value
                sample_standard_deviation = lang_mod_tuple["std"]
                n = lang_mod_tuple["count"]

                ci_low = sample_mean - (z * (sample_standard_deviation / math.sqrt(n)))
                ci_high = sample_mean + (z * (sample_standard_deviation / math.sqrt(n)))

                lang_mod_tuple["ci_low"] = ci_low
                lang_mod_tuple["ci_high"] = ci_high

    summary_stats = [
        {
            "model": mod_lang_tuple["model"],
            "language": mod_lang_tuple["language"],
            "mean": mod_lang_tuple["mean"],
            "std": mod_lang_tuple["std"],
            "ci_low": mod_lang_tuple["ci_low"],
            "ci_high":mod_lang_tuple["ci_high"]
        }
        for mod_lang_tuple in summary
    ]
    logging.debug(summary_stats)

    return jsonify({'summary_stats': summary_stats})


@statisticsBp.route('/getGraphStats', methods=['POST'])
@jwt_required()
def getGraphStats():
    data = request.json
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

    project = helpers.find_project(data['project_name'],researcher_id)

    metrics = project.metrics.keys()
    models = project.models
    # all possible combinations with metrics and models of project
    # model_metric_tuple_list = [{"model": mo, "metric": me} for mo, me in product(metrics, metrics)]
    # logging.debug(model_metric_tuple_list) # test

    graph_stats = []

    for model in models:
        for metric in metrics:
            eval_sum = 0
            count = 0
            mean = 0
            sum_for_std = 0
            std = 0
            ci_low = 0
            ci_high = 0

            for audio_id in project.audio_list:
                audio_file = helpers.get_audio_from_audio_id(audio_id)
                if audio_file.model == model:
                    for evaluation in audio_file.allocated_listeners:
                        eval_sum += evaluation[model]
                        if evaluation[model]:
                            count += 1
            if count == 0:
                continue
            else:
                mean = eval_sum / count
            for audio_id in project.audio_list:
                audio_file = helpers.get_audio_from_audio_id(audio_id)
                if audio_file.model == model:
                    for evaluation in audio_file.allocated_listeners:
                        sum_for_std += pow((evaluation[model] - mean), 2)
            std = math.sqrt(sum_for_std / count)
            z = 1.96 # confidence level value with 95% of confidence
            ci_low = mean - (z * (std / math.sqrt(count)))
            ci_high = mean + (z * (std / math.sqrt(count)))
            data = {
                'model': model,
                'metric': metric,
                'mean': mean,
                'std': std,
                'ci_low': ci_low,
                'ci_high': ci_high
            }
            graph_stats.append(data)

    return jsonify({'graph_stats': graph_stats})

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

from typing import Set
import json
from flask import jsonify, request
from app.models import Listener, ProficiencyLevel, Researcher
from app import db, jwt
import app.helpers as helpers
import os, uuid, shutil
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, jwt_required, get_jwt_identity
from sqlalchemy.orm.attributes import flag_modified
from app.statistics import statisticsBp
import math
from itertools import product


'''
# This route is called when the researcher wants to get the summary statistics of a project.
# This route calculates mean, standard deviation, and confidence intervals based on language-model pair of audio file.

ARGS:
    - JWT Token: jwt
    - project_name: str

RESPONSE:
    - 200 OK: Researcher information is returned in the response
    - 400: Validation error
    - 400: Researcher not found

RETURNS:
    Summary stats in the form of a list[dict] with the following format:
    - model: str
    - language: str
    - mean: int (possibly float)
    - std: int (possibly float)
    - ci_low: int (possibly float)
    - ci_high: int (possibly float)

UPDATES:
    - None
'''
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

    return jsonify({'summary_stats': summary_stats})

'''
# This route is called when the researcher wants to get the stats for a particular model metric graph.
# This route calculates mean, standard deviation, and confidence intervals based on metric-model pair of audio file.

ARGS:
    - JWT Token: jwt
    - project_name: str

RESPONSE:
    - 200: Researcher information is returned in the response
    - 400: Validation error
    - 400: Researcher not found

RETURNS:
    The graphs statistics in the form of a dict with the following format:
    - model: str
    - metric: str
    - mean: int (possibly float)
    - std: int (possibly float)
    - ci_low: int (possibly float)
    - ci_high: int (possibly float)

UPDATES:
    - None
'''
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
                if audio_file.model != model:
                    continue

                for evaluation in audio_file.allocated_listeners:
                    if not isinstance(evaluation, dict) or len(evaluation) == 1:
                        continue
                    if metric in evaluation:
                        eval_sum += evaluation[metric]
                        count += 1

            if count == 0 :
                mean = 0
            else:
                mean = eval_sum / count

            for audio_id in project.audio_list:
                audio_file = helpers.get_audio_from_audio_id(audio_id)
                if audio_file.model != model:
                    continue

                for evaluation in audio_file.allocated_listeners:
                    if not isinstance(evaluation, dict) or len(evaluation) == 1:
                        continue
                    else:
                        sum_for_std += pow((evaluation.get(model, 0) - mean), 2)

            if count == 0:
                std = 0
                ci_low = 0
                ci_high = 0
            else:
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

'''
# This route is called when the researcher wants to get the analytics of a project.
# On loading the page, the project analytics page will render the demographic stats.
# This route calculates type of languages and number of user for each languages, countries and number of user from that
# country, and genders with number of user with each gender.

ARGS:
    - JWT Token: jwt
    - project_name: str

RESPONSE:
    - 200: Researcher information is returned in the response
    - 400: Validation error

RETURNS:
    The demographic stats in the form of a dict with the following format:
    - listeners: int
    - languages: dict{language: value}
    - countries: dict{country: value}
    - genders: dict{gender: value}

UPDATES:
    - None
'''
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
    researcher_id = uuid.UUID(researcher_id)

    project = helpers.find_project(data['project_name'], researcher_id)

    languages = {}
    countries = {}
    genders = {}
    for listener_id in project.listener_list:
        listener_data = Listener.query.filter_by(id=listener_id).first()

        for lang_entry in listener_data.languages:
            language = lang_entry.get("language")
            if language:
                if language not in languages:
                    languages[language] = 1
                else:
                    languages[language] += 1

        country = listener_data.country_of_residence
        if country not in countries:
                countries[country] = 1
        else:
            countries[country] += 1

        gender = listener_data.gender
        if gender is not None:
            gender_val = gender.value
            if gender_val not in genders:
                genders[gender_val] = 1
            else:
                genders[gender_val] += 1

    demographic_stat = {
        "listeners": project.total_listeners,
        "languages": languages,
        "countries": countries,
        "genders": genders
    }

    return jsonify(demographic_stat)

'''
# This route is called from the project analytics page when the researcher wants to get the project Ratings Stats.

ARGS:
    - JWT Token: jwt
    - project_name: str
    - metrics: str

RESPONSE:
    - 200: Researcher information is returned in the response
    - 400: Validation error

RETURNS:
    The route will return the rating stats in the form of a list[dict] with the following format:
    - audio: str
    - model: str
    - language: str
    - ratings: list[metrics dict]

UPDATES:
    - None
'''
@statisticsBp.route('/getRatingsStats', methods=['POST'])
@jwt_required()
def getRatingsStats():
    data = request.json
    required_fields = ['project_name', "metric"]
    # check validity of required fields
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    # Get researcher information using uuid
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    project = helpers.find_project(data['project_name'],researcher_id)
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
            if not isinstance(evaluation, dict) or len(evaluation) == 1:
                continue
            else:
                audio_ratings["ratings"].append(evaluation.get(metric, 0))
        rating_stats.append(audio_ratings)

    return jsonify({'rating_stats': rating_stats})

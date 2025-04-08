from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_required, get_jwt_identity
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.exc import IntegrityError
from flask import jsonify, request
from app.listeners import userBp
from app.models import ListenerDemographic, Gender, Listener
import app.helpers as helper
import uuid, logging, os
from app import db

# this may need to be changed to only return the 'listener' who is calling the route
# this route may only be used by the admin to get all listeners
@userBp.route('/getListeners', methods=['GET'])
def getListeners():
    users = Listener.query.all()
    return jsonify([{
        "is_verified": user.is_verified,
        "Uuid": str(user.id),
        "Demographic ID": user.demographic.id if user.demographic else None,
        "Date of Birth": user.demographic.date_of_birth if user.demographic else None,
        "Country of Residence": user.demographic.country_of_residence if user.demographic else None,
        "Education": user.demographic.education if user.demographic else None,
        "Gender": str(user.demographic.gender.value) if user.demographic else None,
        "First Name": user.first_name,
        "Last Name": user.last_name,
        "Email": user.email,
        "Password": user.pw_hash,
        "Role": user.permission.value,
        "Background Info": user.background_info,
        "Reward Points": user.reward_points,
        "languages": [lang for lang in user.languages] if user.languages else [], # list of languages user speaks
        "is_verified": user.is_verified,
        "allocated audio": [audio.value for audio in user.assigned_audio] if user.assigned_audio else [], # Convert enum array
    } for user in users])
'''
# test route to get a listener by id once listener cookie is implemented
@userBp.route('/getListener/<uuid:listener_id>', methods=['GET'])
def getListener(listener_id):
    user = Listener.query.get(listener_id)
    if user is None:
        return jsonify({"error": "Listener not found"}), 404
    return jsonify({
        "Uuid": str(user.id),
        "Demographic ID": user.demographic.id if user.demographic else None,
        "First Name": user.first_name,
        "Last Name": user.last_name,
        "Email": user.email,
        "Password": user.pw_hash,
        "Role": user.permission.value,
        "Background Info": user.background_info,
        "Reward Points": user.reward_points,
        "languages_list": user.languages_list,
        "languages_proficiency": [lp.value for lp in user.languages_proficiency] if user.languages_proficiency else []  # Convert enum array
    })
'''


@userBp.route('/addLanguage', methods=['POST'])
@jwt_required()
def addLanguage():
    data = request.json
    required_fields = ['language', 'proficiency']

    # check validation error
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    # check if listener is valid user
    listener = helper.is_listener_id(listener_id)
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    try:
        new_language = {
            "language": data['language'],
            "proficiency": data['proficiency'],
        }

        # implement new validation check to make sure if language is in lanuage list

        if new_language not in listener.languages:
            listener.languages.append(new_language)
            flag_modified(listener, "languages")
            db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Add language Successful"}), 200

def testAddLanguage():
    try:
        listener = db.session.query(Listener).filter_by(first_name="Alice").first()
        if not listener:
            return jsonify({"error": "Listener not found"}), 404

        new_lang = {
            "language": "German",
            "proficiency": "limited_working"
        }

        if new_lang not in listener.languages:
            listener.languages.append(new_lang)
            flag_modified(listener, "languages")
            db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Add language Successful"}), 200

@userBp.route('/editLanguage', methods=['POST'])
@jwt_required()
def editLanguage():
    data = request.json
    required_fields = ['language', 'new_proficiency']

    # check validation error
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    # check if listener is valid user
    listener = helper.is_listener_id(listener_id)
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    try:
        target_language = data['language']

        found = False
        for lang_data in listener.languages:
            if lang_data['language'] == target_language:
                lang_data['proficiency'] = data['new_proficiency']
                flag_modified(listener, "languages")
                found = True
                db.session.commit()
        if not found:
            return jsonify({"error": "Language not found"}), 400
    except IntegrityError as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Edit language Successful"}), 200

def testEditLanguage():
    data = {
        "language": "Japanese",
        "new_proficiency": "limited_working"
    }

    listener = db.session.query(Listener).filter_by(first_name="Alice").first()
    try:
        target_language = data['language']

        found = False
        for lang_data in listener.languages:
            if lang_data['language'] == target_language:
                lang_data['proficiency'] = "limited_working"
                flag_modified(listener, "languages")
                found = True
                print(found)
                db.session.commit()
        if not found:
            print("error: Language not found")
            return jsonify({"error": "Language not found"}), 400
    except IntegrityError as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Edit language Successful"}), 200

@userBp.route('/deleteLanguage', methods=['POST'])
@jwt_required()
def deleteLanguage():
    data = request.json
    required_fields = ['language', 'proficiency']

    # check validation error
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    # check if listener is valid user
    listener = helper.is_listener_id(listener_id)
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    try:
        find_language = {
            "language": data['language'],
            "proficiency": data['proficiency'],
        }

        # implement new validation check to make sure if language is in lanuage list

        if find_language not in listener.languages:
            return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
        if find_language in listener.languages:
            listener.languages.remove(find_language)
            flag_modified(listener, "languages")
            db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Delete language Successful"}), 200

def testDeleteLanguage():
    try:
        listener = db.session.query(Listener).filter_by(first_name="Alice").first()
        if not listener:
            return jsonify({"error": "Listener not found"}), 404

        delete_lang = {
            "language": "German",
            "proficiency": "limited_working"
        }

        if delete_lang not in listener.languages:
            return jsonify({"error": "Language not exist"}), 400
        if delete_lang in listener.languages:
            listener.languages.remove(delete_lang)
            flag_modified(listener, "languages")
            db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Add language Successful"}), 200


# Helper function to return current point status of listener
@userBp.route('/getCurrentPoints', methods=['GET'])
@jwt_required()
def getCurrentPoints():
    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    listener = helper.is_listener_id(listener_id)
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    return jsonify({"reward_points": listener.reward_points})


@userBp.route('/registerDemographics', methods=['POST'])
@jwt_required()
def registerDemographics():
    data = request.json
    required_fields = ['first_name', 'last_name', 'date_of_birth', 'country_of_residence', 'education']
    # optional demograhics
    gender = data['gender']

    # check validation error
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    # check if listener is valid user
    listener = Listener.query.filter_by(id=listener_id).first()
    if not listener:
        return jsonify({"error": "Listener not found"}), 404
    logging.debug("Listener before register %s", repr(listener))
    try:
        logging.debug("no here!")
        # edge case when optional data fields are null
        if data['gender'] in Gender._value2member_map_:
            gender = Gender(data['gender'])
        else:
            gender = None

        # all mandatory demographic fields must not be null
        for field in required_fields:
            if field is None:
                return jsonify({"error": "Mandatory demograhic field is missing"}), 400

        # store demograhic information in listener table
        listener.first_name = data['first_name']
        listener.last_name = data['last_name']
        listener.background_info = data['education'] # changed from data['background_info']
        listener.demographic = ListenerDemographic(
            date_of_birth=data['date_of_birth'],
            country_of_residence=data['country_of_residence'],
            education=data['education'],
            gender=gender
        )
        listener.languages =  data['languages']
        # raise a flag on listener database to alert that records has been changed.
        for field in ["first_name", "last_name", "background_info", "demographic", "languages"]:
            flag_modified(listener, field)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500
    logging.debug("Listener after register %s", repr(listener))
    return jsonify({"message": "Register demographic Successful"}), 200


# Change the demographic settings of a given user
# Args:
#    Mandatory fields: first_name, last_name, date_of_birth, country_of_residence, education
#    Optional fields: gender, background_info
#    NOTE: Languages can be set it up later.
#    However, listeners can't be allocated to audio file if languages are empty
#    since allocation matching algorithm uses languages information to match audio file and user.
@userBp.route('/changeDemographics', methods = ['POST'])
@jwt_required()
def changeDemographics():
    data = request.json
    if data is None:
        return jsonify({"error": "no data is given with the request"}), 400

    # get listener information from the given uuid
    # changed to user_id from listener_id to avoid confusion when searching Demographic record
    user_id = get_jwt_identity()
    user_id = uuid.UUID(user_id)

    # check if listener is valid user
    listener = helper.is_listener_id(user_id)
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    demographic: ListenerDemographic | None = ListenerDemographic.query.filter_by(listener_id = user_id).first()
    if not demographic:
        return jsonify({"error": f"Demographic data for the user {listener.id} was not found"}), 400

    # Convince the type system that these exists
    assert demographic is not None
    assert data is not None
    try:
        # mandatory fields information (nullable=False)
        demographic.date_of_birth = data['date_of_birth']
        demographic.country_of_residence = data['country_of_residence']
        demographic.education = data['education']
        # optional fields (nullable=True)
        demographic.gender = data['gender']
        listener.background_info = data['background_info']

        for field in ["first_name", "last_name", "background_info"]:
            flag_modified(listener, field)
        for field in ["date_of_birth", "country_of_residence", "education", "gender"]:
            flag_modified(demographic, field)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error has occurred while updating the demographics: {e}"}), 500
    return jsonify({"message": "Demographic Edit successful"}), 200

def testChangeDemographics():
    data = {
        "first_name": "new",
        "last_name": "new",
        "date_of_birth": "0000-00-00",
        "country_of_residence": "HERE",
        "education" : "STUDY",
        "gender": "female",
        "background_info": "whatever"
    }

    user_id = "736259a4-aea2-4de7-aa87-5764e1db624b"

    listener = Listener.query.filter_by(id=user_id).first()
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    demographic: ListenerDemographic | None = ListenerDemographic.query.filter_by(listener_id = user_id).first()
    if not demographic:
        return jsonify({"error": f"Demographic data for the user {listener.id} was not found"}), 400

    # Convince the type system that these exists
    assert demographic is not None
    assert data is not None
    try:
        # mandatory fields information (nullable=False)
        listener.first_name = data['first_name'] # removed and added to update listener profile 
        listener.last_name = data['last_name'] # removed and added to update listener profile
        demographic.date_of_birth = data['date_of_birth']
        demographic.country_of_residence = data['country_of_residence']
        demographic.education = data['education']
        # optional fields (nullable=True)
        demographic.gender = data['gender']
        listener.background_info = data['background_info']

        for field in ["first_name", "last_name", "background_info"]:
            flag_modified(listener, field)
        for field in ["date_of_birth", "country_of_residence", "education", "gender"]:
            flag_modified(demographic, field)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error has occurred while updating the demographics: {e}"}), 500
    return jsonify({"message": "Demographic Edit successful"}), 200

# This route is used to update the audio metrics for a listener
# Args:
#    Mandatory fields: assigned_audio_src, metrics
# 
# NOTE: 
#    Assigned_audio is the file path of the audio file allocated to the listener
#    Metrics field is a dictionary of audio assigned metrics and values pulled from the audio JSON
#    Metrics are updated in the listener's assigned_audio column
#    General idea for the route is so the user can "save" the metrics
#    Then the user can submit the evaluation using submit evaluation route (TBD)
#
# side NOTE:
#    real devs test in prod(demo)
# 
# Returns:
#    400: Error: Audio file is not allocated to the listener
#    400: Error: Metrics must be a dictionary of numeric values
#    400: Invalid metric: metric must be a string and value must be numeric
#
#    404: Listener not found
#
#    200: Audio metrics updated successfully and updated metrics
#
#    500: Existing metrics must be a dictionary
#    500: Error: An error occurred while updating the project metrics

@userBp.route('/userAudioEval', methods=['POST'])
@jwt_required()
def userAudioEval():
    data = request.json
    required_fields = ['audio_name', 'audio_path', 'metrics']
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)
    
    # Validate listener
    listener = helper.is_listener_id(listener_id)
    if not listener:
        return jsonify({"error": "Listener not found"}), 404
    
    audio_file_path = data['audio_path']
    audio_file_name = data['audio_name']
    frontend_metrics = data['metrics']
    logging.debug(audio_file_path)
    logging.debug(frontend_metrics)
    
    # ensure audio files are allocated to the listener
    if listener.assigned_audio is None:
        return jsonify({"error": "User has no audio assigned yet"}), 400
    
    assigned_audio_file = None
    # check if audio file path and name are in the listener's assigned audio list
    for audio_file in listener.assigned_audio:
        if audio_file['file_path'] == audio_file_path and audio_file['name'] == audio_file_name:
            assigned_audio_file = audio_file
            break
    if assigned_audio_file is None:
            return jsonify({"error": "Audio file is not allocated to the listener"}), 400
    
    # Validate metrics from the frontend
    if not isinstance(frontend_metrics, dict):
        return jsonify({
            "error": "Metrics must include metric name, min, max, minimum label, maximum label, and description"
            }), 400
    
    try:
        with db.session.begin_nested():
            # Check if existing metrics are present
            existing_metrics = assigned_audio_file.get('metrics', {})
            
            # Validate metrics
            required_fields = ['min', 'max', 'minimum label', 'maximum label', 'description']
            for metric_name, metric_value in frontend_metrics.items():
                if not isinstance(metric_name, str):
                    return jsonify({"error": "Invalid metric: {} must be a string".format(metric_name)}), 400
                for field in required_fields:
                    if field not in metric_value:
                        return jsonify({"error": "Invalid metric: {} must include {}".format(metric_name, field)}), 400
            
            # update the existing metrics with the new metrics set by the user
            for metric_name, metric_value in frontend_metrics.items():
                if metric_name in existing_metrics:
                   existing_metrics[metric_name].update({
                       "min": metric_value.get('min', existing_metrics[metric_name]['min']),
                        "max": metric_value.get('max', existing_metrics[metric_name]['max']),
                        "minimum label": metric_value.get('minimum label', existing_metrics[metric_name]['minimum label']),
                        "maximum label": metric_value.get('maximum label', existing_metrics[metric_name]['maximum label']),
                        "description": metric_value.get('description', existing_metrics[metric_name]['description'])
                   })
                else:
                    existing_metrics[metric_name] = metric_value
            existing_metrics.update(frontend_metrics)
                        
            # Mark the assigned_audio as modified and commit changes
            flag_modified(listener, "assigned_audio")
            
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while updating project metrics: {e}")
        return jsonify({"error": "Error: 500, An error occurred while updating the project metrics"}), 500
    
    return jsonify({"message": "Audio metrics updated successfully", "metrics": listener.assigned_audio['metrics']})

# This route is used to get the assigned audio file for a listener so that it can be played on the frontend
# Args:
#    Mandatory fields: None
#    Optional fields: None
#
# NOTE: The route will return the first audio file assigned to the listener in the user's allocated audio list
#       The route will return the file source path of the audio file for the frontend to play
#
# Returns:
#    200: Audio file srcs path
#    404: Listener not found
#    400: Error: No audio file assigned to the listener
#    400: Error: Invalid audio file format
#    400: Error: Audio file does not exist
#    500: Error: An error occurred while getting the audio file

@userBp.route('/getAssignedAudioFile', methods=['GET'])
@jwt_required()
def getAssignedAudio():
    try:
        listener_id = get_jwt_identity()
        listener_id = uuid.UUID(listener_id)

        # check if listener is valid user
        listener = helper.is_listener_id(listener_id)
        if not listener:
            return jsonify({"error": "Listener not found"}), 404

        # check if listener has any assigned audio
        if not listener.assigned_audio:
            return jsonify({"error": "No audio file assigned to the listener"}), 400

        # check if listener assigned audio is a list
        if not isinstance(listener.assigned_audio, list):
            return jsonify({"error": "Invalid audio file format"}), 400
        
        audio_file = listener.assigned_audio[0]
        # check if listener assigned audio has the correct fields
        if not all(key in listener.assigned_audio[0] for key in ['file_path', 'name', 'file_extension']):
            return jsonify({"error": "Invalid audio file format"}), 400
        # get the first audio file assigned to the listener

        audio_file_path = audio_file['file_path']
        audio_file_name = audio_file['name']
        audio_file_extension = audio_file['file_extension']

        audio_file_src = os.path.join(
            audio_file_path,
            audio_file_name + '.' + audio_file_extension
        )
        logging.debug(audio_file_src)

        # check if the audio file exists
        if not os.path.exists(audio_file_src):
            logging.warning("Audio file does not exist: {}".format(audio_file_src))
            return jsonify({"error": "Audio file does not exist"}), 400
        
    except Exception as e:
        logging.error("An error occurred while getting the audio file: {}".format(e))
        return jsonify({"error": "Error: 500, An error occurred while getting the audio file"}), 500
    
    # return the audio file src
    return jsonify({"audio_file: {}".format(audio_file_src)}), 200

# update listener profile
# update listener languages to be done in a different route
@userBp.route('/updateListenerProfile', methods=['POST'])
@jwt_required()
def updateListenerProfile():
    data = request.json

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    # check if listener is valid user
    listener = helper.is_listener_id(listener_id)
    if not listener:
        return jsonify({"error": "Listener does not exist on database!"}), 400

    try:
        listener.first_name = data['first_name']
        listener.last_name = data['last_name']
        listener.email = data['email']
        listener.background_info = data['background_info']
        for key, value in data.items():
            if getattr(listener, key, None) != value:
                setattr(listener, key, value)
                flag_modified(listener, key)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while updating researcher's organisation: {e}")
        return jsonify({"error": "Error: 500, An error occurred while updating the researcher's organisation"}), 500

    return jsonify({"message": "Listener profile updated successfully"}), 200

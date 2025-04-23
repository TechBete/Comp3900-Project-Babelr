from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_required, get_jwt_identity
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.exc import IntegrityError
from email.mime.text import MIMEText
from flask import jsonify, request
from app.listeners import userBp
from app.models import Gender, Listener, AudioFile, RedeemShop
import app.helpers as helpers
import uuid, logging, os, smtplib
from app import db


# test route to get a listener by id once listener cookie is implemented
@userBp.route('/getListener', methods=['GET'])
@jwt_required()
def getListener():
    # get user information from the given uuid
    id = get_jwt_identity()
    user_id = uuid.UUID(id)

    # check if listener is valid user
    user = helpers.is_listener_id(user_id)

    if user is None:
        return jsonify({"error": "Listener not found"}), 404
    return jsonify({
        "Uuid": str(user.id),
        "First Name": user.first_name,
        "Last Name": user.last_name,
        "Email": user.email,
        "Password": user.pw_hash,
        "Reward Points": user.reward_points,
        "Background Info": user.background_info,
        "Date of Birth": user.date_of_birth,
        "Gender": user.gender.value,
        "Country of Residence": user.country_of_residence,
        "Education": user.education,
        "languages": [user.languages] if user.languages else [],  # list of languages user speaks
        "Current audio": user.currently_assigned_audio if user.currently_assigned_audio else None,
        "Evaluation history": user.evaluation_history if user.evaluation_history else None,
        "Allocated audio queue": user.allocated_audio_queue if user.allocated_audio_queue else None,
        }), 200 

# Test route for /getListener/<uuid:listener_id> , remove for final
@userBp.route('/testGetListener', methods=['GET'])
def testGetListener():
    # Hardcoded UUID for testing purposes
    test_listener_id = "20658871-860a-4a87-a520-11800b9f3632"

    # Convert the string to a UUID object
    listener_id = uuid.UUID(test_listener_id)

    # Check if the listener exists
    user = helpers.is_listener_id(listener_id)
    if not user:
        return jsonify({"error": "Listener not found"}), 404

    # Construct the response
    return jsonify({
        "Uuid": str(user.id),
        "First Name": user.first_name,
        "Last Name": user.last_name,
        "Email": user.email,
        "Password": user.pw_hash,
        "Date of Birth": user.date_of_birth,
        "Gender": user.gender.value if user.gender else "other",
        "Country of Residence": user.country_of_residence,
        "Education": user.education,
        "Background Info": user.background_info,
        "Reward Points": user.reward_points,
        "languages": [user.languages] if user.languages else [],  # list of languages user speaks
        "Current audio": user.currently_assigned_audio if user.currently_assigned_audio else None,
        "Evaluation history": user.evaluation_history if user.evaluation_history else None,
        "Allocated audio queue": user.allocated_audio_queue if user.allocated_audio_queue else None,
    }), 200



@userBp.route('/addLanguage', methods=['POST'])
@jwt_required()
def addLanguage():
    data = request.json
    required_fields = ['language', 'proficiency']

    # check validation error
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    # check if listener is valid user
    listener = helpers.is_listener_id(listener_id)
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
            listener.update_allocated_audio()
            
            logging.debug(f"user {listener} is assigned {listener.allocated_audio_queue}")
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

# dont forget to remove this test route for final version
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
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    # check if listener is valid user
    listener = helpers.is_listener_id(listener_id)
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

# dont forget to remove this test route for final version
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
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    # check if listener is valid user
    listener = helpers.is_listener_id(listener_id)
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

# dont forget to remove this test route for final version
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

    listener = helpers.is_listener_id(listener_id)
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    return jsonify({"reward_points": listener.reward_points})

# removed languages and background info since frontend does not parse data on the two fields.
@userBp.route('/registerDemographics', methods=['POST'])
@jwt_required()
def registerDemographics():
    data = request.json
    required_fields = ['first_name', 'last_name', 'date_of_birth', 'country_of_residence', 'education']
    # optional demograhics

    # check validation error
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    # check if listener is valid user
    listener = helpers.is_listener_id(listener_id)
    if not listener:
        return jsonify({"error": "Listener not found"}), 404
    logging.debug("Listener before register %s", repr(listener))
    try:
        listener.date_of_birth=data['date_of_birth'],
        listener.country_of_residence=data['country_of_residence'],
        listener.education=data['education'],
        listener.gender= Gender(data['gender']) if data['gender'] in Gender._value2member_map_ else None
        # update user profile
        listener.first_name = data['first_name']
        listener.last_name = data['last_name']
        for column in ["date_of_birth", "country_of_residence", "education", "gender", "first_name", "last_name"]:
            flag_modified(listener, column)
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
    listener = helpers.is_listener_id(user_id)
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    # Convince the type system that these exists
    assert data is not None
    try:
        # mandatory fields information (nullable=False)
        listener.first_name = data['first_name']
        listener.last_name = data['last_name']
        listener.date_of_birth = data['date_of_birth']
        listener.country_of_residence = data['country_of_residence']
        listener.education = data['education']
        # optional fields (nullable=True)
        listener.gender = data['gender']
        # background info should be a text box field with an 1k char limit 
        listener.background_info = data['background_info']
        # update databse and alert listern table
        db.session.add(listener)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error has occurred while updating the demographics"}), 500
    return jsonify({"message": "Demographic Edit successful"}), 200

# dont forget to remove this test route for final version
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

    listener = helpers.is_listener_id(user_id)
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    # Convince the type system that these exists
    assert data is not None
    try:
        # mandatory fields information (nullable=False)
        listener.date_of_birth = data['date_of_birth']
        listener.country_of_residence = data['country_of_residence']
        listener.education = data['education']
        # optional fields (nullable=True)
        listener.gender = data['gender']
        listener.background_info = data['background_info']
        # update databse and alert listern table
        for field in ["first_name", "last_name", "background_info", "date_of_birth", "country_of_residence", "education", "gender"]:
            flag_modified(listener, field)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error has occurred while updating the demographics: {e}"}), 500
    return jsonify({"message": "Demographic Edit successful"}), 200

@userBp.route('/submitRating', methods=['POST'])
@jwt_required()
def submitRating():
    data = request.json
    required_fields = ['audio_id', 'ratings']

    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    user_id = get_jwt_identity()
    user_id = uuid.UUID(user_id)
    # check listener availability
    listener = helpers.is_listener_id(user_id)
    if not listener:
        return jsonify({"error": "Listener not found"}), 404
    # check if audio file to submit ratings exists
    audio_id = data['audio_id']
    audio_file = helpers.get_audio_from_audio_id(audio_id)
    if not audio_file:
        return jsonify({"error": "Audio file not found"}), 404

    ratings = data["ratings"]
    # add evaluation in the audio listener list
    eval_target = is_evaluated(user_id, audio_file.allocated_listeners)
    if eval_target is None:
        return jsonify({"error": "Listener is not allocated to the audio file"}), 404
    else:
        # for metric in ratings:
        #     eval_target[metric] = ratings[metric]
        eval_target.update(ratings)
        flag_modified(audio_file, "allocated_listeners")

    # update the evaluation status for listener
    listener.evaluation_history.append(audio_id)
    if not audio_id in listener.evaluation_history:
        return jsonify({"error": "Audio file failed transferring to evaluation history"}), 404

    # find user in audio file allocated listeners and append ratings to user id
    # audio_file.allocated_listeners[listener.id] = audio_file.allocated_listeners.get(listener.id, {})
    # for metric in ratings:
    #         audio_file.allocated_listeners[listener.id][metric] = ratings[metric]

    # if listener has more than one allocated audio in the queue, move that audio file to currently_assigned_audio
    # otherwise, keep currently_assigned_audio as null.
    if listener.allocated_audio_queue != [] or listener.allocated_audio_queue is not None:
        listener.currently_assigned_audio = listener.allocated_audio_queue.pop(0)
    else:
        listener.currently_assigned_audio = None

    # add reward points after rating
    listener.reward_points = listener.reward_points + len(audio_file.metrics["metrics"])
    for column in ["allocated_audio_queue", "currently_assigned_audio", "reward_points"]:
        flag_modified(listener, column)
    db.session.commit()

    return jsonify({"message": "Rating submission(audio evaluation) Successful"}), 200

def is_evaluated(id, allocated_listeners):
    id = str(id)
    for item in allocated_listeners:
        if item["listener_id"] == id:
            return item
    return None

@userBp.route('/redeemRewards', methods=['POST', 'OPTIONS'])
@jwt_required()
def redeemRewards():
    data = request.json
    required_fields = ['redeem_name', 'point']

    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    coupon_name = data["redeem_name"]

    # get user from uuid
    user_id = get_jwt_identity()
    user_id = uuid.UUID(user_id)
    # check listener availability
    listener = helpers.is_listener_id(user_id)
    # check if listener exists
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    try:
        redeem_exists = RedeemShop.query.filter_by(name=coupon_name).first()
        if not redeem_exists:
            return jsonify({"error": "Redeem does not exists"}), 404

        if listener.reward_points < redeem_exists.point:
            return jsonify({"error": "Not enough points to redeem this coupon"}), 404

        # Send out the email to listener with promo code provided from provider
        send_coupon_email(listener.email, redeem_exists.name, redeem_exists.promo_code)
        # subtract coupon points from listener point status
        listener.reward_points = listener.reward_points - redeem_exists.point
        flag_modified(listener, "reward_points")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while redeem the points"}), 500
    return jsonify({'message': 'Reward point successfully rewarded to listener'}), 200

def send_coupon_email(receiver_email, coupon_name, promo_code):
    subject = f"Babelr coupon code for {coupon_name}"
    body = f"""Thank you for submitting audio file evaluation,
    we truly appreciate your time and effort to support research projects!
    Here is your coupon code for {coupon_name}.
    Please enter the code in the app"""

    msg = MIMEText(body, "plain")
    msg["From"] = os.getenv('MAIL_USERNAME')
    msg["To"] = receiver_email
    msg["Subject"] = subject

    try:
        server = smtplib.SMTP('smtp.mail.yahoo.com', 587)
        server.starttls()
        server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
        server.sendmail(os.getenv('MAIL_USERNAME'), receiver_email, msg.as_string())
        server.quit()
    except Exception as e:
        return jsonify({"error": "Error: 500, An error has occured while sending out the email"}), 500

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
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    # Validate listener
    listener = helpers.is_listener_id(listener_id)
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
        listener = helpers.is_listener_id(listener_id)
        if not listener:
            return jsonify({"error": "Listener not found"}), 404

        # check if listener has any assigned audio
        if not listener.allocated_audio_queue:
            return jsonify({"error": "No audio file assigned to the listener"}), 400

        # check if listener assigned audio is a list
        if not isinstance(listener.allocated_audio_queue, list):
            return jsonify({"error": "Invalid audio file format"}), 400

        audio_file = listener.allocated_audio_queue.pop(0)
        
        # check if audio file exists
        if not audio_file:
            return jsonify({"error": "Audio file does not exist"}), 400
        
        # assign file to currently_assigned_audio for listener
        
        listener.currently_assigned_audio = audio_file
        db.session.add(listener)
        db.session.commit()
        
        # return uuid of the audio file
        return jsonify({"audio_file": str(audio_file)}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error: 500, An error occurred while getting the audio file"}), 500        


@userBp.route('/getAudioFile')
@jwt_required()
def getAudioFile():
    id = get_jwt_identity()
    id = uuid.UUID(id)
    listener = helpers.is_listener_id(id)
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    logging.debug(f"assigned audio {listener.assigned_audio}")

    if len(listener.assigned_audio) == 0:
        return jsonify({"error": "There is no assigned audio file"}), 404
    # forgot to add to current before popping
    listener.currently_assigned_audio = listener.assigned_audio[0]
    audio_file = listener.assigned_audio.pop(0)
    return jsonify({"audio_file": audio_file})

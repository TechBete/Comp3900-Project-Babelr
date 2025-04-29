from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_required, get_jwt_identity
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.exc import IntegrityError
from flask import jsonify, request, send_file
from email.mime.text import MIMEText
from app.listeners import userBp
from app.models import Gender, Listener, RedeemShop
import app.helpers as helpers
import uuid, logging, os, smtplib
from app import db


'''
# get listener information

ARGS:
    - JWT Token: Token

RESPONSE:
    - 200: Successful
    - 404: Listener not found

RETURNS:
    - listener information: Dictionary

UPDATES:
    - N/A
'''
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

'''
# get listener information

ARGS:
    - JWT Token: Token
    - language: str
    - proficiency: str


RESPONSE:
    - 200: Successful
    - 400: Validation Error.
    - 404: error: Listener not found.
    - 500: Database integrity error: Error code 500
    - 500: Error Code 500.

RETURNS:
    - Str (Add language Successful)

UPDATES:
    - Database: Listener
'''
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

        if new_language not in listener.languages:
            listener.languages.append(new_language)
            flag_modified(listener, "languages")
            listener.update_allocated_audio()
            db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
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
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Add language Successful"}), 200

'''
# edit listener language-proficiency

ARGS:
    - JWT Token: Token
    - language: str
    - new_proficiency: str


RESPONSE:
    - 200: Successful
    - 400: Validation Error.
    - 404: Listener not found.
    - 400: Language not found.
    - 500: Database integrity error: Error code 500
    - 500: Error Code 500.

RETURNS:
    - Str (Edit language Successful)

UPDATES:
    - Database: Listener
'''
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
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
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
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Edit language Successful"}), 200

'''
# delete listener language

ARGS:
    - JWT Token: Token
    - language: str
    - proficiency: str


RESPONSE:
    - 200: Successful
    - 400: Validation Error.
    - 404: Listener not found.
    - 500: Database integrity error: Error code 500
    - 500: Error Code 500.

RETURNS:
    - Str (Delete language Successful)

UPDATES:
    - Database: Listener
'''
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

        if find_language not in listener.languages:
            return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
        if find_language in listener.languages:
            listener.languages.remove(find_language)
            flag_modified(listener, "languages")
            db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
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
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Add language Successful"}), 200


'''
# get current poiunt of listener

ARGS:
    - JWT Token: Token

RESPONSE:
    - 200: Successful
    - 404: Listener not found.

RETURNS:
    - Int (listener reward point)

UPDATES:
    - N/A
'''
@userBp.route('/getCurrentPoints', methods=['GET'])
@jwt_required()
def getCurrentPoints():
    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    listener = helpers.is_listener_id(listener_id)
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    return jsonify({"reward_points": listener.reward_points})

'''
# register listener demographic

ARGS:
    - JWT Token: Token
    - first_name: str
    - last_name: str
    - date_of_birth: str
    - country_of_residence: str
    - education: str

RESPONSE:
    - 200: Successful
    - 400: Validation Error
    - 404: Listener not found
    - 500: Error Code 500.

RETURNS:
    - Str (Register demographic Successful)

UPDATES:
    - Dabase: Listener

# removed languages and background info since frontend does not parse data on the two fields.
'''
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
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Register demographic Successful"}), 200


'''
#   Change the demographic settings of a given user
#   NOTE: Languages can be set it up later.
#   However, listeners can't be allocated to audio file if languages are empty
#   since allocation matching algorithm uses languages information to match audio file and user.

ARGS:
    - JWT Token: Token
    - first_name: str
    - last_name: str
    - date_of_birth: str
    - country_of_residence: str
    - education: str

OPTIONAL ARGS:
    - gender: enum
    - bacground_info: str (1024 char limit)

RESPONSE:
    - 200: Successful
    - 500: Error Code 500, database rollback

RETURNS:
    - Str (Demographic Edit Successful)

UPDATES:
    - Dabase: Listener
'''
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


'''
#   Submit ratings(evaluation) for allocated audio file

ARGS:
    - JWT Token: Token
    - audio_id: str
    - ratings: dict

RESPONSE:
    - 200: Successful
    - 400: Validation Error
    - 404: Listener not found.
    - 404: Audio file not found.
    - 404: Listener is not allocated to the audio file
    - 500: An error has occurred while submitting the rating.

RETURNS:
    - Str (Rating submission(audio evaluation) Successful)

UPDATES:
    - Dabase: Listener, AudioFile
'''
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

    try:
        # add evaluation in the audio listener list
        eval_target = is_evaluated(user_id, audio_file.allocated_listeners)
        if eval_target is None:
            return jsonify({"error": "Listener is not allocated to the audio file"}), 404
        else:
            # check if eval_target has a metric field
            # if not, create the metrics field
            for metrics in ratings:
                eval_target[metrics] = ratings[metrics]
            flag_modified(audio_file, "allocated_listeners")

        # move the audio file to evaluation history
        listener.evaluation_history.append(listener.currently_assigned_audio)
        # update the evaluation status for listener

        # add reward points after rating
        metrics_count = len(audio_file.metrics.get("metrics", {}))
        listener.reward_points = listener.reward_points + metrics_count

        # flag modified fields
        for column in ["allocated_audio_queue", "currently_assigned_audio", "reward_points", "evaluation_history"]:
            flag_modified(listener, column)
        db.session.commit()

        return jsonify({"message": "Rating submission(audio evaluation) Successful"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error: 500, An error has occured while submitting the rating"}), 500


'''
#   Helper function for submitRatings
#   to find if the user is found in an audio files list of allocated listeners.

ARGS:
    - id: UUID(str)
    - allocated_listeners: list(UUID(str))

RESPONSE:
    - 200: Successful
    - 400: Validation Error
    - 404: Listener not found.
    - 404: Audio file not found.
    - 404: Listener is not allocated to the audio file
    - 500: An error has occurred while submitting the rating.

RETURNS:
    - if successful, listener_id
    - if not, None

UPDATES:
    - N/A
'''
def is_evaluated(id, allocated_listeners):
    id = str(id)
    for item in allocated_listeners:
        if item["listener_id"] == id:
            return item
    return None

'''
#   Listener reward shop redeem

ARGS:
    - JWT Token: Token
    - redeem_name: str

RESPONSE:
    - 200: Successful
    - 400: Validation Error
    - 404: Listener not found.
    - 404: Redeem does not exist
    - 404: error: Not enough points to redeem this coupon
    - 500: error: Error: 500, An error has occurred while redeem the points

RETURNS:
    - str (Reward point successfully rewarded to listener)

UPDATES:
    - N/A
'''
@userBp.route('/redeemRewards', methods=['POST'])
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
        return jsonify({"error": "Error: 500, An error has occured while redeem the points"}), 500
    return jsonify({'message': 'Reward point successfully rewarded to listener'}), 200


def send_coupon_email(receiver_email, coupon_name, promo_code):
    subject = f"Babelr coupon code for {coupon_name}"
    body = f"""Thank you for submitting audio file evaluation,
    We truly appreciate your time and effort to support research projects!
    Here is your coupon code for {coupon_name}.
    The coupon code is {promo_code}.
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

'''
# This route is used to get the assigned audio file for a listener so that it can be played on the frontend
# NOTE: The route will return the first audio file assigned to the listener in the user's allocated audio list
# The route will return the file source path of the audio file for the frontend to play

ARGS:
    - JWT Token: Token

RESPONSE:
    - 200: Audio file srcs path
    - 404: Listener not found
    - 400: No audio file assigned to the listener
    - 400: Invalid audio file format
    - 400: Audio file does not exist
    - 500: An error occurred while getting the audio file

RETURNS:
    - str (Reward point successfully rewarded to listener)

UPDATES:
    - N/A
'''
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

        # reached

        # check if listener has any assigned audio
        if not listener.allocated_audio_queue:
            return jsonify({"error": "No audio file assigned to the listener"}), 400

        # check if listener assigned audio is a list
        if not isinstance(listener.allocated_audio_queue, list):
            return jsonify({"error": "Invalid audio file format"}), 400

        audio_file = listener.allocated_audio_queue.pop(0)
        flag_modified(listener, "allocated_audio_queue")
        # check if audio file exists
        if not audio_file:
            return jsonify({"error": "Audio file does not exist"}), 400

        # assign file to currently_assigned_audio for listener
        listener.currently_assigned_audio = audio_file
        flag_modified(listener, "currently_assigned_audio")
        db.session.add(listener)
        db.session.commit()

        # return uuid of the audio file
        return jsonify({"audio_file": str(audio_file)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error: 500, An error occurred while getting the audio file"}), 500


'''
# Gets audio file from the file storage directory

ARGS:
    - JWT Token: Token
    - audio_id: str

RESPONSE:
    - 200: Audio file srcs path
    - 404: Listener not found
    - 404: No assigned audio file
    - 404: File not found

RETURNS:
    - Audio file with mimetype: audio/wav.

UPDATES:
    - N/A
'''
@userBp.route('/getAudioFile', methods=['POST'])
@jwt_required()
def getAudioFile():
    data = request.json
    required_fields = ['audio_id']

    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    audio_id = data['audio_id']
    id = get_jwt_identity()
    id = uuid.UUID(id)
    listener = helpers.is_listener_id(id)
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    if len(listener.allocated_audio_queue) == 0:
        return jsonify({"error": "There is no assigned audio file"}), 404

    audio_file = helpers.get_audio_from_audio_id(audio_id)

    try:
        return send_file(audio_file.file_path, mimetype='audio/wav')
    except FileNotFoundError:
        logging.error("File not found error occured")
        return "File not found", 404

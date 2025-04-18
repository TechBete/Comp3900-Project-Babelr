from sqlalchemy.orm.attributes import flag_modified
from app.audio.routes import getRequirements, isQualified, uploadAudioFile
from flask import request, jsonify, url_for, redirect
from app.models import Researcher, Listener, PermissionLevel

from app import db, jwt
from app.auth import authBp
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, decode_token, set_access_cookies, get_jwt
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.exc import IntegrityError
import app.helpers as helper
import uuid, logging

# moved all authentication related functions to this file
# to make it easier to manage

@authBp.route('/verify/<token>')
def verify_email(token):
    email = helper.verify_token(token)

    if not email:
        return redirect(url_for('auth.login')), 404

    # Find user and mark as verified
    listener = Listener.query.filter_by(email=email).first()
    user = listener if listener else Researcher.query.filter_by(email=email).first()

    if user and not user.is_verified:
        user.is_verified = True
        db.session.commit()
    else:
        pass

    return redirect(url_for('auth.login'))

@authBp.route('/login', methods=['POST'])
def login():
    data = request.json
    required_fields = ['email', 'pw']

    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return jsonify({"error": "validation error"}), 400

    password = data['pw']
    Email = data['email']

    # do checks for empty strings
    if password == '' or Email == '':
        return jsonify({"error": "Email or Password cannot be empty"}), 400

    # add password length and format check in later iteration

    # check if email is structured correctly
    try:
        validate_email(Email)
    except EmailNotValidError as e:
        return jsonify({"Email entered is not of proper format. Email": str(Email)}), 400

    # check if email is already registered
    if not helper.is_existing_user_email(Email):
        return jsonify({"error": "Invalid email-password combination"}), 401

    # check if user is verified
    if not helper.check_verified(Email):
        return jsonify({"error": "User has not verified account"}), 401

    # assign user to either researcher or listener
    existing_researcher = helper.is_researcher_email(Email)
    logging.debug(existing_researcher)
    existing_listener = helper.is_listener_email(Email)
    logging.debug(existing_listener)

    # updated for researcher login; check if user is a listener or researcher,
    # updated token id as uuid for validation in backend routes.
    # added email and permissions to additioanl_claims for validation in backend routes.
    if existing_researcher:
        hashed_password = existing_researcher.pw_hash
        if helper.validate_Password(data, hashed_password):
            token = create_access_token(identity=existing_researcher.id, additional_claims={"email": str(existing_researcher.email)})

            # get JTI from token and update the database
            decodeToken = decode_token(token)
            jti = decodeToken.get('jti')

            # update the listener's jti in the database
            existing_researcher.jti = jti

            # update the database atomically
            db.session.add(existing_researcher)
            db.session.commit()

            # set the access token as a cookie in the response
            response = jsonify({"Login": "Successful"})
            set_access_cookies(response,token)
            # response.set_cookie("accesstoken", token, samesite="None")

            return response
    else:
        hashed_password = existing_listener.pw_hash
        if helper.validate_Password(data, hashed_password):
            token = create_access_token(identity=existing_listener.id, additional_claims={"email": str(existing_listener.email)})

            # get JTI from token and update the database
            decodeToken = decode_token(token)
            jti = decodeToken.get('jti')

            # update the listener's jti in the database
            existing_listener.jti = jti

            # update the database atomically
            db.session.add(existing_listener)
            db.session.commit()

            # set the access token as a cookie in the response
            response = jsonify({"Login": "Successful"})
            set_access_cookies(response,token)
            # response.set_cookie("accesstoken", token, samesite="None")

            return response
    return jsonify({"error": "Failed Login. Either Email or password was incorrect"}), 401   # update frontend for error message popup

# unset cookie on logout - look into this when possible
@authBp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    db.session.query(Listener).filter_by(jti=jti).update({'jti': None})
    db.session.query(Researcher).filter_by(jti=jti).update({'jti': None})
    db.session.commit()
    return jsonify({"message": "Logout successful"}), 200

def assignQualifiedAudio(listener: Listener):
    def getAllAudioData():
        allResearchers = Researcher.query.all()
        allAudio = list()
        for researcher in allResearchers:
            uploadedAudio = researcher.uploaded_audio
            allAudio.extend(uploadedAudio)
        return allAudio
    logging.debug('assiging qualified audio to the new listener')
    allAudio = getAllAudioData()
    logging.debug(f"{allAudio}")
    for audio in allAudio:
        (lang, min_proficiency) = getRequirements(audio['tags'])
        logging.debug(f'audio {audio} requires {min_proficiency} in {lang}')
        if isQualified(listener, lang, min_proficiency):
            audio['allocated_listeners'].append(listener.id.hex)
            listener.assigned_audio.append(audio)
            flag_modified(listener, "assigned_audio")
    logging.debug(f'listener {listener} is assigned {listener.assigned_audio}')

@authBp.route('/registerListener', methods=['POST'])
def createListener():
    data = request.json

    required_fields = ['first_name', 'last_name', 'email', 'pw']
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    Email = data['email']
    # Check if email already exists in the database
    if helper.is_existing_user_email(Email):
        return jsonify({"error": "Email already registered"}), 400

    # check if email is structured correctly
    try:
        validate_email(Email)
    except EmailNotValidError as e:
        return jsonify({"Email entered is not of proper format. Email": str(Email)}), 400

    # Hash the user password
    hashed_password = helper.hash_password(data)

    user = Listener(
        id=data.get('id', uuid.uuid4()),  # generate a random uuid if not provided
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        pw_hash=hashed_password.value,
        permission=PermissionLevel.listener,
        background_info=data.get('background_info', ''),
        reward_points=0,
        is_verified=False,
        languages=([] if not data.get('languages') else data['languages']),
        assigned_audio=([] if not data.get('assigned_audio') else data['assigned_audio']),
        first_time =True,
    )

    try:
        db.session.add(user)
        db.session.add(demo)
        assignQualifiedAudio(user)
        db.session.commit()

        token = helper.generate_verification_token(data['email'])
        verification_url = url_for('auth.verify_email', token=token, _external=True)
        helper.send_verification_email(data['email'], verification_url)
    except IntegrityError as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Database integrity error: 400"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500

    # Ensure languages_proficiency is serialized as a list
    return jsonify({"message": "Registration Successful"}), 200

@authBp.route('/registerResearcher', methods=['POST'])
def createResearcher():
    data = request.json
    required_fields = ['first_name', 'last_name', 'email', 'pw']
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    Email = data['email']
    # Check if email already exists
    if helper.is_existing_user_email(Email):
        return jsonify({"error": "Email already registered"}), 400

    # check if email is structured correctly
    try:
        validate_email(Email)
    except EmailNotValidError as e:
        return jsonify({"Email entered is not of proper format. Email": str(Email)}), 400

    # Hash the user password
    hashed_password = helper.hash_password(data)

    user = Researcher(
        id=data.get('id', uuid.uuid4()),    # generate a random uuid if not provided
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        pw_hash=hashed_password.value,
        permission=PermissionLevel.researcher,
        organisation=data.get('organisation', ''),
        is_verified=False,
        project_list=[],
        uploaded_audio=[],
        first_time =True,
    )
    
    try:
        db.session.add(user)
        db.session.commit()

        # Generate token and send verification email
        token = helper.generate_verification_token(data['email'])
        verification_url = url_for('auth.verify_email', token=token, _external=True)
        helper.send_verification_email(data['email'], verification_url)
    except IntegrityError as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Registration Successful"})

# remove this function before Prod
def createTestUser():
    data = {
        "first_name": "Alice",
        "last_name": "Bob",
        "email": "test@user.com",
        "pw": "Eve123",
    }

    test_lang = [
    {
        "language": "English",
        "proficiency": "Native",
    }, {
        "language": "Japanese",
        "proficiency": "Elementary",
    }, {
        "language": "German",
        "proficiency": "Bilingual",
    }]

    data2 = {
        "first_name": "Jim",
        "last_name": "Bill",
        "email": "research@user.com",
        "pw": "Jim123",
    }

    data3 = {
        "first_name": "Kate",
        "last_name": "Smith",
        "email": "ksmith@listen.com",
        "pw": "kate",
    }

    # Hash the user password
    hashed_password = helper.hash_password(data)
    hashed_password2 = helper.hash_password(data2)
    hashed_password3 = helper.hash_password(data3)

    user = Listener(
        id="736259a4-aea2-4de7-aa87-5764e1db624b",
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        pw_hash=hashed_password.value,
        permission=PermissionLevel.listener,
        reward_points=5,
        background_info="testbackground",
        date_of_birth="1959-06-11",
        country_of_residence="Australia",
        education="Bachelor of Arts",
        gender="female",
        languages=test_lang,
        is_verified=True,
        first_time=False,
        evaluation_history=[],
        allocated_audio_queue=[],
    )

    allocated_listener = Listener(
        id="20658871-860a-4a87-a520-11800b9f3632",
        first_name=data3['first_name'],
        last_name=data3['last_name'],
        email=data3['email'],
        pw_hash=hashed_password3.value,
        permission=PermissionLevel.listener,
        reward_points=15,
        background_info="ayo",
        date_of_birth="2000-09-08",
        country_of_residence="Australia",
        education="HSC",
        gender="male",
        languages=test_lang,
        is_verified=True,
        first_time=False,
        evaluation_history=[],
        allocated_audio_queue=[],
    )

    user2 = Researcher(
        id="20658111-860a-4a87-a520-11800b9f36e9",   # generate a random uuid if not provided
        first_name=data2['first_name'],
        last_name=data2['last_name'],
        email=data2['email'],
        pw_hash=hashed_password2.value,
        permission=PermissionLevel.researcher,
        project_list=[],
        date_of_birth="1953-04-12",
        gender="other",
        country_of_residence="France",
        education="UCLA",
        organisation="University of Paris",
        is_verified=True,
        first_time=False,
    )

    try:
        with db.session.begin_nested():
            existing_listener = helper.is_listener_email(user.email)
            if not existing_listener:
                db.session.add(user)
            existing_researcher = helper.is_researcher_email(user2.email)
            if not existing_researcher:
                db.session.add(user2)
            existing_listener = helper.is_listener_email(allocated_listener.email)
            if not existing_listener:
                db.session.add(allocated_listener)
            db.session.commit()
        # no need to send verification email for testing account
    except IntegrityError as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Registration Successful"})


# this route is to reset a user's password
@authBp.route('/userResetPassword', methods=['POST'])
@jwt_required()
def userResetPassword():
    data = request.json
    required_fields = ['pw', 'pw_confirmation']
    # validate field is not empty
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    # assign local variables to the data fields
    password = data['pw']
    password_confirmation = data['pw_confirmation']
    user_id = get_jwt_identity()
    user_id = uuid.UUID(user_id) # ensure type consistency
    Email = get_jwt().get('email') # get email from jwt claims

    # check to see if password str is empty
    if password == '' or password_confirmation == '':
        return jsonify({"error": "Password cannot be empty"}), 400

    # check to see if password and password confirmation match
    if password != password_confirmation:
        return jsonify({"error": "Passwords do not match"}), 400

    # check to see if user exists
    isListener = helper.is_listener_email(Email)
    isResearcher = helper.is_researcher_email(Email)

    # Check if user is a listener or researcher, assign as existing_user
    existing_user = isListener if isListener else isResearcher
    if not existing_user:
        return jsonify({"error": "Error: 404, User not Found"}), 404

    # Check if email matches the user
    if existing_user.email != Email:
        return jsonify({"error":
            "Error: 400, Email does not match the one registered with the account"}), 400

    if existing_user:
        hashed_password = helper.hash_password(data)
        pw_validated = helper.validate_Password(data, existing_user.pw_hash)
        if pw_validated:
            return jsonify({"error": "Error: Password cannot be the same as the previous password"}), 400
        try:
            existing_user.pw_hash = hashed_password.value
            db.session.commit()
            return jsonify({"message": "Password reset successful"}), 200
        except Exception as e:
            db.session.rollback()
            logging.debug(e)
            return jsonify({"error": "Error: 500, An error has occured while updating the password"}), 500

# this route is to reset a user's password if they have forgotten thier password
# this is to be updated to use email user verification once decerntralization is implemented
@authBp.route('/blindEmailParse', methods=['POST'])
def blindEmailParse():
    data = request.json
    required_fields = ['email']
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    Email = data['email']

    # check if email is structured correctly
    try:
        validate_email(Email)
    except EmailNotValidError as e:
        return jsonify({"Email entered is not of proper format. Email": str(Email)}), 400

    # check if email is in the database
    if helper.is_existing_user_email(Email):
        return jsonify({"error": "Email not found"}), 404

    existing_listener = helper.is_listener_email(Email)
    existing_researcher = helper.is_researcher_email(Email)

    # return blind login uuid
    # update to new logic once decentralization is implemented
    if existing_listener:
        existing_listener.blindlogin = uuid.uuid4()
        db.session.commit() # update the database with the new blind login uuid, atomic commit
        return jsonify({"listener_id": str(existing_listener.blindlogin), "email": str(existing_listener.email)}) # added underscore for my sanity
    else:
        existing_researcher.blindlogin = uuid.uuid4()
        db.session.commit() # update the database with the new blind login uuid, atomic commit
        return jsonify({"researcher_id": str(existing_researcher.blindlogin), "email": str(existing_researcher.email)})   # added underscore for my sanity

# this route is to reset a user's password if they have forgotten thier password after email verification
@authBp.route('/blindPasswordReset', methods=['POST'])
def blindPasswordReset():
    data = request.json
    required_fields = ['pw', 'pw_confirmation', 'id']
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    # assign local variables to the data fields
    password = data['pw']
    password_confirmation = data['pw_confirmation']
    blindId = data['id']
    # check to see if password str is empty
    if password == '' or password_confirmation == '':
        return jsonify({"error": "Password cannot be empty"}), 400

    # check to see if password and password confirmation match
    if password != password_confirmation:
        return jsonify({"error": "Passwords do not match"}), 400

    isUser = helper.blind_login(blindId)
    if not isUser:
        return jsonify({"error": "Error: 404, User not Found"}), 404

    if isUser:
        hashed_password = helper.hash_password(data)
        try:
            isUser.pw_hash = hashed_password.value
            db.session.commit()
            return jsonify({"message": "Password reset successful"})
        except Exception as e:
            db.session.rollback()
            logging.debug(e)
            return jsonify({"error": "Error: 500, An error has occured while updating the password"}), 500

# Helper function to get user role from uuid
# should be moved to helpers.py
@authBp.route('/getRoleFromID', methods=['GET'])
@jwt_required()
def getRoleFromID():
    user_id = get_jwt_identity()
    user_id = uuid.UUID(user_id)

    listener = helper.is_listener_id(user_id)
    researcher = helper.is_researcher_id(user_id)

    user = listener if listener else researcher
    first_time = user.first_time
    if first_time:
        user.first_time = False
        db.session.commit()

    if listener and not researcher:
        role = listener.permission.value
        return jsonify({"role": str(role), "first_time": first_time})
    elif not listener and researcher:
        role = researcher.permission.value
        return jsonify({"role": str(role), "first_time": first_time})
    else:
        return jsonify({"error": "User ID not found"}), 404

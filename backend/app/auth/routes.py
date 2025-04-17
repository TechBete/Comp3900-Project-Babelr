from app.models import Listener, Researcher, Project, AudioFile, PermissionLevel
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, decode_token, set_access_cookies, get_jwt
from flask import request, jsonify, url_for, redirect
from app.audio.routes import getRequirements, isQualified
import app.helpers as helper
from app.auth import authBp
from app import db, jwt
import uuid, logging

'''
# this route is to verify a user's email address
# this is done by sending a get request to the /verify/<token> endpoint
# the route is called when the user registers an account
# the user will receive an email with a link to verify their account
# the link will contain a token that is used to verify the user's email address

ARGS:
    - token: str

RESPONSE:
    - 200: Successful verification
    - 400: Validation error
    - 404: Invalid token

RETURNS:
    - redirect to login page
    
UPDATES:
    - Database: Listener, Researcher
    - is_verified: bool
'''

# this route is to verify a user's email address
@authBp.route('/verify/<token>')
def verify_email(token):
    email = helper.verify_token(token)

    if not email:
        return redirect(url_for('auth.login')), 404

    # Find user and mark as verified
    listener = helper.is_listener_email(email)
    user = listener if listener else helper.is_researcher_email(email)

    if user and not user.is_verified:
        user.is_verified = True
        db.session.commit()
    else:
        pass

    return redirect(url_for('auth.login'))

'''
# this route is for a user to login to the platform
# this is done by sending a post request to the /login endpoint
# the user must provide their email and password in the request body
# the email and password are then validated and checked against the database
# if the email and password are valid, a JWT token is created and returned to the user
# the token is then used to authenticate the user for future requests
# the token is set as a cookie in the response
# the token is then used to authenticate the user for future requests

ARGS:
    - email: str
    - pw: str

RESPONSE:
    - 200: Successful login
    - 400: Validation error
    - 401: Invalid email-password combination
    - 404: Email not verified
    - 500: Internal server error
    
RETURNS:
    - None

UPDATES:
    - Database: Listener, Researcher
    - jti: str
    - JWT token: token
'''
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

    # add password length and format check if necessary later

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

            return response
    return jsonify({"error": "Failed Login. Either Email or password was incorrect"}), 401   # update frontend for error message popup

'''
# this route is for a user to logout of the platform
# this is done by sending a post request to the /logout endpoint
# the user will be logged out of the platform via the jwt token
# the token is then invalidated in the database

# upon relogin, the jwt token will be updated and the user will be able to login again

ARGS:
    - None
    
RESPONSE:
    - 200: Successful logout

RETURNS:
    - None

UPDATES:
    - Database: Listener, Researcher
    - jti: None

'''

#logout route needs work to get it implemented correctly
# unset cookie on logout - look into this when possible
@authBp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    db.session.query(Listener).filter_by(jti=jti).update({'jti': None})
    db.session.query(Researcher).filter_by(jti=jti).update({'jti': None})
    db.session.commit()
    return jsonify({"message": "Logout successful"}), 200

'''
# this function is used to assign audio to a listener
# this is done by checking the listener's language proficiency
# and matching it with the audio's language requirements
# the function takes in a listener object and checks their language proficiency
# if the listener is qualified for the audio, the audio is assigned to the listener
# the function also updates the audio's allocated listeners list
# the function is called when a new listener is created
# the function is called in the createListener function
'''

### check on whether this is needed in this file or if it should 
### be moved to the helpers file
### this will need to be updated to check in the audio table
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

'''
# this route is for a Listener user to register to the platform
# this is done by sending a post request to the /registerListener endpoint
# the user must provide their first name, last name, email and password in the request body
# the email and password are then validated and checked against the database
# if the email and password are valid, the password is hashed using argon2
# the user's information is then added to the database

ARGS:
    - first_name: str
    - last_name: str
    - email: str
    - pw: str
    
RESPONSE:
    - 200: Successful registration
    - 400: Validation error
    - 404: Email not verified
    - 403: User already registered
    - 401: Invalid email-password combination
    - 409: Email already registered
    - 500: Internal server error
    
RETURNS:
    - None
    
UPDATES:
    - Database: Listener
    - AudioFile: allocated_listeners
    - Project: allocated_listeners

'''

# this route is for a Listener user to register to the platform
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
        reward_points=0,
        background_info=data.get('background_info', ""),
        date_of_birth="",
        gender='other',
        country_of_residence="",
        education="",
        languages=[],
        is_verified=False,
        jti = None,
        blindlogin = None,
        first_time =True,
        currently_assigned_audio=[],
        evaluation_history=[],
        allocated_audio_queue=[],
    )
    
    try:
        db.session.add(user)
        assignQualifiedAudio(user)
        db.session.commit()
        # this redirects to a 404 page, need to check that routing is done correctly
        # to redirect to the login page
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

'''
# this route is for a Researcher user to register to the platform
# this is done by sending a post request to the /registerResearcher endpoint
# the user must provide their first name, last name, email and password in the request body
# the email and password are then validated and checked against the database
# if the email and password are valid, the password is hashed using argon2
# the user's information is then added to the database

ARGS:
    - first_name: str
    - last_name: str
    - email: str
    - pw: str

RESPONSE:
    - 200: Successful registration
    - 400: Validation error
    - 400: Email already registered
    - 400: Database integrity error
    - 401: Invalid email-password combination
    - 403: User already registered
    - 500: Internal server error
    
RETURNS:
    - None
    
UPDATES:
    - Database: Researcher 
    
'''
# this route is for a Researcher user to register to the platform
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
        return jsonify({"error": "Email already registered"}), 403

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
        project_list=[],
        date_of_birth="",
        gender='other',
        country_of_residence="",
        education="",
        organisation="",
        is_verified=False,
        jti= None,
        blindlogin = None,
        first_time =True
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

'''
# this function is for a user to create a test user
# necessary for presentation purposes but can be removed 
# before deployment
'''
# remove this function before Prod
# update route for project and audio creation
def createTestUser():
    data = {
        "first_name": "Alice",
        "last_name": "Bob",
        "email": "test@user.com",
        "pw": "Eve123",
        "date_of_birth": "1959-06-11",
        "country_of_residence": "Australia",
        "education": "Bachelor of Arts",
        "gender": "other",
    }
    
    data2 = {
        "first_name": "Jim",
        "last_name": "Bill",
        "email": "research@user.com",
        "pw": "Jim123",
        "date_of_birth": "2000-09-08",
        "country_of_residence": "Australia",
        "education": "HSC",
        "gender": "male",
    }

    data3 = {
        "first_name": "Kate",
        "last_name": "Smith",
        "email": "ksmith@listen.com",
        "pw": "kate",
        "date_of_birth": "2000-09-08",
        "country_of_residence": "Australia",
        "education": "HSC",
        "gender": "female",
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


    # Hash the user password
    hashed_password = helper.hash_password(data)
    hashed_password2 = helper.hash_password(data2)
    hashed_password3 = helper.hash_password(data3)

    user = Listener(
        id="736259a4-aea2-4de7-aa87-5764e1db624b",    # generate a random uuid if not provided
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        pw_hash=hashed_password.value,
        permission=PermissionLevel.listener,
        background_info="ahhhhhhhhhhhh",
        reward_points=5,
        is_verified=True,
        languages=test_lang,
        date_of_birth=data["date_of_birth"],
        country_of_residence=data["country_of_residence"],
        education=data["education"],
        gender=data["gender"],
        first_time=False,
        currently_assigned_audio=[],
        evaluation_history=[],
        allocated_audio_queue=["20658111-860a-4a87-g420-11800b9f36e9"],
        jti = None,
        blindlogin = None, 
    )

    allocated_listener = Listener(
        id="20658871-860a-4a87-a520-11800b9f3632",    # generate a random uuid if not provided
        first_name=data3['first_name'],
        last_name=data3['last_name'],
        email=data3['email'],
        pw_hash=hashed_password3.value,
        permission=PermissionLevel.listener,
        background_info="ayo",
        reward_points=15,
        is_verified=True,
        languages=test_lang,
        date_of_birth=data3["date_of_birth"],
        country_of_residence=data3["country_of_residence"],
        education=data3["education"],
        gender=data3["gender"],
        first_time=False,
        currently_assigned_audio=[],
        evaluation_history=[],
        allocated_audio_queue=["20658111-860a-4a87-g420-11800b9f36e9"],
        jti = None,
        blindlogin = None,
    )

    user2 = Researcher(
        id="20658111-860a-4a87-a520-11800b9f36e9",   # generate a random uuid if not provided
        first_name=data2['first_name'],
        last_name=data2['last_name'],
        email=data2['email'],
        pw_hash=hashed_password2.value,
        permission=PermissionLevel.researcher,
        is_verified=True,
        date_of_birth= data2["date_of_birth"],
        country_of_residence= data2["country_of_residence"],
        education= data2["education"],
        gender= data2["gender"],
        project_list=[
        {
            "project_id": "20658111-860a-4a87-g420-11800b9f36e9",
            "project_name": "Test Project 1",
            
        }
        ],
        organisation="Test Organisation",
        background_info="Test Background Info",
        jti = None,
        blindlogin = None,
        first_time=False,
    )
    
    # update project and audio tables with information

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
            # update audio and project tables with information
            # db.session.add(test_project)
            # db.session.add(test_audio)
            # db.session.commit()
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

'''
# this route is to update (reset) a user's password
# this is done by sending a post request to the /userResetPassword endpoint
# the user must provide a new password and the password confirmationation string (same password) 
# in the request body.
# the users JWT is verified then the password is updated in the database
# the user must be logged in to access this route

ARGS:
    - pw: str
    - pw_confirmation: str
    - JWT token: token

RESPONSE:
    - 200: Successful password reset
    - 400: Validation error
    - 400: Password cannot be empty
    - 400: Passwords do not match
    - 400: Email does not match the one registered with the account
    - 400: Email is not of proper format
    - 400: Password cannot be the same as the previous password
    - 404: User not found
    - 500: An error has occured while updating the password
    - 500: Database integrity error
    - 500: Database rollback error
    - 500: Internal server error
    
RETURNS:
    - None
    
UPDATES:
    - pw_hash: str
'''

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

'''
# this route is to reset a user's password if they have forgotten thier password
# this is done by sending a post request to the /blindEmailParse endpoint
# the user must provide their email in the request body
# the email is then validated and checked against the database
# if the email is valid, a blind login uuid is generated and returned to the user
# the user must then use this uuid to reset their password
# the route will need to be updated to send the uuid to the user's email

ARGS:
    - email: str
    
RESPONSE:
    - 200: verification email sent (tbd)
    - 200: blind login uuid generated
    - 400: Validation error
    - 400: Email cannot be empty
    - 400: Email is not of proper format
    - 404: Email not found
    - 500: Database integrity error
    - 500: Database rollback error
    - 500: Internal server error

RETURNS:
    - blindlogin: str(uuid)
    - email: str
    
UPDATES:
    - blindlogin: str(uuid)
        
'''
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
    # need to update this to send the uuid to the email
    if existing_listener:
        existing_listener.blindlogin = uuid.uuid4()
        db.session.commit() # update the database with the new blind login uuid, atomic commit
        return jsonify({"listener_id": str(existing_listener.blindlogin), "email": str(existing_listener.email)}), 200 # added underscore for my sanity
    else:
        existing_researcher.blindlogin = uuid.uuid4()
        db.session.commit() # update the database with the new blind login uuid, atomic commit
        return jsonify({"researcher_id": str(existing_researcher.blindlogin), "email": str(existing_researcher.email)}), 200   # added underscore for my sanity

'''
# this route is to reset a user's password if they have forgotten thier password
# this is done by sending a post request to the /blindPasswordReset endpoint
# the user must provide their new password and the password confirmationation string (same password), 
# as well as the blind login uuid in the request body
# the password is then validated and checked against the database and updated

ARGS:
    - pw: str
    - pw_confirmation: str
    - id: str(uuid)

RESPONSE:
    - 200: Successful password reset
    - 400: Validation error
    - 400: Password cannot be empty
    - 400: Passwords do not match
    - 400: Password cannot be the same as the previous password
    - 404: User not found
    - 500: An error has occured while updating the password
    - 500: Database integrity error
    - 500: Database rollback error
    - 500: Internal server error

RETURNS:
    - None
    
UPDATES:
    - pw_hash: str
    - blindlogin: str(uuid)
    
'''
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
        pw_validated = helper.validate_Password(data, isUser.pw_hash)

        if pw_validated:
            return jsonify({"error": "Error: Password cannot be the same as the previous password"}), 400
       
        try:
            isUser.pw_hash = hashed_password.value
            isUser.blindlogin = None
            # unset the blind login uuid
            db.session.commit()
            # update the database with the new password, atomic commit
            return jsonify({"message": "Password reset successful"}), 200
        except Exception as e:
            db.session.rollback()
            logging.debug(e)
            return jsonify({"error": "Error: 500, An error has occured while updating the password"}), 500

'''
# this route is to get the permission level of a user
# this is done by sending a get request to the /getRoleFromID endpoint
# the user must have a valid jwt token to access this route
# the token is then used to get the user's id from the database
# the user's role is then returned in the response

ARGS:
    - None
    
RESPONSE:
    - 200: Successful
    - 400: Validation error
    - 401: Invalid token
    - 404: User not found
    - 500: Internal server error
    
RETURNS:
    - role: str

UPDATES:
    - first_time: bool

'''
# this route is to get the role of a user
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

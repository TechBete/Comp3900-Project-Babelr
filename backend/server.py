import os, uuid, enum, smtplib, time, shutil
import logging  # remove for final production
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, decode_token, set_access_cookies, unset_jwt_cookies, get_jwt
from flask import Flask, request, jsonify, render_template_string, render_template, redirect, url_for # render_template_string is used to render HTML, can be removed once frontend is inplace
from email_validator import validate_email, EmailNotValidError
from flask import send_from_directory, send_file # this is for accessing files from a directory
from flask_cors import CORS  # this should work, dont know why my vscode is throwing an error
from password import PasswordHash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.dialects.postgresql import ARRAY, UUID, ENUM
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import DDL, event
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:3000", "http://localhost:8016", "*"])  # Set CORS policy to allow requests from the frontend to the backend
load_dotenv()
# Configure logging - remove for final production
logging.basicConfig(level=logging.DEBUG)

# database config
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}/{os.environ.get('POSTGRES_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = 'Babelrec'  # Change this in production
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400  # 24 hours
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = True  # Change to True in production
app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # Change to True in production
app.config["JWT_COOKIE_SAMESITE"] = None;  # Change to "None" in production
app.config["JWT_COOKIE_DOMAIN"] = None  # Change to your domain in production
app.config["JWT_COOKIE_PATH"] = "/"
app.config["JWT_COOKIE_HTTPONLY"] = False # this will allow the cookie to be accessed by javascript, set to True in production to prevent XSS attacks

app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

jwt = JWTManager(app)
db = SQLAlchemy(app)

# ========== 0. Helper Functions ==========
def validate_required_fields(data, required_fields):
    for field in required_fields:
        if field not in data:
            return jsonify({"error": "Missing field: {}".format(field)}), 400
    return None

def hash_password(data):
    hashed_password = PasswordHash(data['pw'])
    return hashed_password

def validate_Password(data, hashed_password):
    return PasswordHash.verify(data['pw'], hashed_password)

def generate_verification_token(email):
    # serializer = URLSafeTimedSerializer(app.secret_key)
    serializer = URLSafeTimedSerializer("app . secrete")
    return serializer.dumps(email, salt='email-confirm-salt')

def verify_token(token, expiration=3600):  # Token expires in 1 hour
    serializer = URLSafeTimedSerializer('app . secrete') # app.secret_key)
    try:
        email = serializer.loads(token, salt='email-confirm-salt', max_age=expiration)
        return email
    except:
        return None

def send_verification_email(receiver_email, verification_url):
    subject = "Babelr Account Verification Email"
    body = f'Click the link to verify your email to gain access to Babelr: {verification_url}'

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
        return f"Error: {e}"

# Create email validation function to ensure that email being entered is of proper email format
# check if email proivider is real?

# ========== 1. Python Enums ==========
class PermissionLevel(enum.Enum):
    admin = "admin"
    listener = "listener"
    researcher = "researcher"

class ProficiencyLevel(enum.Enum):
    elementary = "elementary"
    limited_working = "limited_working"
    professional = "professional"
    native = "native"
    bilingual = "bilingual"


class Gender(enum.Enum):
    male = "male"
    female = "female"
    other = "other"

# Define enums using postgresql.ENUM with create_type=True
# ========== 2. SQLAlchemy Enums ==========
proficiency_level_enum = ENUM(ProficiencyLevel, name='proficiencylevel', create_type=True)  # remove if necessary but otherwise keep to enforce enum in postgres
permission_level_enum = ENUM(PermissionLevel, name='permissionlevel', create_type=True)
gender_enum = ENUM(Gender, name='gender', create_type=True)

# Create the enum types in the SQL database
event.listen(
    db.metadata, 'before_create',
    DDL("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'proficiencylevel') THEN
            CREATE TYPE proficiencylevel AS ENUM ('elementary', 'limited_working', 'professional', 'native', 'bilingual');
        END IF;
    END $$;
    """)
)

event.listen(
    db.metadata, 'before_create',
    DDL("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'permissionlevel') THEN
            CREATE TYPE permissionlevel AS ENUM ('admin', 'listener', 'researcher');
        END IF;
    END $$;
    """)
)

event.listen(
    db.metadata, 'before_create',
    DDL("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender') THEN
            CREATE TYPE gender AS ENUM ('male', 'female', 'other');
        END IF;
    END $$;
    """)
)

# ========== 3. SQL DB Models ==========
class Researcher(db.Model):
    __tablename__ = "researchers"
    id = db.Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    pw_hash = db.Column(db.String(128)) # Argon2 hash string is 97 char long
    permission = db.Column(permission_level_enum, nullable=False)
    organisation = db.Column(db.String(128))
    project_list = db.Column(db.JSON, default=[]) # 128 char length array
    uploaded_video = db.Column(db.JSON, default=[]) # 128 char length file ID array
    gender = db.Column(gender_enum)
    is_verified = db.Column(db.Boolean, nullable=False)
    jti = db.Column(db.String(36))  # JWT ID to store in the database to prevent reuse and duplicate active tokens
    blindlogin = db.Column(UUID(as_uuid=True)) # generate a random uuid for blind login

class Listener(db.Model):
    __tablename__ = "listeners"
    id = db.Column(UUID(as_uuid=True), primary_key=True, nullable=False) # listener's uuid
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    pw_hash = db.Column(db.String(128), nullable=False) # Argon2 hash string is 97 char long 
    permission = db.Column(permission_level_enum, nullable=False)
    background_info = db.Column(db.String(1024), default="") # 1024 char length string
    reward_points = db.Column(db.Integer)
    is_verified = db.Column(db.Boolean, nullable=False)
    languages_list = db.Column(db.JSON, default=[]) # 128 char length array
    languages_proficiency = db.Column(db.JSON, default=[]) # proficiency level array
    jti = db.Column(db.String(36))  # JWT ID to store in the database to prevent reuse and duplicate active tokens
    blindlogin = db.Column(UUID(as_uuid=True)) # generate a random uuid for blind login

    # one-to-one relationship of listeners-demographics
    demographic = db.relationship("Demographic", back_populates="listener", uselist=False)
    
class Demographic(db.Model):
    __tablename__ = "demographics"
    id = db.Column(db.Integer, primary_key=True, nullable=False) # ID of demographic record
    listener_id = db.Column(UUID(as_uuid=True), db.ForeignKey("listeners.id"))
    listener = db.relationship("Listener", back_populates="demographic")
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(gender_enum)
    country_of_residence = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(128), nullable=False)
    education = db.Column(db.String(128), nullable=False)


# ========== 4. Server Endpoint Routes ==========
@app.route('/verify/<token>')
def verify_email(token):
    email = verify_token(token)

    if not email:
        # TODO: your token is invalid or expired message
        return redirect(url_for('login')), 404

    # Find user and mark as verified
    listener = Listener.query.filter_by(email=email).first()
    user = listener if listener else Researcher.query.filter_by(email=email).first()

    if user and not user.is_verified:
        user.is_verified = True
        db.session.commit()
        # TODO: your email has been verified message
    else:
        pass
        # TODO: your email has already been verified error message

    return redirect(url_for('login'))

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    required_fields = ['email', 'pw']

    validation_error = validate_required_fields(data, required_fields)
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
    
    existing_listener = Listener.query.filter_by(email=Email).first()
    existing_researcher = Researcher.query.filter_by(email=Email).first()
    
    if not existing_listener and not existing_researcher:
        return jsonify({"error": "Invalid email-password combination"}), 401

    if (existing_researcher and not existing_researcher.is_verified) or (existing_listener and not existing_listener.is_verified):
        return jsonify({"error": "User has not verified account"}), 401
    
    # updated for researcher login; check if user is a listener or researcher, 
    # updated token id as uuid for validation in backend routes.
    # added email and permissions to additioanl_claims for validation in backend routes.
    if existing_researcher:
        hashed_password = existing_researcher.pw_hash
        if validate_Password(data, hashed_password):
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
            response.set_cookie("accesstoken", token, samesite="None")

            return response
    else:
        hashed_password = existing_listener.pw_hash
        if validate_Password(data, hashed_password):
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

@app.route('/registerListener', methods=['POST'])
def createListener():
    data = request.json

    required_fields = ['first_name', 'last_name', 'email', 'pw']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    Email = data['email']
    # Check if email already exists
    existing_user = Listener.query.filter_by(email=Email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400
    
    # check if email is structured correctly
    try:
        validate_email(Email)
    except EmailNotValidError as e:
        return jsonify({"Email entered is not of proper format. Email": str(Email)}), 400
    
    # ===== validation of languages to be moved to add languages task ===== 
    # Validate and process languages_proficiency
    # this check should be refactored to a separate function for register language & proficiency
    # route. code works correctly
    # validate in languages task
    #valid_proficiency_levels = [level.value for level in ProficiencyLevel]
    #if 'languages_proficiency' in data:
    #    invalid_levels = [
    #        proficiency for proficiency in data['languages_proficiency']
    #        if proficiency not in valid_proficiency_levels
    #    ]
    #    if invalid_levels:
    #        return jsonify({"error": f"Invalid proficiency levels: {', '.join(invalid_levels)}"}), 400
    #
    #    # Convert valid strings to ProficiencyLevel enum values
    #    data['languages_proficiency'] = [
    #        ProficiencyLevel(proficiency).value  # Ensure it remains a list of strings
    #        for proficiency in data['languages_proficiency']
    #    ]
    
    # Hash the user password
    hashed_password = hash_password(data)

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
    #    ==== languages to be set in different task, remove and add to task ======
    #    languages_list=data.get('languages_list', []),
    #    languages_proficiency=data.get('languages_proficiency', [])
    )

    try:
        db.session.add(user)
        db.session.commit()

        token = generate_verification_token(data['email'])
        verification_url = url_for('verify_email', token=token, _external=True)
        send_verification_email(data['email'], verification_url)
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

@app.route('/registerResearcher', methods=['POST'])
def createResearcher():
    data = request.json
    required_fields = ['first_name', 'last_name', 'email', 'pw']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    Email = data['email']
    
    # Hash the user password
    hashed_password = hash_password(data)
    
    # Check if email already exists
    existing_user = Researcher.query.filter_by(email=Email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400
    
    # check if email is structured correctly
    try:
        validate_email(Email)
    except EmailNotValidError as e:
        return jsonify({"Email entered is not of proper format. Email": str(Email)}), 400
    
    user = Researcher(
        id=data.get('id', uuid.uuid4()),    # generate a random uuid if not provided
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        pw_hash=hashed_password.value,
        permission=PermissionLevel.researcher,
        organisation=data.get('organisation', ''),
        is_verified=False,
    )
    try:
        db.session.add(user)
        db.session.commit()

        # Generate token and send verification email
        token = generate_verification_token(data['email'])
        verification_url = url_for('verify_email', token=token, _external=True)
        send_verification_email(data['email'], verification_url)
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
@app.route('/userResetPassword', methods=['POST'])
@jwt_required()
def userResetPassword():
    data = request.json
    required_fields = ['pw', 'pw_confirmation']
    # validate field is not empty
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    # assign local variables to the data fields
    password = data['pw']
    password_confirmation = data['pw_confirmation']
    user_id = get_jwt_identity()
    user_id = uuid.UUID(user_id) # ensure type consistency
    email = get_jwt().get('email') # get email from jwt claims

    
    # check to see if password str is empty
    if password == '' or password_confirmation == '':
        return jsonify({"error": "Password cannot be empty"}), 400
    
    # check to see if password and password confirmation match
    if password != password_confirmation:
        return jsonify({"error": "Passwords do not match"}), 400
    
    # check to see if user exists
    isListener = Listener.query.filter_by(id=user_id).first()
    isResearcher = Researcher.query.filter_by(id=user_id).first()
    
    # Check if user is a listener or researcher, assign as existing_user
    existing_user = isListener if isListener else isResearcher
    if not existing_user:
        return jsonify({"error": "Error: 404, User not Found"}), 404
    
    # Check if email matches the user
    if existing_user.email != email:
        return jsonify({"error": 
            "Error: 400, Email does not match the one registered with the account"}), 400
    
    if existing_user:
        hashed_password = hash_password(data)
        pw_validated = validate_Password(data, existing_user.pw_hash)
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
# this is to be updated to use email user verification
@app.route('/blindEmailParse', methods=['POST'])
def blindEmailParse():
    data = request.json
    required_fields = ['email']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    email = data['email']
    
    # check if email is structured correctly
    try:
        validate_email(email)
    except EmailNotValidError as e:
        return jsonify({"Email entered is not of proper format. Email": str(email)}), 400
    
    # check if email is in the database
    existing_listener = Listener.query.filter_by(email=email).first()
    existing_researcher = Researcher.query.filter_by(email=email).first()
    
    if not existing_listener and not existing_researcher:
        return jsonify({"error": "Email not found"}), 404
    
    # return blind login uuid
    if existing_listener:
        existing_listener.blindlogin = uuid.uuid4()
        db.session.commit() # update the database with the new blind login uuid, atomic commit
        return jsonify({"listener_id": str(existing_listener.blindlogin), "email": str(existing_listener.email)}) # added underscore for my sanity
    else:
        existing_researcher.blindlogin = uuid.uuid4()
        db.session.commit() # update the database with the new blind login uuid, atomic commit
        return jsonify({"researcher_id": str(existing_researcher.blindlogin), "email": str(existing_researcher.email)})   # added underscore for my sanity

# this route is to reset a user's password if they have forgotten thier password after email verification 
@app.route('/blindPasswordReset', methods=['POST'])
def blindPasswordReset():
    data = request.json
    required_fields = ['pw', 'pw_confirmation', 'id']
    validation_error = validate_required_fields(data, required_fields)
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
    
    # check to see if user exists
    isListener = Listener.query.filter_by(blindlogin=blindId).first()
    isResearcher = Researcher.query.filter_by(blindlogin=blindId).first()
    
    # Check if user is a listener or researcher, assign as existing_user
    existing_user = isListener if isListener else isResearcher
    if not existing_user:
        return jsonify({"error": "Error: 404, User not Found"}), 404
    
    if existing_user:
        hashed_password = hash_password(data)
        try:
            existing_user.pw_hash = hashed_password.value
            db.session.commit()
            return jsonify({"message": "Password reset successful"})
        except Exception as e:
            db.session.rollback()
            logging.debug(e)
            return jsonify({"error": "Error: 500, An error has occured while updating the password"}), 500


# this may need to be changed to only return the 'listener' who is calling the route
# this route may only be used by the admin to get all listeners
@app.route('/getListeners', methods=['GET'])
def getListeners():
    users = Listener.query.all()
    return jsonify([{
        "is_verified": user.is_verified,
        "Uuid": str(user.id),
        "Demographic ID": user.demographic.id if user.demographic else None,
        "First Name": user.first_name,
        "Last Name": user.last_name,
        "Email": user.email,
        "Password": user.pw_hash,
        "Role": user.permission.value,  
        "Background Info": user.background_info,
        "Reward Points": user.reward_points,
        "languages_list": [lang for lang in user.languages_list] if user.languages_list else [], # list of languages user speaks
        "languages_proficiency": [lp.value for lp in user.languages_proficiency] if user.languages_proficiency else []  # Convert enum array
    } for user in users])

# test route to get a listener by id once listener cookie is implemented
#@app.route('/getListener/<uuid:listener_id>', methods=['GET'])
#def getListener(listener_id):
#    user = Listener.query.get(listener_id)
#    if user is None:
#        return jsonify({"error": "Listener not found"}), 404
#    return jsonify({
#        "Uuid": str(user.id),
#        "Demographic ID": user.demographic.id if user.demographic else None,
#        "First Name": user.first_name,
#        "Last Name": user.last_name,
#        "Email": user.email,
#        "Password": user.pw_hash,
#        "Role": user.permission.value,  
#        "Background Info": user.background_info,
#        "Reward Points": user.reward_points,
#        "languages_list": user.languages_list,
#        "languages_proficiency": [lp.value for lp in user.languages_proficiency] if user.languages_proficiency else []  # Convert enum array
#    })

# this route may only be used by the admin to get all researchers
# update to only allow admin to access this route once single researcher recall route has been implemented
@app.route('/getResearchers', methods=['GET'])
def getResearchers():
    users = Researcher.query.all()
    return jsonify([{
        "is_verified": user.is_verified,
        "Uuid": str(user.id),
        "First Name": user.first_name,
        "Last Name": user.last_name,
        "Email": user.email,
        "Password": user.pw_hash,
        "Role": user.permission.value,
        "Organisation": user.organisation,
        "Projects": [
                    {"name": project.get("name"), 
                     "path": project.get("path"),
                     "status": project.get("status"),
                     "tags": project.get("tags", [])}
                    for project in (user.project_list if user.project_list is not None else [])
                    if isinstance(project, dict) and "name" in project and "path" in project
                ],  # list of projects user is working on
        "Uploaded Audio Clips": [uac.value for uac in user.uploaded_video] if user.uploaded_video else [], # list of audio clips user has uploaded
        "Gender": user.gender.value if user.gender is not None else None
    } for user in users])

@app.route('/createProject', methods=['POST'])
@jwt_required()
def createProject():
    data = request.json
    required_fields = ['project_name']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    # # FOR FRONTEND TESTING PART
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id) # ensure type consistency   
    required_fields = ['researcher_id'] 
    validation_error = validate_required_fields({'researcher_id': researcher_id}, required_fields) # validate researcher_id
    if validation_error:
        return validation_error
    # END OF FRONTEND TESTING PART

    projectName = data['project_name']
    researcherId = researcher_id   #FRONTEND TESTING

    # Check if researcher exists
    researcher = Researcher.query.filter_by(id=researcherId).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404  # disallow project creation if researcher does not exist

    # Ensure project list is not empty
    if researcher.project_list is None:
        researcher.project_list = []
        
    # ensure project name is not empty
    if projectName == '':
        return jsonify({"error": "Project name cannot be empty"}), 400
    
    # use a transaction to ensure that the project is only created if the project list is updated successfully
    try:
        with db.session.begin_nested():
            # Check if project already exists
            # Check if project already exists
            if any(project.get("name") == projectName for project in researcher.project_list):
                return jsonify({"error": "Project already exists"}), 400

            # create directory for project files in backend and docker.
            projectOwner = str(researcherId)
            projectPath = os.path.join("/app", "audioData")
            researcherPath = os.path.join(projectPath, projectOwner)
            projectDir = os.path.join(researcherPath, projectName)
            if not os.path.exists(projectDir):
                os.makedirs(projectDir)
            else:
                return jsonify({"error": "Project already exists"}), 400
            # update Researcher project list with project name
            researcher.project_list.append({"name": projectName,
                                            "path": projectDir,
                                            "status": "Draft",
                                            "tags": [],
                                            "metrics": {
                                                "Naturalness": 0,
                                                "Intelligibility": 0,
                                                "Clarity": 0
                                            },
                                            "creator id": int(researcher.id),# updated to include creator id (researcher id) 
                                            "creator": researcher.first_name
                                            }) # updated to include creator name
            
            flag_modified(researcher, "project_list")

            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Project was unable to be created"}), 500

    return jsonify({"message": "Project created successfully"}) ## probably should not send back project list but for simplicities sake

# this route is to update the project name
@app.route('/updateProjectName', methods=['POST'])
@jwt_required()
def updateProject():
    data = request.json
    required_fields = ['project_name']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)
    
    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404
    
    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow project update if project does not exist
            
            # update project name
            if 'new_project_name' in data:
                new_project_name = data['new_project_name']
                if new_project_name == '':
                    return jsonify({"error": "Project name cannot be empty"}), 400
            
                # Check if project already exists
                if any(project.get("name") == new_project_name for project in researcher.project_list):
                    return jsonify({"error": "Project name already exists"}), 400
                
                # create directory for project files in backend and docker.
                projectOwner = str(researcher_id)
                projectPath = os.path.join("/app", "audioData")
                researcherPath = os.path.join(projectPath, projectOwner)
                projectDir = os.path.join(researcherPath, projectName)
                if os.path.exists(projectDir):
                    os.rename(projectDir, os.path.join(researcherPath, new_project_name))
                    project['name'] = new_project_name
                else:
                    return jsonify({"error": "Project already exists"}), 400       
                        
            flag_modified(researcher, "project_list")
            
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Project was unable to be updated"}), 500
    
    return jsonify({"message": "Project updated successfully", "projects_list": researcher.project_list})

# The route is to add tags to a project
@app.route('/addProjectTags', methods=['POST'])
@jwt_required()
def addProjectTags():
    data = request.json
    required_fields = ['project_name', 'tags']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)
    
    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404
    
    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow project update if project does not exist
            
            add_tags = data['tags']
                                    
            # add tags to the project
            #If tags is a string, split it into a list
            if isinstance(add_tags, str):
                added_tags = [tag.strip() for tag in add_tags.split(',')]  # Split by ',' and remove extra spaces
            elif isinstance(add_tags, list):
                added_tags = [str(tag).strip() for tag in add_tags]
                
            for tag in added_tags:
                if tag not in project['tags']:
                    project['tags'].append(tag) # append tags to the project
                    
            flag_modified(researcher, "project_list")
            
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Project was unable to be updated"}), 500
    
    return jsonify({"message": "Tags added successfully.", "projects_list": researcher.project_list})

# The route is to remove tags from a project
@app.route('/removeProjectTags', methods=['POST'])
@jwt_required()
def removeProjectTags():
    data = request.json
    required_fields = ['project_name', 'tags']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)
    
    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404
    
    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow project update if project does not exist
            
            remove_tags = data['tags']
            
            # remove tages
            #If tags is a string, split it into a list
            if isinstance(remove_tags, str):
                removed_tags = [tag.strip() for tag in remove_tags.split(',')]  # Split by ',' and remove extra spaces
            elif isinstance(remove_tags, list):
                removed_tags = [str(tag).strip() for tag in removed_tags]
                
            for tag in removed_tags:
                if tag in project['tags']:
                    project['tags'].remove(tag) # remove tags from the project
                    
            flag_modified(researcher, "project_list")
            
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Project was unable to be updated"}), 500
    
    return jsonify({"message": "Tags removed successfully.", "projects_list": researcher.project_list})

@app.route('/searchProjectByTag', methods=['POST'])
@jwt_required()
def searchProjectByTag():
    data = request.json
    required_fields = ['tag']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)
    
    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404
    
    tag = data['tag']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_list = researcher.project_list
            projects = [project for project in project_list if tag in project.get("tags", [])]
    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while searching for projects"}), 500
    
    return jsonify({"projects_list": projects})


# this route is to update the project status
@app.route('/updateProjectStatus', methods=['POST'])
@jwt_required()
def updateProjectStatus():
    data = request.json
    required_fields = ['project_name', 'status']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)
    
    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404
    
    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow project update if project does not exist
            
            new_status = data['status']
            if new_status == '':
                return jsonify({"error": "Status cannot be empty"}), 400
            
            project['status'] = new_status
            
            flag_modified(researcher, "project_list")
            
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e) # remove in production
        return jsonify({"error": "Project was unable to be updated"}), 500  
    
    return jsonify({"message": "Project status updated successfully.", "projects_list": researcher.project_list})

# this route is to get all the projects of a researcher
@app.route('/getProjects', methods=['GET'])
@jwt_required()
def getProjects():
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)
    
    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404
    
    return jsonify({"projects_list": researcher.project_list})

@app.route('/getProject' , methods=['POST'])
@jwt_required()
def getProject():
    data = request.json
    required_fields = ['project_name']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)
    
    researcher_exists = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher_exists:
        return jsonify({"error": "Researcher not found"}), 404
    
    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists 
            project_dict = {project["name"]: project for project in researcher_exists.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow returning project if project does not exist
    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while retrieving the project"}), 500
    
    return jsonify({"project": project})

# this route is to delete a project
# frontend should ensure that the user is aboslutely sure they want to delete the project as it will 
# delete all the files associated with the project
@app.route('/deleteProject', methods=['POST'])
@jwt_required()
def deleteProject():
    data = request.json
    required_fields = ['project_name']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)
    
    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404
    
    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404
            # Check if researcher owns project
            if project.get("creator") != researcher.first_name: 
                    if project.get("creator id") != str(researcher.id):
                        return jsonify({"error": "You do not have permission to delete this project"}), 403
                # delete project directory
            if os.path.exists(project.get("path")):
                shutil.rmtree(project.get("path"))
                researcher.project_list.remove(project)
            flag_modified(researcher, "project_list")
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Project was unable to be deleted"}), 500

    return jsonify({"message": "Project deleted successfully", "projects_list": researcher.project_list})

# update this route as we get more information on how the metrics should be stored
# this route is to set the metrics for a project once a project has been created.
@app.route('/setProjectMetricField', methods=['POST'])
@jwt_required()
def setProjectMetricsField():

    data = request.json
    required_fields = ['project_name', 'metrics']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        logging.debug("Validation error: Missing required fields")
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']

    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404

            # Process metrics from the frontend
            frontend_metrics = data['metrics']
            if not isinstance(frontend_metrics, dict):
                return jsonify({"error": "Metrics must be a dictionary"}), 400

            # Convert frontend metrics to a dictionary with integer values
            metrics_dict = {metric: 0 for metric in frontend_metrics}

            # Merge with existing metrics
            existing_metrics = project.get('metrics', {})
            if not isinstance(existing_metrics, dict):
                return jsonify({"error": "Existing metrics are not in a valid format"}), 500
            existing_metrics.update(metrics_dict)

            # Update the project's metrics
            project['metrics'] = existing_metrics

            # Mark the project_list as modified and commit changes
            flag_modified(researcher, "project_list")
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(f"Error: {e}")
        return jsonify({"error": "Error: 500, An error occurred while setting the project metrics"}), 500

    return jsonify({"message": "Project metrics set successfully", "metrics": project['metrics']})

@app.route('/getProjectMetrics', methods=['POST'])
@jwt_required()
def getProjectMetrics():
    data = request.json
    required_fields = ['project_name']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)
    
    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404
    
    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404

            # Return the project's metrics
            metrics = project.get("metrics", {})
    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error occurred while retrieving the project metrics"}), 500
    
    return jsonify({"metrics": metrics})

# this route is to update the project metrics
# this will add values to each of the fields in the metrics dictionary
# project metric values should be pulled directly from project data
@app.route('/updateProjectMetrics', methods=['POST'])
@jwt_required()
def updateProjectMetrics():

    data = request.json
    required_fields = ['project_name', 'metrics']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    # Validate researcher
    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    project_name = data['project_name']
    if not isinstance(project_name, str) or not project_name.strip():
        logging.error("Project name must be a non-empty string")
        return jsonify({"error": "Project name must be a non-empty string"}), 400

    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(project_name)
            logging.debug(f"Project: {project}")
            if project is None:
                return jsonify({"error": "Project not found"}), 404

            # Validate metrics from the frontend
            frontend_metrics = data['metrics']
            logging.debug(f"Frontend metrics: {frontend_metrics}")
            if not isinstance(frontend_metrics, dict):
                return jsonify({"error": "Metrics must be a dictionary of numeric values"}), 400

            frontend_metrics = {key: float(value) for key, value in frontend_metrics.items()}
            logging.debug(f"Frontend metrics: {frontend_metrics}")
            
            # Validate and update metrics
            existing_metrics = project.get('metrics', {})
            if not isinstance(existing_metrics, dict):
                logging.error("Existing metrics must be a dictionary")
                return jsonify({"error": "Existing metrics must be a dictionary"}), 500
            existing_metrics.update(frontend_metrics)
            
            # Mark the project_list as modified and commit changes
            flag_modified(researcher, "project_list")
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while updating project metrics: {e}")
        return jsonify({"error": "Error: 500, An error occurred while updating the project metrics"}), 500

    return jsonify({"message": "Project metrics updated successfully", "metrics": project['metrics']})

# this route is to delete a specified metric in a project. 
# this will remove the key value pair from the metrics dictionary
# this can only be called when a project status is set to 'Draft'
@app.route('/deleteProjectMetrics', methods=['POST'])
@jwt_required()
def deleteProjectMetrics():
    data = request.json
    required_fields = ['project_name', 'metric']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)
    
    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404
        
    projectName = data['project_name']
    
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404

            if project.status != 'Draft':
                return jsonify({"error": "The Project status must be set to 'Draft' to delete metrics"}), 400
            
            # check if mertics is a valid dictionary
            if not isinstance(project['metrics'], dict):
                return jsonify({"error": "Metrics are not in a valid format"}), 500
            
            # delete the metric from the project
            metric = data['metric']
            if metric not in project['metrics']:
                return jsonify({"error": "Metric not found"}), 404
            # Delete the metric from the project
            del project['metrics'][metric]

            # Mark the project_list as modified and commit changes
            flag_modified(researcher, "project_list")
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error occurred while deleting the project metric"}), 500   
    
    return jsonify({"message": "Project metric deleted successfully", "metrics": project['metrics']})



# ======== TESTING ROUTES ========
# These routes are for testing purposes only and should be removed once the frontend is in place
# These routes are used to simulate the frontend form submissions
# The frontend will make POST requests to these routes with the form data
# The form data will be validated and then used to create a new user in the database

@app.route('/', methods=['GET'])
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Index Page</title>
    </head>
    <body>
        <h1>Welcome to the User Management System</h1>
        <p>Use the links below to register a Listener or a Researcher:</p>
        <ul>
            <li><a href="/userResetPassword">Reset User Password #w orking</a></li>
            <li><a href="/blindEmailParse">Blind Email Parse # working</a></li>
            <li><a href="/blindPasswordReset">Blind Password Reset # working</a></li>
            <li><a href="/createProject">Create Project # working</a></li>
            <li><a href="/updateProjectName">Update Project Name # working</a></li>
            <li><a href="/addProjectTags">Add Project Tags # working</a></li>
            <li><a href="/removeProjectTags">Remove Project Tags # working</a></li>
            <li><a href="/searchProjectByTag">Search Project By Tag # working</a></li>
            <li><a href="/updateProjectStatus">Update Project Status # working</a></li>
            <li><a href="/getProjects">Get Projects # working</a></li>
            <li><a href="/getProject">Get Project # working</a></li>
            <li><a href="/deleteProject">Delete Project # working</a></li>
            <li><a href="/setProjectMetricField">Set Project Metrics Field # working</a></li>
            <li><a href="/getProjectMetrics">Get Project Metrics # working</a></li>
            <li><a href="/updateProjectMetrics">Update Project Metrics # working</a></li>
            <li><a href="/deleteProjectMetrics">Delete Project Metrics # working</a></li>
        </ul>
    </body>
    </html>
    ''')
    
@app.route('/userResetPassword', methods=['GET'])
def userResetPasswordForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reset Password</title>
    </head>
    <body>
        <h1>User Reset Password</h1>
        <form action="/userResetPassword" method="post">
            <label for="pw">New Password:</label><br>
            <input type="password" id="pw" name="pw"><br>
            <label for="pw_confirmation">Confirm Password:</label><br>
            <input type="password" id="pw_confirmation" name="pw_confirmation"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/userResetPassword', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                    .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')
    
@app.route('/blindEmailParse', methods=['GET'])
def blindEmailParseForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Blind Email Parse</title>
    </head>
    <body>
        <h1>Blind Email Parse</h1>
        <form action="/blindEmailParse" method="post">
            <label for="email">Email:</label><br>
            <input type="email" id="email" name="email"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/blindEmailParse', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                    .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')
    
@app.route('/blindPasswordReset', methods=['GET'])
def blindPasswordResetForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Blind Password Reset</title>
    </head>
    <body>
        <h1>Blind Password Reset</h1>
        <form action="/blindPasswordReset" method="post">
            <label for="id">Blind ID:</label><br>
            <input type="text" id="id" name="id"><br>
            <label for="pw">New Password:</label><br>
            <input type="password" id="pw" name="pw"><br>
            <label for="pw_confirmation">Confirm Password:</label><br>
            <input type="password" id="pw_confirmation" name="pw_confirmation"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/blindPasswordReset', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                    .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')
    
@app.route('/updateProjectName', methods=['GET'])
def updateProjectForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Update Project Name</title>
    </head>
    <body>
        <h1>Update Project Name</h1>
        <form action="/updateProject" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <label for="new_project_name">New Project Name:</label><br>
            <input type="text" id="new_project_name" name="new_project_name"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/updateProjectName', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/addProjectTags', methods=['GET'])
def addProjectTagsForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add Project Tags</title>
    </head>
    <body>
        <h1>Add Project Tags</h1>
        <form action="/addProjectTags" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <label for="tags">Tags:</label><br>
            <input type="text" id="tags" name="tags"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);

                // Convert tags to a list
                if (jsonData.tags) {
                    jsonData.tags = jsonData.tags.split(',').map(tag => tag.trim());
                }

                fetch('/addProjectTags', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/removeProjectTags', methods=['GET'])
def removeProjectTagsForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Remove Project Tags</title>
    </head>
    <body>
        <h1>Remove Project Tags</h1>
        <form action="/removeProjectTags" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <label for="tags">Tags:</label><br>
            <input type="text" id="tags" name="tags"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);

                // Convert tags to a list
                if (jsonData.tags) {
                    jsonData.tags = jsonData.tags.split(',').map(tag => tag.trim());
                }

                fetch('/removeProjectTags', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/updateProjectStatus', methods=['GET'])
def updateProjectStatusForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Update Project Status</title>
    </head>
    <body>
        <h1>Update Project Status</h1>
        <form action="/updateProjectStatus" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <label for="status">Status:</label><br>
            <input type="text" id="status" name="status"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/updateProjectStatus', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/getProjects', methods=['GET'])
def getProjectsForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Get Projects</title>
    </head>
    <body>
        <h1>Get Projects</h1>
        <button id="getProjects">Get Projects</button>
        <script>
            document.getElementById('getProjects').addEventListener('click', function () {
                fetch('/getProjects', {
                    method: 'GET'
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/getProject', methods=['GET'])
def getProjectForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Get Project</title>
    </head>
    <body>
        <h1>Get Project</h1>
        <form action="/getProject" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/getProject', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/deleteProject', methods=['GET'])
def deleteProjectForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Delete Project</title>
    </head>
    <body>
        <h1>Delete Project</h1>
        <form action="/deleteProject" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/deleteProject', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/setProjectMetricField', methods=['GET'])
def setProjectMetricFieldForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Set Project Metrics</title>
        <style>
            .metric-input { margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <h1>Set Project Metrics</h1>
        <form id="metricsForm" action="/setProjectMetricField" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name" required><br><br>
            
            <div id="metricsContainer">
                <div class="metric-input">
                    <label for="metric_1">Metric Name:</label>
                    <input type="text" id="metric_1" name="metric_name_1" placeholder="Metric Name" required>
                    <label for="value_1">Value:</label>
                    <input type="number" id="value_1" name="metric_value_1" placeholder="Value" required>
                </div>
            </div>
            
            <button type="button" id="addMetric">Add Metric</button><br><br>
            <button type="submit">Submit</button>
        </form>
        
        <script>
            let metricCount = 1;

            // Add a new metric input field
            document.getElementById('addMetric').addEventListener('click', function () {
                metricCount++;
                const metricsContainer = document.getElementById('metricsContainer');
                const newMetricDiv = document.createElement('div');
                newMetricDiv.className = 'metric-input';
                newMetricDiv.innerHTML = `
                    <label for="metric_${metricCount}">Metric Name:</label>
                    <input type="text" id="metric_${metricCount}" name="metric_name_${metricCount}" placeholder="Metric Name" required>
                    <label for="value_${metricCount}">Value:</label>
                    <input type="number" id="value_${metricCount}" name="metric_value_${metricCount}" placeholder="Value" required>
                `;
                metricsContainer.appendChild(newMetricDiv);
            });

            // Handle form submission
            document.getElementById('metricsForm').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);

                // Convert form data into JSON format
                const jsonData = {};
                const metrics = {};
                for (const [key, value] of formData.entries()) {
                    if (key.startsWith('metric_name_')) {
                        const metricIndex = key.split('_')[2]; // Extract the index from the key
                        metrics[formData.get(`metric_name_${metricIndex}`)] = parseFloat(formData.get(`metric_value_${metricIndex}`)) || 0;
                    } else if (key !== `metric_value_${key.split('_')[2]}`) {
                        jsonData[key] = value; // Add other fields like project_name
                    }
                }
                jsonData.metrics = metrics;

                // Send the data to the backend
                fetch('/setProjectMetricField', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/getProjectMetrics', methods=['GET'])
def getProjectMetricsForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Get Project Metrics</title>
    </head>
    <body>
        <h1>Get Project Metrics</h1>
        <form action="/getProjectMetrics" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/getProjectMetrics', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/updateProjectMetrics', methods=['GET'])
def updateProjectMetricsForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Update Project Metrics</title>
    </head>
    <body>
        <h1>Update Project Metrics</h1>
        <form action="/updateProjectMetrics" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name" required><br><br>
            <label for="metrics">Metrics (Data input format: key1:value1, key2:value2):</label><br>
            <input type="text" id="metrics" name="metrics" placeholder="key1:value1, key2:value2" required><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);

                // Convert metrics to a dictionary
                const metrics = {};
                const metricsArray = jsonData.metrics.split(',');
                for (const metric of metricsArray) {
                    const [key, value] = metric.split(':');
                    metrics[key] = parseFloat(value) || 0;
                }
                // ensure metrics is a dictionary
                if (typeof metrics !== 'object') {
                    console.error('Metrics must be a dictionary');
                    return;
                }
                
                jsonData.metrics = metrics;

                // Send the parsed data to the backend
                fetch('/updateProjectMetrics', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data))
                .catch(error => console.error('Error:', error));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/deleteProjectMetrics', methods=['GET'])
def deleteProjectMetricsForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Delete Project Metrics</title>
    </head>
    <body>
        <h1>Delete Project Metrics</h1>
        <form action="/deleteProjectMetrics" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <label for="metric">Metric:</label><br>
            <input type="text" id="metric" name="metric"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/deleteProjectMetrics', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/searchProjectByTag', methods=['GET'])
def searchProjectByTagForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Search Project By Tag</title>
    </head>
    <body>
        <h1>Search Project By Tag</h1>
        <form action="/searchProjectByTag" method="post">
            <label for="tag">Tag:</label><br>
            <input type="text" id="tag" name="tag"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/searchProjectByTag', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

# ======== END OF TESTING ROUTES ========


# ========== 5. Run the Flask App ==========
if __name__ == '__main__':
    for _ in range(5):
        try:
            with app.app_context():
            # initialize the database
                db.create_all()
            break
        except OperationalError as e:
            print("Database not ready yet, retrying...")
            time.sleep(5)   
    else:
        print("Database failed to initialize, exiting...")
        exit(1)
    # host='0.0.0.0' to make the server accessible from outside the container
    app.run(debug=True, host='0.0.0.0', port=8016)
import os, uuid, enum, smtplib
import logging  # remove for final production
from flask_cors import CORS  # this should work, dont know why my vscode is throwing an error
from flask import Flask, request, jsonify, render_template_string, render_template, redirect, url_for # render_template_string is used to render HTML, can be removed once frontend is inplace
from password import PasswordHash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY, UUID, ENUM
from sqlalchemy.exc import IntegrityError
from sqlalchemy import DDL, event
from dotenv import load_dotenv
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from email.mime.text import MIMEText

import smtplib

app = Flask(__name__)

load_dotenv()
# Configure logging - remove for final production
logging.basicConfig(level=logging.DEBUG)

# database config
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}/{os.environ.get('POSTGRES_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = 'secret'

# Mail server configuration (use your actual email service settings)
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)

cors = CORS()
cors.init_app(app) # suppressing cors due to error thown by not in use

# ========== 0. Helper Functions ==========
def validate_required_fields(data, required_fields):
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
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

def send_verification_email(email, verification_url):
    receiver_email = email

    subject = "Flask Email Test == Upgraded"
    body = f'Click the link to verify your email: {verification_url}'
    
    # Create email message
    msg = MIMEText(body, "plain")
    msg["From"] = os.getenv('MAIL_USERNAME')
    msg["To"] = receiver_email
    msg["Subject"] = subject

    try:
        # Connect to SMTP server and send email
        server = smtplib.SMTP('smtp.mail.yahoo.com', 587)
        server.starttls()
        server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
        server.sendmail(os.getenv('MAIL_USERNAME'), receiver_email, msg.as_string())
        server.quit()
        return "Email sent successfully!"
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
proficiency_level_enum = ENUM(ProficiencyLevel, name='proficiencylevel', create_type=True)
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
    project_list = db.Column(ARRAY(db.String(128))) # 128 char length array
    uploaded_video = db.Column(ARRAY(db.String(128))) # 128 char length file ID array
    gender = db.Column(gender_enum)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)

class Listener(db.Model):
    __tablename__ = "listeners"
    id = db.Column(UUID(as_uuid=True), primary_key=True, nullable=False) # listener's uuid
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    pw_hash = db.Column(db.String(128), nullable=False) # Argon2 hash string is 97 char long 
    permission = db.Column(permission_level_enum, nullable=False)
    background_info = db.Column(db.String(512))
    reward_points = db.Column(db.Integer)
    languages_list = db.Column(ARRAY(db.String(128)))
    languages_proficiency = db.Column(ARRAY(proficiency_level_enum))
    is_verified = db.Column(db.Boolean, nullable=False)
    is_active = db.Column(db.Boolean, nullable = False)

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
        return redirect(url_for('login')), 405

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
    
    existing_listener = Listener.query.filter_by(email=data['email']).first()
    existing_researcher = Researcher.query.filter_by(email=data['email']).first()
    user = existing_listener if existing_listener else existing_researcher
    
    if not user:
        return jsonify({"error": "Invalid email-password combination"}), 401
    
    hashed_password = user.pw_hash

    if validate_Password(data, hashed_password):
        if not user.is_verified:
            return jsonify({"error": "user has not verified account"}), 401
        
        token = create_access_token(identity=data['email'])

        user.is_active = True
        db.session.commit()

        return jsonify(access_token=token), 200

    return jsonify({"error": "Invalid email-password combination"}), 401

@app.route('/registerListener', methods=['POST'])
def createListener():
    data = request.json

    required_fields = ['first_name', 'last_name', 'email', 'pw']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    # Check if email already exists
    existing_user = Listener.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400
    
    hashed_password = hash_password(data)

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
        is_active=False,
    #    ==== languages to be set in different task, remove and add to task ======
    #    languages_list=data.get('languages_list', []),
    #    languages_proficiency=data.get('languages_proficiency', [])
    )

    try:
        db.session.add(user)
        db.session.commit()

        # Generate token and send verification email
        token = generate_verification_token(data['email'])
        verification_url = url_for('verify_email', token=token, _external=True)

        send_verification_email(data['email'], verification_url)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    # Ensure languages_proficiency is serialized as a list
    return jsonify({"message": "Registration Successful"}), 200

@app.route('/registerResearcher', methods=['POST'])
def createResearcher():
    data = request.json
    required_fields = ['first_name', 'last_name', 'email', 'pw']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    # Hash the user password
    hashed_password = hash_password(data)
    
    # Check if email already exists
    existing_user = Researcher.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400
    
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
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database integrity error: " + str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    return jsonify({"message": "Registration Successful"})

@app.route('/resetPassword', methods=['POST'])
def resetPassword():
    data = request.json
    required_fields = ['pw', 'pw_confirmation', 'id', 'email']
    # validate field is not empty
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    # assign local variables to the data fields
    password = data['pw']
    password_confirmation = data['pw_confirmation']
    user_id = data['id']
    email = data['email']
    
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
        return jsonify({"error": "User not Found"}), 404
    
    # Check if email matches the user
    if existing_user.email != email:
        return jsonify({"error":
            "Email does not match the one registered with the account"}), 400
    
    if existing_user:
        hashed_password = hash_password(data)
        pw_validated = validate_Password(data, existing_user.pw_hash)
        if pw_validated:
            return jsonify({"error": "Password cannot be the same as the previous password"}), 400
        try:
            existing_user.pw_hash = hashed_password.value
            db.session.commit()
            return jsonify({"message": "Password reset successful"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "An error has occured while updating the password"}), 500

# this may need to be changed to only return the 'listener' who is calling the route
# will need more discussion on this 
@app.route('/getListeners', methods=['GET'])
def getListeners():
    users = Listener.query.all()
    return jsonify([{
        "is_verified": user.is_verified,
        "is_active": user.is_active,
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
@app.route('/getResearchers', methods=['GET'])
def getResearchers():
    users = Researcher.query.all()
    return jsonify([{
        "Uuid": str(user.id),
        "First Name": user.first_name,
        "Last Name": user.last_name,
        "Email": user.email,
        "Password": user.pw_hash,
        "Role": user.permission.value,  
        "Organisation": user.organisation,
        "Projects": user.project_list,
        "Uploaded Audio Clips": [adc.value for adc in user.uploaded_video] if user.uploaded_video else [],
        "Gender": user.gender.value if user.gender is not None else None
    } for user in users])

# ======== TESTING ROUTES ========
# These routes are for testing purposes only and should be removed once the frontend is in place
# These routes are used to simulate the frontend form submissions
# The frontend will make POST requests to these routes with the form data
# The form data will be validated and then used to create a new user in the database

@app.route('/') 
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
            <li><a href="/addListener">Register Listener</a></li>
            <li><a href="/addResearcher">Register Researcher</a></li>
            <li><a href="/loginPage">Login Page</a></li>
        </ul>
    </body>
    </html>
    ''')

@app.route('/addListener', methods=['GET'])
def addListener():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add Listener</title>
    </head>
    <body>
        <h1>Add Listener</h1>
        <form action="/registerListener" method="post">
            <label for="first_name">First Name:</label><br>
            <input type="text" id="first_name" name="first_name"><br>
            <label for="last_name">Last Name:</label><br>
            <input type="text" id="last_name" name="last_name"><br>
            <label for="email">Email:</label><br>
            <input type="email" id="email" name="email"><br>
            <label for="pw">Password:</label><br>
            <input type="password" id="pw" name="pw"><br>
            <label for="background_info">Background Info:</label><br>
            <input type="text" id="background_info" name="background_info"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/registerListener', {
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

@app.route('/addResearcher', methods=['GET'])
def addResearcher():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add Researcher</title>
    </head>
    <body>
        <h1>Add Researcher</h1>
        <form action="/registerResearcher" method="post">
            <label for="first_name">First Name:</label><br>
            <input type="text" id="first_name" name="first_name"><br>
            <label for="last_name">Last Name:</label><br>
            <input type="text" id="last_name" name="last_name"><br>
            <label for="email">Email:</label><br>
            <input type="email" id="email" name="email"><br>
            <label for="pw">Password:</label><br>
            <input type="password" id="pw" name="pw"><br>
            <label for="organisation">Organisation:</label><br>
            <input type="text" id="organisation" name="organisation"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/registerResearcher', {
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

@app.route('/resetPassword', methods=['GET'])
def resetPasswordForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reset Password</title>
    </head>
    <body>
        <h1>Reset Password</h1>
        <form action="/resetPassword" method="post">
            <label for="id">User ID:</label><br>
            <input type="text" id="id" name="id"><br>
            <label for="email">Email:</label><br>
            <input type="email" id="email" name="email"><br>
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
                fetch('/resetPassword', {
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

if __name__ == '__main__':
    # The db.create_all() call is inside the if __name__ == '__main__': block,
    # which means it will only run when the script is executed directly.
    # This can cause issues when deploying the application in a production environment.
    # find a way to resolve if necessary.
    with app.app_context():
        # initialize the database
        db.create_all() 
    # host='0.0.0.0' to make the server accessible from outside the container
    app.run(debug=True, host='0.0.0.0', port=8016)
from flask import jsonify
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer
from password import PasswordHash
from app.models import Researcher, Listener, Project # ls
from app import db
import os, smtplib, re
import secrets # secrets not used ?

# ========== 0. Helper Functions ==========


def check_verified(email):
    existing_listener = is_listener_email
    existing_researcher = is_researcher_email(email)
    if existing_listener and existing_listener.is_verified:
        return True
    if existing_researcher and existing_researcher.is_verified:
        return True
    
    return jsonify({"error": "Email not verified"}), 401

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
    
def is_existing_user_email(email):
    existing_listener = Listener.query.filter_by(email=email).first()
    existing_researcher = Researcher.query.filter_by(email=email).first()
    if existing_listener or existing_researcher:
        return True
    return False

def is_researcher_email(email):
    return Researcher.query.filter_by(email=email).first()

def is_listener_email(email):
    return Listener.query.filter_by(email=email).first()

def is_researcher_id(id):
    return Researcher.query.filter_by(id=id).first()

def is_listener_id(id):
    return Listener.query.filter_by(id=id).first()

def blind_login(id):
    existing_listener = Listener.query.filter_by(blind_login=id).first()
    existing_researcher = Researcher.query.filter_by(blind_login=id).first()
    if existing_listener:
        return existing_listener.blindlogin
    elif existing_researcher:
        return existing_researcher.blindlogin
    else:
        return None

def sanitize_project_name(projectName):
    return re.sub(r'[^\w\s-]', '', projectName).strip()

def check_invalid_project_name(projectName):
    return re.search(r'[<>:"/\\|?*]', projectName)

def find_project(projectName, id):
    return Project.query.filter_by(project_name=projectName, creator_id=id).first()

def find_researcher_project(projectName, id):
    return Researcher.project_list.filter_by(project_uuid=id, project_name=projectName).first()

def update_project_creator(current_value, new_value, id):
    # Update the project creator in the Project model
    try:
        projects = Project.query.filter_by(creator_name=current_value, creator_id=id).all()
        if not projects:
            return 
        
        for project in projects:
            project.creator_name = new_value
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False
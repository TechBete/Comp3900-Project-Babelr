from flask import jsonify
from Babelr.models import Researcher
import Babelr.helpers as helpers
from Babelr.researchers import researchersBp
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import IntegrityError


# this route may only be used by the admin to get all researchers
# update to only allow admin to access this route once single researcher recall route has been implemented
@researchersBp.route('/getResearchers', methods=['GET'])
def getResearchers():
    users = Researcher.query.all()
    return jsonify([{
        "Is verified": user.is_verified,
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
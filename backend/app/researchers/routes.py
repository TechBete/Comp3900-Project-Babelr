from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.exc import IntegrityError
from app.researchers import researchersBp
from app.models import Researcher
from app import db
import app.helpers as helper
import uuid, logging

# this route may only be used by the admin to get all researchers
# update to only allow admin to access this route once single researcher recall route has been implemented
# move this route to admin route in future
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

# this route is used to get the researcher's profile
# TODO: add a route to get the researcher's profile


# this route is used to update the researcher's profile, changed from updateOrganisation
# I dont see a justification for researcher to update the researchers organisation by itself,
# its better to allow the researcher to call route to update entire profile and let researcher
# choose what fields to update

@researchersBp.route('/updateResearcherProfile', methods=['POST'])
@jwt_required()
def updateResearcherProfile():
    data = request.json
    
    # check if request body is empty
    if not data:
        return jsonify({"error": "No data was provided"}), 400

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id) # ensure type consistency

    # search researcher name from researcher uuid
    researcher = helper.is_researcher_id(researcher_id)
    if not researcher:
        return jsonify({"error": "Researcher does not exist on database!"}), 400

    try:
        researcher.first_name = data['first_name']
        researcher.last_name = data['last_name']
        researcher.email = data['email']
        researcher.organisation = data['new_organisation']
        researcher.demographic.date_of_birth = data['date_of_birth']
        researcher.demographic.gender = data['gender']
        researcher.demographic.country = data['country']
        researcher.demographic.education = data['education']
        
        for key, value in data.items():
            if getattr(researcher, key, None) != value:
                setattr(researcher, key, value)
                flag_modified(researcher, key)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while updating researcher's organisation: {e}")
        return jsonify({"error": "Error: 500, An error occurred while updating the researcher's organisation"}), 500

    return jsonify({"message": "Researcher organisation updated successfully"}), 200


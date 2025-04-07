from flask import jsonify
from app.models import Researcher
import app.helpers as helpers
from app.researchers import researchersBp
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.exc import IntegrityError
from app import db


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

@researchersBp.route('/updateOrganisation', methods=['POST'])
@jwt_required()
def updateOrganisation():
    data = request.json
    required_fields = ['new_organisation']

    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id) # ensure type consistency

    # search researcher name from researcher uuid
    researcher = session.get(Researcher, researcher_id)
    if not researcher:
        return jsonify({"error": "Researcher does not exist on database!"}), 400

    try:
        researcher.organisation = data['new_organisation']
        flag_modified(researcher, "organisation")
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while updating researcher's organisation: {e}")
        return jsonify({"error": "Error: 500, An error occurred while updating the researcher's organisation"}), 500

    return jsonify({"message": "Researcher organisation updated successfully"}), 200

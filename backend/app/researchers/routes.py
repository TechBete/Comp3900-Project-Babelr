from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import jsonify, request
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.exc import IntegrityError
from app.models import Researcher
from app.researchers import researchersBp
import app.helpers as helper
import uuid, logging
from app import db

'''
# This route is used to get a specific researcher profile
# this is done by sending a GET request to the /getResearcher endpoint
# The request must include a JWT token in the Authorization header
# The token is used to identify the researcher
# The researcher is then retrieved from the database using the token
# The researcher information is then returned in the response

ARGS:
    - None

RESPONSE:
    - 200 OK: Researcher information is returned in the response
    - 400 Bad Request: If the researcher does not exist in the database
    - 400 Bad Request: If the user is not a researcher

RETURNS:
    Researcher information in JSON format
    Uuid, First Name, Last Name, Email, Password,
    Date of Birth, Gender, Country, Education, Organisation,
    Project List. 
    
UPDATES:
    - None
'''

# update route to get specific researcher
@researchersBp.route('/getResearcher', methods=['GET'])
@jwt_required()
def getResearchers():
    # get user information from the given uuid
    id = get_jwt_identity()
    user_id = uuid.UUID(id)
    
    # check if listener is valid user
    user = helper.is_researcher_id(user_id)
    
    if not user:
        return jsonify({"error": "User does not exist on database!"}), 400
    
    # check if user is a researcher
    if not user.permission.value == "researcher":
        return jsonify({"error": "User is not a researcher!"}), 400
    
    return jsonify({
        "Uuid": str(user.id),
        "First Name": user.first_name,
        "Last Name": user.last_name,
        "Email": user.email,
        "Password": user.pw_hash,
        
        "Date of Birth": user.date_of_birth,
        "Gender": user.gender,
        "Country": user.country_of_residence,
        "Education": user.education,
        "Organisation": user.organisation,
        
        "Project List": user.project_list,
        }, 200)




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


# set researcher demographic route
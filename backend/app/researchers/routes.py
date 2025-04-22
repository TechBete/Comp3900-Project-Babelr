from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy.orm.attributes import flag_modified
from app.researchers import researchersBp
from flask import jsonify, request
import app.helpers as helper
import uuid
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

# updated route to get specific researcher
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
        "Gender": str(user.gender),
        "Country": user.country_of_residence,
        "Education": user.education,
        "Organisation": user.organisation,
        
        "Project List": user.project_list,
        }), 200 


'''
# This route is used to update a specific researcher profile
# this is done by sending a POST request to the /updateResearcherProfile endpoint
# The request must include a JWT token in the Authorization header
# The token is used to identify the researcher
# The researcher is then retrieved from the database using the token
# The researcher information is then updated in the database
# The updated researcher information is then returned in the response

ARGS:
    - first_name: str
    - last_name: str
    - date_of_birth: str
    - gender: str
    - country: str
    - education: str
    - organisation: str
    
RESPONSE:
    - 200: Researcher profile updated successfully, updated fields
    - 400: No data was provided
    - 400: Researcher does not exist on database
    - 400: Email already exists
    - 500: Internal Server Error
    
RETURNS:
    - Researcher information in JSON format
    - updated values
    
UPDATES:
    - Database: Researcher
        
'''

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
        # mandatory fields information (nullable=False)
        researcher.first_name = data['first_name']
        researcher.last_name = data['last_name']
        researcher.date_of_birth = data['date_of_birth']
        researcher.country_of_residence = data['country_of_residence']
        researcher.education = data['education']
        researcher.organisation = data['organisation']
        # optional fields (nullable=True)
        researcher.gender = data['gender']
        # update databse and alert listern table
        db.session.add(researcher)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error has occurred while updating the Researcher Profile"}), 500
    return jsonify({"message": "Profile Update successful"}), 200


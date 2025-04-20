from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import jsonify, request
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
        "Gender": user.gender,
        "Country": user.country_of_residence,
        "Education": user.education,
        "Organisation": user.organisation,
        
        "Project List": user.project_list,
        }, 200)


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
    - email: str
    - password: str
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
        
        # Map of request field names to model field names
        field_map = {
            "first_name": "first_name",
            "last_name": "last_name",
            "email": "email",
            "password": "pw_hash",
            "date_of_birth": "date_of_birth",
            "gender": 'gender',
            "country": "country_of_residence",
            "education": "education",
            "organisation": "organisation"
        }
        
        fields_to_update = []
        for request_field, model_field in field_map.items():
            if request_field in data:
                # Check if the field is present in the request data
                current_value = getattr(researcher, model_field)
                new_value = data[request_field]
                
                # Check if the current value is different from the new value
                if current_value != new_value:
                    if request_field == "email":
                        # Check if the email already exists in the database
                        existing_researcher = helper.is_researcher_email(new_value)
                        if existing_researcher:
                            return jsonify({"error": "Email already exists!"}), 400
                    # If the field is password, hash the new password
                    if request_field == "password":
                        new_value = helper.hash_password(new_value)
                    
                    if request_field == "first_name":
                        helper.update_project_creator(current_value, new_value, researcher_id)
                    
                    
                    # Update the field in the model
                    setattr(researcher, model_field, new_value)
                    fields_to_update.append(model_field)
                
                
        if fields_to_update:
            # Update the modified fields in the database
            db.session.commit()
        return jsonify({
                    "message": "Researcher profile updated successfully",
                    "updated fields": fields_to_update
                    }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(e)
        return jsonify({"Error": "500, Internal Server Error"}), 500


from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_required, get_jwt_identity
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.exc import IntegrityError
from flask import jsonify, request
from app.listeners import userBp
from app.models import Demographic, Gender, Listener
import app.helpers as helpers
import uuid, logging
from app import db

# this may need to be changed to only return the 'listener' who is calling the route
# this route may only be used by the admin to get all listeners
@userBp.route('/getListeners', methods=['GET'])
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
        "languages_proficiency": [lp.value for lp in user.languages_proficiency] if user.languages_proficiency else [], # Convert enum array
        "is_verified": user.is_verified,
        "allocated audio": [audio.value for audio in user.allocated_audio] if user.allocated_audio else [], # Convert enum array
    } for user in users])
'''
# test route to get a listener by id once listener cookie is implemented
@userBp.route('/getListener/<uuid:listener_id>', methods=['GET'])
def getListener(listener_id):
    user = Listener.query.get(listener_id)
    if user is None:
        return jsonify({"error": "Listener not found"}), 404
    return jsonify({
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
    })
'''


@userBp.route('/addLanguage', methods=['POST'])
@jwt_required()
def addLanguage():
    data = request.json
    required_fields = ['language', 'proficiency']

    # check validation error
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    # check if listener is valid user
    listener = Listener.query.filter_by(id=listener_id).first()
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    try:
        new_language = {
            "language": data['language'],
            "proficiency": data['proficiency'],
        }

        # implement new validation check to make sure if language is in lanuage list

        if new_language not in listener.languages:
            listener.languages.append(new_language)
            flag_modified(listener, "languages")
            db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Add language Successful"}), 200

def testAddLanguage():
    try:
        listener = db.session.query(Listener).filter_by(first_name="Alice").first()
        if not listener:
            return jsonify({"error": "Listener not found"}), 404

        new_lang = {
            "language": "German",
            "proficiency": "limited_working"
        }

        if new_lang not in listener.languages:
            listener.languages.append(new_lang)
            flag_modified(listener, "languages")
            db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Add language Successful"}), 200

@userBp.route('/editLanguage', methods=['POST'])
@jwt_required()
def editLanguage():
    data = request.json
    required_fields = ['language', 'new_proficiency']

    # check validation error
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    # check if listener is valid user
    listener = Listener.query.filter_by(id=listener_id).first()
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    try:
        target_language = data['language']

        found = False
        for lang_data in listener.languages:
            if lang_data['language'] == target_language:
                lang_data['proficiency'] = data['new_proficiency']
                flag_modified(listener, "languages")
                found = True
                db.session.commit()
        if not found:
            return jsonify({"error": "Language not found"}), 400
    except IntegrityError as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Edit language Successful"}), 200

def testEditLanguage():
    data = {
        "language": "Japanese",
        "new_proficiency": "limited_working"
    }

    listener = db.session.query(Listener).filter_by(first_name="Alice").first()
    try:
        target_language = data['language']

        found = False
        for lang_data in listener.languages:
            if lang_data['language'] == target_language:
                lang_data['proficiency'] = "limited_working"
                flag_modified(listener, "languages")
                found = True
                print(found)
                db.session.commit()
        if not found:
            print("error: Language not found")
            return jsonify({"error": "Language not found"}), 400
    except IntegrityError as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Edit language Successful"}), 200

@userBp.route('/deleteLanguage', methods=['POST'])
@jwt_required()
def deleteLanguage():
    data = request.json
    required_fields = ['language', 'proficiency']

    # check validation error
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    # check if listener is valid user
    listener = Listener.query.filter_by(id=listener_id).first()
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    try:
        find_language = {
            "language": data['language'],
            "proficiency": data['proficiency'],
        }

        # implement new validation check to make sure if language is in lanuage list

        if find_language not in listener.languages:
            return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
        if find_language in listener.languages:
            listener.languages.remove(find_language)
            flag_modified(listener, "languages")
            db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Delete language Successful"}), 200

def testDeleteLanguage():
    try:
        listener = db.session.query(Listener).filter_by(first_name="Alice").first()
        if not listener:
            return jsonify({"error": "Listener not found"}), 404

        delete_lang = {
            "language": "German",
            "proficiency": "limited_working"
        }

        if delete_lang not in listener.languages:
            return jsonify({"error": "Language not exist"}), 400
        if delete_lang in listener.languages:
            listener.languages.remove(delete_lang)
            flag_modified(listener, "languages")
            db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Database integrity error: " + "Error Code 400"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500
    return jsonify({"message": "Add language Successful"}), 200


# Helper function to return current point status of listener
@userBp.route('/getCurrentPoints', methods=['GET'])
@jwt_required()
def getCurrentPoints():
    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    listener = Listener.query.filter_by(id=listener_id).first()
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    return jsonify({"reward_points": listener.reward_points})


@userBp.route('/registerDemographics', methods=['POST'])
@jwt_required()
def registerDemographics():
    data = request.json
    required_fields = ['first_name', 'last_name', 'date_of_birth', 'country_of_residence', 'education']
    # optional demograhics
    gender = data['gender']
    background_info = data['background_info']

    # check validation error
    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    # check if listener is valid user
    listener = Listener.query.filter_by(id=listener_id).first()
    if not listener:
        return jsonify({"error": "Listener not found"}), 404
    logging.debug("Listener before register %s", repr(listener))
    try:
        logging.debug("no here!")
        # edge case when optional data fields are null
        if data['gender'] in Gender._value2member_map_:
            gender = Gender(data['gender'])
        else:
            gender = None

        # all mandatory demographic fields must not be null
        for field in required_fields:
            if field is None:
                return jsonify({"error": "Mandatory demograhic field is missing"}), 400

        # store demograhic information in listener table
        listener.first_name = data['first_name']
        listener.last_name = data['last_name']
        listener.background_info = data['education'] # changed from data['background_info']
        listener.demographic = Demographic(
            date_of_birth=data['date_of_birth'],
            country_of_residence=data['country_of_residence'],
            education=data['education'],
            gender=gender
        )
        listener.languages =  data['languages']
        # raise a flag on listener database to alert that records has been changed.
        for field in ["first_name", "last_name", "background_info", "demographic", "languages"]:
            flag_modified(listener, field)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500
    logging.debug("Listener after register %s", repr(listener))
    return jsonify({"message": "Register demographic Successful"}), 200


# Change the demographic settings of a given user
# Args:
#    Mandatory fields: first_name, last_name, date_of_birth, country_of_residence, education
#    Optional fields: gender, background_info
#    NOTE: Languages can be set it up later.
#    However, listeners can't be allocated to audio file if languages are empty
#    since allocation matching algorithm uses languages information to match audio file and user.
@userBp.route('/changeDemographics', methods = ['POST'])
@jwt_required()
def changeDemographics():
    data = request.json
    if data is None:
        return jsonify({"error": "no data is given with the request"}), 400

    # get listener information from the given uuid
    # changed to user_id from listener_id to avoid confusion when searching Demographic record
    user_id = get_jwt_identity()
    user_id = uuid.UUID(user_id)

    # check if listener is valid user
    listener = Listener.query.filter_by(id=user_id).first()
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    demographic: Demographic | None = Demographic.query.filter_by(listener_id = user_id).first()
    if not demographic:
        return jsonify({"error": f"Demographic data for the user {listener.id} was not found"}), 400

    # Convince the type system that these exists
    assert demographic is not None
    assert data is not None
    try:
        # mandatory fields information (nullable=False)
        listener.first_name = data['first_name']
        listener.last_name = data['last_name']
        demographic.date_of_birth = data['date_of_birth']
        demographic.country_of_residence = data['country_of_residence']
        demographic.education = data['education']
        # optional fields (nullable=True)
        demographic.gender = data['gender']
        listener.background_info = data['background_info']

        for field in ["first_name", "last_name", "background_info"]:
            flag_modified(listener, field)
        for field in ["date_of_birth", "country_of_residence", "education", "gender"]:
            flag_modified(demographic, field)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error has occurred while updating the demographics: {e}"}), 500
    return jsonify({"message": "Demographic Edit successful"}), 200

def testChangeDemographics():
    data = {
        "first_name": "new",
        "last_name": "new",
        "date_of_birth": "0000-00-00",
        "country_of_residence": "HERE",
        "education" : "STUDY",
        "gender": None,
        "background_info": "whatever"
    }

    user_id = "736259a4-aea2-4de7-aa87-5764e1db624b"

    listener = Listener.query.filter_by(id=user_id).first()
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    demographic: Demographic | None = Demographic.query.filter_by(listener_id = user_id).first()
    if not demographic:
        return jsonify({"error": f"Demographic data for the user {listener.id} was not found"}), 400

    # Convince the type system that these exists
    assert demographic is not None
    assert data is not None
    try:
        # mandatory fields information (nullable=False)
        listener.first_name = data['first_name']
        listener.last_name = data['last_name']
        demographic.date_of_birth = data['date_of_birth']
        demographic.country_of_residence = data['country_of_residence']
        demographic.education = data['education']
        # optional fields (nullable=True)
        demographic.gender = data['gender']
        listener.background_info = data['background_info']

        for field in ["first_name", "last_name", "background_info"]:
            flag_modified(listener, field)
        for field in ["date_of_birth", "country_of_residence", "education", "gender"]:
            flag_modified(demographic, field)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error has occurred while updating the demographics: {e}"}), 500
    return jsonify({"message": "Demographic Edit successful"}), 200

@userBp.route('/submitRating', methods=['POST'])
@jwt_required()
def submitRating():
    data = request.json

    print("**********************************************")
    print(data['id'])

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)
    listener = Listener.query.filter_by(id=listener_id).first()
    listener.reward_points = listener.reward_points + 1
    db.session.commit()

    return jsonify({'message': 'reward_id is: ' + str(listener.reward_points)})

@userBp.route('/redeemRewards', methods=['POST', 'OPTIONS'])
@jwt_required()
def redeemRewards():
    data = request.json

    return jsonify({'message': 'reward_id is: ' + data.reward_id})

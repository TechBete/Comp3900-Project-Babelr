from flask import jsonify, request
from Babelr.models import Listener
from Babelr import db
from Babelr.listeners import userBp
import Babelr.helpers as helpers
import uuid, logging
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import flag_modified

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



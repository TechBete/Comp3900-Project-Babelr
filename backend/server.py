import os, uuid, time, shutil
import logging  # remove for final production
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, decode_token, set_access_cookies, unset_jwt_cookies, get_jwt
from flask import Flask, request, jsonify, render_template_string, render_template, redirect, url_for # render_template_string is used to render HTML, can be removed once frontend is inplace
from email_validator import validate_email, EmailNotValidError
from flask import send_from_directory, send_file # this is for accessing files from a directory

from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.exc import IntegrityError, OperationalError

# Configure logging - remove for final production
logging.basicConfig(level=logging.DEBUG)

# ========== 4. Server Endpoint Routes ==========


# this may need to be changed to only return the 'listener' who is calling the route
# this route may only be used by the admin to get all listeners
@app.route('/getListeners', methods=['GET'])
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
        "languages_proficiency": [lp.value for lp in user.languages_proficiency] if user.languages_proficiency else []  # Convert enum array
    } for user in users])

'''
# test route to get a listener by id once listener cookie is implemented
@app.route('/getListener/<uuid:listener_id>', methods=['GET'])
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

# this route may only be used by the admin to get all researchers
# update to only allow admin to access this route once single researcher recall route has been implemented
@app.route('/getResearchers', methods=['GET'])
def getResearchers():
    users = Researcher.query.all()
    return jsonify([{
        "is_verified": user.is_verified,
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

@app.route('/createProject', methods=['POST'])
@jwt_required()
def createProject():
    data = request.json
    required_fields = ['project_name']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    # # FOR FRONTEND TESTING PART
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id) # ensure type consistency
    required_fields = ['researcher_id']
    validation_error = validate_required_fields({'researcher_id': researcher_id}, required_fields) # validate researcher_id
    if validation_error:
        return validation_error
    # END OF FRONTEND TESTING PART

    projectName = data['project_name']
    researcherId = researcher_id   #FRONTEND TESTING

    # Check if researcher exists
    researcher = Researcher.query.filter_by(id=researcherId).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404  # disallow project creation if researcher does not exist

    # Ensure project list is not empty
    if researcher.project_list is None:
        researcher.project_list = []

    # ensure project name is not empty
    if projectName == '':
        return jsonify({"error": "Project name cannot be empty"}), 400

    # use a transaction to ensure that the project is only created if the project list is updated successfully
    try:
        with db.session.begin_nested():
            # Check if project already exists
            # Check if project already exists
            if any(project.get("name") == projectName for project in researcher.project_list):
                return jsonify({"error": "Project already exists"}), 400

            # create directory for project files in backend and docker.
            projectOwner = str(researcherId)
            projectPath = os.path.join("/app", "audioData")
            researcherPath = os.path.join(projectPath, projectOwner)
            projectDir = os.path.join(researcherPath, projectName)
            if not os.path.exists(projectDir):
                os.makedirs(projectDir)
            else:
                return jsonify({"error": "Project already exists"}), 400
            # update Researcher project list with project name
            researcher.project_list.append({"name": projectName,
                                            "path": projectDir,
                                            "status": "Draft",
                                            "tags": [],
                                            "metrics": {
                                                "Naturalness": 0,
                                                "Intelligibility": 0,
                                                "Clarity": 0
                                            },
                                            "creator id": int(researcher.id),# updated to include creator id (researcher id) 
                                            "creator": researcher.first_name
                                            }) # updated to include creator name

            flag_modified(researcher, "project_list")

            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Project was unable to be created"}), 500

    return jsonify({"message": "Project created successfully"}) ## probably should not send back project list but for simplicities sake

# this route is to update the project name
@app.route('/updateProjectName', methods=['POST'])
@jwt_required()
def updateProject():
    data = request.json
    required_fields = ['project_name']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow project update if project does not exist

            # update project name
            if 'new_project_name' in data:
                new_project_name = data['new_project_name']
                if new_project_name == '':
                    return jsonify({"error": "Project name cannot be empty"}), 400

                # Check if project already exists
                if any(project.get("name") == new_project_name for project in researcher.project_list):
                    return jsonify({"error": "Project name already exists"}), 400

                # create directory for project files in backend and docker.
                projectOwner = str(researcher_id)
                projectPath = os.path.join("/app", "audioData")
                researcherPath = os.path.join(projectPath, projectOwner)
                projectDir = os.path.join(researcherPath, projectName)
                if os.path.exists(projectDir):
                    os.rename(projectDir, os.path.join(researcherPath, new_project_name))
                    project['name'] = new_project_name
                else:
                    return jsonify({"error": "Project already exists"}), 400

            flag_modified(researcher, "project_list")

            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Project was unable to be updated"}), 500

    return jsonify({"message": "Project updated successfully", "projects_list": researcher.project_list})

# The route is to add tags to a project
@app.route('/addProjectTags', methods=['POST'])
@jwt_required()
def addProjectTags():
    data = request.json
    required_fields = ['project_name', 'tags']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow project update if project does not exist

            add_tags = data['tags']

            # add tags to the project
            #If tags is a string, split it into a list
            if isinstance(add_tags, str):
                added_tags = [tag.strip() for tag in add_tags.split(',')]  # Split by ',' and remove extra spaces
            elif isinstance(add_tags, list):
                added_tags = [str(tag).strip() for tag in add_tags]

            for tag in added_tags:
                if tag not in project['tags']:
                    project['tags'].append(tag) # append tags to the project

            flag_modified(researcher, "project_list")

            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Project was unable to be updated"}), 500

    return jsonify({"message": "Tags added successfully.", "projects_list": researcher.project_list})

# The route is to remove tags from a project
@app.route('/removeProjectTags', methods=['POST'])
@jwt_required()
def removeProjectTags():
    data = request.json
    required_fields = ['project_name', 'tags']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow project update if project does not exist

            remove_tags = data['tags']

            # remove tages
            #If tags is a string, split it into a list
            if isinstance(remove_tags, str):
                removed_tags = [tag.strip() for tag in remove_tags.split(',')]  # Split by ',' and remove extra spaces
            elif isinstance(remove_tags, list):
                removed_tags = [str(tag).strip() for tag in removed_tags]

            for tag in removed_tags:
                if tag in project['tags']:
                    project['tags'].remove(tag) # remove tags from the project

            flag_modified(researcher, "project_list")

            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Project was unable to be updated"}), 500

    return jsonify({"message": "Tags removed successfully.", "projects_list": researcher.project_list})

@app.route('/searchProjectByTag', methods=['POST'])
@jwt_required()
def searchProjectByTag():
    data = request.json
    required_fields = ['tag']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    tag = data['tag']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_list = researcher.project_list
            projects = [project for project in project_list if tag in project.get("tags", [])]
    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while searching for projects"}), 500

    return jsonify({"projects_list": projects})

# this route is to update the project status
@app.route('/updateProjectStatus', methods=['POST'])
@jwt_required()
def updateProjectStatus():
    data = request.json
    required_fields = ['project_name', 'status']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow project update if project does not exist

            new_status = data['status']
            if new_status == '':
                return jsonify({"error": "Status cannot be empty"}), 400

            project['status'] = new_status

            flag_modified(researcher, "project_list")

            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e) # remove in production
        return jsonify({"error": "Project was unable to be updated"}), 500

    return jsonify({"message": "Project status updated successfully.", "projects_list": researcher.project_list})

# this route is to get all the projects of a researcher
@app.route('/getProjects', methods=['GET'])
@jwt_required()
def getProjects():
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    return jsonify({"projects_list": researcher.project_list})

@app.route('/getProject' , methods=['POST'])
@jwt_required()
def getProject():
    data = request.json
    required_fields = ['project_name']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher_exists = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher_exists:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher_exists.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow returning project if project does not exist
    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while retrieving the project"}), 500

    return jsonify({"project": project})

# this route is to delete a project
# frontend should ensure that the user is aboslutely sure they want to delete the project as it will
# delete all the files associated with the project
@app.route('/deleteProject', methods=['POST'])
@jwt_required()
def deleteProject():
    data = request.json
    required_fields = ['project_name']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404
            # Check if researcher owns project
            if project.get("creator") != researcher.first_name:
                    if project.get("creator id") != str(researcher.id):
                        return jsonify({"error": "You do not have permission to delete this project"}), 403
                # delete project directory
            if os.path.exists(project.get("path")):
                shutil.rmtree(project.get("path"))
                researcher.project_list.remove(project)
            flag_modified(researcher, "project_list")
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Project was unable to be deleted"}), 500

    return jsonify({"message": "Project deleted successfully", "projects_list": researcher.project_list})

# update this route as we get more information on how the metrics should be stored
# this route is to set the metrics for a project once a project has been created.
@app.route('/setProjectMetricField', methods=['POST'])
@jwt_required()
def setProjectMetricsField():
    data = request.json
    required_fields = ['project_name', 'metrics']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        logging.debug("Validation error: Missing required fields")
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']

    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404

            # Process metrics from the frontend
            frontend_metrics = data['metrics']
            if not isinstance(frontend_metrics, dict):
                return jsonify({"error": "Metrics must be a dictionary"}), 400

            # Convert frontend metrics to a dictionary with integer values
            metrics_dict = {metric: 0 for metric in frontend_metrics}

            # Merge with existing metrics
            existing_metrics = project.get('metrics', {})
            if not isinstance(existing_metrics, dict):
                return jsonify({"error": "Existing metrics are not in a valid format"}), 500
            existing_metrics.update(metrics_dict)

            # Update the project's metrics
            project['metrics'] = existing_metrics

            # Mark the project_list as modified and commit changes
            flag_modified(researcher, "project_list")
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(f"Error: {e}")
        return jsonify({"error": "Error: 500, An error occurred while setting the project metrics"}), 500

    return jsonify({"message": "Project metrics set successfully", "metrics": project['metrics']})

@app.route('/getProjectMetrics', methods=['POST'])
@jwt_required()
def getProjectMetrics():
    data = request.json
    required_fields = ['project_name']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404

            # Return the project's metrics
            metrics = project.get("metrics", {})
    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error occurred while retrieving the project metrics"}), 500

    return jsonify({"metrics": metrics})

# this route is to update the project metrics
# this will add values to each of the fields in the metrics dictionary
# project metric values should be pulled directly from project data
@app.route('/updateProjectMetrics', methods=['POST'])
@jwt_required()
def updateProjectMetrics():

    data = request.json
    required_fields = ['project_name', 'metrics']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    # Validate researcher
    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    project_name = data['project_name']
    if not isinstance(project_name, str) or not project_name.strip():
        logging.error("Project name must be a non-empty string")
        return jsonify({"error": "Project name must be a non-empty string"}), 400

    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(project_name)
            logging.debug(f"Project: {project}")
            if project is None:
                return jsonify({"error": "Project not found"}), 404

            # Validate metrics from the frontend
            frontend_metrics = data['metrics']
            logging.debug(f"Frontend metrics: {frontend_metrics}")
            if not isinstance(frontend_metrics, dict):
                return jsonify({"error": "Metrics must be a dictionary of numeric values"}), 400

            frontend_metrics = {key: float(value) for key, value in frontend_metrics.items()}
            logging.debug(f"Frontend metrics: {frontend_metrics}")

            # Validate and update metrics
            existing_metrics = project.get('metrics', {})
            if not isinstance(existing_metrics, dict):
                logging.error("Existing metrics must be a dictionary")
                return jsonify({"error": "Existing metrics must be a dictionary"}), 500
            existing_metrics.update(frontend_metrics)

            # Mark the project_list as modified and commit changes
            flag_modified(researcher, "project_list")
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while updating project metrics: {e}")
        return jsonify({"error": "Error: 500, An error occurred while updating the project metrics"}), 500

    return jsonify({"message": "Project metrics updated successfully", "metrics": project['metrics']})

# this route is to delete a specified metric in a project.
# this will remove the key value pair from the metrics dictionary
# this can only be called when a project status is set to 'Draft'
@app.route('/deleteProjectMetrics', methods=['POST'])
@jwt_required()
def deleteProjectMetrics():
    data = request.json
    required_fields = ['project_name', 'metric']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']

    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404

            if project.status != 'Draft':
                return jsonify({"error": "The Project status must be set to 'Draft' to delete metrics"}), 400

            # check if mertics is a valid dictionary
            if not isinstance(project['metrics'], dict):
                return jsonify({"error": "Metrics are not in a valid format"}), 500

            # delete the metric from the project
            metric = data['metric']
            if metric not in project['metrics']:
                return jsonify({"error": "Metric not found"}), 404
            # Delete the metric from the project
            del project['metrics'][metric]

            # Mark the project_list as modified and commit changes
            flag_modified(researcher, "project_list")
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error occurred while deleting the project metric"}), 500

    return jsonify({"message": "Project metric deleted successfully", "metrics": project['metrics']})

@app.route('/uploadAudioFile', methods=['POST'])
@jwt_required()
def uploadAudioFile():
    if "file" not in request.files:
        return jsonify({"error": "File doesn't exists."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "There is no selected file."}), 400

    # assign local variables to the data fields
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id) # ensure type consistency

    # search researcher name from researcher uuid
    researcher = session.get(Researcher, researcher_id)
    if researcher:
        researcher_name = researcher.first_name + researcher.last_name
    else:
        return jsonify({"error": "Researcher does not exist on database!"}), 400

    audio_file_path = "../audioData" # root directory path for all audio files
    researcher_dir = os.path.join(audio_file_path, researcher_name)

    # if directory with researcher name doesn't exist, make directory
    os.makedirs(researcher_dir, exist_ok=True)

    file_path = os.path.join(researcher_dir, file.filename)
    file.save(file_path)

    return jsonify({"message": f"{file.filename} is successfully uploaded and stored!"}), 200

@app.route('/addLanguage', methods=['POST'])
@jwt_required()
def addLanguage():
    data = request.json
    required_fields = ['language', 'proficiency']

    # check validation error
    validation_error = validate_required_fields(data, required_fields)
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

@app.route('/editLanguage', methods=['POST'])
@jwt_required()
def editLanguage():
    data = request.json
    required_fields = ['language', 'new_proficiency']

    # check validation error
    validation_error = validate_required_fields(data, required_fields)
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

@app.route('/deleteLanguage', methods=['POST'])
@jwt_required()
def deleteLanguage():
    data = request.json
    required_fields = ['language', 'proficiency']

    # check validation error
    validation_error = validate_required_fields(data, required_fields)
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

# ======== TESTING ROUTES ========
# These routes are for testing purposes only and should be removed once the frontend is in place
# These routes are used to simulate the frontend form submissions
# The frontend will make POST requests to these routes with the form data
# The form data will be validated and then used to create a new user in the database

@app.route('/', methods=['GET'])
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
            <li><a href="/userResetPassword">Reset User Password #w orking</a></li>
            <li><a href="/blindEmailParse">Blind Email Parse # working</a></li>
            <li><a href="/blindPasswordReset">Blind Password Reset # working</a></li>
            <li><a href="/createProject">Create Project # working</a></li>
            <li><a href="/updateProjectName">Update Project Name # working</a></li>
            <li><a href="/addProjectTags">Add Project Tags # working</a></li>
            <li><a href="/removeProjectTags">Remove Project Tags # working</a></li>
            <li><a href="/searchProjectByTag">Search Project By Tag # working</a></li>
            <li><a href="/updateProjectStatus">Update Project Status # working</a></li>
            <li><a href="/getProjects">Get Projects # working</a></li>
            <li><a href="/getProject">Get Project # working</a></li>
            <li><a href="/deleteProject">Delete Project # working</a></li>
            <li><a href="/setProjectMetricField">Set Project Metrics Field # working</a></li>
            <li><a href="/getProjectMetrics">Get Project Metrics # working</a></li>
            <li><a href="/updateProjectMetrics">Update Project Metrics # working</a></li>
            <li><a href="/deleteProjectMetrics">Delete Project Metrics # working</a></li>
            <li><a href="/testUploadAudio">Test Audio uploading function # idkidk </a></li>
            <li><a href="/testAddLang">Test add language function </a></li>
            <li><a href="/getListenerData">Test get user data function </a></li>
        </ul>
    </body>
    </html>
    ''')

@app.route('/userResetPassword', methods=['GET'])
def userResetPasswordForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reset Password</title>
    </head>
    <body>
        <h1>User Reset Password</h1>
        <form action="/userResetPassword" method="post">
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
                fetch('/userResetPassword', {
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

@app.route('/blindEmailParse', methods=['GET'])
def blindEmailParseForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Blind Email Parse</title>
    </head>
    <body>
        <h1>Blind Email Parse</h1>
        <form action="/blindEmailParse" method="post">
            <label for="email">Email:</label><br>
            <input type="email" id="email" name="email"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/blindEmailParse', {
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

@app.route('/blindPasswordReset', methods=['GET'])
def blindPasswordResetForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Blind Password Reset</title>
    </head>
    <body>
        <h1>Blind Password Reset</h1>
        <form action="/blindPasswordReset" method="post">
            <label for="id">Blind ID:</label><br>
            <input type="text" id="id" name="id"><br>
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
                fetch('/blindPasswordReset', {
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

@app.route('/updateProjectName', methods=['GET'])
def updateProjectForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Update Project Name</title>
    </head>
    <body>
        <h1>Update Project Name</h1>
        <form action="/updateProject" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <label for="new_project_name">New Project Name:</label><br>
            <input type="text" id="new_project_name" name="new_project_name"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/updateProjectName', {
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

@app.route('/addProjectTags', methods=['GET'])
def addProjectTagsForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add Project Tags</title>
    </head>
    <body>
        <h1>Add Project Tags</h1>
        <form action="/addProjectTags" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <label for="tags">Tags:</label><br>
            <input type="text" id="tags" name="tags"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);

                // Convert tags to a list
                if (jsonData.tags) {
                    jsonData.tags = jsonData.tags.split(',').map(tag => tag.trim());
                }

                fetch('/addProjectTags', {
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

@app.route('/removeProjectTags', methods=['GET'])
def removeProjectTagsForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Remove Project Tags</title>
    </head>
    <body>
        <h1>Remove Project Tags</h1>
        <form action="/removeProjectTags" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <label for="tags">Tags:</label><br>
            <input type="text" id="tags" name="tags"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);

                // Convert tags to a list
                if (jsonData.tags) {
                    jsonData.tags = jsonData.tags.split(',').map(tag => tag.trim());
                }

                fetch('/removeProjectTags', {
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

@app.route('/updateProjectStatus', methods=['GET'])
def updateProjectStatusForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Update Project Status</title>
    </head>
    <body>
        <h1>Update Project Status</h1>
        <form action="/updateProjectStatus" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <label for="status">Status:</label><br>
            <input type="text" id="status" name="status"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/updateProjectStatus', {
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

@app.route('/getProjects', methods=['GET'])
def getProjectsForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Get Projects</title>
    </head>
    <body>
        <h1>Get Projects</h1>
        <button id="getProjects">Get Projects</button>
        <script>
            document.getElementById('getProjects').addEventListener('click', function () {
                fetch('/getProjects', {
                    method: 'GET'
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/getProject', methods=['GET'])
def getProjectForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Get Project</title>
    </head>
    <body>
        <h1>Get Project</h1>
        <form action="/getProject" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/getProject', {
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

@app.route('/deleteProject', methods=['GET'])
def deleteProjectForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Delete Project</title>
    </head>
    <body>
        <h1>Delete Project</h1>
        <form action="/deleteProject" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/deleteProject', {
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

@app.route('/setProjectMetricField', methods=['GET'])
def setProjectMetricFieldForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Set Project Metrics</title>
        <style>
            .metric-input { margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <h1>Set Project Metrics</h1>
        <form id="metricsForm" action="/setProjectMetricField" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name" required><br><br>

            <div id="metricsContainer">
                <div class="metric-input">
                    <label for="metric_1">Metric Name:</label>
                    <input type="text" id="metric_1" name="metric_name_1" placeholder="Metric Name" required>
                    <label for="value_1">Value:</label>
                    <input type="number" id="value_1" name="metric_value_1" placeholder="Value" required>
                </div>
            </div>

            <button type="button" id="addMetric">Add Metric</button><br><br>
            <button type="submit">Submit</button>
        </form>

        <script>
            let metricCount = 1;

            // Add a new metric input field
            document.getElementById('addMetric').addEventListener('click', function () {
                metricCount++;
                const metricsContainer = document.getElementById('metricsContainer');
                const newMetricDiv = document.createElement('div');
                newMetricDiv.className = 'metric-input';
                newMetricDiv.innerHTML = `
                    <label for="metric_${metricCount}">Metric Name:</label>
                    <input type="text" id="metric_${metricCount}" name="metric_name_${metricCount}" placeholder="Metric Name" required>
                    <label for="value_${metricCount}">Value:</label>
                    <input type="number" id="value_${metricCount}" name="metric_value_${metricCount}" placeholder="Value" required>
                `;
                metricsContainer.appendChild(newMetricDiv);
            });

            // Handle form submission
            document.getElementById('metricsForm').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);

                // Convert form data into JSON format
                const jsonData = {};
                const metrics = {};
                for (const [key, value] of formData.entries()) {
                    if (key.startsWith('metric_name_')) {
                        const metricIndex = key.split('_')[2]; // Extract the index from the key
                        metrics[formData.get(`metric_name_${metricIndex}`)] = parseFloat(formData.get(`metric_value_${metricIndex}`)) || 0;
                    } else if (key !== `metric_value_${key.split('_')[2]}`) {
                        jsonData[key] = value; // Add other fields like project_name
                    }
                }
                jsonData.metrics = metrics;

                // Send the data to the backend
                fetch('/setProjectMetricField', {
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

@app.route('/getProjectMetrics', methods=['GET'])
def getProjectMetricsForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Get Project Metrics</title>
    </head>
    <body>
        <h1>Get Project Metrics</h1>
        <form action="/getProjectMetrics" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/getProjectMetrics', {
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

@app.route('/updateProjectMetrics', methods=['GET'])
def updateProjectMetricsForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Update Project Metrics</title>
    </head>
    <body>
        <h1>Update Project Metrics</h1>
        <form action="/updateProjectMetrics" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name" required><br><br>
            <label for="metrics">Metrics (Data input format: key1:value1, key2:value2):</label><br>
            <input type="text" id="metrics" name="metrics" placeholder="key1:value1, key2:value2" required><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);

                // Convert metrics to a dictionary
                const metrics = {};
                const metricsArray = jsonData.metrics.split(',');
                for (const metric of metricsArray) {
                    const [key, value] = metric.split(':');
                    metrics[key] = parseFloat(value) || 0;
                }
                // ensure metrics is a dictionary
                if (typeof metrics !== 'object') {
                    console.error('Metrics must be a dictionary');
                    return;
                }

                jsonData.metrics = metrics;

                // Send the parsed data to the backend
                fetch('/updateProjectMetrics', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jsonData)
                }).then(response => response.json())
                .then(data => console.log(data))
                .catch(error => console.error('Error:', error));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/deleteProjectMetrics', methods=['GET'])
def deleteProjectMetricsForm():
    return render_template_string(''''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Delete Project Metrics</title>
    </head>
    <body>
        <h1>Delete Project Metrics</h1>
        <form action="/deleteProjectMetrics" method="post">
            <label for="project_name">Project Name:</label><br>
            <input type="text" id="project_name" name="project_name"><br>
            <label for="metric">Metric:</label><br>
            <input type="text" id="metric" name="metric"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/deleteProjectMetrics', {
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

@app.route('/searchProjectByTag', methods=['GET'])
def searchProjectByTagForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Search Project By Tag</title>
    </head>
    <body>
        <h1>Search Project By Tag</h1>
        <form action="/searchProjectByTag" method="post">
            <label for="tag">Tag:</label><br>
            <input type="text" id="tag" name="tag"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/searchProjectByTag', {
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

@app.route('/testUploadAudio', methods=['GET'])
def audioFileUploadForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Audio file upload testing</title>
    </head>
    <body>
        <h1>Audio file upload</h1>
        <form id="uploadForm">
            <label for="audio">Upload Audio File:</label><br>
            <input type="file" id="audio" name="audio" accept="audio/*"><br><br>

            <button type="submit">Submit</button>
        </form>

        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();

                const formData = new FormData(e.target);

                fetch('/uploadAudioFile', {
                    method: 'POST',
                    body: formData
                }).then(response => response.json())
                .then(data => console.log(data));
                .catch(error => console.error('Error:', error));
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/testAddLang', methods=['GET'])
def testAddLanguageForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add language</title>
    </head>
    <body>
        <h1>User Add Language</h1>
        <form action="/addLanguage" method="post">
            <label for="language">Language:</label><br>
            <input type="text" id="language" name="language"><br>
            <label for="proficiency">Proficiency level:</label><br>
            <input type="text" id="proficiency" name="proficiency"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                fetch('/addLanguage', {
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

@app.route('/getListenerData', methods=['GET'])
def getListenerDataForm():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Get Listener</title>
    </head>
    <body>
        <h1>Get Listener</h1>
        <form action="/getListeners" method="post">
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                fetch('/getListeners', {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify("")
                }).then(response => response.json())
                .then(data => console.log(data));
            });
        </script>
    </body>
    </html>
    ''')

# ======== END OF TESTING ROUTES ========


# ========== 5. Run the Flask App ==========
if __name__ == '__main__':
    for _ in range(5):
        try:
            with app.app_context():
            # initialize the database
                db.create_all()
                # creates test user for frontend testing, verification for this account is waived
                createTestUser()
                # testAddLanguage() # for testing add language functionality; To be removed
                testEditLanguage()
            break
        except OperationalError as e:
            print("Database not ready yet, retrying...")
            time.sleep(5)
    else:
        print("Database failed to initialize, exiting...")
        exit(1)
    # host='0.0.0.0' to make the server accessible from outside the container
    app.run(debug=True, host='0.0.0.0', port=8016)

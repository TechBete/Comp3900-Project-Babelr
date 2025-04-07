from flask import jsonify, request
from app.models import Researcher
from app import db, jwt
import app.helpers as helper
import os, uuid, shutil, logging
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, jwt_required, get_jwt_identity
from sqlalchemy.orm.attributes import flag_modified
from app.projects import projectsBp


@projectsBp.route('/createProject', methods=['POST'])
@jwt_required()
def createProject():
    data = request.json
    required_fields = ['project_name']
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    # # FOR FRONTEND TESTING PART
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id) # ensure type consistency
    required_fields = ['researcher_id']
    validation_error = helper.validate_required_fields({'researcher_id': researcher_id}, required_fields) # validate researcher_id
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
                                            "tags": [], # big set of tags used for each audio files in the project
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
@projectsBp.route('/updateProjectName', methods=['POST'])
@jwt_required()
def updateProject():
    data = request.json
    required_fields = ['project_name']
    validation_error = helper.validate_required_fields(data, required_fields)
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
@projectsBp.route('/addProjectTags', methods=['POST'])
@jwt_required()
def addProjectTags():
    data = request.json
    required_fields = ['project_name', 'tags']
    validation_error = helper.validate_required_fields(data, required_fields)
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
@projectsBp.route('/removeProjectTags', methods=['POST'])
@jwt_required()
def removeProjectTags():
    data = request.json
    required_fields = ['project_name', 'tags']
    validation_error = helper.validate_required_fields(data, required_fields)
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

@projectsBp.route('/searchProjectByTag', methods=['POST'])
@jwt_required()
def searchProjectByTag():
    data = request.json
    required_fields = ['tag']
    validation_error = helper.validate_required_fields(data, required_fields)
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
@projectsBp.route('/updateProjectStatus', methods=['POST'])
@jwt_required()
def updateProjectStatus():
    data = request.json
    required_fields = ['project_name', 'status']
    validation_error = helper.validate_required_fields(data, required_fields)
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
@projectsBp.route('/getProjects', methods=['GET'])
@jwt_required()
def getProjects():
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    return jsonify({"projects_list": researcher.project_list})

@projectsBp.route('/getProject' , methods=['POST'])
@jwt_required()
def getProject():
    data = request.json
    required_fields = ['project_name']
    validation_error = helper.validate_required_fields(data, required_fields)
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
@projectsBp.route('/deleteProject', methods=['POST'])
@jwt_required()
def deleteProject():
    data = request.json
    required_fields = ['project_name']
    validation_error = helper.validate_required_fields(data, required_fields)
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
@projectsBp.route('/setProjectMetricField', methods=['POST'])
@jwt_required()
def setProjectMetricsField():
    data = request.json
    required_fields = ['project_name', 'metrics']
    validation_error = helper.validate_required_fields(data, required_fields)
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

@projectsBp.route('/getProjectMetrics', methods=['POST'])
@jwt_required()
def getProjectMetrics():
    data = request.json
    required_fields = ['project_name']
    validation_error = helper.validate_required_fields(data, required_fields)
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
@projectsBp.route('/updateProjectMetrics', methods=['POST'])
@jwt_required()
def updateProjectMetrics():
    data = request.json
    required_fields = ['project_name', 'metrics']
    validation_error = helper.validate_required_fields(data, required_fields)
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
            #TODO: update all audio files to have same updated metrics
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"An error occurred while updating project metrics: {e}")
        return jsonify({"error": "Error: 500, An error occurred while updating the project metrics"}), 500

    return jsonify({"message": "Project metrics updated successfully", "metrics": project['metrics']})

# this route is to delete a specified metric in a project.
# this will remove the key value pair from the metrics dictionary
# this can only be called when a project status is set to 'Draft'
@projectsBp.route('/deleteProjectMetrics', methods=['POST'])
@jwt_required()
def deleteProjectMetrics():
    data = request.json
    required_fields = ['project_name', 'metric']
    validation_error = helper.validate_required_fields(data, required_fields)
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

@projectsBp.route('/uploadAudioFile', methods=['POST'])
@jwt_required()
def uploadAudioFile():
    data = request.json
    required_fields = ['project_name', 'tags']

    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    if "file" not in request.files:
        return jsonify({"error": "File doesn't exists."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "There is no selected file."}), 400

    # assign local variables to the data fields
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id) # ensure type consistency

    # search researcher name from researcher uuid
    researcher = helper.is_researcher_id(researcher_id)
    if researcher:
        researcher_name = researcher.first_name + researcher.last_name
    else:
        return jsonify({"error": "Researcher does not exist on database!"}), 400

    audio_file_path = "../audioData" # root directory path for all audio files
    researcher_dir = os.path.join(audio_file_path, researcher_name)

    # if directory with researcher name doesn't exist, make directory
    os.makedirs(researcher_dir, exist_ok=True)

    file_path = os.path.join(researcher_dir, file.filename)
    file.save(file_path) # save the file in the directory

    try:
        project_dict = {project["name"]: project for project in researcher.project_list}
        project = project_dict.get(data['project_name'])
        if project is None:
            return jsonify({"error": "Project not found"}), 404

        if project.status != 'Draft':
            return jsonify({"error": "The Project status must be set to 'Draft' to delete metrics"}), 400

        audio_data = {
            "name": file.filename,
            "file_extension": filetype.guess(file_path).extension,
            "file_path": file_path,
            "allocated_listeners": [],
            "metrics": project["metrics"], # metrics for the audio file set here
            "tags": [data['tags']]
            # subset of the project tags, these tags are specific tags for each audio file
        }

        if audio_data not in researcher["uploaded_audio"]:
            researcher["uploaded_audio"].append(audio_data)
            flag_modified(researcher, "uploaded_audio")
            db.session.commit()
        else:
            return jsonify({"message": "Audio file already exist"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500

    return jsonify({"message": f"{file.filename} is successfully uploaded and stored!"}), 200

def testUploadAudioFile():
    project_name = "Test Project 1"

    # assign local variables to the data fields
    researcher_id = "20658111-860a-4a87-a520-11800b9f36e9"

    # search researcher name from researcher uuid
    researcher = Researcher.query.filter_by(id=researcher_id).first()
    if researcher:
        researcher_name = researcher.first_name + researcher.last_name
    else:
        return jsonify({"error": "Researcher does not exist on database!"}), 400

    audio_file_path = "../audioData" # root directory path for all audio files
    researcher_dir = os.path.join(audio_file_path, researcher_name)

    # if directory with researcher name doesn't exist, make directory
    os.makedirs(researcher_dir, exist_ok=True)

    file_path = os.path.join(researcher_dir, "test")
    # file.save(file_path)

    try:
        project_dict = {project["name"]: project for project in researcher.project_list}
        project = project_dict.get(project_name)

        if project is None:
            return jsonify({"error": "Project not found"}), 404

        audio_data = {
            "name": file.filename,
            "file_extension": filetype.guess(file_path).extension,
            "file_path": file_path,
            "allocated_listeners": [],
            "metrics": project["metrics"],
            "tags": [data['tags']]
            # subset of the project tags, these tags are specific tags for each audio file
        }

        if audio_data not in researcher["uploaded_audio"]:
            researcher["uploaded_audio"].append(audio_data)
            flag_modified(researcher, "uploaded_audio")
            db.session.commit()
        else:
            return jsonify({"message": "Audio file already exist"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500

    return jsonify({"message": "file is successfully uploaded and stored!"}), 200

# this route is to get the metrics for a specific audio file in a project
# this will return the metrics for the audio file
# the route will check if the audio file exists in the project
# if the audio file does not exist, it will return an error

@projectsBp.route('/getAudioFileMetrics', methods=['POST'])
@jwt_required()
def getAudioFileMetrics():
    data = request.json
    required_fields = ['project_name', 'audio_file_name']
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher = helper.is_researcher_id(researcher_id)
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']
    audio_file_name = data['audio_file_name']

    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
            # disallow returning project if project does not exist
                return jsonify({"error": "Project not found"}), 404

            # Check if audio file exists
            audio_files = [audio for audio in researcher.uploaded_audio if audio['name'] == audio_file_name]
            if not audio_files:
                return jsonify({"error": "Audio file not found"}), 404

            # Get the metrics for the specified audio file
            audio_file_metrics = audio_files[0].get('metrics', {})
    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while retrieving the audio file metrics"}), 500

    return jsonify({"audio_file_metrics": audio_file_metrics})


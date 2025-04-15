from app.audio import audioBp
from app.models import Listener, ProficiencyLevel
from flask import jsonify, request
from app import db, jwt
import app.helpers as helper
import os, uuid, shutil, filetype, logging
import app.helpers as helpers
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, jwt_required, get_jwt_identity
from sqlalchemy.orm.attributes import flag_modified

def formatTags(tags: str) -> list[str]:
    return tags.split(",")

def getRequirements(tags: list[str]) -> tuple[str, ProficiencyLevel]:
    logging.debug(f'tags[1]: {tags[1]}')
    logging.debug(f'tags[2]: {tags[2]}')
    language = tags[1];
    proficiency_level = ProficiencyLevel[f'{tags[2]}']
    return (language, proficiency_level)
def isQualified(listener: Listener, lang, min_proficiency) -> bool:
    for language in listener.languages:
        if language['language'] == lang and ProficiencyLevel[language['proficiency'].lower()] >= min_proficiency:
            return True
    return False

@audioBp.route('/uploadAudioFile', methods=['POST'])
@jwt_required()
def uploadAudioFile():
    def getQualifiedListeners(requirements: tuple[str, ProficiencyLevel]) -> list[Listener]:
        (lang, min_proficiency) = requirements

        all_listeners = Listener.query.all()

        qualified_listeners = []

        for listener in all_listeners:
            if isQualified(listener, lang, min_proficiency):
                logging.debug(f'{listener} is qualified')
                qualified_listeners.append(listener)

        logging.debug(f'qualified listeners: {qualified_listeners}')
        return qualified_listeners

    data = request.form
    required_fields = ['project_name', 'tags']

    validation_error = helpers.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    # file availibility validation
    # TODO: @halliya i think this is what you need to fix?
    if "file" not in request.files:
        return jsonify({"error": "File doesn't exists."}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "There is no selected file."}), 400

    # Get researcher information using uuid
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)
    # search researcher name from researcher uuid

    researcher = helpers.is_researcher_id(researcher_id)

    if researcher:
        researcher_name = researcher.first_name + researcher.last_name
    else:
        return jsonify({"error": "Researcher does not exist on database!"}), 400

    # NOTE: file path syntax = /root/audioData/researcherId/projectName/researcherName/fileName
    file_path = "/app/audioData" # root directory path for all audio files
    researcher_dir = os.path.join(file_path, str(researcher_id))
    # if directory with researcher id doesn't exist, make directory
    project_path_dir = os.path.join(researcher_dir, data['project_name'])

    researcher_name_dir = os.path.join(project_path_dir, researcher_name)
    os.makedirs(researcher_name_dir, exist_ok=True)
    file_path = os.path.join(researcher_name_dir, file.filename)
    file.save(file_path) # save the file in the directory

    tags = formatTags(data['tags'])

    requirements = getRequirements(tags)
    qualified_listener = getQualifiedListeners(requirements)

    get_id = lambda listener: listener.id.hex
    qualified_listener_ids = list(map(get_id, qualified_listener))
    try:
        project_dict = {project["name"]: project for project in researcher.project_list}

        project = project_dict.get(data['project_name'])

        if project is None:
            return jsonify({"error": "Project not found"}), 404

        if project['status'] != 'Draft':
            return jsonify({"error": "The Project status must be set to 'Draft' to delete metrics"}), 400

        audio_data = {
            "name": file.filename,
            "file_extension": filetype.guess(file_path).extension,
            "file_path": file_path,
            "allocated_listeners": qualified_listener_ids,
            "metrics": project["metrics"], # metrics for the audio file set here
            "tags": tags,
            "Researcher": str(researcher.id),
            "project_name": data['project_name'],
            "project_path": project_path_dir,
            # subset of the project tags, these tags are specific tags for each audio file
        }
        if audio_data not in researcher.uploaded_audio:
            researcher.uploaded_audio.append(audio_data)
            flag_modified(researcher, "uploaded_audio")
            for listener in qualified_listener:
                listener.assigned_audio.append(audio_data)
                logging.debug(f'listener {listener} has assigned audio files {listener.assigned_audio}')
            db.session.commit()
        else:
            return jsonify({"message": "Audio file already exist"}), 400
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error Code: 500"}), 500

    return jsonify({"message": f"{file.filename} is successfully uploaded and stored!"}), 200
# def uploadAudioFile():
#     data = request.form
#     required_fields = ['project_name', 'tags']
#
#     validation_error = helper.validate_required_fields(data, required_fields)
#     if validation_error:
#         return validation_error
#
#     # file availibility validation
#     if "file" not in request.files:
#         return jsonify({"error": "File doesn't exists."}), 400
#     file = request.files["file"]
#     if file.filename == "":
#         return jsonify({"error": "There is no selected file."}), 400
#
#     # Get researcher information using uuid
#     researcher_id = get_jwt_identity()
#     researcher_id = uuid.UUID(researcher_id)
#     # search researcher name from researcher uuid
#
#     researcher = helper.is_researcher_id(researcher_id)
#
#     if researcher:
#         researcher_name = researcher.first_name + researcher.last_name
#     else:
#         return jsonify({"error": "Researcher does not exist on database!"}), 400
#
#     # NOTE: file path syntax = /root/audioData/researcherId/projectName/researcherName/fileName
#     # look into this, there should be a simpler way to do it
#
#     file_path = "/app/audioData" # root directory path for all audio files
#     researcher_dir = os.path.join(file_path, str(researcher_id))
#     # if directory with researcher id doesn't exist, make directory
#     project_path_dir = os.path.join(researcher_dir, data['project_name'])
#     researcher_name_dir = os.path.join(project_path_dir, researcher_name)
#     os.makedirs(researcher_name_dir, exist_ok=True)
#     file_path = os.path.join(researcher_name_dir, file.filename)
#
#     file.save(file_path) # save the file in the directory
#
#     try:
#         project_dict = {project["name"]: project for project in researcher.project_list}
#
#         project = project_dict.get(data['project_name'])
#
#         if project is None:
#             return jsonify({"error": "Project not found"}), 404
#
#         if project['status'] != 'Draft':
#             return jsonify({"error": "The Project status must be set to 'Draft' to delete metrics"}), 400
#
#         audio_data = {
#             "name": file.filename,
#             "file_extension": filetype.guess(file_path).extension,
#             "file_path": file_path,
#             "allocated_listeners": [],
#             "metrics": project["metrics"], # metrics for the audio file set here
#             "tags": [data['tags']],
#             "Researcher": str(researcher.id),
#             "project_name": data['project_name'],
#             "project_path": project_path_dir,
#             # subset of the project tags, these tags are specific tags for each audio file
#         }
#         if audio_data not in researcher.uploaded_audio:
#             researcher.uploaded_audio.append(audio_data)
#             flag_modified(researcher, "uploaded_audio")
#             db.session.commit()
#         else:
#             return jsonify({"message": "Audio file already exist"}), 400
#     except Exception as e:
#         db.session.rollback()
#         logging.debug(e)
#         return jsonify({"error": "Error Code: 500"}), 500
#
#     return jsonify({"message": f"{file.filename} is successfully uploaded and stored!"}), 200

def testUploadAudioFile():
    project_name = "Test Project 1"

    # assign local variables to the data fields
    researcher_id = "20658111-860a-4a87-a520-11800b9f36e9"

    # search researcher name from researcher uuid
    researcher = helper.is_researcher_id(researcher_id)
    if researcher:
        researcher_name = researcher.first_name + researcher.last_name
    else:
        return jsonify({"error": "Researcher does not exist on database!"}), 400

    # NOTE: file path syntax = /root/audioData/researcherId/projectName/researcherName/fileName
    # follow up on this as well
    
    file_path = "../../../audioData" # root directory path for all audio files
    researcher_dir = os.path.join(file_path, researcher_id)
    # if directory with researcher id doesn't exist, make directory
    os.makedirs(researcher_dir, exist_ok=True)
    researcher_name_dir = os.path.join(researcher_dir, researcher_name)
    os.makedirs(researcher_name_dir, exist_ok=True)
    
    file_path = os.path.join(researcher_name_dir, "testfile")
    # file.save(file_path) # save the file in the directory

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

@audioBp.route('/getAudioFileMetrics', methods=['POST'])
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

# this route is to get the audio files for a specific project
# this will return the audio files for the project
@audioBp.route('/getProjectAudioFiles', methods=['POST'])
@jwt_required()
def getProjectAudioFiles():
    data = request.json
    required_fields = ['project_name']
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)
    researcher = helper.is_researcher_id(researcher_id)
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']
    
    try:
        with db.session.begin_nested(): 
             # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            logging.debug(project_dict)
            
            # Get project details if name exists
            project = project_dict.get(projectName)
            if project is None:
                logging.debug(project)
                return jsonify({"error": "Project not found"}), 404

            # Check if audio files exist for project
            audio_file_names = project.get('Audio File Name', [])
            
            # search for audio files in the uploaded_audio list in the researcher object
            # Check if audio files exist
            if not audio_file_names:
                return jsonify({"error": "No audio files found for this project"}), 404
            
            # Get the audio files for the specified project
            audio_files = [audio for audio in researcher.uploaded_audio if audio['name'] in audio_file_names]
            logging.debug(audio_files)
            if not audio_files:
                return jsonify({"error": "Audio file not found"}), 404
            
    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while retrieving the audio files"}), 500
    
    return jsonify({"audio_files": audio_files})

# test route to get the audio files for a specific project
@audioBp.route('/testgetProjectAudioFiles', methods=['GET'])
def testgetProjectAudioFiles():

    researcher_id = "20658111-860a-4a87-a520-11800b9f36e9"
    researcher = helper.is_researcher_id(researcher_id)

    projectName = "Test Project 1"

    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            logging.debug(project_dict)
            project = project_dict.get(projectName)
            if project is None:
                logging.debug(project)
                return jsonify({"error": "Project not found"}), 404

            # Check if audio files exist
            audio_file_names = project.get('Audio File Name', [])
            
            # search for audio files in the uploaded_audio list in the researcher object
            # Check if audio files exist
            if not audio_file_names:
                return jsonify({"error": "No audio files found for this project"}), 404
            
            # Get the audio files for the specified project
            audio_files = [audio for audio in researcher.uploaded_audio if audio['name'] in audio_file_names]
            logging.debug(audio_files)
            if not audio_files:
                return jsonify({"error": "Audio file not found"}), 404

    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while retrieving the audio file metrics"}), 500

    return jsonify({"audio_file_metrics": audio_files})

# this route is to get specific audio file from a project 
# and return the audio data so that it can be allocated to the users
# database
 
@audioBp.route('/getAudioFileData', methods=['POST'])
@jwt_required()
def getAudioFileData():
    data = request.json
    required_fields = ['project_name', 'audio_file_name']
    
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher = helper.is_researcher_id(researcher_id)
    # Validate researcher
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404


    projectName = data['project_name']
    audio_file_name = data['audio_file_name']

    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            
            # Check if project exists
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow returning project if project does not exist

            # Check if audio file exists
            audio_files = [audio for audio in researcher.uploaded_audio if audio['name'] == audio_file_name]
            if not audio_files:
                return jsonify({"error": "Audio file not found"}), 404

            # Get the specified audio file
            audio_file = audio_files[0]
            
            # update audio file metrics from project metrics
            # this is to ensure metrics are consistent across all audio files in the project
            # and up to date with the project metrics
            # ensure that the metrics are in a valid format 
            if not isinstance(project['metrics'], dict):
                return jsonify({"error": "Project metrics are not in a valid format"}), 500
            # check if audio file metrics are in a valid format
            if not isinstance(audio_file['metrics'], dict):
                return jsonify({"error": "Audio file metrics are not in a valid format"}), 500
            
    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while retrieving the audio file"}), 500

    return jsonify({"audio_file": audio_file})

# test route for get audio file
@audioBp.route('/testgetAudioFileData', methods=['GET'])
def testgetAudioFileData():
    researcher_id = "20658111-860a-4a87-a520-11800b9f36e9"
    researcher = helper.is_researcher_id(researcher_id)

    projectName = "Test Project 1"
    audio_file_name = "testFile1"

    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            
            # Check if project exists
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow returning project if project does not exist

            # Check if audio file exists
            audio_files = [audio for audio in researcher.uploaded_audio if audio['name'] == audio_file_name]
            if not audio_files:
                return jsonify({"error": "Audio file not found"}), 404

            # Get the specified audio file
            audio_file = audio_files[0]
            
            # update audio file metrics from project metrics
            # this is to ensure metrics are consistent across all audio files in the project
            # and up to date with the project metrics
            # ensure that the metrics are in a valid format 
            if not isinstance(project['metrics'], dict):
                return jsonify({"error": "Project metrics are not in a valid format"}), 500
            # check if audio file metrics are in a valid format
            if not isinstance(audio_file['metrics'], dict):
                return jsonify({"error": "Audio file metrics are not in a valid format"}), 500
            # update audio file metrics with project metrics
            audio_file['metrics'] = project['metrics']
            
    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while retrieving the audio file"}), 500

    return jsonify({"audio_file": audio_file})

# this function is used to update the metrics of a specific audio file in a project
@audioBp.route('/updateAudioMetrics', methods=['POST'])
@jwt_required()
def updateAudioMetrics():
    data = request.json
    required_fields = ['project_name', 'audio_file_name']
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)
    researcher = helper.is_researcher_id(researcher_id)
    
    # Validate researcher
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404
    
    # set local variables to the data fields
    project_name = data['project_name']
    audio_file_name = data['audio_file_name']
    
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(project_name)
            
            # Check if project exists
            if project is None:
                return jsonify({"error": "Project not found"}), 404
            # Check if audio file exists
            audio_files = [audio for audio in researcher.uploaded_audio if audio['name'] == audio_file_name]
            if not audio_files:
                return jsonify({"error": "Audio file not found"}), 404
            
            # Get the specified audio file
            audio_file = audio_files[0]
            
            # check if audio file metrics are in a valid format
            if not isinstance(audio_file['metrics'], dict):
                return jsonify({"error": "Audio file metrics are not in a valid format"}), 500
            
            # check if project metrics are in a valid format
            if not isinstance(project['metrics'], dict):
                return jsonify({"error": "Project metrics are not in a valid format"}), 500
 
            # Validate the structure of project metrics
            required_fields = ['min', 'max', 'minimum label', 'maximum label', 'description']
            for metric_name, metric_data in project['metrics'].items():
                if not isinstance(metric_data, dict):
                    return jsonify({"error": "Metric {} is not in a valid format".format(metric_data)}), 500
                for field in required_fields:
                    if field not in metric_data:
                        return jsonify({"error": "Metric {} is missing required field {}".format(metric_name, field)}), 500
            
            # update audio file metrics from project metrics
            # this is to ensure metrics are consistent
            audio_file['metrics'] = project['metrics']
            
            # Mark the project_list as modified and commit changes
            flag_modified(researcher, "uploaded_audio")
            db.session.commit()
    # handle any errors that occur during the process    
    except Exception as e:
            logging.debug(e)
            return jsonify({"error": "Error: 500, An error has occured while updating the audio file metrics"}), 500
    return jsonify({"message": "Audio metrics updated successfully"}), 200


# this function is used to update the metrics of all audio files in a project
# this will be called when the project is set to Published
@audioBp.route('/updateAllAudioMetrics', methods=['POST'])
@jwt_required()
def updateAllAudioMetrics():
    data = request.json
    required_fields = ['project_name']
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)
    researcher = helper.is_researcher_id(researcher_id)
    
    # Validate researcher
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404
    # set local variables to the data fields
    project_name = data['project_name']
    
    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(project_name)
            
            # Check if project exists
            if project is None:
                return jsonify({"error": "Project not found"}), 404
            
            # check if audio file metrics are in a valid format
            if not isinstance(project['metrics'], dict):
                return jsonify({"error": "Project metrics are not in a valid format"}), 500
            
            # Validate the structure of project metrics
            required_fields = ['min', 'max', 'minimum label', 'maximum label', 'description']
            for metric_name, metric_data in project['metrics'].items():
                if not isinstance(metric_data, dict):
                    return jsonify({"error": "Metric {} is not in a valid format".format(metric_data)}), 500
                for field in required_fields:
                    if field not in metric_data:
                        return jsonify({"error": "Metric {} is missing required field {}".format(metric_name, field)}), 500
            
            # update audio file metrics from project metrics
            # this is to ensure metrics are consistent across all audio files in the project
            for audio_file in researcher.uploaded_audio:
                if audio_file['project_name'] == project_name:
                    audio_file['metrics'] = project['metrics']
                    
            # Mark the project_list as modified and commit changes
            flag_modified(researcher, "uploaded_audio")
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while updating the audio file metrics"}), 500
    return jsonify({"message": "Audio metrics updated successfully"}), 200

from app.audio import audioBp
from app.models import Listener, ProficiencyLevel, ProjectStatus, AudioFile
from flask import jsonify, request
from app import db
import app.helpers as helper
import os, uuid, filetype, logging
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, jwt_required, get_jwt_identity
from sqlalchemy.orm.attributes import flag_modified


def formatTags(tags: str) -> list[str]:
    return tags.split(",")

def getRequirements(tags: list[str]) -> tuple[str, ProficiencyLevel]:
    language = tags[1]
    proficiency_level = ProficiencyLevel[f'{tags[3]}']
    return (language, proficiency_level)


'''
# this route is for researcher to upload audio file on the existing project
# to upload the audio file, status of project must not be draft

ARGS:
    - token: str
    - project_name: srt
    - model: str
    - language: str
    = min_proficiency: str(enum)
    - tagsL list[str]

RESPONSE:
    - 200: “File" is successfully uploaded and stored
    - 400: Validation Error
    - 400: File doesn't exists
    - 400: There is no selected file
    - 400: Researcher does not exist on database!
    - 400: Audio file already exists
    - 400: The Project status must be set to 'draft' to upload audio clips
    - 500: Server Error

RETURNS:
    - str of successful message

UPDATES:
    - Database: Project
'''
@audioBp.route('/uploadAudioFile', methods=['POST'])
@jwt_required()
def uploadAudioFile():
    data = request.form
    required_fields = ['project_name', 'model', 'language', 'min_proficiency', 'tags']

    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    # file availibility validation
    if "file" not in request.files:
        return jsonify({"error": "File doesn't exists."}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "There is no selected file."}), 400

    # Get researcher information using uuid
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)
    # search researcher name from researcher uuid
    researcher = helper.is_researcher_id(researcher_id)

    if researcher:
        researcher_name = researcher.first_name + researcher.last_name
    else:
        return jsonify({"error": "Researcher does not exist on database!"}), 400

    # NOTE: file path syntax = /root/audioData/researcherId/projectName/researcherName/fileName
    # look into this, there should be a simpler way to do it
    file_path = "/app/audioData" # root directory path for all audio files
    researcher_dir = os.path.join(file_path, str(researcher_id))
    # if directory with researcher id doesn't exist, make directory
    project_path_dir = os.path.join(researcher_dir, data['project_name'])

    researcher_name_dir = os.path.join(project_path_dir, researcher_name)
    os.makedirs(researcher_name_dir, exist_ok=True)
    file_path = os.path.join(researcher_name_dir, file.filename)
    file.save(file_path) # save the file in the directory

    try:
        project = helper.find_project(data['project_name'], researcher_id)

        if project is None:
            return jsonify({"error": "Project not found"}), 404

        if project.status != ProjectStatus.draft:
            return jsonify({"error": "The Project status must be set to 'draft' to upload audio clips"}), 400

        audio_data = AudioFile(
            id=str(data.get(id, uuid.uuid4())),
            file_name=file.filename,
            file_extension=filetype.guess(file_path).extension,
            file_path=file_path,
            model=data['model'],
            language=data['language'],
            min_proficiency=data['min_proficiency'],
            metrics=project.metrics,
            tags=data['tags'],
            researcher_id=str(researcher.id),
            project_name=project.project_name,
        )

        if db.session.query(AudioFile).filter_by(file_path=file_path).first():
            return jsonify({"message": "Audio file already exist"}), 400
        db.session.add(audio_data)
        project.audio_list.append(str(audio_data.id))
        flag_modified(project, "audio_list")

        # update project with the audio file tags and model
        # check to see if tag is already inside project tags
        add_tags = data['tags']
        if isinstance(add_tags, str):
            added_tags = [tag.strip() for tag in add_tags.split(',')]  # Split by ',' and remove extra spaces
        elif isinstance(add_tags, list):
            added_tags = [str(tag).strip() for tag in add_tags]

        for tag in added_tags:
            if tag not in project.tags:
                project.tags.append(tag)

        flag_modified(project, "tags")

        # check to see if model is already inside project model
        if data['model'] not in project.models:
            project.models.append(data['model'])
        flag_modified(project, "models")

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error Code: 500"}), 500

    return jsonify({"message": f"{file.filename} is successfully uploaded and stored!"}), 200

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
            # data and file are throwing errors because test function is not getting data from request
            # nor is file being passed in
        }

        if audio_data not in researcher["uploaded_audio"]:
            researcher["uploaded_audio"].append(audio_data)
            flag_modified(researcher, "uploaded_audio")
            db.session.commit()
        else:
            return jsonify({"message": "Audio file already exist"}), 400

        # add audio file to project assigned_audio
        if "assigned_audio" not in project:
            project["assigned_audio"] = {
                "audio": []
            }
        # check if audio file already exists in the project
        if file.filename not in project["assigned_audio"]["audio"]:
            project["assigned_audio"]["audio"].append(file.filename)
            flag_modified(researcher, "project_list")
            db.session.commit()
        else:
            return jsonify({"message": "Audio file already exist in project"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error Code: 500"}), 500

    return jsonify({"message": "file is successfully uploaded and stored!"}), 200

'''
# this route is to get the metrics for a specific audio file in a project
# this will return the metrics for the audio file
# the route will check if the audio file exists in the project
# if the audio file does not exist, it will return an error

ARGS:
    - token: str
    - project_name: srt
    - audio_file_name

RESPONSE:
    - 200: audio_file_metrics.
    - 400: Validation error
    - 404: Researcher not found
    - 404: Project not found
    - 404: Audio file not Found
    - 500: An error has occurred while retrieving the audio file metrics

RETURNS:
    - Metrics in the form of list[dict]

UPDATES:
    - N/A
'''
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
            project = helper.find_project(projectName, researcher_id)
            if project is None:
            # disallow returning project if project does not exist
                return jsonify({"error": "Project not found"}), 404

            # Check if audio file exists
            audio_file = AudioFile.query.filter_by(file_name=audio_file_name)
            if not audio_file:
                return jsonify({"error": "Audio file not found"}), 404

            # Get the metrics for the specified audio file
            audio_file_metrics = audio_file.metrics
    except Exception as e:
        return jsonify({"error": "Error: 500, An error has occured while retrieving the audio file metrics"}), 500

    return jsonify({"audio_file_metrics": audio_file_metrics})

'''
# this route is to get the audio files for a specific project
# this will return the audio files for the project
# might need to check this route, pretty sure it is broken

ARGS:
    - token: str
    - project_name: srt

RESPONSE:
    - 200: audio_files
    - 400: Validation Error
    - 404: Researcher not found
    - 404: Project not found
    - 404: No audio files found for this project
    - 404: Audio files not found
    - 500: Error: 500, An error has occurred while retrieving the audio files

RETURNS:
    - A list of dictionaries containing audio file information

UPDATES:
    - N/A
'''
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
            project = helper.find_project(projectName, researcher_id)
            if project is None:
                return jsonify({"error": "Project not found"}), 404

            # Check if audio files exist
            if project.audio_list == []:
                return jsonify({"error": "No audio files found for this project"}), 404

            # Get the audio files for the specified project
            audio_files = []
            audio_files = helper.get_all_audio_files(projectName, researcher_id)
            if not audio_files or audio_files == []:
                return jsonify({"error": "Audio files not found"}), 404

            # convert audio_files to serializable format
            serialized_audio_files = []
            for audio_file in audio_files:
                if hasattr(audio_file, '__dict__'):
                    num_of_allocated = 0
                    num_of_evaluated = 0
                    for listener in audio_file.allocated_listeners:
                        if len(listener) > 1:
                            num_of_evaluated += 1
                        num_of_allocated += 1

                    # If field is an ORM object like AudioFile
                    audio_file_dict = {
                        "id": str(getattr(audio_file, 'id', '')) if getattr(audio_file, 'id', '') else None,
                        "file_name": getattr(audio_file, 'file_name', ''),
                        "file_extension": getattr(audio_file, 'file_extension', ''),
                        "file_path": getattr(audio_file, 'file_path', ''),
                        "model": getattr(audio_file, 'model', ''),
                        "language": getattr(audio_file, 'language', ''),
                        "min_proficiency": str(getattr(audio_file, 'min_proficiency', '')),
                        "metrics": getattr(audio_file, 'metrics', {}),
                        "tags": getattr(audio_file, 'tags', []),
                        "researcher_id": str(getattr(audio_file, 'researcher_id', '')) if getattr(audio_file, 'researcher_id', '') else None,
                        "project_name": getattr(audio_file, 'project_name', ''),
                        "allocated_listeners": getattr(audio_file, 'allocated_listeners', []),
                        "num_of_allocated": num_of_allocated,
                        "num_of_evaluated": num_of_evaluated,
                    }
                    serialized_audio_files.append(audio_file_dict)
                else:
                    # If already a basic type (string, int, etc.)
                    serialized_audio_files.append(audio_file)

    except Exception as e:
        return jsonify({"error": "Error: 500, An error has occured while retrieving the audio files"}), 500

    return jsonify({"audio_files": serialized_audio_files})

# test route to get the audio files for a specific project
# this is broken, need to fix
@audioBp.route('/testgetProjectAudioFiles', methods=['GET'])
def testgetProjectAudioFiles():

    researcher_id = "20658111-860a-4a87-a520-11800b9f36e9"
    researcher = helper.is_researcher_id(researcher_id)

    projectName = "Test Project 1"

    try:
        with db.session.begin_nested():
            # Check if project exists
            project_dict = {project["name"]: project for project in researcher.project_list}
            project = project_dict.get(projectName)
            if project is None:
                return jsonify({"error": "Project not found"}), 404

            # Check if audio files exist
            audio_file_names = project.get('Audio File Name', [])

            # search for audio files in the uploaded_audio list in the researcher object
            # Check if audio files exist
            if not audio_file_names:
                return jsonify({"error": "No audio files found for this project"}), 404

            # Get the audio files for the specified project
            audio_files = [audio for audio in researcher.uploaded_audio if audio['name'] in audio_file_names]
            if not audio_files:
                return jsonify({"error": "Audio file not found"}), 404

    except Exception as e:
        return jsonify({"error": "Error: 500, An error has occured while retrieving the audio file metrics"}), 500

    return jsonify({"audio_file_metrics": audio_file_names})

'''
# this route is to get specific audio file from a project
# and return the audio data so that it can be allocated to the users
# database

ARGS:
    - token: str
    - audio_id: srt

RESPONSE:
    - 200: audio_files
    - 400: Validation Error
    - 404: Listener not found
    - 404: Audio file not found
    - 404: Project not found
    - 500: Project metrics are not in a valid format
    - 500: Audio file metrics are not in a valid format
    - 500: error: Error: 500, An error has occurred while retrieving the audio file

RETURNS:
    - a dictionary that contains the audio file data

UPDATES:
    - N/A
'''
@audioBp.route('/getAudioFileData', methods=['POST'])
@jwt_required()
def getAudioFileData():
    data = request.json
    required_fields = ['audio_id']

    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    listener_id = get_jwt_identity()
    listener_id = uuid.UUID(listener_id)

    listener = helper.is_listener_id(listener_id)
    # Validate listener
    if not listener:
        return jsonify({"error": "Listener not found"}), 404

    audio_id = data['audio_id']

    try:
        with db.session.begin_nested():
            # Check if project exists
            audio_file = helper.get_audio_from_audio_id(audio_id)

            # Check if audio file exists and get specific audio file
            if not audio_file:
                return jsonify({"error": "Audio file not found"}), 404

            project = helper.find_project(audio_file.project_name, audio_file.researcher_id)
            if project is None:
                return jsonify({"error": "Project not found"}), 404

            # ensure metrics are consistent with audio file and the project
            # ensure that the metrics are in a valid format
            if not isinstance(project.metrics, dict):
                return jsonify({"error": "Project metrics are not in a valid format"}), 500
            # check if audio file metrics are in a valid format
            if not isinstance(audio_file.metrics, dict):
                return jsonify({"error": "Audio file metrics are not in a valid format"}), 500

            # update audio file metrics from project metrics
            audio_file.metrics = project.metrics

            # make sure that audiofile can be returned as a JSON object
            audio_file_dict = {
                "id": str(audio_file.id),
                "file_name": audio_file.file_name,
                "file_extension": audio_file.file_extension,
                "file_path": audio_file.file_path,
                "model": audio_file.model,
                "language": audio_file.language,
                "min_proficiency": str(audio_file.min_proficiency),
                "metrics": audio_file.metrics,
                "tags": audio_file.tags,
                "researcher_id": str(audio_file.researcher_id),
                "project_name": audio_file.project_name
            }

    except Exception as e:
        return jsonify({"error": "Error: 500, An error has occured while retrieving the audio file"}), 500

    return jsonify({"audio_file": audio_file_dict})

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
        return jsonify({"error": "Error: 500, An error has occured while retrieving the audio file"}), 500

    return jsonify({"audio_file": audio_file})

'''
# this function is used to update the metrics of a specific audio file in a project

ARGS:
    - token: str
    - audio_file_name: str

RESPONSE:
    - 200: audio_files
    - 400: Validation Error
    - 404: Researcher not found
    - 404: Project not found
    - 404: Audio file not found
    - 500: Project metrics are not in a valid format
    - 500: Audio file metrics are not in a valid format
    - 500: error: Metric data is not in a valid format
    - 500: error: Metric name is missing a required field
    - 500: error: Error: 500, An error has occured while updating the audio file metrics

RETURNS:
    - Str message: Audio metrics updated successfully

UPDATES:
    - Database: AudioFile
'''
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
    projectName = data['project_name']
    audio_file_name = data['audio_file_name']

    try:
        with db.session.begin_nested():
            # Check if project exists
            project = helper.find_project(projectName, researcher_id)
            if project is None:
                return jsonify({"error": "Project not found"}), 404

            # Check if audio file exists
            audio_file = AudioFile.query.filter(file_name=audio_file_name, project_name=projectName).first()
            if not audio_file:
                return jsonify({"error": "Audio file not found"}), 404

            # check if audio file metrics are in a valid format
            if not isinstance(audio_file.metrics, dict):
                return jsonify({"error": "Audio file metrics are not in a valid format"}), 500

            # check if project metrics are in a valid format
            if not isinstance(project.metrics, dict):
                return jsonify({"error": "Project metrics are not in a valid format"}), 500

            # Validate the structure of project metrics
            required_fields = ['min', 'max', 'minimum label', 'maximum label', 'description']
            validation_error = helper.validate_required_fields(data, required_fields)
            if validation_error:
                return validation_error
            for metric_name, metric_data in project.metrics.items():
                if not isinstance(metric_data, dict):
                    return jsonify({"error": "Metric {} is not in a valid format".format(metric_data)}), 500
                for field in required_fields:
                    if field not in metric_data:
                        return jsonify({"error": "Metric {} is missing required field {}".format(metric_name, field)}), 500

            # update audio file metrics from project metrics
            # this is to ensure metrics are consistent
            audio_file.metrics = project.metrics
            flag_modified(audio_file, "metrics")
            db.session.commit()
    # handle any errors that occur during the process
    except Exception as e:
            return jsonify({"error": "Error: 500, An error has occured while updating the audio file metrics"}), 500
    return jsonify({"message": "Audio metrics updated successfully"}), 200

'''
# this function is used to update the metrics of all audio files in a project
# this will be called when the project is set to Published

ARGS:
    - token: str
    - project_name: str

RESPONSE:
    - 200: audio_files
    - 400: Validation Error
    - 404: Researcher not found
    - 404: Project not found
    - 500: Project metrics are not in a valid format
    - 404: error: No audio files found for this project
    - 404: Audio file not found
    - 500: error: Metric data is not in a valid format
    - 500: error: Metric name is missing a required field
    - 500: error: Error: 500, An error has occured while updating the audio file metrics

RETURNS:
    - Str: Audio metrics updated successfully

UPDATES:
    - Database: AudioFile
'''
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
    projectName = data['project_name']

    try:
        with db.session.begin_nested():
            # Check if project exists
            project = helper.find_project(projectName, researcher_id)
            if project is None:
                return jsonify({"error": "Project not found"}), 404

            # check if audio file metrics are in a valid format
            if not isinstance(project.metrics, dict):
                return jsonify({"error": "Project metrics are not in a valid format"}), 500

            # get all audio files in the project
            all_audio_files = helper.get_all_audio_files(projectName, researcher_id)
            if not all_audio_files:
                return jsonify({"error": "No audio files found for this project"}), 404

            for audio_file_name in all_audio_files:
                # Check if audio file exists
                audio_file = AudioFile.query.filter(file_name=audio_file_name, project_name=projectName).first()
                if not audio_file:
                    return jsonify({"error": "Audio file not found"}), 404

                # Validate the structure of project metrics
                required_fields = ['min', 'max', 'minimum label', 'maximum label', 'description']
                for metric_name, metric_data in project.metrics.items():
                    if not isinstance(metric_data, dict):
                        return jsonify({"error": "Metric {} is not in a valid format".format(metric_data)}), 500
                    for field in required_fields:
                        if field not in metric_data:
                            return jsonify({"error": "Metric {} is missing required field {}".format(metric_name, field)}), 500

                # update audio file metrics from project metrics
                audio_file.metrics = project.metrics

            # Mark the project_list as modified and commit changes
            flag_modified(audio_file, "metrics")
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error: 500, An error has occured while updating the audio file metrics"}), 500
    return jsonify({"message": "Audio metrics updated successfully"}), 200


'''
# this routes returns all audio files

ARGS:
    - N/A

RESPONSE:
    - 200: audio_files

RETURNS:
    - Audio files in the format of list[dict]
    - If the list is empty, return empty list itself.

UPDATES:
    - N/A
'''
@audioBp.route('getAudioFiles', methods=['GET'])
def getAudioFiles():
    AudioFiles = AudioFile.query.all()
    audio_files = []
    for audio_file in AudioFiles:
        audio_files.append({
            "id": str(audio_file.id),
            "file_name": audio_file.file_name,
            "file_extension": audio_file.file_extension,
            "file_path": audio_file.file_path,
            "model": audio_file.model,
            "language": audio_file.language,
            "min_proficiency": str(audio_file.min_proficiency),
            "metrics": audio_file.metrics,
            "tags": audio_file.tags,
            "researcher_id": str(audio_file.researcher_id),
            "project_name": audio_file.project_name,
            "allocated_listeners": audio_file.allocated_listeners,
        })
    return jsonify({"audio_files": audio_files}), 200

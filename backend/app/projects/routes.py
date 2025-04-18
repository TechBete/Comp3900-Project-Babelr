from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, jwt_required, get_jwt_identity
from app.models import Researcher, Project, AudioFile, ProjectStatus
from flask import jsonify, request
from app import db
import app.helpers as helper
import os, uuid, shutil, logging
from sqlalchemy.orm.attributes import flag_modified
from app.projects import projectsBp

'''
# this route is used to create a new project for a researcher
# this is done by sending a post request to the /createProject endpoint
# the project name is passed in the request body
# the project name must be unique for each researcher
# the project name must not be empty
# the project name must not contain any special characters
# underscore or hyphen is allowed
# the project name must not be longer than 128 characters
# the project is created in the database and a directory is created for the project
# the project is updated in the researcher object and the project table

ARGS:
    - project_name: the name of the project
    - researcher_id: the id of the researcher
    
RESPONSE:
    - 200: Project created successfully
    - 400: Project name already exists
    - 400: Project Name data Field is empty
    - 400: Researcher ID data Field is empty
    - 400: Project name must be a non-empty string
    - 400: Cannot Create Project
    - 400: Project name contains invalid characters
    - 400: Project name is too long
    
    - 404: Researcher not found
    - 500: Project was unable to be created
    
RETURNS:
    - None
    
UPDATES:
    - Database: Researcher, Project tables
    
'''

@projectsBp.route('/createProject', methods=['POST'])
@jwt_required()
def createProject():
    data = request.json
    required_fields = ['project_name']
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id) # ensure type consistency
    
    # Validate researcher
    required_fields = ['researcher_id']
    validation_error = helper.validate_required_fields({'researcher_id': researcher_id}, required_fields) # validate researcher_id
    if validation_error:
        return validation_error

    projectName = data['project_name']
    researcherId = researcher_id

    # Check if researcher exists
    researcher = helper.is_researcher_id(researcherId)
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404  # disallow project creation if researcher does not exist

    # Ensure project list is not empty
    if researcher.project_list is None:
        researcher.project_list = []

    # ensure project name is not an empty string
    strippedProjectName = projectName.strip()
    if not projectName or len(strippedProjectName) == 0:
        return jsonify({"error": "Project name cannot be empty"}), 400
    
    # ensure project does not have invalid characters
    if helper.check_invalid_project_name(projectName):
        return jsonify({"error": "Project name contains invalid characters"}), 400
    
    # ensure project name is not too long
    if len(projectName) > 128:
        return jsonify({"error": "Project name is too long"}), 400
    
    # sanitize project name to remove special characters
    safeProjectName = helper.sanitize_project_name(projectName)
    if safeProjectName != projectName:
        return jsonify({"error": "Project name contains invalid characters"}), 400
    
    # use a transaction to ensure that the project is only created if the project list is updated successfully
    try:
        with db.session.begin_nested():
            # Check if project name already exists
            if any(project.get("project_name") == projectName for project in researcher.project_list):
                return jsonify({"error": "Project already exists"}), 400

            try:
                # create directory for project files in backend and docker.
                projectOwner = str(researcherId)
                projectPath = os.path.join("/app", "audioData")
                researcherPath = os.path.join(projectPath, projectOwner)
                projectDir = os.path.join(researcherPath, safeProjectName)
                
                if not os.path.exists(projectDir):
                    os.makedirs(projectDir)

            except Exception as e:
                return jsonify({"error": "Cannot Create Project, Project Path Already Exists"}), 400
            
            # create project in the database
            project = Project(
                id=uuid.uuid4(),
                project_name=projectName,
                path=projectDir,
                status=ProjectStatus.draft,  # default status
                tags=[],  # big set of tags used for each audio files in the project
                metrics={
                    # default values
                    # these are hard coded as per instructions but can be changed by the researcher
                    "Naturalness": {
                        "min": 1, 
                        "max": 5, 
                        "minimum label": "Robotic",
                        "maximum label": "Natural",
                        "description": "How natural the audio sounds"
                    },
                    "Intelligibility": {
                        "min": 1,
                        "max": 5,
                        "minimum label": "Unintelligible",
                        "maximum label": "Intelligible",
                        "description": "How easy it is to understand the audio"
                    },
                    "Clarity": {
                        "min": 1,
                        "max": 5,
                        "minimum label": "Unclear",
                        "maximum label": "Clear",
                        "description": "How clear the audio sounds"
                    },
                },
                creator_id=researcher.id,  # updated to include creator id (researcher id)
                creator_name=researcher.first_name,
                audio_list=[]
            )
            
            # update Researcher project list with project name
            researcher.project_list.append({
                                    "project_uuid": str(project.id),
                                    "project_name": projectName,
                                })

            flag_modified(project, "metrics")
            db.session.add(project)
            flag_modified(researcher, "project_list")
            db.session.add(researcher)
            # commit the changes to the database
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Project was unable to be created"}), 500

    return jsonify({"message": "Project created successfully"}) ## probably should not send back project list but for simplicities sake

'''
# this route is used to update the project name incase the researcher wants to change it
# this is done by sending a post request to the /updateProjectName endpoint
# the project name is passed in the request body
# the same project name rules apply as in the create project route

ARGS:
    - project_name: the name of the project
    - researcher_id: the id of the researcher
    
RESPONSE:
    - 200: Project updated successfully
    - 400: Project name must be a non-empty string
    - 400: Project name contains invalid characters
    - 400: Researcher ID data Field is empty
    - 400: Project Name data Field is empty
    - 400: Project name already exists
    - 400: Project name is too long
    - 400: Cannot Create Project
    - 404: Researcher not found
    - 500: Project was unable to be updated
    
RETURNS:
    - None

UPDATES:
    - Database: Researcher, Project tables
    - File System: Project directory

'''

# this route is to update the project name
@projectsBp.route('/renameProject', methods=['POST'])
@jwt_required()
def renameProject():
    data = request.json
    required_fields = ['project_name', 'new_project_name']
    validation_error = helper.validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error

    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher = helper.is_researcher_id(researcher_id)
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    projectName = data['project_name']
    newProjectName = data['new_project_name']
    
    # Project name checks:
    # ensure project name is not an empty string
    strippedOldName = projectName.strip()
    strippedNewName = newProjectName.strip()
    if not projectName or len(strippedOldName) == 0:
        return jsonify({"error": "Project name cannot be empty"}), 400
    if not newProjectName or len(strippedNewName) == 0:
        return jsonify({"error": "Project name cannot be empty"}), 400
    
    # ensure project does not have invalid characters
    if helper.check_invalid_project_name(projectName):
        return jsonify({"error": "Project name contains invalid characters"}), 400
    if helper.check_invalid_project_name(newProjectName):
        return jsonify({"error": "Project name contains invalid characters"}), 400
    
    # ensure project name is not too long
    if len(projectName) > 128 or len(newProjectName) > 128:
        return jsonify({"error": "Project name is too long"}), 400
    
    # sanitize project name to remove special characters
    safeProjectNameOld = helper.sanitize_project_name(projectName)
    if safeProjectNameOld != projectName:
        return jsonify({"error": "Project name contains invalid characters"}), 400 
    
    # sanitize new project name to remove special characters
    safeProjectNameNew = helper.sanitize_project_name(newProjectName)
    if safeProjectNameNew != newProjectName:
        return jsonify({"error": "Project name contains invalid characters"}), 400 
    
    # check if new project name already exists
    checkA = helper.find_project(safeProjectNameNew, researcher_id)
    # check researcher project list
    checkB = helper.find_researcher_project(safeProjectNameNew, researcher_id)
    if checkA or checkB:
        return jsonify({"error": "Project name already exists"}), 400
    
    try:
        with db.session.begin_nested():
            # Check if project exists and is owned by the researcher
            project = helper.find_project(safeProjectNameOld, researcher_id)
            # find project in the researcher project list
            researcherProject=helper.find_researcher_project(safeProjectNameOld, researcher_id)
            
            if not project or not researcherProject:
                return jsonify({"error": "Project not found"}), 404
            
            # create directory for project files in backend and docker.
            try:
                projectOwner = str(researcher_id)
                projectPath = os.path.join("/app", "audioData")
                researcherPath = os.path.join(projectPath, projectOwner)
                projectDir = os.path.join(researcherPath, safeProjectNameOld)
                
                if os.path.exists(projectDir):
                    os.rename(projectDir, os.path.join(researcherPath, safeProjectNameNew))
                    project.path = os.path.join(researcherPath, safeProjectNameNew) 
                    project.project_name = safeProjectNameNew
                    db.session.add(project)
                    
                    researcherProject.project_name = safeProjectNameNew
                    flag_modified(researcher, "project_list")
                    db.session.add(researcher)
                    
            except Exception as e:
                return jsonify({"error": "Project was unable to be updated"}), 500
        
            db.session.commit()    
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Project was unable to be updated"}), 500

    return jsonify({"message": "Project updated successfully"}), 200

'''
# this route is used to add tags to a project
# this is done by sending a post request to the /addProjectTags endpoint
# the project name and tags are passed in the request body
# same project name rules apply as in the create project route
# the tags are passed in as a list of strings
# the tags are added to the project in the database

ARGS:
    - project_name: the name of the project
    - tags: the tags to be added to the project
    
RESPONSE:
    - 200: Tags added successfully
    - 400: Project name must be a non-empty string
    - 400: Project name contains invalid characters
    - 400: Researcher ID data Field is empty
    - 400: Project Name data Field is empty
    - 400: Project is not in draft status
    - 400: Project name already exists
    - 400: Project name is too long
    - 404: Researcher not found
    - 404: Project not found
    - 500: Project was unable to be updated

RETURNS:
    - List of updated Tags
    
UPDATES:
    - Database: Project table

'''

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

    researcher = helper.is_researcher_id(researcher_id)
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    # Project name checks:
    projectName = data['project_name']
    # ensure project name is not an empty string
    stripped_project_name = projectName.strip()
    if not projectName or len(stripped_project_name) == 0:
        return jsonify({"error": "Project name cannot be empty"}), 400
    
    # ensure project does not have invalid characters
    if helper.check_invalid_project_name(projectName):
        return jsonify({"error": "Project name contains invalid characters"}), 400
    
    # ensure project name is not too long
    if len(projectName) > 128:
        return jsonify({"error": "Project name is too long"}), 400
    
    # sanitize project name to remove special characters
    safeProjectName = helper.sanitize_project_name(projectName)
    if safeProjectName != projectName:
        return jsonify({"error": "Project name contains invalid characters"}), 400
    
    try:
        with db.session.begin_nested():
            # Check if project exists
            project = helper.find_project(safeProjectName, researcher_id)
        
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow project update if project does not exist

            # check if project is set to draft
            if project.status != ProjectStatus.draft:
                return jsonify({"error": "Project is not in draft status"}), 400

            add_tags = data['tags']

            # add tags to the project
            #If tags is a string, split it into a list
            if isinstance(add_tags, str):
                added_tags = [tag.strip() for tag in add_tags.split(',')]  # Split by ',' and remove extra spaces
            elif isinstance(add_tags, list):
                added_tags = [str(tag).strip() for tag in add_tags]

            for tag in added_tags:
                if tag not in project.tags:  # Check if the tag is already in the list
                    project.tags.append(tag)  # Add the tag to the project
            
            flag_modified(project, "tags")
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Project was unable to be updated"}), 500

    return jsonify({"message": "Tags added successfully.", "Project Tags": project.tags}), 200

'''
# this route is used to remove tags from a project
# this is done by sending a post request to the /removeProjectTags endpoint
# the project name and tags are passed in the request body
# same project name rules apply as in the create project route
# the tags are passed in as a list of strings
# the tags are removed from the project in the database

ARGS:
    - project_name: the name of the project
    - tags: the tags to be removed from the project
    
RESPONSE:
    - 200: Tags removed successfully
    - 400: Project name must be a non-empty string
    - 400: Project name contains invalid characters
    - 400: Researcher ID data Field is empty
    - 400: Project Name data Field is empty
    - 400: Project is not in draft status
    - 400: Project name already exists
    - 400: Project name is too long
    - 404: Researcher not found
    - 404: Project not found
    - 500: Project was unable to be updated

RETURNS:
    - List of updated Tags
    
UPDATES:
    - Database: Project table
'''

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

    researcher = helper.is_researcher_id(researcher_id)
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    # Project name checks:
    projectName = data['project_name']
    stripped_project_name = projectName.strip()
    if not projectName or len(stripped_project_name) == 0:
        return jsonify({"error": "Project name cannot be empty"}), 400
    
    # ensure project does not have invalid characters
    if helper.check_invalid_project_name(projectName):
        return jsonify({"error": "Project name contains invalid characters"}), 400
    
    # ensure project name is not too long
    if len(projectName) > 128:
        return jsonify({"error": "Project name is too long"}), 400
    
    # sanitize project name to remove special characters
    safeProjectName = helper.sanitize_project_name(projectName)
    if safeProjectName != projectName:
        return jsonify({"error": "Project name contains invalid characters"}), 400
    
    try:
        with db.session.begin_nested():
            # Check if project exists
            project = helper.find_project(safeProjectName, researcher_id)
            
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow project update if project does not exist

            # check if project is set to draft
            if project.status != ProjectStatus.draft:
                return jsonify({"error": "Project is not in draft status"}), 400

            remove_tags = data['tags']

            # remove tages
            #If tags is a string, split it into a list
            if isinstance(remove_tags, str):
                removed_tags = [tag.strip() for tag in remove_tags.split(',')]  # Split by ',' and remove extra spaces
            elif isinstance(remove_tags, list):
                removed_tags = [str(tag).strip() for tag in removed_tags]

            for tag in removed_tags:
                if tag in project.tags:
                    project.tags.remove(tag)

            flag_modified(project, "tags")

            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Project was unable to be updated"}), 500

    return jsonify({"message": "Tags removed successfully.", "projects_list": researcher.project_list})

'''
# this route is used to search for a project by tag
# this is done by sending a post request to the /searchProjectByTag endpoint
# the tag is passed in the request body
# the tag is used to search for all projects that contain the tag
# the projects are returned in a list

ARGS:
    - tag: the tag to be searched for
    
RESPONSE:
    - 200: Projects found successfully
    - 200: No projects found
    - 400: Tag data Field is empty
    - 404: Researcher not found
    - 500: An error has occured while searching for projects
    
RETURNS:
    - List of projects that contain the tag
    
UPDATES:
    - None

'''

# this route is to search for a project by tag
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

    researcher = helper.is_researcher_id(researcher_id)
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    tags = data['tag']
    #If tags is a string, split it into a list
    if isinstance(tags, str):
        search_tags = [tag.strip() for tag in tags.split(',')]  # Split by ',' and remove extra spaces
    elif isinstance(tags, list):
        search_tags = [str(tag).strip() for tag in tags]
    
    try:
        # Check if project exists
        # nesting is a bit excessive 
        # a way to use less nesting can be done using the query filter:
        # projects_list = Project.query.filter(
        # Project.creator_id == researcher_id,or_(*[Project.tags.contains(cast([tag], JSONB)) for tag in search_tags])).all()
        # but this is more readable and easier to understand
        # without having to be at the mercy of sqlalchemy voodoo
        projects_list = []
        for projectEntry in researcher.project_list:
            projectName = projectEntry.get("project_name")
            if projectName:
                project = helper.find_project(projectName, researcher_id)
                if project is not None:
                    if any(tag in project.tags for tag in search_tags):
                        projects_list.append(project)
 
        # Check if any projects were found
        if not projects_list:   
            return jsonify({"message": "No projects found"}), 200
                                
    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while searching for projects"}), 500

    return jsonify({"projects_list": projects_list}), 200

'''
# this route is to change the project status
# this is done by sending a post request to the /updateProjectStatus endpoint
# the project name and status are passed in the request body
# the status is used to update the project status in the database
# the status can only be one of the following: draft or in_progress
# project name rules apply

ARGS:
    - project_name: the name of the project
    - status: the status to be set for the project
    
RESPONSE:
    - 200: Project status updated successfully
    - 400: Project name must be a non-empty string
    - 400: Project name contains invalid characters
    - 400: Researcher ID data Field is empty
    - 400: Project Name data Field is empty
    - 400: Project name already exists
    - 400: Project name is too long
    - 404: Researcher not found
    - 500: Project was unable to be updated

RETURNS:
    - None
    
UPDATES:
    - Database: Project table
    
'''

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

    researcher = helper.is_researcher_id(researcher_id)
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    # Project name checks:
    projectName = data['project_name']
    # ensure project name is not an empty string
    strippedProjectName = projectName.strip()
    if not projectName or len(strippedProjectName) == 0:
        return jsonify({"error": "Project name cannot be empty"}), 400
    
    # ensure project does not have invalid characters
    if helper.check_invalid_project_name(projectName):
        return jsonify({"error": "Project name contains invalid characters"}), 400
    
    # ensure project name is not too long
    if len(projectName) > 128:
        return jsonify({"error": "Project name is too long"}), 400
    
    # sanitize project name to remove special characters
    safeProjectName = helper.sanitize_project_name(projectName)
    if safeProjectName != projectName:
        return jsonify({"error": "Project name contains invalid characters"}), 400
    
    try:
        with db.session.begin_nested():
            # Check if project exists
            project = helper.find_project(projectName, researcher_id)
            
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow project update if project does not exist

            new_status = data['status']
            
            if new_status == '':
                return jsonify({"error": "Status cannot be empty"}), 400

            # Check if the new status is valid
            if new_status == "draft":
                project.status = ProjectStatus.draft
            
            elif new_status == "in_progress":
                project.status = ProjectStatus.in_progress
                
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.debug(e) # remove in production
        return jsonify({"error": "Project was unable to be updated"}), 500

    return jsonify({"message": "Project status updated successfully.", "projects_list": researcher.project_list})

'''
# this route returns all the projects of a researcher
# this is done by sending a get request to the /getProjects endpoint
# the researcher id is passed in the request header
# the researcher id is used to get all the projects of the researcher
# the projects are returned in a list

ARGS:
    - researcher_id: the id of the researcher
    
RESPONSE:
    - 200: Projects found successfully
    - 404: Researcher not found
    - 500: An error has occured while searching for projects

RETURNS:
    - List of projects that belong to the researcher

UPDATES:
    - None
    
'''
# this route is to get all the projects of a researcher
@projectsBp.route('/getProjects', methods=['GET'])
@jwt_required()
def getProjects():
    researcher_id = get_jwt_identity()
    researcher_id = uuid.UUID(researcher_id)

    researcher = helper.is_researcher_id(researcher_id)
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    return jsonify({"projects_list": researcher.project_list})

'''
# this route is to get a specific project of a researcher
# this is done by sending a post request to the /getProject endpoint
# the project name is passed in the request body
# the project name is used to get the project of the researcher
# the project object is returned in the response
# project name rules apply

ARGS:
    - project_name: the name of the project
    - researcher_id: the id of the researcher

RESPONSE:
    - 200: Project returned successfully
    - 400: Project name must be a non-empty string
    - 400: Project name contains invalid characters
    - 400: Researcher ID data Field is empty
    - 400: Project Name data Field is empty
    - 400: Project name already exists
    - 400: Project name is too long
    - 404: Researcher not found
    - 500: An error has occured while retrieving the project
    
RETURNS:
    - Project object in JSON format

UPDATES:
    - None

'''

# this route is to get a specific project of a researcher
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

    researcher_exists = helper.is_researcher_id(researcher_id)
    if not researcher_exists:
        return jsonify({"error": "Researcher not found"}), 404

    # Project name checks:
    projectName = data['project_name']
    # ensure project name is not an empty string
    strippedProjectName = projectName.strip()
    if not projectName or len(strippedProjectName) == 0:
        return jsonify({"error": "Project name cannot be empty"}), 400
    
    # ensure project does not have invalid characters
    if helper.check_invalid_project_name(projectName):
        return jsonify({"error": "Project name contains invalid characters"}), 400
    
    # ensure project name is not too long
    if len(projectName) > 128:
        return jsonify({"error": "Project name is too long"}), 400
    
    # sanitize project name to remove special characters
    safeProjectName = helper.sanitize_project_name(projectName)
    if safeProjectName != projectName:
        return jsonify({"error": "Project name contains invalid characters"}), 400
    
    try:
        with db.session.begin_nested():
            # Check if project exists
            project = helper.find_project(safeProjectName, researcher_id)
                        
            if project is None:
                return jsonify({"error": "Project not found"}), 404 # disallow returning project if project does not exist
    except Exception as e:
        logging.debug(e)
        return jsonify({"error": "Error: 500, An error has occured while retrieving the project"}), 500

    return jsonify({"project": project})

'''
# this route is to delete a project
# this is done by sending a post request to the /deleteProject endpoint
# the project name is passed in the request body
# the project name is used to delete the project of the researcher
# the project is deleted from the database and the project directory is deleted from the file system
# the project name rules apply
# Prompt the user to confirm deletion before proceeding
# if the project is deleted all the audio files in the project are deleted

ARGS:
    - project_name: the name of the project
    - researcher_id: the id of the researcher

RESPONSE:
    - 200: Project deleted successfully
- 400: Project name must be a non-empty string
    - 400: Project name contains invalid characters
    - 400: Researcher ID data Field is empty
    - 400: Project Name data Field is empty
    - 400: Project name already exists
    - 400: Project name is too long
    - 404: Researcher not found
    - 500: An error has occured while attempting to delete the project

RETURNS:
    - None

UPDATES:
    - Database: Researcher, Project table

'''

# this route is to delete a project
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

    researcher = helper.is_researcher_id(researcher_id)
    if not researcher:
        return jsonify({"error": "Researcher not found"}), 404

    # Project name checks:
    projectName = data['project_name']
    # ensure project name is not an empty string
    strippedProjectName = projectName.strip()
    if not projectName or len(strippedProjectName) == 0:
        return jsonify({"error": "Project name cannot be empty"}), 400
    
    # ensure project does not have invalid characters
    if helper.check_invalid_project_name(projectName):
        return jsonify({"error": "Project name contains invalid characters"}), 400
    
    # ensure project name is not too long
    if len(projectName) > 128:
        return jsonify({"error": "Project name is too long"}), 400
    
    # sanitize project name to remove special characters
    safeProjectName = helper.sanitize_project_name(projectName)
    if safeProjectName != projectName:
        return jsonify({"error": "Project name contains invalid characters"}), 400
    
    try:
        with db.session.begin_nested():
            # Check if project exists
            project = helper.find_project(safeProjectName, researcher_id)
            if project is None:
                return jsonify({"error": "Project not found"}), 404
            
            # Check if researcher owns project
            # double check researcher first name and id
            # project creator name and id should match researcher name and id
            if project.creator_name != researcher.first_name or project.creator_id != researcher.id:
                        return jsonify({"error": "You do not have permission to delete this project"}), 403
            
            # delete project directory
            if os.path.exists(project.path):
                try:
                    # delete the project directory from storage
                    # this will delete the directory and all its contents
                    shutil.rmtree(project.path)
                except OSError as e:
                    return jsonify({"error": "Failed to delete project files"}), 500 
                   
                #remove the project from the researcher project list
                researcherProject = helper.find_researcher_project(safeProjectName, researcher_id)
                
                # remove the project from the researcher project list
                if researcherProject:
                    # remove the project from the researcher project list
                    researcher.project_list.remove(researcherProject)
                
                # update audio tables to remove all files associated with the project
                # this will delete all the audio files associated with the project
                audio_files = helper.get_all_audio_files(safeProjectName, researcher_id)
                for audio_file in audio_files:
                    db.session.delete(audio_file)

                # delete the project from the database
                db.session.delete(project)
                
            flag_modified(researcher, "project_list")
            db.session.commit()
            
    except Exception as e:
        db.session.rollback()
        logging.debug(e)
        return jsonify({"error": "Project was unable to be deleted"}), 500

    return jsonify({"message": "Project deleted successfully"}), 200

# this route is to get the metrics for a specific project
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

# this route is to set the metrics for a project once a project has been created.
# this will set the metrics for the project
# this will be called when the project is created
# metrics should be a dictionary with the following keys:
# Naturalness, Intelligibility, Clarity hard coded as default values per instructions
# metric structure: metric name {min, max, minimum label, maximum label, description}
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

    researcher = helper.is_researcher_id(researcher_id)
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
            metrics_dict = {}
            for metric_name, metric_data in frontend_metrics.items():
                if not isinstance(metric_data, dict):
                    return jsonify({"error": "Metrics data must be a dictionary"}), 400
                
                # validate metric data
                required_fields = ['min', 'max', 'minimum label', 'maximum label', 'description']
                for field in required_fields:
                    if field not in metric_data:
                        return jsonify({"error": "Missing required field: {} for metric {}".format(field, metric_name)}), 400
                
                # Ensure min and max are numeric (in this case floats so as to handle future cases)
                try:
                    metric_data['min'] = float(metric_data['min'])
                    metric_data['max'] = float(metric_data['max'])
                except ValueError:
                    return jsonify({"error": "Min and max values must be numeric"}), 400
                
                # Ensure min is less than max
                if metric_data['min'] >= metric_data['max']:
                    return jsonify({"error": "Min value must be less than max value"}), 400
                
                # Add the metric to the dictionary
                metrics_dict[metric_name] = {
                    "min": metric_data['min'],
                    "max": metric_data['max'],
                    "minimum label": metric_data['minimum label'],
                    "maximum label": metric_data['maximum label'],
                    "description": metric_data['description']
                }
                
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


            # Validate and update metrics
            existing_metrics = project.get('metrics', {})
            if not isinstance(existing_metrics, dict):
                logging.error("Existing metrics must be a dictionary")
                return jsonify({"error": "Existing metrics must be a dictionary"}), 500
            for metric_name, metric_value in frontend_metrics.items():
                if metric_name in existing_metrics:
                   existing_metrics[metric_name].update({
                       "min": metric_value.get('min', existing_metrics[metric_name]['min']),
                        "max": metric_value.get('max', existing_metrics[metric_name]['max']),
                        "minimum label": metric_value.get('minimum label', existing_metrics[metric_name]['minimum label']),
                        "maximum label": metric_value.get('maximum label', existing_metrics[metric_name]['maximum label']),
                        "description": metric_value.get('description', existing_metrics[metric_name]['description'])
                   })
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
# this can only be called when a project status is set to 'draft'
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

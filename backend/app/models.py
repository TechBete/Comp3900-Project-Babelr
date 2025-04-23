from __future__ import annotations # get python to recognise classes before they are declared
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm.session import Session
from sqlalchemy import DDL, event
from functools import total_ordering
from typing import Self
import enum, uuid, logging
from flask import jsonify
from app import db


#========== 1. Python Enums ==========
class PermissionLevel(enum.Enum):
    admin = "admin"
    listener = "listener"
    researcher = "researcher"

@total_ordering
class ProficiencyLevel(enum.Enum):
    elementary = ("elementary", 0)
    limited_working = ("limited_working", 1)
    professional = ("professional", 2)
    native = ("native", 3)
    bilingual = ("bilingual", 4)

    def __init__(self, label, order):
        self._label = label
        self._order = order

    def __eq__(self, other):
        if isinstance(other, ProficiencyLevel):
            return self._order == other._order
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, ProficiencyLevel):
            return self._order < other._order
        return NotImplemented

    def __hash__(self):
        return hash(self.name)

class Gender(enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class ProjectStatus(enum.Enum):
    draft = "draft"
    in_progress = "in_progress"

# Define enums using postgresql.ENUM with create_type=True
# ========== 2. SQLAlchemy Enums ==========
proficiency_level_enum = ENUM(ProficiencyLevel, name='proficiencylevel', create_type=True)  # remove if necessary but otherwise keep to enforce enum in postgres
permission_level_enum = ENUM(PermissionLevel, name='permissionlevel', create_type=True)
gender_enum = ENUM(Gender, name='gender', create_type=True)
project_state_enum = ENUM(ProjectStatus, name='projectstate', create_type=True)

# Create the enum types in the SQL database
event.listen(
    db.metadata, 'before_create',
    DDL("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'proficiencylevel') THEN
            CREATE TYPE proficiencylevel AS ENUM ('elementary', 'limited_working', 'professional', 'native', 'bilingual');
        END IF;
    END $$;
    """)
)

event.listen(
    db.metadata, 'before_create',
    DDL("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'permissionlevel') THEN
            CREATE TYPE permissionlevel AS ENUM ('admin', 'listener', 'researcher');
        END IF;
    END $$;
    """)
)

event.listen(
    db.metadata, 'before_create',
    DDL("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender') THEN
            CREATE TYPE gender AS ENUM ('male', 'female', 'other');
        END IF;
    END $$;
    """)
)

event.listen(
    db.metadata, 'before_create',
    DDL("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'projectstate') THEN
            CREATE TYPE projectstate AS ENUM ('draft', 'in_progress');
        END IF;
    END $$;
    """)
)

# ========== 3. SQL DB Models ==========
class Researcher(db.Model):
    __tablename__        = "researchers"
    id                   = db.Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    first_name           = db.Column(db.String(128), nullable=False)
    last_name            = db.Column(db.String(128), nullable=False)
    email                = db.Column(db.String(128), nullable=False, unique=True)
    pw_hash              = db.Column(db.String(128)) # Argon2 hash string is 97 char long
    permission           = db.Column(permission_level_enum, nullable=False)

    project_list         = db.Column(db.JSON, default=list) # list of projects that researcher handles
    '''
    {
        "project_uuid": "uuid of project",
        "project_name": "test Project 1"
    }
    '''

    # demographic details
    date_of_birth        = db.Column(db.String(15), nullable=False)
    gender               = db.Column(gender_enum, default=Gender.other)
    country_of_residence = db.Column(db.String(30), nullable=False)
    education            = db.Column(db.String(128), nullable=False)
    organisation         = db.Column(db.String(128), nullable=False)

    # verification related details
    is_verified          = db.Column(db.Boolean, nullable=False)
    jti                  = db.Column(db.String(36))  # JWT ID to store in the database to prevent reuse and duplicate active tokens
    blindlogin           = db.Column(UUID(as_uuid=True)) # generate a random uuid for blind login
    first_time           = db.Column(db.Boolean, nullable=False)

class Project(db.Model):
    __tablename__ = "projects"
    id                   = db.Column(UUID(as_uuid=True), primary_key=True, nullable=False) # project's uuid
    project_name         = db.Column(db.String(128), nullable=False)
    path                 = db.Column(db.String(128), nullable=False) # project directory
    status               = db.Column(project_state_enum, nullable=False)
    tags                 = db.Column(db.JSON, default=list)
    metrics              = db.Column(db.JSON, nullable=False)
    '''
    {
        "metrics": {
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
        }
    }
    '''
    models               = db.Column(db.JSON, default=list) # list of models used in the project
    creator_id           = db.Column(UUID(as_uuid=True), nullable=False)
    creator_name         = db.Column(db.String(128), nullable=False)
    # list of audio file uuid to track all uploaded audio file under the project
    audio_list           = db.Column(db.JSON, default=list)
    total_listeners      = db.Column(db.Integer, default=0) # total number of listeners in the project
    listener_list        = db.Column(db.JSON, default=list) # list of all listener id within the project
    '''
    listener_list = [
        {
            "uuid of listener 1",
            "uuid of listener 2",
            ...,
        }
    ]
    '''

class Listener(db.Model):
    __tablename__ = "listeners"
    id                   = db.Column(UUID(as_uuid=True), primary_key=True, nullable=False) # listener's uuid
    first_name           = db.Column(db.String(128), nullable=False)
    last_name            = db.Column(db.String(128), nullable=False)
    email                = db.Column(db.String(128), nullable=False, unique=True)
    pw_hash              = db.Column(db.String(128), nullable=False) # Argon2 hash string is 97 char long
    permission           = db.Column(permission_level_enum, nullable=False)
    reward_points        = db.Column(db.Integer, nullable=False)

    # demographic details
    background_info      = db.Column(db.String(1024), default="") # 1024 char length string
    date_of_birth        = db.Column(db.String(15), nullable=False)
    gender               = db.Column(gender_enum, default=Gender.other)
    country_of_residence = db.Column(db.String(30), nullable=False)
    education            = db.Column(db.String(128), nullable=False)
    languages            = db.Column(db.JSON, default=list) # sets of language:proficiency

    is_verified          = db.Column(db.Boolean, nullable=False)
    jti                  = db.Column(db.String(36))  # JWT ID to store in the database to prevent reuse and duplicate active tokens
    blindlogin           = db.Column(UUID(as_uuid=True)) # generate a random uuid for blind login
    first_time           = db.Column(db.Boolean, nullable=False)

    ### Listener audio file details
    # uuid of currently allocated audio file (still evaluating)
    currently_assigned_audio  = db.Column(db.JSON, default=list) # list of audio uuid

    # list of audio uuid
    # after evaluation is done from listener side it moves from currently_assigned_audio to evaluation_history
    evaluation_history        = db.Column(db.JSON, default=list)

    # All allocated audio file for a user is stored here as a list of audio uuid
    # once finishing evaluation of currently_assigned_audio, first element of this list will be moved to currently_assigned_audio for evaluation
    allocated_audio_queue     = db.Column(db.JSON, default=list) # list of video IDs completed by the listener

    def assign_audio(self, audio: AudioFile):
        self.allocated_audio_queue.append(str(audio.id))
        flag_modified(self, "allocated_audio_queue")
        logging.debug(f"Listener {self} is allocated {self.allocated_audio_queue}")

    def is_qualified(self, audio: AudioFile) -> bool:
        """
        Check whether this listener is qualified to evaluate an audio file
        """
        for language in self.languages:
            if language['language'] == audio.language and ProficiencyLevel[language['proficiency'].lower()] >= audio.min_proficiency:
                return True
        return False

    def update_allocated_audio(self) -> list[AudioFile]:
        """
        This function is used to assign audio to a listener.

        This is done by checking the listener's language proficiency and matching it with the 
        audio's language requirements.

        The function takes in a listener object and checks their language proficiency.

        If the listener is qualified for the audio, the audio is assigned to the listener.

        The function also updates the audio's allocated listeners list.

        The function is called when a new listener is created.

        The function is called in the createListener function.
        """

        logging.debug('assiging qualified audio to the new listener')
        allAudio: list[AudioFile] = AudioFile.query.all()
        logging.debug(f"{allAudio}")
        qualifiedAudio = list()
        for audio in allAudio:
            logging.debug(f'audio {audio} requires {audio.min_proficiency} in {audio.language}')
            if self.is_qualified(audio):
                audio.assign_listener(self)
                self.assign_audio(audio)
                qualifiedAudio.append(audio)
                project = Project.query.filter_by(project_name=audio.project_name, creator_id=audio.researcher_id).first()
                if project:
                    if str(self.id) not in project.listener_list:
                        try:
                            project.listener_list.append(str(self.id))
                            flag_modified(project, "listener_list")
                            project.total_listeners += 1
                            db.session.commit()
                        except Exception as e:
                            db.session.rollback()
                            return jsonify({"error": "Failed to update project listener list"}), 500
                            
        return qualifiedAudio


class AudioFile(db.Model):
    __tablename__       = "audiofiles"
    id                  = db.Column(UUID(as_uuid=True), primary_key=True, nullable=False) # audio file uuid
    file_name           = db.Column(db.String(128), nullable=False)
    file_extension      = db.Column(db.String(30), nullable=False)
    file_path           = db.Column(db.String(128), nullable=False)
    model               = db.Column(db.String(128), nullable=False)
    language            = db.Column(db.String(128), nullable=False)
    min_proficiency     = db.Column(proficiency_level_enum, nullable=False)
    metrics             = db.Column(db.JSON, nullable=False)
    '''
    {
        "metrics": {
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
        }
    }
    '''
    tags                = db.Column(db.JSON, default=list)
    researcher_id       = db.Column(UUID(as_uuid=True),nullable=False)
    project_name        = db.Column(db.String(128), nullable=False)
    allocated_listeners = db.Column(db.JSON, default=list)
    '''
    {
        "listener_id": "uuid of listener",
        "Naturalness": 1,
        "Intelligibility": 5,
        "Clarity": 3
    }
    '''
    
    def __init__(self, id, file_name, file_extension, file_path, model, language, min_proficiency: str | ProficiencyLevel, metrics, tags, researcher_id, project_name) -> None:

        self.id = id
        self.file_name = file_name
        self.file_extension = file_extension
        self.file_path = file_path
        self.model = model
        self.language = language
        self.min_proficiency = ProficiencyLevel[min_proficiency.lower()] if isinstance(min_proficiency, str) else min_proficiency
        self.metrics = metrics
        self.tags = tags
        self.researcher_id = researcher_id
        self.project_name = project_name

        qualified = self.get_qualified_listeners()
        allocated_listeners = [{"listener_id": str(x.id)} for x in qualified]

        for listener in qualified:
            listener.assign_audio(self)
            project = Project.query.filter_by(project_name=self.project_name, creator_id=self.researcher_id).first()
            if project:
                    if str(listener.id) not in project.listener_list:
                        try:
                            project.listener_list.append(str(listener.id))
                            flag_modified(project, "listener_list")
                            project.total_listeners += 1
                            db.session.commit()
                        except Exception as e:
                            db.session.rollback()
                            return jsonify({"error": "Failed to update project listener list"}), 500
                            

        self.allocated_listeners = allocated_listeners

    def assign_listener(self, listener: Listener):
        listener_id = str(listener.id)
        if not any(isinstance(entry, dict) and entry.get("listener_id") == listener_id for entry in self.allocated_listeners):
            self.allocated_listeners.append({"listener_id": str(listener.id)})
            flag_modified(self, "allocated_listeners")
            logging.debug(f"Audio file {self} is allocated {self.allocated_listeners}")

    def get_qualified_listeners(self: AudioFile) -> list[Listener]:
        """
        Get a list of listeners qualified to evaluate this audio file.
        """
        all_listeners: list[Listener] = Listener.query.all()

        qualified_listeners = []

        for listener in all_listeners:
            if listener.is_qualified(self):
                logging.debug(f'{listener} is qualified')
                qualified_listeners.append(listener)

        logging.debug(f'qualified listeners: {qualified_listeners}')
        return qualified_listeners

    def set_allocated_listeners(self, new_allocated_listeners: list[str] | list[Listener] | list [str | Listener]):
        # Ensure all elements of the list is a stringified UUID
        new_allocated_listeners = [{"listener_id": str(l.id)} if isinstance(l, Listener) else l for l in new_allocated_listeners]
        self.allocated_listeners = new_allocated_listeners

    def update_allocated_listeners(self) -> list[Listener]:
        """
        Update the list of allocated listeners for this audio file, if there are changes in the listeners.

        Returns the updated list of listeners.
        """
        new_allocated_listeners = self.get_qualified_listeners()

        self.set_allocated_listeners(new_allocated_listeners)

        for listener in new_allocated_listeners:
            listener.assign_audio(self)
            project = Project.query.filter_by(project_name=self.project_name, creator_id=self.researcher_id).first()
            if project:
                    if str(listener.id) not in project.listener_list:
                        try:
                            project.listener_list.append(str(listener.id))
                            flag_modified(project, "listener_list")
                            project.total_listeners += 1
                            db.session.commit()
                        except Exception as e:
                            db.session.rollback()
                            return jsonify({"error": "Failed to update project listener list"}), 500
                            

        logging.debug(f"Audio file now is allocated {self.allocated_listeners}")
        return new_allocated_listeners


class RedeemShop(db.Model):
    __tablename__ = "redeem_shop"
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    point = db.Column(db.Integer, nullable=False)
    promo_code = db.Column(db.String(128), nullable=False)

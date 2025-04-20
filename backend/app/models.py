import enum, uuid
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy import DDL, event
from app import db
from functools import total_ordering

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
    
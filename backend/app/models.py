import enum, uuid
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy import DDL, event
from backend.app import db
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

# Define enums using postgresql.ENUM with create_type=True
# ========== 2. SQLAlchemy Enums ==========
proficiency_level_enum = ENUM(ProficiencyLevel, name='proficiencylevel', create_type=True)  # remove if necessary but otherwise keep to enforce enum in postgres
permission_level_enum = ENUM(PermissionLevel, name='permissionlevel', create_type=True)
gender_enum = ENUM(Gender, name='gender', create_type=True)

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

# ========== 3. SQL DB Models ==========
class Researcher(db.Model):
    __tablename__ = "researchers"
    id = db.Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    pw_hash = db.Column(db.String(128)) # Argon2 hash string is 97 char long
    permission = db.Column(permission_level_enum, nullable=False)
    organisation = db.Column(db.String(128))
    project_list = db.Column(db.JSON, default=list) # 128 char length array
    '''
    {
        "name": projectName,
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
    }
    '''
    uploaded_audio = db.Column(db.JSON, default=list) # 128 char length file ID array
    '''
    {
        "name": file.filename,
        "file_extension": filetype.guess(file_path).extension,
        "file_path": file_path,
        "allocated_listeners": [],
        "metrics": project["metrics"],
        "tags": [data['tags']]
        # subset of the project tags, these tags are specific tags for each audio file
    }
    '''
    is_verified = db.Column(db.Boolean, nullable=False)
    jti = db.Column(db.String(36))  # JWT ID to store in the database to prevent reuse and duplicate active tokens
    blindlogin = db.Column(UUID(as_uuid=True)) # generate a random uuid for blind login
    first_time = db.Column(db.Boolean, nullable=False)
    
    # one-to-one relationship of researchers-demographics
    demographic = db.relationship("ResearcherDemographic", back_populates="researcher", uselist=False)

class Listener(db.Model):
    __tablename__ = "listeners"
    id              = db.Column(UUID(as_uuid=True), primary_key=True, nullable=False) # listener's uuid
    first_name      = db.Column(db.String(128), nullable=False)
    last_name       = db.Column(db.String(128), nullable=False)
    email           = db.Column(db.String(128), nullable=False, unique=True)
    pw_hash         = db.Column(db.String(128), nullable=False) # Argon2 hash string is 97 char long
    permission      = db.Column(permission_level_enum, nullable=False)
    background_info = db.Column(db.String(1024), default="") # 1024 char length string
    reward_points   = db.Column(db.Integer)
    is_verified     = db.Column(db.Boolean, nullable=False)
    languages       = db.Column(db.JSON, default=list) # sets of language:proficiency
    jti             = db.Column(db.String(36))  # JWT ID to store in the database to prevent reuse and duplicate active tokens
    blindlogin      = db.Column(UUID(as_uuid=True)) # generate a random uuid for blind login
    assigned_audio  = db.Column(db.JSON, default=list) # list of video IDs assigned to the listener
    first_time      = db.Column(db.Boolean, nullable=False)

    # one-to-one relationship of listeners-demographics
    demographic = db.relationship("ListenerDemographic", back_populates="listener", uselist=False)

# consider updating the demographic model to polymorphic model to reduce redundancy
# in later iterations but this is fine for now

# ========== 4. Demographics Models ==========

# Demographics model for Listeners
class ListenerDemographic(db.Model):
    __tablename__ = "listener_demographics"
    id                   = db.Column(db.Integer, primary_key=True, nullable=False) # ID of demographic record
    listener_id          = db.Column(UUID(as_uuid=True), db.ForeignKey("listeners.id"), unique=True, nullable=False)
    listener             = db.relationship("Listener", back_populates="demographic")
    date_of_birth        = db.Column(db.String(15), nullable=False)
    gender               = db.Column(gender_enum)
    country_of_residence = db.Column(db.String(30), nullable=False)
    education            = db.Column(db.String(128), nullable=False)

# Demographics model for Researchers
class ResearcherDemographic(db.Model):
    __tablename__ = "researcher_demographics"
    id                   = db.Column(db.Integer, primary_key=True, nullable=False) # ID of demographic record
    researcher_id        = db.Column(UUID(as_uuid=True), db.ForeignKey("researchers.id"), unique=True, nullable=False)
    researcher           = db.relationship("Researcher", back_populates="demographic")
    date_of_birth        = db.Column(db.String(15), nullable=False)
    gender               = db.Column(gender_enum)
    country_of_residence = db.Column(db.String(30), nullable=False)
    education            = db.Column(db.String(128), nullable=False)

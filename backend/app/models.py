import enum, uuid
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy import DDL, event
from app import db

#========== 1. Python Enums ==========
class PermissionLevel(enum.Enum):
    admin = "admin"
    listener = "listener"
    researcher = "researcher"

class ProficiencyLevel(enum.Enum):
    elementary = "elementary"
    limited_working = "limited_working"
    professional = "professional"
    native = "native"
    bilingual = "bilingual"

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
    uploaded_audio = db.Column(db.JSON, default=list) # 128 char length file ID array
    is_verified = db.Column(db.Boolean, nullable=False)
    jti = db.Column(db.String(36))  # JWT ID to store in the database to prevent reuse and duplicate active tokens
    blindlogin = db.Column(UUID(as_uuid=True)) # generate a random uuid for blind login

class Listener(db.Model):
    __tablename__ = "listeners"
    id = db.Column(UUID(as_uuid=True), primary_key=True, nullable=False) # listener's uuid
    first_name = db.Column(db.String(128), nullable=False)
    last_name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=False, unique=True)
    pw_hash = db.Column(db.String(128), nullable=False) # Argon2 hash string is 97 char long
    permission = db.Column(permission_level_enum, nullable=False)
    background_info = db.Column(db.String(1024), default="") # 1024 char length string
    reward_points = db.Column(db.Integer)
    is_verified = db.Column(db.Boolean, nullable=False)
    languages = db.Column(db.JSON, default=list) # sets of language:proficiency
    jti = db.Column(db.String(36))  # JWT ID to store in the database to prevent reuse and duplicate active tokens
    blindlogin = db.Column(UUID(as_uuid=True)) # generate a random uuid for blind login
    assigned_audio = db.Column(db.JSON, default=list) # list of video IDs assigned to the listener
    completed_audio = db.Column(db.JSON, default=list) # list of video IDs completed by the listener
    
    # one-to-one relationship of listeners-demographics
    demographic = db.relationship("Demographic", back_populates="listener", uselist=False)

class Demographic(db.Model):
    __tablename__ = "demographics"
    id = db.Column(db.Integer, primary_key=True, nullable=False) # ID of demographic record
    listener_id = db.Column(UUID(as_uuid=True), db.ForeignKey("listeners.id"))
    listener = db.relationship("Listener", back_populates="demographic")
    date_of_birth = db.Column(db.String(15), nullable=False)
    gender = db.Column(gender_enum)
    country_of_residence = db.Column(db.String(30), nullable=False)
    education = db.Column(db.String(128), nullable=False)

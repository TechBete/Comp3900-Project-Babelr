import os, uuid, enum
from flask import Flask, request, jsonify, render_template_string # render_template_string is used to render HTML, can be removed once frontend is inplace
from password import PasswordHash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY, UUID, ENUM
from sqlalchemy.exc import IntegrityError
from sqlalchemy import DDL, event
from dotenv import load_dotenv


app = Flask(__name__)
load_dotenv()

# database config
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}/{os.environ.get('POSTGRES_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


def validate_required_fields(data, required_fields):
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    return None
    
@app.route('/registerListener', methods=['POST'])
def createListener():
    data = request.json
    required_fields = ['first_name', 'last_name', 'email', 'pw']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    # Validate and process languages_proficiency
    valid_proficiency_levels = [level.value for level in ProficiencyLevel]
    if 'languages_proficiency' in data:
        invalid_levels = [
            proficiency for proficiency in data['languages_proficiency']
            if proficiency not in valid_proficiency_levels
        ]
        if invalid_levels:
            return jsonify({"error": f"Invalid proficiency levels: {', '.join(invalid_levels)}"}), 400

        # Convert valid strings to ProficiencyLevel enum values
        data['languages_proficiency'] = [
            proficiency_level_enum(proficiency)
            for proficiency in data['languages_proficiency']
        ]
    user = Listener(
        id=data.get('id', uuid.uuid4()),  # generate a random uuid if not provided
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        pw_hash=PasswordHash.hash_password(str(data['pw'])),
        permission=permission_level_enum.LISTENER,
        background_info=data.get('background_info', ''),
        reward_points=0,
        languages_list=data.get('languages_list', []),
        languages_proficiency=data.get('languages_proficiency', [])
    )
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database integrity error: " + str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    return jsonify({"Registration Successful"})    
    
@app.route('/registerResearcher', methods=['POST'])
def createResearcher():
    data = request.json
    required_fields = ['first_name', 'last_name', 'email', 'pw']
    validation_error = validate_required_fields(data, required_fields)
    if validation_error:
        return validation_error
    user = Researcher(
        id=data.get('id', uuid.uuid4()),    # generate a random uuid if not provided
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        pw_hash=PasswordHash.hash_password(str(data['pw'])),
        permission=permission_level_enum.RESEARCHER,
        organisation=data.get('organisation', ''),
        uploaded_video=data.get('uploaded_video', [])
    )
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"error": "Database integrity error: " + str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    return jsonify({"Registration Successful"})



# Define the enum type creation SQL 
#create_proficiencylevel_enum = DDL(
#    "CREATE TYPE proficiencylevel AS ENUM ('elementary', 'limited_working', 'professional', 'native', 'bilingual');"
#)

class PermissionLevel(enum.Enum):
    ADMIN = "admin"
    LISTENER = "listener"
    RESEARCHER = "researcher"

class ProficiencyLevel(enum.Enum):
    ELEMENTARY = "elementary"
    LIMITED = "limited_working"
    PROFESSIONAL = "professional"
    NATIVE = "native"
    BILINGUAL = "bilingual"


class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

# Define enums using postgresql.ENUM with create_type=True
proficiency_level_enum = ENUM(
    ProficiencyLevel,
    name='proficiencylevel',
    create_type=True
)

permission_level_enum = ENUM(
    PermissionLevel,
    name='permissionlevel',
    create_type=True
)
gender_enum = ENUM(
    Gender,
    name='gender',
    create_type=True
    )

class Researcher(db.Model):
    __tablename__ = "researchers"
    id = db.Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30))
    email = db.Column(db.String(30))
    pw_hash = db.Column(db.String(128)) # Argon2 hash string is 97 char long, 
    permission = db.Column(permission_level_enum, nullable=False)
    organisation = db.Column(db.String(30))
    uploaded_video = db.Column(ARRAY(db.String(68))) # 68 char length file ID array
    gender = db.Column(gender_enum)

class Listener(db.Model):
    __tablename__ = "listeners"
    id = db.Column(UUID(as_uuid=True), primary_key=True, nullable=False) # listener's uuid
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    pw_hash = db.Column(db.String(128), nullable=False) # Argon2 hash string is 97 char long
    permission = db.Column(permission_level_enum, nullable=False)
    background_info = db.Column(db.String(100))
    reward_points = db.Column(db.Integer)
    languages_list = db.Column(ARRAY(db.String(8)))
    languages_proficiency = db.Column(ARRAY(proficiency_level_enum))

    # one-to-one relationship of listeners-demographics
    demographic = db.relationship("Demographic", back_populates="listener", uselist=False)
    
class Demographic(db.Model):
    __tablename__ = "demographics"
    id = db.Column(db.Integer, primary_key=True, nullable=False) # ID of demographic record
    listener_id = db.Column(UUID(as_uuid=True), db.ForeignKey("listeners.id"))
    listener = db.relationship("Listener", back_populates="demographic")
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(gender_enum)
    country_of_residence = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(68), nullable=False)
    education = db.Column(db.String(68), nullable=False)


@app.route('/getListeners', methods=['GET'])
def getListeners():
    users = Listener.query.all()
    return jsonify([user.__dict__ for user in users])

@app.route('/getResearchers', methods=['GET'])
def getResearchers():
    users = Researcher.query.all()
    return jsonify([user.__dict__ for user in users])

@app.route('/') # testing route to render HTML form; remove once frontend is inplace
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
            <li><a href="/addListener">Register Listener</a></li>
            <li><a href="/addResearcher">Register Researcher</a></li>
        </ul>
    </body>
    </html>
    ''')
@app.route('/addListener', methods=['GET'])
def addListener():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add Listener</title>
    </head>
    <body>
        <h1>Add Listener</h1>
        <form action="/registerListener" method="post">
            <label for="first_name">First Name:</label><br>
            <input type="text" id="first_name" name="first_name"><br>
            <label for="last_name">Last Name:</label><br>
            <input type="text" id="last_name" name="last_name"><br>
            <label for="email">Email:</label><br>
            <input type="email" id="email" name="email"><br>
            <label for="pw">Password:</label><br>
            <input type="password" id="pw" name="pw"><br>
            <label for="background_info">Background Info:</label><br>
            <input type="text" id="background_info" name="background_info"><br>
            <label for="languages_list">Languages List (comma-separated):</label><br>
            <input type="text" id="languages_list" name="languages_list"><br>
            <label for="languages_proficiency">Languages Proficiency (comma-separated):</label><br>
            <input type="text" id="languages_proficiency" name="languages_proficiency"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                jsonData.languages_list = jsonData.languages_list.split(',').map(item => item.trim());
                const validProficiencyLevels = ["elementary", "limited_working", "professional", "native", "bilingual"];
                jsonData.languages_proficiency = jsonData.languages_proficiency.split(',').map(item => item.trim());
                if (!jsonData.languages_proficiency.every(level => validProficiencyLevels.includes(level))) {
                    alert("Invalid proficiency level. Valid levels are: elementary, limited_working, professional, native, bilingual");
                    return;
                }
                fetch('/registerListener', {
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

@app.route('/addResearcher', methods=['GET'])
def addResearcher():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add Researcher</title>
    </head>
    <body>
        <h1>Add Researcher</h1>
        <form action="/registerResearcher" method="post">
            <label for="first_name">First Name:</label><br>
            <input type="text" id="first_name" name="first_name"><br>
            <label for="last_name">Last Name:</label><br>
            <input type="text" id="last_name" name="last_name"><br>
            <label for="email">Email:</label><br>
            <input type="email" id="email" name="email"><br>
            <label for="pw">Password:</label><br>
            <input type="password" id="pw" name="pw"><br>
            <label for="organisation">Organisation:</label><br>
            <input type="text" id="organisation" name="organisation"><br>
            <label for="uploaded_video">Uploaded Video (comma-separated):</label><br>
            <input type="text" id="uploaded_video" name="uploaded_video"><br>
            <button type="submit">Submit</button>
        </form>
        <script>
            document.querySelector('form').addEventListener('submit', function (e) {
                e.preventDefault();
                const formData = new FormData(e.target);
                const jsonData = Object.fromEntries(formData);
                jsonData.uploaded_video = jsonData.uploaded_video.split(',').map(item => item.trim());
                fetch('/registerResearcher', {
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

if __name__ == '__main__':
    # The db.create_all() call is inside the if __name__ == '__main__': block,
    # which means it will only run when the script is executed directly.
    # This can cause issues when deploying the application in a production environment.
    # find a way to resolve if necessary.
    with app.app_context():
        # initialize the database
        db.create_all() 
    # host='0.0.0.0' to make the server accessible from outside the container
    app.run(debug=True, host='0.0.0.0', port=8016)


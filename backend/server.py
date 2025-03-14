from flask import Flask, request, jsonify, render_template_string # render_template_string is used to render HTML, can be removed once frontend is inplace
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY
from dotenv import load_dotenv
import os, enum
import backend.password as hashPword 

app = Flask(__name__)
load_dotenv()

# database config
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}/{os.environ.get('POSTGRES_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# model
    
@app.route('/registerListener', methods=['POST'])
def create_user():
    data = request.json
    user = Listener(id=data['id'], first_name=data['first_name'], last_name=data['last_name'], email=data['email'], pw_hash=hashPword.PasswordHash(str(data['pw'])), permission=PermissionLevel.LISTENER, background_info=data['background_info'], reward_points=0, languages_list=data['languages_list'], laguages_proficiency=data['laguages_proficiency'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"Message: User id": user.id})    
    
@app.route('/registerResearcher', methods=['POST'])
def create_user():
    data = request.json
    user = Researcher(id=data['id'], first_name=data['first_name'], last_name=data['last_name'], email=data['email'], pw_hash=hashPword.PasswordHash(str(data['pw'])), permission=PermissionLevel.RESEARCHER, organisation=data['organisation'], uploaded_video=[])
    db.session.add(user)
    db.session.commit()
    return jsonify({"Message: User id": user.id})

class PermissionLevel(enum.Enum):
    ADMIN = "admin"
    LISTENER = "listener"
    RESEARCHER = "researcher"

class ProficiencyLevel(enum.Enum):
    ELEMENTRY = "elementry"
    LIMITED = "limited_working"
    PROFESSIONAL = "professional"
    NATIVE = "native"
    BILINGUAL = "bilingual"

class Researcher(db.Model):
    __tablename__ = "researchers"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30))
    email = db.Column(db.String(30))
    pw_hash = db.Column(db.String(68)) # Argon2, 64 bytes + 4 bytes of salt
    permission = db.Column(db.Enum(PermissionLevel))
    organisation = db.Column(db.String(30))
    uploaded_video = db.Column(ARRAY(db.String(68))) # 68 char length file ID array

class Listener(db.Model):
    __tablename__ = "listeners"
    id = db.Column(db.Integer, primary_key=True, nullable=False) # listener's uuid
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    pw_hash = db.Column(db.String(68), nullable=False) # Argon2, 64 bytes + 4 bytes of salt
    permission = db.Column(db.Enum(PermissionLevel), nullable=False)
    background_info = db.Column(db.String(100))
    reward_points = db.Column(db.Integer)
    languages_list = db.Column(ARRAY(db.String(3)))
    laguages_proficiency = db.Column(ARRAY(db.Enum(ProficiencyLevel)))

    # one-to-one relationship of listeners-demographics
    demographic = db.relationship("Demographic", back_populates="listener", uselist=False)


class Demographic(db.Model):
    __tablename__ = "demographics"
    id = db.Column(db.Integer, primary_key=True, nullable=False) # ID of demographic record
    listener_id = db.Column(db.Integer, db.ForeignKey("listeners.id"))
    listener = db.relationship("Listener", back_populates="demographic")
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.Integer, nullable=False)
    country_of_residence = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(68), nullable=False)
    education = db.Column(db.String(68), nullable=False)

@app.route('/addusers', methods=['POST'])
def create_user():
    data = request.json
    user = User(name=data['name'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"Message: User id": user.id})

@app.route('/getListeners', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "name": user.name, "email": user.email} for user in users])@app.route('/')

@app.route('/getResearchers', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "name": user.name, "email": user.email} for user in users])

@app.route('/') # testing route to render HTML form; remove once frontend is inplace
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Add User</title>
    </head>
    <body>
        <h1>Add User</h1>
        <form id="userForm">
            <label for="name">Name:</label>
            <input type="text" id="name" name="name" required>
            <br>
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>
            <br>
            <button type="submit">Add User</button>
        </form>

        <script>
            document.getElementById('userForm').addEventListener('submit', function(event) {
                event.preventDefault();

                const name = document.getElementById('name').value;
                const email = document.getElementById('email').value;

                fetch('http://localhost:8016/addusers', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ name: name, email: email })
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
                    alert('User added successfully!');
                })
                .catch((error) => {
                    console.error('Error:', error);
                    alert('Failed to add user.');
                });
            });
        </script>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    with app.app_context():
        # intialize the database
        db.create_all() 
    # host='0.0.0.0' to make the server accessible from outside the container
    app.run(debug=True, host='0.0.0.0', port=8016)


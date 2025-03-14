from flask import Flask, request, jsonify, render_template_string # render_template_string is used to render HTML, can be removed once frontend is inplace
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import backend.password as hashword 

app = Flask(__name__)
load_dotenv()

# database config
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@{os.environ.get('POSTGRES_HOST')}/{os.environ.get('POSTGRES_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

hashword.PasswordHash(str('password'))
# model
class userListener(db.Model):
    __tablename__ = 'Listener'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    Role = db.Column(db.String(50))

class userResearcher(db.Model):
    __tablename__ = 'Researcher'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    Role = db.Column(db.String(50))
    
@app.route('/registerListener', methods=['POST'])
def create_user():
    data = request.json
    user = userListener(name=data['name'], email=data['email'], Role = 'Listener')
    db.session.add(user)
    db.session.commit()
    return jsonify({"Message: User id": user.id})    
    
@app.route('/registerResearcher', methods=['POST'])
def create_user():
    data = request.json
    user = userResearcher(name=data['name'], email=data['email'], Role = 'Researcher')
    db.session.add(user)
    db.session.commit()
    return jsonify({"Message: User id": user.id})

    
@app.route('/addusers', methods=['POST']) # testing route for registering users in database
def create_user():
    data = request.json
    user = User(name=data['name'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"Message: User id": user.id})

@app.route('/getListeners', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "name": user.name, "email": user.email} for user in users])

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

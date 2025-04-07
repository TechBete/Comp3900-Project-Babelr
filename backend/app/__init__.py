from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
import logging

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # Configure logging - remove for final production
    logging.basicConfig(level=logging.DEBUG)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, supports_credentials=True, 
         origins=["http://localhost:3000", "https://localhost:8016", "*"])

    # Register blueprints
    from app.auth.routes import authBp
    from app.projects.routes import projectsBp
    from app.researchers.routes import researchersBp
    from app.listeners.routes import userBp
#   from app.admin.routes import adminBp     commenting out for now
    
    # Register the blueprints with their respective URL prefixes
    app.register_blueprint(authBp, url_prefix='/auth')
    app.register_blueprint(researchersBp, url_prefix='/researcher')
    app.register_blueprint(userBp, url_prefix='/listener')
    app.register_blueprint(projectsBp, url_prefix='/projects')
#   app.register_blueprint(adminBp, url_prefix='/admin') commenting out for now

    return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, supports_credentials=True, 
         origins=["http://localhost:3000", "https://localhost:8016", "*"])

    # Register blueprints
    from Babelr.auth.routes import authBp
    from Babelr.projects.routes import projectsBp
    from Babelr.researchers.routes import researchersBp
    from Babelr.listeners.routes import userBp
#   from Babelr.admin.routes import adminBp     commenting out for now
    from Babelr.main.routes import mainBp
    
    # Register the blueprints with their respective URL prefixes
    app.register_blueprint(authBp, url_prefix='/auth')
    app.register_blueprint(researchersBp, url_prefix='/researcher')
    app.register_blueprint(userBp, url_prefix='/listener')
    app.register_blueprint(projectsBp, url_prefix='/projects')
#   app.register_blueprint(adminBp, url_prefix='/admin') commenting out for now
    app.register_blueprint(mainBp, url_prefix='/')

    return app

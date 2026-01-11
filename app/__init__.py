from flask import Flask 
from .config import Config
from .extensions import db, jwt, limiter

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    
    #create database tables
    with app.app_context():
        db.create_all()

    from .auth import auth_bp
    app.register_blueprint(auth_bp,url_prefix="/auth")

    return app
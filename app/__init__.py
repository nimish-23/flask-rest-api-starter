from flask import Flask 
from .config import Config
from .extensions import db, jwt, limiter
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    # Initialize Flask-Migrate (like openbuild)
    migrate = Migrate(app, db)
    
    # Import models AFTER migrate initialization
    from .models import User

    from .routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    
    from .routes import user_bp
    app.register_blueprint(user_bp, url_prefix="/users")

    return app
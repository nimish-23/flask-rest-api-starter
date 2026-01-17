from flask import Flask 
from .config import Config
from .extensions import db, jwt, limiter
from flask_migrate import Migrate
from .errors import BadRequestError, UnauthorizedError
from flask import jsonify

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

    @app.errorhandler(BadRequestError)
    def handle_bad_request(error):
        return jsonify({"error": "Bad Request", "message": str(error)}), 400

    @app.errorhandler(UnauthorizedError)
    def handle_unauthorized(error):
        return jsonify({"error": "Unauthorized", "message": str(error)}), 401

    return app
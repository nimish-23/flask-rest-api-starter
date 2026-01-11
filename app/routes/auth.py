from flask import Blueprint, request, jsonify
from app.extensions import db, limiter
from app.models.user import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from app.schemas import RegistrationSchema, LoginSchema

from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
@limiter.limit("3 per minute")
def register():
    try:
        data = RegistrationSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

    email = data.get("email")
    password = data.get("password")
    username = data.get("username")

    # Check if user already exists
    if db.session.query(User).filter((User.email == email) | (User.username == username)).first():
        return jsonify({"error": "User already exists"}), 409

    hashed_password = generate_password_hash(password)

    new_user = User(email=email, password=hashed_password, username=username)
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    try:
        data = LoginSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

    email = data.get("email")
    password = data.get("password")

    user = db.session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token, "token_type": "Bearer"}), 200

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify({"message": "Logged out successfully"}), 200

from flask import Blueprint, request, jsonify
from app.extensions import db, limiter
from app.models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.auth.schemas import RegistrationSchema , LoginSchema
from marshmallow import ValidationError

auth_bp = Blueprint("auth",__name__)


#check input data(json) -> validate data -> check if user already exists -> create user-> hash password -> add to db -> return success message(json)
@auth_bp.route("/register",methods=["POST"])
@limiter.limit("3 per minute")
def register():

    # here We take input data, validate it, and convert it into clean backend-safe data.
    try:
        data = RegistrationSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify({"error":e.messages}),400

    email = data.get("email")
    password = data.get("password")
    username = data.get("username")

    user = User.query.filter((User.email==email) | (User.username==username)).first()
    if user:
        return jsonify({"error":"User already exists"}),409

    hashed_password = generate_password_hash(password)

    new_user = User(email=email,password=hashed_password,username=username)
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}),500

    return jsonify({"message":"User registered successfully"}),201

@auth_bp.route("/login",methods=["POST"])
@limiter.limit("5 per minute")
def login():

    try:
        data = LoginSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify({"error":e.messages}),400

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error":"Invalid credentials"}),401

    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token":access_token,"token_type":"Bearer"}),200

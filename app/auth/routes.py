from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint("auth",__name__)

@auth_bp.route("/register",methods=["POST"])
def register():
    return "Register"

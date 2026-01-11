from flask import Blueprint, request, jsonify
from app.extensions import db, jwt, limiter
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint("user", __name__)

@user_bp.route("/me", methods=["GET"])
@jwt_required()
@limiter.limit("10 per minute")
def get_me():
    
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "username":user.username,
        "email":user.email
    }), 200
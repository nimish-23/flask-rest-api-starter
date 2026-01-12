from flask import Blueprint, request, jsonify
from app.extensions import db, jwt, limiter
from app.models.user import User
from app.schemas import UpdateUserSchema
from app.utils.decorators import admin_required
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash

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

@user_bp.route("/me", methods=["DELETE"])
@jwt_required()
@limiter.limit("10 per minute")
def delete_me():
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200

@user_bp.route("/me", methods=["PATCH"])
@jwt_required()
@limiter.limit("10 per minute")
def patch_me():
    """Update current user's profile (username, email, and/or password)"""
    current_user_id = get_jwt_identity()
    
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Validate request data with UpdateUserSchema (all fields optional)
    try:
        data = UpdateUserSchema().load(request.json)
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

    # Update username if provided
    if "username" in data:
        # Check if username already exists (excluding current user)
        existing_user = User.query.filter_by(username=data["username"]).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({"error": "Username already taken"}), 409
        user.username = data["username"]
    
    # Update email if provided
    if "email" in data:
        # Check if email already exists (excluding current user)
        existing_user = User.query.filter_by(email=data["email"]).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({"error": "Email already taken"}), 409
        user.email = data["email"]
    
    # Update password if provided (MUST be hashed!)
    if "password" in data:
        user.password = generate_password_hash(data["password"])

    db.session.commit()

    return jsonify({
        "message": "Profile updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }), 200


@user_bp.route("", methods=["GET"])  # "" makes it /users (blueprint prefix)
@admin_required  # Includes @jwt_required() inside the decorator
@limiter.limit("10 per minute")
def list_users():
    """List all users (admin only) with pagination"""
    # Get pagination parameters
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    
    # Limit the maximum results per page
    if limit > 100:
        limit = 100
    
    # Query users with pagination
    pagination = User.query.paginate(page=page, per_page=limit, error_out=False)
    
    users = [{
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat() if user.created_at else None
    } for user in pagination.items]
    
    return jsonify({
        "users": users,
        "total": pagination.total,
        "page": page,
        "limit": limit,
        "total_pages": pagination.pages
    }), 200
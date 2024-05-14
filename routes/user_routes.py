import os
from typing import Dict, Any, List, Optional, Tuple

import bcrypt
from flask import Blueprint, request, jsonify, Response
from werkzeug.datastructures import FileStorage

from config import ALLOWED_IMAGE_EXTENSIONS, db, SALT
from db import User
from routes.auth_wrapper import auth_required
from utils import allowed_file, validate_user_name, validate_user_role, map_user, get_response_image, filename_secure, \
    validate_password

user_bp = Blueprint("user_routes", __name__)


@user_bp.route("/upload_image", methods=["POST"])
@auth_required
def upload_image(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    file: FileStorage = request.files['file']

    if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        try:
            user: User = User.query.filter_by(id=current_user["id"]).first()
            filename: str = filename_secure(file)
            file.save(os.path.join("images", filename))

            if os.path.exists(user.image_path):
                os.remove(user.image_path)

            user.image_path = "images/" + filename
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Unhandled exception: {e}"}), 500

    return jsonify({"type": "Validation Error", "message": "The image type is not allowed"}), 400


@user_bp.route("/change_user_name", methods=["POST"])
@auth_required
def change_user_name(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        data: Dict[str, Any] = request.get_json()
        validation: Dict[str, Any] = validate_user_name(data["name"])

        if validation["isValid"]:
            user: User = User.query.filter_by(id=current_user["id"]).first()
            user.name = data["name"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@user_bp.route("/change_user_role", methods=["POST"])
@auth_required
def change_user_role(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        data: Dict[str, Any] = request.get_json()
        validation: Dict[str, Any] = validate_user_role(data["role"])

        if validation["isValid"]:
            user: User = User.query.filter_by(id=current_user["id"]).first()
            user.role = data["role"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@user_bp.route("/change_user_password", methods=["POST"])
@auth_required
def change_user_password(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        data: Dict[str, Any] = request.get_json()
        user: User = User.query.filter_by(id=current_user["id"]).first()
        validation: Dict[str, Any] = validate_password(data["currentPassword"], data["newPassword"], data["confirmPassword"], user.password)

        if validation["isValid"]:
            user.password = bcrypt.hashpw(data["newPassword"].encode(), SALT).decode()
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}", "type": "error"}), 500


@user_bp.route("/update_notifications_token", methods=["POST"])
@auth_required
def update_notifications_token(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        data: Dict[str, Any] = request.get_json()
        user: User = User.query.filter_by(id=current_user["id"]).first()
        user.push_notifications_token = data["token"]
        db.session.commit()
        return jsonify({"message": "Success"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}", "type": "error"}), 500


@user_bp.route("/search_users", methods=["GET"])
@auth_required
def search_users(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        search_query: str = request.args.get("search_query")
        users: List[User] = User.query.filter(
            User.name.ilike(f'%{search_query}%'),
            User.id != current_user["id"]
        ).all()
        return jsonify([map_user(x.id) for x in users]), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@user_bp.route("/get_user", methods=["GET"])
@auth_required
def get_user(_: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        user_id: int = int(request.args.get("user_id"))
        user: Optional[User] = User.query.filter_by(id=user_id).first()
        if user:
            response: Dict[str, Any] = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "image": get_response_image(user.image_path),
                "role": user.role
            }
        else:
            response: Dict[str, Any] = {
                "id": user_id,
                "name": "UnknownUser",
                "email": "UnknownEmail",
                "image": get_response_image("images/deleted_user.png"),
                "role": "NA"
            }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@user_bp.route("/delete_user", methods=["DELETE"])
@auth_required
def delete_user(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        user: User = User.query.filter_by(id=current_user["id"]).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Success"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500

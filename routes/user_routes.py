import os

import bcrypt
from flask import Blueprint, request, jsonify

from config import ALLOWED_IMAGE_EXTENSIONS, db, SALT
from db import User
from routes.auth_wrapper import auth_required
from utils import allowed_file, validate_user_name, validate_user_role, map_user, get_response_image, filename_secure, \
    validate_password

user_bp = Blueprint("user_routes", __name__)


@user_bp.route("/upload_image", methods=["POST"])
@auth_required
def upload_image(current_user):
    file = request.files['file']

    if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        try:
            user = User.query.filter_by(id=current_user["id"]).first()
            filename = filename_secure(file)
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
def change_user_name(current_user):
    try:
        data = request.get_json()
        validation = validate_user_name(data["name"])

        if validation["isValid"]:
            user = User.query.filter_by(id=current_user["id"]).first()
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
def change_user_role(current_user):
    try:
        data = request.get_json()
        validation = validate_user_role(data["role"])

        if validation["isValid"]:
            user = User.query.filter_by(id=current_user["id"]).first()
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
def change_user_password(current_user):
    try:
        data = request.get_json()
        user = User.query.filter_by(id=current_user["id"]).first()
        validation = validate_password(data["currentPassword"], data["newPassword"], data["confirmPassword"], user.password)

        if validation["isValid"]:
            user.password = bcrypt.hashpw(data["newPassword"].encode(), SALT).decode()
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}", "type": "error"}), 500


@user_bp.route("/search_users", methods=["GET"])
@auth_required
def search_users(current_user):
    try:
        search_query = request.args.get("search_query")
        users = User.query.filter(
            User.name.ilike(f'%{search_query}%'),
            User.id != current_user["id"]
        ).all()
        return jsonify([map_user(x.id) for x in users]), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@user_bp.route("/get_user", methods=["GET"])
@auth_required
def get_user(current_user):
    try:
        user_id = request.args.get("user_id")
        user = User.query.filter_by(id=user_id).first()
        if user:
            response = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "image": get_response_image(user.image_path),
                "role": user.role
            }
        else:
            return {
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
def delete_user(current_user):
    try:
        user = User.query.filter_by(id=current_user["id"]).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Success"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500

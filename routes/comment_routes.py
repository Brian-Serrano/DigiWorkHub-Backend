from flask import Blueprint, request, jsonify

from config import db
from db import TaskComment
from routes.auth_wrapper import auth_required
from utils import validate_comment, int_list_to_string, map_comments, string_to_int_list, \
    remove_item_from_stringed_list, add_item_from_stringed_list

comment_bp = Blueprint("comment_routes", __name__)


@comment_bp.route("/add_comment_to_task", methods=["POST"])
@auth_required
def add_comment_to_task(current_user):
    try:
        data = request.get_json()
        validation = validate_comment(data["description"])

        if validation["isValid"]:
            new_comment = TaskComment(
                description=data["description"],
                user_id=current_user["id"],
                task_id=data["taskId"],
                reply_id=int_list_to_string(data["replyId"]),
                mentions_id=int_list_to_string(data["mentionsId"])
            )
            db.session.add(new_comment)
            db.session.commit()
            return jsonify(map_comments(new_comment)), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@comment_bp.route("/like_comment", methods=["POST"])
@auth_required
def like_comment(current_user):
    try:
        data = request.get_json()
        comment_to_like = TaskComment.query.filter_by(comment_id=data["commentId"]).first()
        if current_user["id"] in string_to_int_list(comment_to_like.likes_id):
            comment_to_like.likes_id = remove_item_from_stringed_list(comment_to_like.likes_id, current_user["id"])
        else:
            comment_to_like.likes_id = add_item_from_stringed_list(comment_to_like.likes_id, current_user["id"])
        db.session.commit()
        return jsonify({"message": "Success"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@comment_bp.route("/delete_comment", methods=["DELETE"])
@auth_required
def delete_comment(current_user):
    try:
        comment_to_delete = TaskComment.query.filter_by(comment_id=request.args.get("comment_id")).first()
        if current_user["id"] == comment_to_delete.user_id:
            db.session.delete(comment_to_delete)
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "You cannot delete comment that you did not send."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500

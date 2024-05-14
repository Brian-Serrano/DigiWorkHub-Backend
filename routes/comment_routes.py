from typing import Dict, Any, Tuple

from flask import Blueprint, request, jsonify, Response

from config import db
from db import TaskComment, Task
from routes.auth_wrapper import auth_required
from utils import validate_comment, int_list_to_string, map_comments, string_to_int_list, \
    remove_item_from_stringed_list, add_item_from_stringed_list, send_notification_to_assignees

comment_bp = Blueprint("comment_routes", __name__)


@comment_bp.route("/add_comment_to_task", methods=["POST"])
@auth_required
def add_comment_to_task(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the request body
        data: Dict[str, Any] = request.get_json()
        # validate the comment description
        validation: Dict[str, Any] = validate_comment(data["description"])
        # get the task the comment attached, used for sending push notifications to the creator and assignees of task
        task: Task = Task.query.filter_by(task_id=data["taskId"]).first()

        # check if the comment is valid
        if validation["isValid"]:
            # create the comment
            new_comment: TaskComment = TaskComment(
                description=data["description"],
                user_id=current_user["id"],
                task_id=data["taskId"],
                reply_id=int_list_to_string(data["replyId"]),
                mentions_id=int_list_to_string(data["mentionsId"])
            )
            # save the comment to the database
            db.session.add(new_comment)

            # send push notifications to the creator and assignees of task
            send_notification_to_assignees(
                "Sent Comment",
                current_user["name"] + " have sent comment to task.",
                [*string_to_int_list(task.assignee), task.creator_id]
            )

            # commit/apply the sent comment
            db.session.commit()
            # return the created comment as response
            return jsonify(map_comments(new_comment)), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@comment_bp.route("/like_comment", methods=["POST"])
@auth_required
def like_comment(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the request body
        data: Dict[str, Any] = request.get_json()
        # get the comment to like
        comment_to_like: TaskComment = TaskComment.query.filter_by(comment_id=data["commentId"]).first()

        # check if the user already liked the comment
        if current_user["id"] in string_to_int_list(comment_to_like.likes_id):
            # if yes unlike it
            comment_to_like.likes_id = remove_item_from_stringed_list(comment_to_like.likes_id, current_user["id"])
        else:
            # if no like it
            comment_to_like.likes_id = add_item_from_stringed_list(comment_to_like.likes_id, current_user["id"])

        # commit/apply the liked comment
        db.session.commit()
        # return message
        return jsonify({"message": "Success"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@comment_bp.route("/delete_comment", methods=["DELETE"])
@auth_required
def delete_comment(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the comment to delete
        comment_to_delete: TaskComment = TaskComment.query.filter_by(comment_id=request.args.get("comment_id")).first()

        # check if the user want to delete the comment is the sender of comment
        if current_user["id"] == comment_to_delete.user_id:
            # delete the comment
            db.session.delete(comment_to_delete)
            # commit/apply the deleted comment
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "You cannot delete comment that you did not send."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500

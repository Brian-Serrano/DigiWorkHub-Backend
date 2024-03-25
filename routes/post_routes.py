import os
from datetime import datetime

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from config import db, ALLOWED_FILE_EXTENSIONS, ALLOWED_IMAGE_EXTENSIONS
from db import Task, TaskComment, Message, Subtask, Checklist, Attachment, User
from routes.auth_wrapper import auth_required
from utils import list_to_string, string_to_date, validate_task, validate_comment, validate_message, string_to_int_list, \
    validate_due, validate_name, validate_description, validate_assignee, validate_subtask, validate_checklist, \
    allowed_file, remove_item_from_stringed_list, add_item_from_stringed_list, map_checklists, map_subtasks, \
    map_comments, map_attachments, validate_user_name, validate_user_role

post_bp = Blueprint("post_routes", __name__)


@post_bp.route("/add_task", methods=["POST"])
@auth_required
def add_task(user):
    try:
        data = request.get_json()
        validation = validate_task(data["title"], data["description"], string_to_date(data["due"]), data["assignee"])

        if validation["isValid"]:
            new_task = Task(
                title=data["title"],
                description=data["description"],
                priority=data["priority"],
                due=string_to_date(data["due"]),
                creator_id=user["id"],
                type=data["type"],
                assignee=list_to_string(data["assignee"])
            )
            db.session.add(new_task)
            db.session.commit()
            return jsonify({"message": validation["message"]}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/add_comment_to_task", methods=["POST"])
@auth_required
def add_comment_to_task(user):
    try:
        data = request.get_json()
        validation = validate_comment(data["description"])

        if validation["isValid"]:
            new_comment = TaskComment(
                description=data["description"],
                user_id=user["id"],
                task_id=data["taskId"]
            )
            db.session.add(new_comment)
            db.session.commit()
            return jsonify(map_comments(new_comment)), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/message_user", methods=["POST"])
@auth_required
def message_user(user):
    try:
        data = request.get_json()
        validation = validate_message(data["title"], data["description"])

        if validation["isValid"]:
            new_message = Message(
                sender_id=user["id"],
                receiver_id=data["receiverId"],
                title=data["title"],
                description=data["description"]
            )
            db.session.add(new_message)
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/change_task_status", methods=["POST"])
@auth_required
def change_task_status(user):
    try:
        data = request.get_json()
        task_to_change = Task.query.filter_by(task_id=data["taskId"]).first()
        if user["id"] in string_to_int_list(task_to_change.assignee):
            task_to_change.status = data["status"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only assignees can edit status"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/edit_assignees", methods=["POST"])
@auth_required
def edit_assignees(user):
    try:
        data = request.get_json()
        task_to_change = Task.query.filter_by(task_id=data["taskId"]).first()
        validation = validate_assignee(data["assignee"], user["id"], task_to_change.creator_id)

        if validation["isValid"]:
            task_to_change.assignee = list_to_string(data["assignee"])
            db.session.commit()
            return jsonify({"message": validation["message"]}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/change_due_date", methods=["POST"])
@auth_required
def change_due_date(user):
    try:
        data = request.get_json()
        task_to_change = Task.query.filter_by(task_id=data["taskId"]).first()
        validation = validate_due(string_to_date(data["due"]), user["id"], task_to_change.creator_id)

        if validation["isValid"]:
            task_to_change.due = string_to_date(data["due"])
            db.session.commit()
            return jsonify({"message": validation["message"]}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/change_priority", methods=["POST"])
@auth_required
def change_priority(user):
    try:
        data = request.get_json()
        task_to_change = Task.query.filter_by(task_id=data["taskId"]).first()
        if task_to_change.creator_id == user["id"]:
            task_to_change.priority = data["priority"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only task creator can edit priority"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/change_type", methods=["POST"])
@auth_required
def change_type(user):
    try:
        data = request.get_json()
        task_to_change = Task.query.filter_by(task_id=data["taskId"]).first()
        if task_to_change.creator_id == user["id"]:
            task_to_change.type = data["type"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only task creator can edit type"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/change_name", methods=["POST"])
@auth_required
def change_name(user):
    try:
        data = request.get_json()
        task_to_change = Task.query.filter_by(task_id=data["taskId"]).first()
        validation = validate_name(data["title"], user["id"], task_to_change.creator_id)

        if validation["isValid"]:
            task_to_change.title = data["title"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/change_description", methods=["POST"])
@auth_required
def change_description(user):
    try:
        data = request.get_json()
        task_to_change = Task.query.filter_by(task_id=data["taskId"]).first()
        validation = validate_description(data["description"], user["id"], task_to_change.creator_id)
        if validation["isValid"]:
            task_to_change.description = data["description"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/add_subtask", methods=["POST"])
@auth_required
def add_subtask(user):
    try:
        data = request.get_json()
        task = Task.query.filter_by(task_id=data["taskId"]).first()
        validation = validate_subtask(data["description"], string_to_date(data["due"]), data["assignee"], user["id"], task.creator_id, task.assignee)

        if validation["isValid"]:
            new_subtask = Subtask(
                task_id=data["taskId"],
                description=data["description"],
                priority=data["priority"],
                due=string_to_date(data["due"]),
                creator_id=user["id"],
                type=data["type"],
                assignee=list_to_string(data["assignee"])
            )
            db.session.add(new_subtask)
            db.session.commit()
            return jsonify(map_subtasks(new_subtask)), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/add_checklist", methods=["POST"])
@auth_required
def add_checklist(user):
    try:
        data = request.get_json()
        task = Task.query.filter_by(task_id=data["taskId"]).first()
        validation = validate_checklist(data["description"], data["assignee"], user["id"], task.creator_id, task.assignee)

        if validation["isValid"]:
            new_checklist = Checklist(
                task_id=data["taskId"],
                user_id=user["id"],
                description=data["description"],
                assignee=list_to_string(data["assignee"])
            )
            db.session.add(new_checklist)
            db.session.commit()
            return jsonify(map_checklists(new_checklist)), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/upload_attachment", methods=["POST"])
@auth_required
def upload_attachment(user):
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 500
    file = request.files['file']
    if file.filename == '':
        return jsonify({"type": "Validation Error", "message": "No selected file"}), 400
    if file and allowed_file(file.filename, ALLOWED_FILE_EXTENSIONS):
        try:
            filename = secure_filename(datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + '.' + file.filename.rsplit('.', 1)[1])
            file.save(os.path.join("attachments", filename))
            new_attachment = Attachment(
                task_id=int(request.form["taskId"]),
                user_id=user["id"],
                attachment_path="attachments/" + filename,
                file_name=file.filename
            )
            db.session.add(new_attachment)
            db.session.commit()
            return jsonify(map_attachments(new_attachment)), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Unhandled exception: {e}"}), 500

    return jsonify({"type": "Validation Error", "message": "The file type is not allowed"}), 400


@post_bp.route("/upload_image", methods=["POST"])
@auth_required
def upload_image(user):
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 500
    file = request.files['file']
    if file.filename == '':
        return jsonify({"type": "Validation Error", "message": "No selected file"}), 400
    if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
        try:
            user_obj = User.query.filter_by(id=user["id"]).first()
            filename = secure_filename(datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + '.' + file.filename.rsplit('.', 1)[1])
            file.save(os.path.join("images", filename))

            if os.path.exists(user_obj.image_path):
                os.remove(user_obj.image_path)

            user_obj.image_path = "images/" + filename
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Unhandled exception: {e}"}), 500

    return jsonify({"type": "Validation Error", "message": "The image type is not allowed"}), 400


@post_bp.route("/change_subtask_description", methods=["POST"])
@auth_required
def change_subtask_description(user):
    try:
        data = request.get_json()
        task_to_change = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()
        validation = validate_description(data["description"], user["id"], task_to_change.creator_id)
        if validation["isValid"]:
            task_to_change.description = data["description"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/change_subtask_priority", methods=["POST"])
@auth_required
def change_subtask_priority(user):
    try:
        data = request.get_json()
        task_to_change = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()
        if task_to_change.creator_id == user["id"]:
            task_to_change.priority = data["priority"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only task creator can edit priority"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/change_subtask_due_date", methods=["POST"])
@auth_required
def change_subtask_due_date(user):
    try:
        data = request.get_json()
        task_to_change = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()
        validation = validate_due(string_to_date(data["due"]), user["id"], task_to_change.creator_id)

        if validation["isValid"]:
            task_to_change.due = string_to_date(data["due"])
            db.session.commit()
            return jsonify({"message": validation["message"]}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/edit_subtask_assignees", methods=["POST"])
@auth_required
def edit_subtask_assignees(user):
    try:
        data = request.get_json()
        task_to_change = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()
        validation = validate_assignee(data["assignee"], user["id"], task_to_change.creator_id)

        if validation["isValid"]:
            task_to_change.assignee = list_to_string(data["assignee"])
            db.session.commit()
            return jsonify({"message": validation["message"]}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/change_subtask_type", methods=["POST"])
@auth_required
def change_subtask_type(user):
    try:
        data = request.get_json()
        task_to_change = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()
        if task_to_change.creator_id == user["id"]:
            task_to_change.type = data["type"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only task creator can edit type"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/change_subtask_status", methods=["POST"])
@auth_required
def change_subtask_status(user):
    try:
        data = request.get_json()
        task_to_change = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()
        if user["id"] in string_to_int_list(task_to_change.assignee):
            task_to_change.status = data["status"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only assignees can edit status"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/toggle_checklist", methods=["POST"])
@auth_required
def toggle_checklist(user):
    try:
        data = request.get_json()
        checklist_to_toggle = Checklist.query.filter_by(checklist_id=data["checklistId"]).first()
        if user["id"] in string_to_int_list(checklist_to_toggle.assignee):
            checklist_to_toggle.is_checked = data["check"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only assignees can edit checklist"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/like_comment", methods=["POST"])
@auth_required
def like_comment(user):
    try:
        data = request.get_json()
        comment_to_like = TaskComment.query.filter_by(comment_id=data["commentId"]).first()
        if user["id"] in string_to_int_list(comment_to_like.likes_id):
            comment_to_like.likes_id = remove_item_from_stringed_list(comment_to_like.likes_id, user["id"])
        else:
            comment_to_like.likes_id = add_item_from_stringed_list(comment_to_like.likes_id, user["id"])
        db.session.commit()
        return jsonify({"message": "Success"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/change_user_name", methods=["POST"])
@auth_required
def change_user_name(user):
    try:
        data = request.get_json()
        validation = validate_user_name(data["name"])

        if validation["isValid"]:
            user = User.query.filter_by(id=user["id"]).first()
            user.name = data["name"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@post_bp.route("/change_user_role", methods=["POST"])
@auth_required
def change_user_role(user):
    try:
        data = request.get_json()
        validation = validate_user_role(data["role"])

        if validation["isValid"]:
            user = User.query.filter_by(id=user["id"]).first()
            user.role = data["role"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500

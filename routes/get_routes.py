from flask import Blueprint, jsonify, request, send_from_directory
from sqlalchemy import desc

from db import Task, User, TaskComment, Message, Subtask, Checklist, Attachment
from routes.auth_wrapper import auth_required
from utils import string_to_int_list, map_tasks, map_sent_messages, map_received_messages, date_to_string, map_comments, \
    map_user, map_subtasks, map_checklists, map_attachments, get_response_image

get_bp = Blueprint("get_routes", __name__)


@get_bp.route("/get_tasks", methods=["GET"])
@auth_required
def get_tasks(user):
    try:
        tasks = Task.query.filter(Task.assignee.like(f"%{user['id']}%")).all()
        return jsonify([*map(map_tasks, tasks)]), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@get_bp.route("/get_task", methods=["GET"])
@auth_required
def get_task(user):
    try:
        task_id = request.args.get("task_id")
        task = Task.query.filter_by(task_id=task_id).first()
        assignee_ids = string_to_int_list(task.assignee)
        comments = TaskComment.query.filter_by(task_id=task_id).all()
        subtasks = Subtask.query.filter_by(task_id=task_id).all()
        checklists = Checklist.query.filter_by(task_id=task_id).all()
        attachments = Attachment.query.filter_by(task_id=task_id).all()
        mapped_comments = [*map(map_comments, comments)]
        mapped_subtasks = [*map(map_subtasks, subtasks)]
        mapped_checklists = [*map(map_checklists, checklists)]
        mapped_attachments = [*map(map_attachments, attachments)]
        response = {
            "taskId": task.task_id,
            "title": task.title,
            "description": task.description,
            "due": date_to_string(task.due),
            "priority": task.priority,
            "status": task.status,
            "type": task.type,
            "sentDate": date_to_string(task.date_sent),
            "assignees": [map_user(x) for x in assignee_ids],
            "creator": map_user(task.creator_id),
            "comments": mapped_comments,
            "subtasks": mapped_subtasks,
            "checklists": mapped_checklists,
            "attachments": mapped_attachments
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@get_bp.route("/get_sent_messages", methods=["GET"])
@auth_required
def get_sent_messages(user):
    try:
        messages = Message.query.filter_by(sender_id=user["id"]).order_by(desc(Message.date_sent)).all()
        response = [*map(map_sent_messages, messages)]
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@get_bp.route("/get_received_messages", methods=["GET"])
@auth_required
def get_received_messages(user):
    try:
        messages = Message.query.filter_by(receiver_id=user["id"]).order_by(desc(Message.date_sent)).all()
        response = [*map(map_received_messages, messages)]
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@get_bp.route("/get_message", methods=["GET"])
@auth_required
def get_message(user):
    try:
        message = Message.query.filter_by(message_id=request.args.get("message_id")).first()
        response = {
            "messageId": message.message_id,
            "title": message.title,
            "description": message.description,
            "sentDate": date_to_string(message.date_sent),
            "sender": map_user(message.sender_id),
            "receiver": map_user(message.receiver_id),
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@get_bp.route("/get_created_tasks", methods=["GET"])
@auth_required
def get_created_tasks(user):
    try:
        tasks = Task.query.filter_by(creator_id=user["id"]).all()
        return jsonify([*map(map_tasks, tasks)]), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@get_bp.route("/search_users", methods=["GET"])
@auth_required
def search_users(user):
    try:
        search_query = request.args.get("search_query")
        users = User.query.filter(
            User.name.ilike(f'%{search_query}%'),
            User.id != user["id"]
        ).all()
        return jsonify([map_user(x.id) for x in users]), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@get_bp.route("/download_attachment", methods=["GET"])
@auth_required
def download_attachment(user):
    try:
        return send_from_directory("attachments", request.args.get("attachment_name"), as_attachment=True), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@get_bp.route("/get_user", methods=["GET"])
@auth_required
def get_user(user):
    try:
        user = User.query.filter_by(id=request.args.get("user_id")).first()
        response = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "image": get_response_image(user.image_path),
            "role": user.role
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500

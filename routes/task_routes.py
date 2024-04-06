from flask import Blueprint, request, jsonify

from config import db
from db import Task, TaskComment, Subtask, Checklist, Attachment
from routes.auth_wrapper import auth_required
from utils import validate_task, string_to_date, int_list_to_string, string_to_int_list, validate_assignee, \
    validate_due, validate_name, validate_description, map_tasks, map_comments, map_subtasks, map_checklists, \
    map_attachments, date_to_string, map_user

task_bp = Blueprint("task_routes", __name__)


@task_bp.route("/add_task", methods=["POST"])
@auth_required
def add_task(current_user):
    try:
        data = request.get_json()
        validation = validate_task(data["title"], data["description"], string_to_date(data["due"]), data["assignee"])

        if validation["isValid"]:
            new_task = Task(
                title=data["title"],
                description=data["description"],
                priority=data["priority"],
                due=string_to_date(data["due"]),
                creator_id=current_user["id"],
                type=data["type"],
                assignee=int_list_to_string(data["assignee"])
            )
            db.session.add(new_task)
            db.session.commit()
            return jsonify(map_tasks(new_task)), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/change_task_status", methods=["POST"])
@auth_required
def change_task_status(current_user):
    try:
        data = request.get_json()
        task_to_change = Task.query.filter_by(task_id=data["taskId"]).first()
        if current_user["id"] in string_to_int_list(task_to_change.assignee):
            task_to_change.status = data["status"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only assignees can edit status"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/edit_assignees", methods=["POST"])
@auth_required
def edit_assignees(current_user):
    try:
        data = request.get_json()
        task_to_change = Task.query.filter_by(task_id=data["taskId"]).first()
        validation = validate_assignee(data["assignee"], current_user["id"], task_to_change.creator_id)

        if validation["isValid"]:
            task_to_change.assignee = int_list_to_string(data["assignee"])
            db.session.commit()
            return jsonify({"message": validation["message"]}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/change_due_date", methods=["POST"])
@auth_required
def change_due_date(current_user):
    try:
        data = request.get_json()
        task_to_change = Task.query.filter_by(task_id=data["taskId"]).first()
        validation = validate_due(string_to_date(data["due"]), current_user["id"], task_to_change.creator_id)

        if validation["isValid"]:
            task_to_change.due = string_to_date(data["due"])
            db.session.commit()
            return jsonify({"message": validation["message"]}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/change_priority", methods=["POST"])
@auth_required
def change_priority(current_user):
    try:
        data = request.get_json()
        task_to_change = Task.query.filter_by(task_id=data["taskId"]).first()
        if task_to_change.creator_id == current_user["id"]:
            task_to_change.priority = data["priority"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only task creator can edit priority"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/change_type", methods=["POST"])
@auth_required
def change_type(current_user):
    try:
        data = request.get_json()
        task_to_change = Task.query.filter_by(task_id=data["taskId"]).first()
        if task_to_change.creator_id == current_user["id"]:
            task_to_change.type = data["type"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only task creator can edit type"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/change_name", methods=["POST"])
@auth_required
def change_name(current_user):
    try:
        data = request.get_json()
        task_to_change = Task.query.filter_by(task_id=data["taskId"]).first()
        validation = validate_name(data["title"], current_user["id"], task_to_change.creator_id)

        if validation["isValid"]:
            task_to_change.title = data["title"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/change_description", methods=["POST"])
@auth_required
def change_description(current_user):
    try:
        data = request.get_json()
        task_to_change = Task.query.filter_by(task_id=data["taskId"]).first()
        validation = validate_description(data["description"], current_user["id"], task_to_change.creator_id)
        if validation["isValid"]:
            task_to_change.description = data["description"]
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/delete_task", methods=["DELETE"])
@auth_required
def delete_task(current_user):
    try:
        task_id = request.args.get("task_id")
        task_to_delete = Task.query.filter_by(task_id=task_id).first()
        if current_user["id"] == task_to_delete.creator_id:
            db.session.delete(task_to_delete)
            db.session.query(TaskComment).filter_by(task_id=task_id).delete()
            db.session.query(Subtask).filter_by(task_id=task_id).delete()
            db.session.query(Checklist).filter_by(task_id=task_id).delete()
            db.session.query(Attachment).filter_by(task_id=task_id).delete()
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only task creator can delete tasks."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/get_tasks", methods=["GET"])
@auth_required
def get_tasks(current_user):
    try:
        tasks = Task.query.filter(Task.assignee.like(f"%{current_user['id']}%")).all()
        return jsonify([map_tasks(x) for x in tasks]), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/get_task", methods=["GET"])
@auth_required
def get_task(current_user):
    try:
        task_id = request.args.get("task_id")
        task = Task.query.filter_by(task_id=task_id).first()
        assignee_ids = string_to_int_list(task.assignee)
        comments = TaskComment.query.filter_by(task_id=task_id).all()
        subtasks = Subtask.query.filter_by(task_id=task_id).all()
        checklists = Checklist.query.filter_by(task_id=task_id).all()
        attachments = Attachment.query.filter_by(task_id=task_id).all()
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
            "comments": [map_comments(x) for x in comments],
            "subtasks": [map_subtasks(x) for x in subtasks],
            "checklists": [map_checklists(x) for x in checklists],
            "attachments": [map_attachments(x) for x in attachments]
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/get_created_tasks", methods=["GET"])
@auth_required
def get_created_tasks(current_user):
    try:
        tasks = Task.query.filter_by(creator_id=current_user["id"]).all()
        return jsonify([map_tasks(x) for x in tasks]), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500

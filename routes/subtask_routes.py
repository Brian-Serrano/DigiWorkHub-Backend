from flask import Blueprint, request, jsonify

from config import db
from db import Task, Subtask
from routes.auth_wrapper import auth_required
from utils import validate_subtask, string_to_date, int_list_to_string, map_subtasks, validate_description, \
    validate_due, validate_assignee, string_to_int_list, send_notification_to_assignees

subtask_bp = Blueprint("subtask_routes", __name__)


@subtask_bp.route("/add_subtask", methods=["POST"])
@auth_required
def add_subtask(current_user):
    try:
        data = request.get_json()
        task = Task.query.filter_by(task_id=data["taskId"]).first()
        validation = validate_subtask(data["description"], string_to_date(data["due"]), data["assignee"], current_user["id"], task.creator_id, task.assignee)

        if validation["isValid"]:
            new_subtask = Subtask(
                task_id=data["taskId"],
                description=data["description"],
                priority=data["priority"],
                due=string_to_date(data["due"]),
                creator_id=current_user["id"],
                type=data["type"],
                assignee=int_list_to_string(data["assignee"])
            )
            db.session.add(new_subtask)

            send_notification_to_assignees(
                "New Subtask Created",
                current_user["name"] + "  have assigned to you a new subtask.",
                data["assignee"]
            )

            db.session.commit()
            return jsonify(map_subtasks(new_subtask)), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@subtask_bp.route("/change_subtask_description", methods=["POST"])
@auth_required
def change_subtask_description(current_user):
    try:
        data = request.get_json()
        task_to_change = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()
        validation = validate_description(data["description"], current_user["id"], task_to_change.creator_id)
        if validation["isValid"]:
            task_to_change.description = data["description"]

            send_notification_to_assignees(
                "Subtask Description Updated",
                current_user["name"] + " changed description of subtask.",
                string_to_int_list(task_to_change.assignee)
            )

            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@subtask_bp.route("/change_subtask_priority", methods=["POST"])
@auth_required
def change_subtask_priority(current_user):
    try:
        data = request.get_json()
        task_to_change = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()
        if task_to_change.creator_id == current_user["id"]:
            task_to_change.priority = data["priority"]

            send_notification_to_assignees(
                "Subtask Priority Updated",
                current_user["name"] + " changed priority of subtask.",
                string_to_int_list(task_to_change.assignee)
            )

            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only task creator can edit priority"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@subtask_bp.route("/change_subtask_due_date", methods=["POST"])
@auth_required
def change_subtask_due_date(current_user):
    try:
        data = request.get_json()
        task_to_change = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()
        validation = validate_due(string_to_date(data["due"]), current_user["id"], task_to_change.creator_id)

        if validation["isValid"]:
            task_to_change.due = string_to_date(data["due"])

            send_notification_to_assignees(
                "Subtask Due Date Updated",
                current_user["name"] + " changed due date of subtask.",
                string_to_int_list(task_to_change.assignee)
            )

            db.session.commit()
            return jsonify({"message": validation["message"]}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@subtask_bp.route("/edit_subtask_assignees", methods=["POST"])
@auth_required
def edit_subtask_assignees(current_user):
    try:
        data = request.get_json()
        task_to_change = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()
        validation = validate_assignee(data["assignee"], current_user["id"], task_to_change.creator_id)

        if validation["isValid"]:
            task_to_change.assignee = int_list_to_string(data["assignee"])

            send_notification_to_assignees(
                "Subtask Assignees Updated",
                current_user["name"] + " changed assignees of subtask.",
                data["assignee"]
            )

            db.session.commit()
            return jsonify({"message": validation["message"]}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@subtask_bp.route("/change_subtask_type", methods=["POST"])
@auth_required
def change_subtask_type(current_user):
    try:
        data = request.get_json()
        task_to_change = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()
        if task_to_change.creator_id == current_user["id"]:
            task_to_change.type = data["type"]

            send_notification_to_assignees(
                "Subtask Type Updated",
                current_user["name"] + " changed type of subtask.",
                string_to_int_list(task_to_change.assignee)
            )

            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only task creator can edit type"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@subtask_bp.route("/change_subtask_status", methods=["POST"])
@auth_required
def change_subtask_status(current_user):
    try:
        data = request.get_json()
        task_to_change = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()
        assignees = string_to_int_list(task_to_change.assignee)
        if current_user["id"] in assignees:
            task_to_change.status = data["status"]

            send_notification_to_assignees(
                "Subtask Status Updated",
                current_user["name"] + " changed status of subtask.",
                [*assignees, task_to_change.creator_id]
            )

            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only assignees can edit status"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@subtask_bp.route("/delete_subtask", methods=["DELETE"])
@auth_required
def delete_subtask(current_user):
    try:
        subtask_to_delete = Subtask.query.filter_by(subtask_id=request.args.get("subtask_id")).first()
        if current_user["id"] == subtask_to_delete.creator_id:
            db.session.delete(subtask_to_delete)

            send_notification_to_assignees(
                "Subtask Deleted",
                current_user["name"] + " deleted subtask.",
                string_to_int_list(subtask_to_delete.assignee)
            )

            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "You cannot delete a subtask that you did not create."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500

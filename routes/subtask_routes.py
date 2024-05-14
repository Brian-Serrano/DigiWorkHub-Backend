from typing import Dict, Any, List, Tuple

from flask import Blueprint, request, jsonify, Response

from config import db
from db import Task, Subtask
from routes.auth_wrapper import auth_required
from utils import validate_subtask, string_to_date, int_list_to_string, map_subtasks, validate_description, \
    validate_due, validate_assignee, string_to_int_list, send_notification_to_assignees

subtask_bp = Blueprint("subtask_routes", __name__)


@subtask_bp.route("/add_subtask", methods=["POST"])
@auth_required
def add_subtask(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the subtask request body
        data: Dict[str, Any] = request.get_json()
        # get the task where the subtask is sent (used to check if user send the subtask is a creator or assignee of task)
        task: Task = Task.query.filter_by(task_id=data["taskId"]).first()
        # validate the subtask
        validation: Dict[str, Any] = validate_subtask(data["description"], string_to_date(data["due"]), data["assignee"], current_user["id"], task.creator_id, task.assignee)

        # check if subtask is valid
        if validation["isValid"]:
            # create the subtask that will be saved in database
            new_subtask: Subtask = Subtask(
                task_id=data["taskId"],
                description=data["description"],
                priority=data["priority"],
                due=string_to_date(data["due"]),
                creator_id=current_user["id"],
                type=data["type"],
                assignee=int_list_to_string(data["assignee"])
            )
            # add the subtask to the database
            db.session.add(new_subtask)

            # send push notifications to the assignees of subtask
            send_notification_to_assignees(
                "New Subtask Created",
                current_user["name"] + "  have assigned to you a new subtask.",
                data["assignee"]
            )

            # commit/apply the added subtask
            db.session.commit()
            # return the created subtask
            return jsonify(map_subtasks(new_subtask)), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@subtask_bp.route("/change_subtask_description", methods=["POST"])
@auth_required
def change_subtask_description(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the subtask request data
        data: Dict[str, Any] = request.get_json()
        # get the subtask to change its description
        task_to_change: Subtask = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()
        # validate the subtask (who change it)
        validation: Dict[str, Any] = validate_description(data["description"], current_user["id"], task_to_change.creator_id)

        # check if the data is valid
        if validation["isValid"]:
            # change the description
            task_to_change.description = data["description"]

            # send push notifications to the assignees of subtask
            send_notification_to_assignees(
                "Subtask Description Updated",
                current_user["name"] + " changed description of subtask.",
                string_to_int_list(task_to_change.assignee)
            )

            # commit/apply the changed subtask
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@subtask_bp.route("/change_subtask_priority", methods=["POST"])
@auth_required
def change_subtask_priority(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the subtask request data
        data: Dict[str, Any] = request.get_json()
        # get the subtask to change its priority
        task_to_change: Subtask = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()

        # check if the user changed the subtask is the creator of subtask
        if task_to_change.creator_id == current_user["id"]:
            # change the priority
            task_to_change.priority = data["priority"]

            # send push notifications to the assignees of subtask
            send_notification_to_assignees(
                "Subtask Priority Updated",
                current_user["name"] + " changed priority of subtask.",
                string_to_int_list(task_to_change.assignee)
            )

            # commit/apply the changed subtask
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only task creator can edit priority"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@subtask_bp.route("/change_subtask_due_date", methods=["POST"])
@auth_required
def change_subtask_due_date(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the subtask request data
        data: Dict[str, Any] = request.get_json()
        # get the subtask to change its due date
        task_to_change: Subtask = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()
        # validate the subtask (who change it)
        validation: Dict[str, Any] = validate_due(string_to_date(data["due"]), current_user["id"], task_to_change.creator_id)

        # check if the data is valid
        if validation["isValid"]:
            # change the due date
            task_to_change.due = string_to_date(data["due"])

            # send push notifications to the assignees of subtask
            send_notification_to_assignees(
                "Subtask Due Date Updated",
                current_user["name"] + " changed due date of subtask.",
                string_to_int_list(task_to_change.assignee)
            )

            # commit/apply the changed subtask
            db.session.commit()
            # return message
            return jsonify({"message": validation["message"]}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@subtask_bp.route("/edit_subtask_assignees", methods=["POST"])
@auth_required
def edit_subtask_assignees(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the subtask request data
        data: Dict[str, Any] = request.get_json()
        # get the subtask to change its assignees
        task_to_change: Subtask = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()
        # validate the subtask (who change it)
        validation: Dict[str, Any] = validate_assignee(data["assignee"], current_user["id"], task_to_change.creator_id)

        # check if the data is valid
        if validation["isValid"]:
            # change the assignees
            task_to_change.assignee = int_list_to_string(data["assignee"])

            # send push notifications to the new assignees of subtask
            send_notification_to_assignees(
                "Subtask Assignees Updated",
                current_user["name"] + " changed assignees of subtask.",
                data["assignee"]
            )

            # commit/apply the changed subtask
            db.session.commit()
            # return message
            return jsonify({"message": validation["message"]}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@subtask_bp.route("/change_subtask_type", methods=["POST"])
@auth_required
def change_subtask_type(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the subtask request data
        data: Dict[str, Any] = request.get_json()
        # get the subtask to change its type
        task_to_change: Subtask = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()

        # check if the user changed the subtask is the creator of subtask
        if task_to_change.creator_id == current_user["id"]:
            # change the type
            task_to_change.type = data["type"]

            # send push notifications to the assignees of subtask
            send_notification_to_assignees(
                "Subtask Type Updated",
                current_user["name"] + " changed type of subtask.",
                string_to_int_list(task_to_change.assignee)
            )

            # commit/apply the changed subtask
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only task creator can edit type"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@subtask_bp.route("/change_subtask_status", methods=["POST"])
@auth_required
def change_subtask_status(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the subtask request data
        data: Dict[str, Any] = request.get_json()
        # get the subtask to change its status
        task_to_change: Subtask = Subtask.query.filter_by(subtask_id=data["subtaskId"]).first()

        # check if the user changed the subtask is an assignee of subtask
        assignees: List[int] = string_to_int_list(task_to_change.assignee)
        if current_user["id"] in assignees:
            # change the status
            task_to_change.status = data["status"]

            # send push notifications to the assignees and creator of subtask
            send_notification_to_assignees(
                "Subtask Status Updated",
                current_user["name"] + " changed status of subtask.",
                [*assignees, task_to_change.creator_id]
            )

            # commit/apply the changed subtask
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only assignees can edit status"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@subtask_bp.route("/delete_subtask", methods=["DELETE"])
@auth_required
def delete_subtask(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the subtask to delete
        subtask_to_delete: Subtask = Subtask.query.filter_by(subtask_id=request.args.get("subtask_id")).first()

        # check if the user want to delete the subtask is the creator of subtask
        if current_user["id"] == subtask_to_delete.creator_id:
            # delete the subtask
            db.session.delete(subtask_to_delete)

            # send push notifications to the assignees of subtask
            send_notification_to_assignees(
                "Subtask Deleted",
                current_user["name"] + " deleted subtask.",
                string_to_int_list(subtask_to_delete.assignee)
            )

            # commit/apply the deleted subtask
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "You cannot delete a subtask that you did not create."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500

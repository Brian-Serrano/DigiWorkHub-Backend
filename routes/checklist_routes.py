from typing import Tuple, Dict, Any

from flask import Blueprint, request, jsonify, Response

from config import db
from db import Task, Checklist
from routes.auth_wrapper import auth_required
from utils import validate_checklist, int_list_to_string, map_checklists, string_to_int_list, \
    send_notification_to_assignees

checklist_bp = Blueprint("checklist_routes", __name__)


@checklist_bp.route("/add_checklist", methods=["POST"])
@auth_required
def add_checklist(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get request body
        data: Dict[str, Any] = request.get_json()
        # get the task the checklist belong (used for checking the current user create checklist if he/she is assignee or creator of task)
        task: Task = Task.query.filter_by(task_id=data["taskId"]).first()
        # validate the checklist and the user create it
        validation: Dict[str, Any] = validate_checklist(data["description"], data["assignee"], current_user["id"], task.creator_id, task.assignee)

        # check if checklist is valid
        if validation["isValid"]:
            # create the checklist information
            new_checklist: Checklist = Checklist(
                task_id=data["taskId"],
                user_id=current_user["id"],
                description=data["description"],
                assignee=int_list_to_string(data["assignee"])
            )
            # add the checklist to database
            db.session.add(new_checklist)

            # send push notifications to the assignees of checklist
            send_notification_to_assignees(
                "New Checklist Created",
                current_user["name"] + " created new checklist.",
                data["assignee"]
            )

            # commit/apply the creation of checklist
            db.session.commit()
            # return the created checklist as response
            return jsonify(map_checklists(new_checklist)), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@checklist_bp.route("/toggle_checklist", methods=["POST"])
@auth_required
def toggle_checklist(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the request body
        data: Dict[str, Any] = request.get_json()
        # get the checklist to check/uncheck
        checklist_to_toggle: Checklist = Checklist.query.filter_by(checklist_id=data["checklistId"]).first()

        # check if the user toggle checklist is an assignee of checklist
        if current_user["id"] in string_to_int_list(checklist_to_toggle.assignee):
            # check/uncheck the checklist
            checklist_to_toggle.is_checked = data["check"]
            # send push notifications to the checklist assignees
            send_notification_to_assignees(
                "Checklist " + ("Checked" if data["check"] else "Unchecked"),
                current_user["name"] + " " + ("checked" if data["check"] else "unchecked") + " checklist.",
                string_to_int_list(checklist_to_toggle.assignee)
            )
            # commit/apply the toggled checklist
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only assignees can edit checklist"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@checklist_bp.route("/delete_checklist", methods=["DELETE"])
@auth_required
def delete_checklist(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the checklist to delete
        checklist_to_delete: Checklist = Checklist.query.filter_by(checklist_id=request.args.get("checklist_id")).first()

        # check if the user want to delete is the creator of checklist
        if current_user["id"] == checklist_to_delete.user_id:
            # delete the checklist
            db.session.delete(checklist_to_delete)
            # send push notifications to the assignees of checklist that the checklist is deleted
            send_notification_to_assignees(
                "Checklist Deleted",
                current_user["name"] + " deleted checklist.",
                string_to_int_list(checklist_to_delete.assignee)
            )

            # commit/apply the deleted checklist
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "You cannot delete checklist you did not create."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500

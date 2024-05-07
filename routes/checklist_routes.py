from flask import Blueprint, request, jsonify

from config import db
from db import Task, Checklist
from routes.auth_wrapper import auth_required
from utils import validate_checklist, int_list_to_string, map_checklists, string_to_int_list, \
    send_notification_to_assignees

checklist_bp = Blueprint("checklist_routes", __name__)


@checklist_bp.route("/add_checklist", methods=["POST"])
@auth_required
def add_checklist(current_user):
    try:
        data = request.get_json()
        task = Task.query.filter_by(task_id=data["taskId"]).first()
        validation = validate_checklist(data["description"], data["assignee"], current_user["id"], task.creator_id, task.assignee)

        if validation["isValid"]:
            new_checklist = Checklist(
                task_id=data["taskId"],
                user_id=current_user["id"],
                description=data["description"],
                assignee=int_list_to_string(data["assignee"])
            )
            db.session.add(new_checklist)

            send_notification_to_assignees(
                "New Checklist Created",
                current_user["name"] + " created new checklist.",
                data["assignee"]
            )

            db.session.commit()
            return jsonify(map_checklists(new_checklist)), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@checklist_bp.route("/toggle_checklist", methods=["POST"])
@auth_required
def toggle_checklist(current_user):
    try:
        data = request.get_json()
        checklist_to_toggle = Checklist.query.filter_by(checklist_id=data["checklistId"]).first()
        if current_user["id"] in string_to_int_list(checklist_to_toggle.assignee):
            checklist_to_toggle.is_checked = data["check"]

            send_notification_to_assignees(
                "Checklist " + ("Checked" if data["check"] else "Unchecked"),
                current_user["name"] + " " + ("checked" if data["check"] else "unchecked") + " checklist.",
                string_to_int_list(checklist_to_toggle.assignee)
            )

            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only assignees can edit checklist"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@checklist_bp.route("/delete_checklist", methods=["DELETE"])
@auth_required
def delete_checklist(current_user):
    try:
        checklist_to_delete = Checklist.query.filter_by(checklist_id=request.args.get("checklist_id")).first()
        if current_user["id"] == checklist_to_delete.user_id:
            db.session.delete(checklist_to_delete)

            send_notification_to_assignees(
                "Checklist Deleted",
                current_user["name"] + " deleted checklist.",
                string_to_int_list(checklist_to_delete.assignee)
            )

            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "You cannot delete checklist you did not create."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500

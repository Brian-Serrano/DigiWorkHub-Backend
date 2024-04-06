from flask import Blueprint, request, jsonify

from config import db
from db import Task, Checklist
from routes.auth_wrapper import auth_required
from utils import validate_checklist, int_list_to_string, map_checklists, string_to_int_list

checklist_bp = Blueprint("checklist_routes", __name__)


@checklist_bp.route("/add_checklist", methods=["POST"])
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
                assignee=int_list_to_string(data["assignee"])
            )
            db.session.add(new_checklist)
            db.session.commit()
            return jsonify(map_checklists(new_checklist)), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@checklist_bp.route("/toggle_checklist", methods=["POST"])
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


@checklist_bp.route("/delete_checklist", methods=["DELETE"])
@auth_required
def delete_checklist(user):
    try:
        checklist_to_delete = Checklist.query.filter_by(checklist_id=request.args.get("checklist_id")).first()
        if user["id"] == checklist_to_delete.user_id:
            db.session.delete(checklist_to_delete)
            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "You cannot delete checklist you did not create."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500
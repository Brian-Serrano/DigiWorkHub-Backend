from typing import Dict, Any, List, Tuple

from flask import Blueprint, request, jsonify, Response

from config import db
from db import Task, TaskComment, Subtask, Checklist, Attachment
from routes.auth_wrapper import auth_required
from utils import validate_task, string_to_date, int_list_to_string, string_to_int_list, validate_assignee, \
    validate_due, validate_name, validate_description, map_tasks, map_comments, map_subtasks, map_checklists, \
    map_attachments, date_to_string, map_user, send_notification_to_assignees

task_bp = Blueprint("task_routes", __name__)


@task_bp.route("/add_task", methods=["POST"])
@auth_required
def add_task(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the task request body
        data: Dict[str, Any] = request.get_json()
        # validate the task
        validation: Dict[str, Any] = validate_task(data["title"], data["description"], string_to_date(data["due"]), data["assignee"])

        # check if task is valid
        if validation["isValid"]:
            # create the task to be saved in the database
            new_task: Task = Task(
                title=data["title"],
                description=data["description"],
                priority=data["priority"],
                due=string_to_date(data["due"]),
                creator_id=current_user["id"],
                type=data["type"],
                assignee=int_list_to_string(data["assignee"])
            )
            # add the created task to the database
            db.session.add(new_task)

            # send push notifications to the assignees of task
            send_notification_to_assignees(
                "New Task Created",
                current_user["name"] + " have assigned to you a new task.",
                data["assignee"]
            )

            # commit/apply the added task
            db.session.commit()
            # return the created task as response
            return jsonify(map_tasks(new_task)), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/change_task_status", methods=["POST"])
@auth_required
def change_task_status(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the task request data
        data: Dict[str, Any] = request.get_json()
        # get the task to change its status
        task_to_change: Task = Task.query.filter_by(task_id=data["taskId"]).first()

        # check if the user want to change status is an assignee of task
        assignees: List[int] = string_to_int_list(task_to_change.assignee)
        if current_user["id"] in assignees:
            # change the status
            task_to_change.status = data["status"]

            # send push notifications to the assignees and creator of task
            send_notification_to_assignees(
                "Task Status Updated",
                current_user["name"] + " changed status of task \"" + task_to_change.title + "\".",
                [*assignees, task_to_change.creator_id]
            )

            # commit/apply the changed task
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only assignees can edit status"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/edit_assignees", methods=["POST"])
@auth_required
def edit_assignees(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the task request data
        data: Dict[str, Any] = request.get_json()
        # get the task to change its assignees
        task_to_change: Task = Task.query.filter_by(task_id=data["taskId"]).first()
        # validate the task (who change it)
        validation: Dict[str, Any] = validate_assignee(data["assignee"], current_user["id"], task_to_change.creator_id)

        # check if task is valid
        if validation["isValid"]:
            # change the assignees
            task_to_change.assignee = int_list_to_string(data["assignee"])

            # send push notifications to the new assignees of task
            send_notification_to_assignees(
                "Task Assignees Updated",
                current_user["name"] + " changed assignees of task \"" + task_to_change.title + "\".",
                data["assignee"]
            )

            # commit/apply the changed task
            db.session.commit()
            # return message
            return jsonify({"message": validation["message"]}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/change_due_date", methods=["POST"])
@auth_required
def change_due_date(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the task request data
        data: Dict[str, Any] = request.get_json()
        # get the task to change its due date
        task_to_change: Task = Task.query.filter_by(task_id=data["taskId"]).first()
        # validate the task (who change it)
        validation: Dict[str, Any] = validate_due(string_to_date(data["due"]), current_user["id"], task_to_change.creator_id)

        # check if task is valid
        if validation["isValid"]:
            # change the due date
            task_to_change.due = string_to_date(data["due"])

            # send push notifications to the assignees of task
            send_notification_to_assignees(
                "Task Due Date Updated",
                current_user["name"] + " changed due date of task \"" + task_to_change.title + "\".",
                string_to_int_list(task_to_change.assignee)
            )

            # commit/apply the changed task
            db.session.commit()
            # return message
            return jsonify({"message": validation["message"]}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/change_priority", methods=["POST"])
@auth_required
def change_priority(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the task request data
        data: Dict[str, Any] = request.get_json()
        # get the task to change its priority
        task_to_change: Task = Task.query.filter_by(task_id=data["taskId"]).first()

        # check if the user want to change priority is the creator of task
        if task_to_change.creator_id == current_user["id"]:
            # change the priority
            task_to_change.priority = data["priority"]

            # send push notifications to the assignees of task
            send_notification_to_assignees(
                "Task Priority Updated",
                current_user["name"] + " changed priority of task \"" + task_to_change.title + "\".",
                string_to_int_list(task_to_change.assignee)
            )

            # commit/apply the changed task
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only task creator can edit priority"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/change_type", methods=["POST"])
@auth_required
def change_type(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the task request data
        data: Dict[str, Any] = request.get_json()
        # get the task to change its type
        task_to_change: Task = Task.query.filter_by(task_id=data["taskId"]).first()

        # check if the user want to change type is the creator of task
        if task_to_change.creator_id == current_user["id"]:
            # change the type
            task_to_change.type = data["type"]

            # send push notifications to the assignees of task
            send_notification_to_assignees(
                "Task Type Updated",
                current_user["name"] + " changed type of task \"" + task_to_change.title + "\".",
                string_to_int_list(task_to_change.assignee)
            )

            # commit/apply the changed task
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only task creator can edit type"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/change_name", methods=["POST"])
@auth_required
def change_name(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the task request data
        data: Dict[str, Any] = request.get_json()
        # get the task to change its name
        task_to_change: Task = Task.query.filter_by(task_id=data["taskId"]).first()
        # validate the task (who change it)
        validation: Dict[str, Any] = validate_name(data["title"], current_user["id"], task_to_change.creator_id)

        # check if task is valid
        if validation["isValid"]:
            # change the name
            task_to_change.title = data["title"]

            # send push notifications to the assignees of task
            send_notification_to_assignees(
                "Task Name Updated",
                current_user["name"] + " changed name of task \"" + task_to_change.title + "\".",
                string_to_int_list(task_to_change.assignee)
            )

            # commit/apply the changed task
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/change_description", methods=["POST"])
@auth_required
def change_description(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the task request data
        data: Dict[str, Any] = request.get_json()
        # get the task to change its description
        task_to_change: Task = Task.query.filter_by(task_id=data["taskId"]).first()
        # validate the task (who change it)
        validation: Dict[str, Any] = validate_description(data["description"], current_user["id"], task_to_change.creator_id)

        # check if task is valid
        if validation["isValid"]:
            # change the description
            task_to_change.description = data["description"]

            # send push notifications to the assignees of task
            send_notification_to_assignees(
                "Task Description Updated",
                current_user["name"] + " changed description of task \"" + task_to_change.title + "\".",
                string_to_int_list(task_to_change.assignee)
            )

            # commit/apply the changed task
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/delete_task", methods=["DELETE"])
@auth_required
def delete_task(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        task_id: int = int(request.args.get("task_id"))
        # get the task to delete
        task_to_delete: Task = Task.query.filter_by(task_id=task_id).first()

        # check if the user want to delete the task is the creator of task
        if current_user["id"] == task_to_delete.creator_id:
            # delete the task, its comments, checklists, subtasks and attachments
            db.session.delete(task_to_delete)
            db.session.query(TaskComment).filter_by(task_id=task_id).delete()
            db.session.query(Subtask).filter_by(task_id=task_id).delete()
            db.session.query(Checklist).filter_by(task_id=task_id).delete()
            db.session.query(Attachment).filter_by(task_id=task_id).delete()

            # send push notifications to the assignees of task
            send_notification_to_assignees(
                "Task Deleted",
                current_user["name"] + " deleted task \"" + task_to_delete.title + "\".",
                string_to_int_list(task_to_delete.assignee)
            )

            # commit/apply the deleted task, its comments, checklists, subtasks and attachments
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "Only task creator can delete tasks."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/get_tasks", methods=["GET"])
@auth_required
def get_tasks(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get assigned tasks
        tasks: List[Task] = Task.query.filter(Task.assignee.like(f"%{current_user['id']}%")).all()
        return jsonify([map_tasks(x) for x in tasks]), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@task_bp.route("/get_task", methods=["GET"])
@auth_required
def get_task(_: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        task_id: int = int(request.args.get("task_id"))
        # get everything from task, its comments, checklists, subtasks and attachments
        task: Task = Task.query.filter_by(task_id=task_id).first()
        assignee_ids: List[int] = string_to_int_list(task.assignee)
        comments: List[TaskComment] = TaskComment.query.filter_by(task_id=task_id).all()
        subtasks: List[Subtask] = Subtask.query.filter_by(task_id=task_id).all()
        checklists: List[Checklist] = Checklist.query.filter_by(task_id=task_id).all()
        attachments: List[Attachment] = Attachment.query.filter_by(task_id=task_id).all()

        # return the task, its comments, checklists, subtasks and attachments
        response: Dict[str, Any] = {
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
def get_created_tasks(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get created tasks
        tasks: List[Task] = Task.query.filter_by(creator_id=current_user["id"]).all()
        return jsonify([map_tasks(x) for x in tasks]), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500

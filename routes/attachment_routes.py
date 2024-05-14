import os
from typing import Dict, Any, Tuple

from flask import Blueprint, request, jsonify, send_from_directory, Response
from werkzeug.datastructures import FileStorage

from config import ALLOWED_FILE_EXTENSIONS, db
from db import Attachment, Task
from routes.auth_wrapper import auth_required
from utils import allowed_file, map_attachments, filename_secure, send_notification_to_assignees, string_to_int_list

attachment_bp = Blueprint("attachment_routes", __name__)


@attachment_bp.route("/upload_attachment", methods=["POST"])
@auth_required
def upload_attachment(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    # get the request form datas
    file: FileStorage = request.files['file']
    task_id: int = int(request.form["taskId"])
    # get the task from task id
    task: Task = Task.query.filter_by(task_id=task_id).first()

    # check if file allowed
    if file and allowed_file(file.filename, ALLOWED_FILE_EXTENSIONS):
        try:
            # create file name
            filename: str = filename_secure(file)
            # save file to attachments directory
            file.save(os.path.join("attachments", filename))
            # create the attachment information
            new_attachment: Attachment = Attachment(
                task_id=task_id,
                user_id=current_user["id"],
                attachment_path="attachments/" + filename,
                file_name=file.filename
            )
            # save attachment information in database
            db.session.add(new_attachment)
            # send push notifications to the assignees and creator of task
            send_notification_to_assignees(
                "Attachment",
                current_user["name"] + " sent attachment.",
                [*string_to_int_list(task.assignee), task.creator_id]
            )
            # commit/apply the added attachment
            db.session.commit()
            # return the created attachment as response
            return jsonify(map_attachments(new_attachment)), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Unhandled exception: {e}"}), 500

    return jsonify({"type": "Validation Error", "message": "The file type is not allowed"}), 400


@attachment_bp.route("/download_attachment", methods=["GET"])
@auth_required
def download_attachment(_: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the attachment
        return send_from_directory("attachments", request.args.get("attachment_name"), as_attachment=True), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@attachment_bp.route("/delete_attachment", methods=["DELETE"])
@auth_required
def delete_attachment(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the attachment to delete
        attachment_to_delete: Attachment = Attachment.query.filter_by(attachment_id=request.args.get("attachment_id")).first()

        # check if the user want to delete is the user uploaded the attachment
        if current_user["id"] == attachment_to_delete.user_id:
            # delete the attachment information in database
            db.session.delete(attachment_to_delete)

            # delete the attachment file in directory if exists
            if os.path.exists(attachment_to_delete.attachment_path):
                os.remove(attachment_to_delete.attachment_path)

            # commit/apply the deletion
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "You cannot delete attachment you did not upload."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500

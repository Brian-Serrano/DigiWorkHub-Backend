import os

from flask import Blueprint, request, jsonify, send_from_directory

from config import ALLOWED_FILE_EXTENSIONS, db
from db import Attachment, Task
from routes.auth_wrapper import auth_required
from utils import allowed_file, map_attachments, filename_secure, send_notification_to_assignees, string_to_int_list

attachment_bp = Blueprint("attachment_routes", __name__)


@attachment_bp.route("/upload_attachment", methods=["POST"])
@auth_required
def upload_attachment(current_user):
    file = request.files['file']
    task_id = int(request.form["taskId"])
    task = Task.query.filter_by(task_id=task_id).first()

    if file and allowed_file(file.filename, ALLOWED_FILE_EXTENSIONS):
        try:
            filename = filename_secure(file)
            file.save(os.path.join("attachments", filename))
            new_attachment = Attachment(
                task_id=task_id,
                user_id=current_user["id"],
                attachment_path="attachments/" + filename,
                file_name=file.filename
            )
            db.session.add(new_attachment)

            send_notification_to_assignees(
                "Attachment",
                current_user["name"] + " sent attachment.",
                [*string_to_int_list(task.assignee), task.creator_id]
            )

            db.session.commit()
            return jsonify(map_attachments(new_attachment)), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Unhandled exception: {e}"}), 500

    return jsonify({"type": "Validation Error", "message": "The file type is not allowed"}), 400


@attachment_bp.route("/download_attachment", methods=["GET"])
@auth_required
def download_attachment(current_user):
    try:
        return send_from_directory("attachments", request.args.get("attachment_name"), as_attachment=True), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@attachment_bp.route("/delete_attachment", methods=["DELETE"])
@auth_required
def delete_attachment(current_user):
    try:
        attachment_to_delete = Attachment.query.filter_by(attachment_id=request.args.get("attachment_id")).first()
        if current_user["id"] == attachment_to_delete.user_id:
            db.session.delete(attachment_to_delete)

            if os.path.exists(attachment_to_delete.attachment_path):
                os.remove(attachment_to_delete.attachment_path)

            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "You cannot delete attachment you did not upload."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500

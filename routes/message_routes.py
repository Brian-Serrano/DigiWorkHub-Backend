import json
import os

from flask import Blueprint, request, jsonify
from sqlalchemy import desc

from config import db
from db import Message, MessageReply
from routes.auth_wrapper import auth_required
from utils import validate_message, list_to_string, map_replies, map_sent_messages, \
    map_received_messages, date_to_string, map_user, string_to_list, filename_secure, validate_reply, \
    send_notification_to_assignees

message_bp = Blueprint("message_routes", __name__)


@message_bp.route("/message_user", methods=["POST"])
@auth_required
def message_user(current_user):
    try:
        data = json.loads(request.form["messageBody"])
        files = request.files.getlist("file")
        attachment_paths = []
        file_names = []
        validation = validate_message(data["title"], data["description"], files)

        if validation["isValid"]:
            for idx, file in enumerate(files):
                filename = filename_secure(file, f"_idx_{idx}")
                file.save(os.path.join("attachments", filename))
                attachment_paths.append("attachments/" + filename)
                file_names.append(file.filename)

            new_message = Message(
                sender_id=current_user["id"],
                receiver_id=data["receiverId"],
                title=data["title"],
                description=data["description"],
                attachment_paths=list_to_string(attachment_paths),
                file_names=list_to_string(file_names)
            )
            db.session.add(new_message)

            send_notification_to_assignees(
                "New Message",
                current_user["name"] + " send you a message.",
                [data["receiverId"]]
            )

            db.session.commit()
            return jsonify(map_sent_messages(new_message)), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@message_bp.route("/reply_to_message", methods=["POST"])
@auth_required
def reply_to_message(current_user):
    try:
        data = json.loads(request.form["replyBody"])
        files = request.files.getlist("file")
        attachment_paths = []
        file_names = []
        validation = validate_reply(data["description"], files)

        if validation["isValid"]:
            for idx, file in enumerate(files):
                filename = filename_secure(file, f"_idx_{idx}")
                file.save(os.path.join("attachments", filename))
                attachment_paths.append("attachments/" + filename)
                file_names.append(file.filename)

            new_reply = MessageReply(
                message_id=data["messageId"],
                description=data["description"],
                from_id=current_user["id"],
                attachment_paths=list_to_string(attachment_paths),
                file_names=list_to_string(file_names)
            )

            message = Message.query.filter_by(message_id=data["messageId"]).first()
            message.deleted_from_sender = False
            message.deleted_from_receiver = False

            db.session.add(new_reply)

            send_notification_to_assignees(
                "New Reply",
                current_user["name"] + " replies to your message.",
                [message.receiver_id if current_user["id"] == message.sender_id else message.sender_id]
            )

            db.session.commit()
            return jsonify(map_replies(new_reply)), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@message_bp.route("/get_sent_messages", methods=["GET"])
@auth_required
def get_sent_messages(current_user):
    try:
        messages = Message.query.filter_by(sender_id=current_user["id"], deleted_from_sender=False).order_by(desc(Message.date_sent)).all()
        return jsonify([map_sent_messages(x) for x in messages]), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@message_bp.route("/get_received_messages", methods=["GET"])
@auth_required
def get_received_messages(current_user):
    try:
        messages = Message.query.filter_by(receiver_id=current_user["id"], deleted_from_receiver=False).order_by(desc(Message.date_sent)).all()
        return jsonify([map_received_messages(x) for x in messages]), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@message_bp.route("/get_message", methods=["GET"])
@auth_required
def get_message(current_user):
    try:
        message_id = request.args.get("message_id")
        message = Message.query.filter_by(message_id=message_id).first()
        message_replies = MessageReply.query.filter_by(message_id=message_id).all()

        if message.sender_id == current_user["id"] and message.deleted_from_sender:
            return jsonify({"type": "Validation Error", "message": "Unable to view the message."}), 400

        if message.receiver_id == current_user["id"] and message.deleted_from_receiver:
            return jsonify({"type": "Validation Error", "message": "Unable to view the message."}), 400

        response = {
            "messageId": message.message_id,
            "title": message.title,
            "description": message.description,
            "sentDate": date_to_string(message.date_sent),
            "sender": map_user(message.sender_id),
            "receiver": map_user(message.receiver_id),
            "attachmentPaths": string_to_list(message.attachment_paths),
            "fileNames": string_to_list(message.file_names),
            "replies": [map_replies(x) for x in message_replies]
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@message_bp.route("/delete_message", methods=["DELETE"])
@auth_required
def delete_message(current_user):
    try:
        message_id = request.args.get("message_id")
        message_to_delete = Message.query.filter_by(message_id=message_id).first()
        if current_user["id"] == message_to_delete.sender_id:
            db.session.delete(message_to_delete)
            replies_to_delete = MessageReply.query.filter_by(message_id=message_id).all()

            for path in string_to_list(message_to_delete.attachment_paths):
                if os.path.exists(path):
                    os.remove(path)

            for reply in replies_to_delete:
                db.session.delete(reply)
                for path in string_to_list(reply.attachment_paths):
                    if os.path.exists(path):
                        os.remove(path)

            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "You cannot delete a message you did not send."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@message_bp.route("/delete_message_reply", methods=["DELETE"])
@auth_required
def delete_message_reply(current_user):
    try:
        reply_to_delete = MessageReply.query.filter_by(message_reply_id=request.args.get("message_reply_id")).first()
        if current_user["id"] == reply_to_delete.from_id:
            db.session.delete(reply_to_delete)

            for path in string_to_list(reply_to_delete.attachment_paths):
                if os.path.exists(path):
                    os.remove(path)

            db.session.commit()
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "You cannot delete a reply you did not send."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@message_bp.route("/delete_message_from_user", methods=["POST"])
@auth_required
def delete_message_from_user(current_user):
    try:
        data = request.get_json()
        message = Message.query.filter_by(message_id=data["messageId"]).first()

        if message.sender_id == current_user["id"]:
            message.deleted_from_sender = True
        elif message.receiver_id == current_user["id"]:
            message.deleted_from_receiver = True

        db.session.commit()
        return jsonify({"message": "Success"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500

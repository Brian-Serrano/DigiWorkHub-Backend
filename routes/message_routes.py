import json
import os
from typing import Any, Dict, List, Optional, Tuple

from flask import Blueprint, request, jsonify, Response
from sqlalchemy import desc
from werkzeug.datastructures import FileStorage

from config import db
from db import Message, MessageReply
from routes.auth_wrapper import auth_required
from utils import validate_message, list_to_string, map_replies, map_sent_messages, \
    map_received_messages, date_to_string, map_user, string_to_list, filename_secure, validate_reply, \
    send_notification_to_assignees

message_bp = Blueprint("message_routes", __name__)


@message_bp.route("/message_user", methods=["POST"])
@auth_required
def message_user(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the request form datas
        data: Dict[str, Any] = json.loads(request.form["messageBody"])
        files: List[FileStorage] = request.files.getlist("file")
        # initialize empty attachment paths and file names list
        attachment_paths: List[str] = []
        file_names: List[Optional[str]] = []
        # validate message (its files)
        validation: Dict[str, Any] = validate_message(data["title"], data["description"], files)

        # check if the message is valid
        if validation["isValid"]:
            # loop through attachments in message
            for idx, file in enumerate(files):
                # get file name that will be used in directory when saved
                filename: str = filename_secure(file, f"_idx_{idx}")
                # save the file in attachment directory
                file.save(os.path.join("attachments", filename))
                # add to attachment paths the path of attachment in directory
                attachment_paths.append("attachments/" + filename)
                # add to file names the original name of file
                file_names.append(file.filename)

            # create the message that will be saved
            new_message: Message = Message(
                sender_id=current_user["id"],
                receiver_id=data["receiverId"],
                title=data["title"],
                description=data["description"],
                attachment_paths=list_to_string(attachment_paths),
                file_names=list_to_string(file_names)
            )
            # add the message in database
            db.session.add(new_message)

            # send push notifications to the recipient
            send_notification_to_assignees(
                "New Message",
                current_user["name"] + " send you a message.",
                [data["receiverId"]]
            )

            # commit/apply the added message
            db.session.commit()
            # return the created message as response
            return jsonify(map_sent_messages(new_message)), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@message_bp.route("/reply_to_message", methods=["POST"])
@auth_required
def reply_to_message(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the request form datas
        data: Dict[str, Any] = json.loads(request.form["replyBody"])
        files: List[FileStorage] = request.files.getlist("file")
        # initialize empty attachment paths and file names list
        attachment_paths: List[str] = []
        file_names: List[Optional[str]] = []
        # validate reply to message (its files)
        validation: Dict[str, Any] = validate_reply(data["description"], files)

        # check if the reply is valid
        if validation["isValid"]:
            # loop through attachments in reply
            for idx, file in enumerate(files):
                # get file name that will be used in directory when saved
                filename: str = filename_secure(file, f"_idx_{idx}")
                # save the file in attachment directory
                file.save(os.path.join("attachments", filename))
                # add to attachment paths the path of attachment in directory
                attachment_paths.append("attachments/" + filename)
                # add to file names the original name of file
                file_names.append(file.filename)

            # create reply that will be saved
            new_reply: MessageReply = MessageReply(
                message_id=data["messageId"],
                description=data["description"],
                from_id=current_user["id"],
                attachment_paths=list_to_string(attachment_paths),
                file_names=list_to_string(file_names)
            )

            # mark the message (where the reply attached) as undeleted for sender and receiver (if any deleted it from them)
            message: Message = Message.query.filter_by(message_id=data["messageId"]).first()
            message.deleted_from_sender = False
            message.deleted_from_receiver = False

            # add the reply in database
            db.session.add(new_reply)
            # send push notification to other (receiver will receive the notification, if the user send the reply is message sender, vice versa)
            send_notification_to_assignees(
                "New Reply",
                current_user["name"] + " replies to your message.",
                [message.receiver_id if current_user["id"] == message.sender_id else message.sender_id]
            )

            # commit/apply the changes in message and the added reply
            db.session.commit()
            # return the created reply as response
            return jsonify(map_replies(new_reply)), 201
        else:
            return jsonify({"type": "Validation Error", "message": validation["message"]}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@message_bp.route("/get_sent_messages", methods=["GET"])
@auth_required
def get_sent_messages(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        messages: List[Message] = Message.query.filter_by(sender_id=current_user["id"], deleted_from_sender=False).order_by(desc(Message.date_sent)).all()
        return jsonify([map_sent_messages(x) for x in messages]), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@message_bp.route("/get_received_messages", methods=["GET"])
@auth_required
def get_received_messages(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        messages: List[Message] = Message.query.filter_by(receiver_id=current_user["id"], deleted_from_receiver=False).order_by(desc(Message.date_sent)).all()
        return jsonify([map_received_messages(x) for x in messages]), 200
    except Exception as e:
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@message_bp.route("/get_message", methods=["GET"])
@auth_required
def get_message(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        message_id: int = int(request.args.get("message_id"))
        # get the message and its replies from message id
        message: Message = Message.query.filter_by(message_id=message_id).first()
        message_replies: List[MessageReply] = MessageReply.query.filter_by(message_id=message_id).all()

        # check if message is deleted from the user if the user is the sender
        if message.sender_id == current_user["id"] and message.deleted_from_sender:
            return jsonify({"type": "Validation Error", "message": "Unable to view the message."}), 400
        # check if message is deleted from the user if the user is the receiver
        if message.receiver_id == current_user["id"] and message.deleted_from_receiver:
            return jsonify({"type": "Validation Error", "message": "Unable to view the message."}), 400

        # return the message and its replies as response
        response: Dict[str, Any] = {
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
def delete_message(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        message_id: int = int(request.args.get("message_id"))
        # get the message to delete
        message_to_delete: Message = Message.query.filter_by(message_id=message_id).first()

        # check if the user is the sender of message
        if current_user["id"] == message_to_delete.sender_id:
            # delete the message permanently for both sender and receiver
            db.session.delete(message_to_delete)
            # get the replies to delete
            replies_to_delete: List[MessageReply] = MessageReply.query.filter_by(message_id=message_id).all()

            # delete the message attachments in the directory
            for path in string_to_list(message_to_delete.attachment_paths):
                if os.path.exists(path):
                    os.remove(path)

            # delete all replies in message and its attachments in the directory
            for reply in replies_to_delete:
                db.session.delete(reply)
                for path in string_to_list(reply.attachment_paths):
                    if os.path.exists(path):
                        os.remove(path)

            # commit/apply all the deletion
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "You cannot delete a message you did not send."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@message_bp.route("/delete_message_reply", methods=["DELETE"])
@auth_required
def delete_message_reply(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the reply to delete
        reply_to_delete: MessageReply = MessageReply.query.filter_by(message_reply_id=request.args.get("message_reply_id")).first()

        # check if the user want to delete reply is the sender of it
        if current_user["id"] == reply_to_delete.from_id:
            # delete the reply
            db.session.delete(reply_to_delete)

            # delete the reply's attachments in the directory
            for path in string_to_list(reply_to_delete.attachment_paths):
                if os.path.exists(path):
                    os.remove(path)

            # commit/apply the deletion
            db.session.commit()
            # return message
            return jsonify({"message": "Success"}), 201
        else:
            return jsonify({"type": "Validation Error", "message": "You cannot delete a reply you did not send."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500


@message_bp.route("/delete_message_from_user", methods=["POST"])
@auth_required
def delete_message_from_user(current_user: Dict[str, Any]) -> Tuple[Response, int]:
    try:
        # get the request body
        data: Dict[str, Any] = request.get_json()
        # get the message to delete from the user
        message: Message = Message.query.filter_by(message_id=data["messageId"]).first()

        # check if the user want to delete the message is sender or receiver
        if message.sender_id == current_user["id"]:
            # if sender, delete from sender
            message.deleted_from_sender = True
        elif message.receiver_id == current_user["id"]:
            # if receiver, delete from receiver
            message.deleted_from_receiver = True

        # commit/apply the deletion
        db.session.commit()
        # return message
        return jsonify({"message": "Success"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Unhandled exception: {e}"}), 500

import io
import re
from base64 import encodebytes
from datetime import datetime

import bcrypt
from PIL import Image
from werkzeug.utils import secure_filename

from config import EMAIL_REGEX, PASSWORD_REGEX, NAME_REGEX, ALLOWED_FILE_EXTENSIONS
from db import User


def remove_item_from_stringed_list(stringed_list, item):
    lst = string_to_int_list(stringed_list)
    lst.remove(item)
    return int_list_to_string(lst)


def add_item_from_stringed_list(stringed_list, item):
    lst = string_to_int_list(stringed_list)
    lst.append(item)
    return int_list_to_string(lst)


def string_to_int_list(string):
    return [int(x) for x in string.split(',')] if string else []


def int_list_to_string(lst):
    return ','.join([str(x) for x in lst])


def string_to_list(string):
    return string.split('|') if string else []


def list_to_string(lst):
    return '|'.join(lst)


def date_to_string(date):
    return date.strftime("%d/%m/%Y %I:%M %p")


def string_to_date(string):
    return datetime.strptime(string, "%d/%m/%Y %I:%M %p")


def validate_signup(name, email, password, confirm_password):
    if not name or not email or not password or not confirm_password:
        return {"isValid": False, "message": "Fill up all empty fields"}
    if not 5 <= len(name) <= 20 or not 15 <= len(email) <= 40 or not 8 <= len(password) <= 20:
        return {"isValid": False, "message": "Fill up fields with specified length"}
    if password != confirm_password:
        return {"isValid": False, "message": "Passwords do not match"}
    if not re.search(NAME_REGEX, name):
        return {"isValid": False, "message": "Invalid Username"}
    if not re.search(EMAIL_REGEX, email):
        return {"isValid": False, "message": "Invalid Email"}
    if not re.search(PASSWORD_REGEX, password):
        return {"isValid": False, "message": "Invalid Password"}
    if any(x.name == name for x in User.query.all()):
        return {"isValid": False, "message": "Username already exist"}
    if any(x.email == email for x in User.query.all()):
        return {"isValid": False, "message": "Email already exist"}

    return {"isValid": True, "message": "Success"}


def validate_login(user, email, password):
    if not email or not password:
        return {"isValid": False, "message": "Fill up all empty fields"}
    if not 15 <= len(email) <= 40 or not 8 <= len(password) <= 20:
        return {"isValid": False, "message": "Fill up fields with specified length"}
    if not user:
        return {"isValid": False, "message": "User not found"}
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        return {"isValid": False, "message": "Wrong password"}

    return {"isValid": True, "message": "User Logged In"}


def validate_task(title, description, due, assignees):
    if not title or not description:
        return {"isValid": False, "message": "Name and description should not be empty"}
    if not 15 <= len(title) <= 100:
        return {"isValid": False, "message": "Name should be 15-100 characters"}
    if not 50 <= len(description) <= 1000:
        return {"isValid": False, "message": "Description should be 50-1000 characters"}
    if due.date() <= datetime.now().date():
        return {"isValid": False, "message": "Due should not be earlier than now"}
    if not 1 <= len(assignees) <= 5:
        return {"isValid": False, "message": "Assignees should range from 1 to 5"}

    return {"isValid": True, "message": "Success"}


def validate_message(title, description, files):
    if not title or not description:
        return {"isValid": False, "message": "Name and description should not be empty"}
    if not 15 <= len(title) <= 100:
        return {"isValid": False, "message": "Name should be 15-100 characters"}
    if not 50 <= len(description) <= 3000:
        return {"isValid": False, "message": "Description should be 50-3000 characters"}
    if not all(file and allowed_file(file.filename, ALLOWED_FILE_EXTENSIONS) for file in files):
        return {"isValid": False, "message": "The file type is not allowed"}
    if len(files) > 5:
        return {"isValid": False, "message": "You can only upload up to 5 files"}

    return {"isValid": True, "message": "Success"}


def validate_comment(description):
    if not description or not 10 <= len(description) <= 500:
        return {"isValid": False, "message": "Description should be 10-500 characters"}

    return {"isValid": True, "message": "Success"}


def validate_due(due, user_id, creator_id):
    if due.date() <= datetime.now().date():
        return {"isValid": False, "message": "Due should not be earlier than now"}
    if user_id != creator_id:
        return {"isValid": False, "message": "Only task creator can edit due date"}

    return {"isValid": True, "message": "Success"}


def validate_assignee(assignees, user_id, creator_id):
    if not 1 <= len(assignees) <= 5:
        return {"isValid": False, "message": "Assignees should range from 1 to 5"}
    if user_id != creator_id:
        return {"isValid": False, "message": "Only task creator can edit assignees"}

    return {"isValid": True, "message": "Success"}


def validate_name(title, user_id, creator_id):
    if not title or not 15 <= len(title) <= 100:
        return {"isValid": False, "message": "Name should be 15-100 characters"}
    if user_id != creator_id:
        return {"isValid": False, "message": "Only task creator can edit name"}

    return {"isValid": True, "message": "Success"}


def validate_description(description, user_id, creator_id):
    if not description or not 50 <= len(description) <= 1000:
        return {"isValid": False, "message": "Description should be 50-1000 characters"}
    if user_id != creator_id:
        return {"isValid": False, "message": "Only task creator can edit description"}

    return {"isValid": True, "message": "Success"}


def validate_subtask(description, due, assignees, user_id, task_creator_id, task_assignees):
    if not description or not 50 <= len(description) <= 1000:
        return {"isValid": False, "message": "Description should be 50-1000 characters"}
    if due.date() <= datetime.now().date():
        return {"isValid": False, "message": "Due should not be earlier than now"}
    if not 1 <= len(assignees) <= 5:
        return {"isValid": False, "message": "Assignees should range from 1 to 5"}
    if user_id != task_creator_id and user_id not in string_to_int_list(task_assignees):
        return {"isValid": False, "message": "Only assignees and task creator can add subtask"}

    return {"isValid": True, "message": "Success"}


def validate_checklist(description, assignees, user_id, task_creator_id, task_assignees):
    if not description or not 50 <= len(description) <= 1000:
        return {"isValid": False, "message": "Description should be 50-1000 characters"}
    if not 1 <= len(assignees) <= 5:
        return {"isValid": False, "message": "Assignees should range from 1 to 5"}
    if user_id != task_creator_id and user_id not in string_to_int_list(task_assignees):
        return {"isValid": False, "message": "Only assignees and task creator can add checklist"}

    return {"isValid": True, "message": "Success"}


def validate_user_name(name):
    if not name or not 5 <= len(name) <= 20:
        return {"isValid": False, "message": "Username should be 5-20 characters"}
    if not re.search(NAME_REGEX, name):
        return {"isValid": False, "message": "Invalid Username"}

    return {"isValid": True, "message": "Success"}


def validate_user_role(role):
    if not role or not 5 <= len(role) <= 50:
        return {"isValid": False, "message": "Role should be 5-50 characters"}

    return {"isValid": True, "message": "Success"}


def validate_password(current_password, new_password, confirm_password, current_password_2):
    if not current_password or not new_password or not confirm_password:
        return {"isValid": False, "message": "Fill up empty fields."}
    if not bcrypt.checkpw(current_password.encode(), current_password_2.encode()):
        return {"isValid": False, "message": "Current password do not match."}
    if not re.search(PASSWORD_REGEX, new_password):
        return {"isValid": False, "message": "Invalid New Password."}
    if new_password != confirm_password:
        return {"isValid": False, "message": "New password do not match."}

    return {"isValid": True, "message": "Success"}


def validate_reply(description, files):
    if not description or not 10 <= len(description) <= 500:
        return {"isValid": False, "message": "Description should be 10-500 characters"}
    if not all(file and allowed_file(file.filename, ALLOWED_FILE_EXTENSIONS) for file in files):
        return {"isValid": False, "message": "The file type is not allowed"}
    if len(files) > 5:
        return {"isValid": False, "message": "You can only upload up to 5 files"}

    return {"isValid": True, "message": "Success"}


def map_tasks(task):
    assignee_ids = string_to_int_list(task.assignee)
    return {
        "taskId": task.task_id,
        "title": task.title,
        "description": task.description,
        "due": date_to_string(task.due),
        "priority": task.priority,
        "status": task.status,
        "type": task.type,
        "assignees": [map_user(x) for x in assignee_ids],
        "creator": map_user(task.creator_id)
    }


def map_sent_messages(message):
    return {
        "messageId": message.message_id,
        "sentDate": date_to_string(message.date_sent),
        "other": map_user(message.receiver_id),
        "title": message.title
    }


def map_received_messages(message):
    return {
        "messageId": message.message_id,
        "sentDate": date_to_string(message.date_sent),
        "other": map_user(message.sender_id),
        "title": message.title
    }


def map_comments(comment):
    return {
        "commentId": comment.comment_id,
        "taskId": comment.task_id,
        "description": comment.description,
        "replyId": string_to_int_list(comment.reply_id),
        "mentionsName": [get_name(x) for x in string_to_int_list(comment.mentions_id)],
        "user": map_user(comment.user_id),
        "sentDate": date_to_string(comment.date_sent),
        "likesId": string_to_int_list(comment.likes_id)
    }


def get_name(user_id):
    user = User.query.filter_by(id=user_id).first()
    return user.name if user else "UnknownUser"


def map_subtasks(subtask):
    assignee_ids = string_to_int_list(subtask.assignee)
    return {
        "subtaskId": subtask.subtask_id,
        "taskId": subtask.task_id,
        "description": subtask.description,
        "due": date_to_string(subtask.due),
        "priority": subtask.priority,
        "status": subtask.status,
        "type": subtask.type,
        "assignees": [map_user(x) for x in assignee_ids],
        "creator": map_user(subtask.creator_id)
    }


def map_checklists(checklist):
    assignee_ids = string_to_int_list(checklist.assignee)
    return {
        "checklistId": checklist.checklist_id,
        "taskId": checklist.task_id,
        "user": map_user(checklist.user_id),
        "description": checklist.description,
        "isChecked": checklist.is_checked,
        "assignees": [map_user(x) for x in assignee_ids],
        "sentDate": date_to_string(checklist.date_sent)
    }


def map_attachments(attachment):
    return {
        "attachmentId": attachment.attachment_id,
        "taskId": attachment.task_id,
        "user": map_user(attachment.user_id),
        "attachmentPath": attachment.attachment_path,
        "fileName": attachment.file_name,
        "sentDate": date_to_string(attachment.date_sent)
    }


def map_replies(reply):
    return {
        "messageReplyId": reply.message_reply_id,
        "messageId": reply.message_id,
        "sentDate": date_to_string(reply.date_sent),
        "description": reply.description,
        "fromId": reply.from_id,
        "attachmentPaths": string_to_list(reply.attachment_paths),
        "fileNames": string_to_list(reply.file_names)
    }


def get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r')
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG')
    encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii')
    return encoded_img


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def filename_secure(file, idx=""):
    return secure_filename(datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + idx + '.' + file.filename.rsplit('.', 1)[1])


def map_user(user_id):
    user = User.query.filter_by(id=user_id).first()

    if user:
        return {
            "id": user.id,
            "name": user.name,
            "image": get_response_image(user.image_path)
        }
    else:
        return {
            "id": user_id,
            "name": "UnknownUser",
            "image": get_response_image("images/deleted_user.png")
        }

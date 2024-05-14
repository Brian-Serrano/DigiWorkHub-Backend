import io
import re
from base64 import encodebytes
from datetime import datetime

import bcrypt
from PIL import Image
from firebase_admin import messaging
from typing import List, Dict, Optional, Any, Set

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from config import EMAIL_REGEX, PASSWORD_REGEX, NAME_REGEX, ALLOWED_FILE_EXTENSIONS
from db import User, Task, Message, TaskComment, Subtask, Checklist, Attachment, MessageReply


def remove_item_from_stringed_list(stringed_list: str, item: int) -> str:
    """Remove an item/id from a stringed list of items/ids

    :param stringed_list: list containing the items/ids
    :param item: item/id to remove
    :return: stringed list with the item/id removed
    """
    lst: List[int] = string_to_int_list(stringed_list)
    lst.remove(item)
    return int_list_to_string(lst)


def add_item_from_stringed_list(stringed_list: str, item: int) -> str:
    """Add an item/id from a stringed list of items/ids

    :param stringed_list: list containing the items/ids
    :param item: item/id to add
    :return: stringed list with the item/id added
    """
    lst: List[int] = string_to_int_list(stringed_list)
    lst.append(item)
    return int_list_to_string(lst)


def string_to_int_list(string: str) -> List[int]:
    """Convert stringed int list to int list"""
    return [int(x) for x in string.split(',')] if string else []


def int_list_to_string(lst: List[int]) -> str:
    """Convert int list to stringed int list"""
    return ','.join([str(x) for x in lst])


def string_to_list(string: str) -> List[str]:
    """Convert stringed list with pipe as separator to string list"""
    return string.split('|') if string else []


def list_to_string(lst: List[str]) -> str:
    """Convert string list to stringed list with pipe as separator"""
    return '|'.join(lst)


def date_to_string(date: datetime) -> str:
    """Format date to string"""
    return date.strftime("%d/%m/%Y %I:%M %p")


def string_to_date(string: str) -> datetime:
    """Parse string to date"""
    return datetime.strptime(string, "%d/%m/%Y %I:%M %p")


def validate_signup(name: str, email: str, password: str, confirm_password: str) -> Dict[str, Any]:
    """Validate signup of user

    :param name: name of user to validate
    :param email: email of user to validate
    :param password: password of user to validate
    :param confirm_password: confirm password to validate
    :return: if the signup is valid with message
    """
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


def validate_login(user: Optional[User], email: str, password: str) -> Dict[str, Any]:
    """Validate login of user

    :param user: The user or None if the user not exist
    :param email: The email to validate
    :param password: The password to validate
    :return: if the login is valid with message
    """
    if not email or not password:
        return {"isValid": False, "message": "Fill up all empty fields"}
    if not 15 <= len(email) <= 40 or not 8 <= len(password) <= 20:
        return {"isValid": False, "message": "Fill up fields with specified length"}
    if not user:
        return {"isValid": False, "message": "User not found"}
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        return {"isValid": False, "message": "Wrong password"}

    return {"isValid": True, "message": "User Logged In"}


def validate_forgot_password(user: User, code: str, password: str, confirm_password: str) -> Dict[str, Any]:
    """Validate the data when the user change password with code

    :param user: user that change password, used the forgot password code when matches the code come from client
    :param code: code that was sent to mail
    :param password: new password of user
    :param confirm_password: confirm password of user
    :return: if the new password and code is valid with message
    """
    if code != user.forgot_password_code:
        return {"isValid": False, "message": "Invalid Code"}
    if not re.search(PASSWORD_REGEX, password):
        return {"isValid": False, "message": "Invalid Password"}
    if password != confirm_password:
        return {"isValid": False, "message": "Passwords do not match"}

    return {"isValid": True, "message": "Password changed successfully."}


def validate_task(title: str, description: str, due: datetime, assignees: List[int]) -> Dict[str, Any]:
    """Validate the task information

    :param title: should be 15-100 characters
    :param description: should be 50-1000 characters
    :param due: should not be earlier than current date
    :param assignees: should range from 1 to 5
    :return: if the task information is valid with message
    """
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


def validate_message(title: str, description: str, files: List[FileStorage]) -> Dict[str, Any]:
    """Validate message send by user

    :param title: should be 15-100 characters
    :param description: should be 50-3000 characters
    :param files: should be included in allowed file extensions and not exceed 5 files
    :return: if the message information is valid with message
    """
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


def validate_comment(description: str) -> Dict[str, Any]:
    """Validate comment of task

    :param description: should be 10-500 characters
    :return: if the comment is valid with message
    """
    if not description or not 10 <= len(description) <= 500:
        return {"isValid": False, "message": "Description should be 10-500 characters"}

    return {"isValid": True, "message": "Success"}


def validate_due(due: datetime, user_id: int, creator_id: int) -> Dict[str, Any]:
    """Validate due of task/subtask

    :param due: should not be earlier than current date
    :param user_id: the user want to change due
    :param creator_id: the user created the task/subtask
    :return: if the due date is valid and user change due is the creator with message
    """
    if due.date() <= datetime.now().date():
        return {"isValid": False, "message": "Due should not be earlier than now"}
    if user_id != creator_id:
        return {"isValid": False, "message": "Only task creator can edit due date"}

    return {"isValid": True, "message": "Success"}


def validate_assignee(assignees: List[int], user_id: int, creator_id: int) -> Dict[str, Any]:
    """Validate assignees of task/subtask

    :param assignees: should range from 1 to 5
    :param user_id: the user want to change assignee
    :param creator_id: the user created the task/subtask
    :return: if the assignees are in range and the user change is the creator with message
    """
    if not 1 <= len(assignees) <= 5:
        return {"isValid": False, "message": "Assignees should range from 1 to 5"}
    if user_id != creator_id:
        return {"isValid": False, "message": "Only task creator can edit assignees"}

    return {"isValid": True, "message": "Success"}


def validate_name(title: str, user_id: int, creator_id: int) -> Dict[str, Any]:
    """Validate title/name of task

    :param title: should be 15-100 characters
    :param user_id: the user want to change title
    :param creator_id: the user created the task
    :return: if the title is valid and user change the name is the creator with message
    """
    if not title or not 15 <= len(title) <= 100:
        return {"isValid": False, "message": "Name should be 15-100 characters"}
    if user_id != creator_id:
        return {"isValid": False, "message": "Only task creator can edit name"}

    return {"isValid": True, "message": "Success"}


def validate_description(description: str, user_id: int, creator_id: int) -> Dict[str, Any]:
    """Validate description of task/subtask

    :param description: should be 50-1000 characters
    :param user_id: the user want to change description
    :param creator_id: the creator of task/subtask
    :return: if the description is valid and user change the description is the creator with message
    """
    if not description or not 50 <= len(description) <= 1000:
        return {"isValid": False, "message": "Description should be 50-1000 characters"}
    if user_id != creator_id:
        return {"isValid": False, "message": "Only task creator can edit description"}

    return {"isValid": True, "message": "Success"}


def validate_subtask(description: str, due: datetime, assignees: List[int], user_id: int, task_creator_id: int,
                     task_assignees: str) -> Dict[str, Any]:
    """Validate subtask of task

    :param description: should be 50-1000 characters
    :param due: should not be earlier than current date
    :param assignees: should range from 1 to 5
    :param user_id: the user that create the subtask of task
    :param task_creator_id: the creator of task
    :param task_assignees: the assignees of task
    :return: if the subtask is valid with message
    """
    if not description or not 50 <= len(description) <= 1000:
        return {"isValid": False, "message": "Description should be 50-1000 characters"}
    if due.date() <= datetime.now().date():
        return {"isValid": False, "message": "Due should not be earlier than now"}
    if not 1 <= len(assignees) <= 5:
        return {"isValid": False, "message": "Assignees should range from 1 to 5"}
    if user_id != task_creator_id and user_id not in string_to_int_list(task_assignees):
        return {"isValid": False, "message": "Only assignees and task creator can add subtask"}

    return {"isValid": True, "message": "Success"}


def validate_checklist(description: str, assignees: List[int], user_id: int, task_creator_id: int,
                       task_assignees: str) -> Dict[str, Any]:
    """Validate checklist of task

    :param description: should be 50-1000 characters
    :param assignees: should range from 1 to 5
    :param user_id: the user created the checklist of task
    :param task_creator_id: the user created the task
    :param task_assignees: the assignees of task
    :return:
    """
    if not description or not 50 <= len(description) <= 1000:
        return {"isValid": False, "message": "Description should be 50-1000 characters"}
    if not 1 <= len(assignees) <= 5:
        return {"isValid": False, "message": "Assignees should range from 1 to 5"}
    if user_id != task_creator_id and user_id not in string_to_int_list(task_assignees):
        return {"isValid": False, "message": "Only assignees and task creator can add checklist"}

    return {"isValid": True, "message": "Success"}


def validate_user_name(name: str) -> Dict[str, Any]:
    """Validate the name of user

    :param name: the name to validate
    :return: if the name is valid with message
    """
    if not name or not 5 <= len(name) <= 20:
        return {"isValid": False, "message": "Username should be 5-20 characters"}
    if not re.search(NAME_REGEX, name):
        return {"isValid": False, "message": "Invalid Username"}

    return {"isValid": True, "message": "Success"}


def validate_user_role(role: str) -> Dict[str, Any]:
    """Validate role of user

    :param role: the role to validate
    :return: if the role is valid with message
    """
    if not role or not 5 <= len(role) <= 50:
        return {"isValid": False, "message": "Role should be 5-50 characters"}

    return {"isValid": True, "message": "Success"}


def validate_password(current_password: str, new_password: str, confirm_password: str, current_password_2: str) -> Dict[
    str, Any]:
    """Validate password of user

    :param current_password: the current password of user from request
    :param new_password: the new password of user
    :param confirm_password: confirm password of user
    :param current_password_2: the current password of user from database, used to check if current password from request matches
    :return: if the password is valid with message
    """
    if not current_password or not new_password or not confirm_password:
        return {"isValid": False, "message": "Fill up empty fields."}
    if not bcrypt.checkpw(current_password.encode(), current_password_2.encode()):
        return {"isValid": False, "message": "Current password do not match."}
    if not re.search(PASSWORD_REGEX, new_password):
        return {"isValid": False, "message": "Invalid New Password."}
    if new_password != confirm_password:
        return {"isValid": False, "message": "New password do not match."}

    return {"isValid": True, "message": "Success"}


def validate_reply(description: str, files: List[FileStorage]) -> Dict[str, Any]:
    """Validate reply to message

    :param description: should be 10-500 characters
    :param files: should be included in allowed file extensions and not exceed 5 files
    :return: if the reply is valid with message
    """
    if not description or not 10 <= len(description) <= 500:
        return {"isValid": False, "message": "Description should be 10-500 characters"}
    if not all(file and allowed_file(file.filename, ALLOWED_FILE_EXTENSIONS) for file in files):
        return {"isValid": False, "message": "The file type is not allowed"}
    if len(files) > 5:
        return {"isValid": False, "message": "You can only upload up to 5 files"}

    return {"isValid": True, "message": "Success"}


def map_tasks(task: Task) -> Dict[str, Any]:
    """Convert task object to dictionary that can be sent as a response to the client

    :param task: Task to convert
    :return: dictionary with the task information
    """
    assignee_ids: List[int] = string_to_int_list(task.assignee)
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


def map_sent_messages(message: Message) -> Dict[str, Any]:
    """Convert sent message object to dictionary that can be sent as a response to the client

    :param message: The message to convert
    :return: dictionary with the message information
    """
    return {
        "messageId": message.message_id,
        "sentDate": date_to_string(message.date_sent),
        "other": map_user(message.receiver_id),
        "title": message.title
    }


def map_received_messages(message: Message) -> Dict[str, Any]:
    """Convert received message object to dictionary that can be sent as a response to the client

    :param message: The message to convert
    :return: dictionary with the message information
    """
    return {
        "messageId": message.message_id,
        "sentDate": date_to_string(message.date_sent),
        "other": map_user(message.sender_id),
        "title": message.title
    }


def map_comments(comment: TaskComment) -> Dict[str, Any]:
    """Convert comment object to dictionary that can be sent as a response to the client

    :param comment: The comment to convert
    :return: dictionary with the comment information
    """
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


def get_name(user_id: int) -> str:
    """Get username from user id

    :param user_id: id of user
    :return: name of user
    """
    user: Optional[User] = User.query.filter_by(id=user_id).first()
    return user.name if user else "UnknownUser"


def map_subtasks(subtask: Subtask) -> Dict[str, Any]:
    """Convert subtask object to dictionary that can be sent as a response to the client

    :param subtask: The subtask to convert
    :return: dictionary with the subtask information
    """
    assignee_ids: List[int] = string_to_int_list(subtask.assignee)
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


def map_checklists(checklist: Checklist) -> Dict[str, Any]:
    """Convert checklist object to dictionary that can be sent as a response to the client

    :param checklist: The checklist to convert
    :return: dictionary with the checklist information
    """
    assignee_ids: List[int] = string_to_int_list(checklist.assignee)
    return {
        "checklistId": checklist.checklist_id,
        "taskId": checklist.task_id,
        "user": map_user(checklist.user_id),
        "description": checklist.description,
        "isChecked": checklist.is_checked,
        "assignees": [map_user(x) for x in assignee_ids],
        "sentDate": date_to_string(checklist.date_sent)
    }


def map_attachments(attachment: Attachment) -> Dict[str, Any]:
    """Convert attachment object to dictionary that can be sent as a response to the client

    :param attachment: The attachment to convert
    :return: dictionary with the attachment information
    """
    return {
        "attachmentId": attachment.attachment_id,
        "taskId": attachment.task_id,
        "user": map_user(attachment.user_id),
        "attachmentPath": attachment.attachment_path,
        "fileName": attachment.file_name,
        "sentDate": date_to_string(attachment.date_sent)
    }


def map_replies(reply: MessageReply) -> Dict[str, Any]:
    """Convert message reply object to dictionary that can be sent as a response to the client

    :param reply: The reply to convert
    :return: dictionary with the reply information
    """
    return {
        "messageReplyId": reply.message_reply_id,
        "messageId": reply.message_id,
        "sentDate": date_to_string(reply.date_sent),
        "description": reply.description,
        "fromId": reply.from_id,
        "attachmentPaths": string_to_list(reply.attachment_paths),
        "fileNames": string_to_list(reply.file_names)
    }


def get_response_image(image_path: str) -> str:
    """Get base64 encoded image from image path

    :param image_path: The path of image to convert
    :return: base64 encoded image
    """
    pil_img: Image = Image.open(image_path, mode='r')
    byte_arr: io.BytesIO = io.BytesIO()
    pil_img.save(byte_arr, format='PNG')
    encoded_img: str = encodebytes(byte_arr.getvalue()).decode('ascii')
    return encoded_img


def allowed_file(filename: str, allowed_extensions: Set[str]) -> bool:
    """Check if the file is included in allowed file extensions

    :param filename: The file name of file
    :param allowed_extensions: The file extensions
    :return: true if the file is included in allowed file extensions, false otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def filename_secure(file: FileStorage, idx: str = "") -> str:
    """Create file name (date when uploaded) for attachment/image

    :param file: the file, needs the file extension
    :param idx: (Optional) string that appended when the created file name is the same with other, file names of attachments should be unique (e.g. multiple attachments send and save at the same time (same date))
    :return:
    """
    return secure_filename(datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + idx + '.' + file.filename.rsplit('.', 1)[1])


def send_notification_to_assignees(title: str, body: str, assignees_id: List[int]):
    """Wrapper function for sending push notifications to users

    :param title: Title of the notification
    :param body: Body of the notification
    :param assignees_id: The users that will receive the push notification
    """
    for assignee in assignees_id:
        user: Optional[User] = User.query.filter_by(id=assignee).first()
        if user:
            notification: messaging.Message = messaging.Message(
                data={"title": title, "body": body},
                android=messaging.AndroidConfig(priority="high"),
                token=user.push_notifications_token
            )
            messaging.send(notification)


def map_user(user_id: int) -> Dict[str, Any]:
    """Get user and convert it to dictionary that can be sent as a response to the client

    :param user_id: the user to get
    :return: dictionary with the user information
    """
    user: Optional[User] = User.query.filter_by(id=user_id).first()

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
